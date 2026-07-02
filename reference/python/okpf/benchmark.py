# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""`okpf benchmark`: measure OKPF against naive alternatives it should beat.

Implements the automatable subset of docs/benchmark-plan.md against a real
pack: attribution completeness (Q1), ingestion ambiguity (Q3), and
validator-caught structural errors (Q7). Retrieval accuracy and
hallucination-rate benchmarks (Q4, Q5) require a RAG/eval harness and are
explicitly out of scope here — this module does not overclaim them.

Naive alternatives are generated with the existing `okpf compare-layout`
command (markdown-folder/, jsonl-only/records.jsonl) rather than a second,
divergent implementation, so the benchmark always compares against what
that command actually produces.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from okpf import export
from okpf_validate import validate_pack

# The ingestion questions a loader must answer before using a knowledge
# source. Kept small and concrete rather than exhaustive -- see
# docs/benchmark-plan.md Q3.
INGESTION_QUESTIONS = (
    "package identity",
    "license",
    "domain",
    "version",
    "AI/RAG usage permission",
)


@dataclass
class AlternativeMetrics:
    name: str
    attribution_completeness: float
    lineage_completeness: float
    ingestion_questions_answered: int
    ingestion_questions_total: int
    validator_note: str = "not applicable (no validator exists for this format)"

    @property
    def ingestion_questions_requiring_guessing(self) -> int:
        return self.ingestion_questions_total - self.ingestion_questions_answered


@dataclass
class BenchmarkResult:
    pack_path: str
    okpf: AlternativeMetrics
    alternatives: list[AlternativeMetrics] = field(default_factory=list)
    validator_errors: int = 0
    validator_warnings: int = 0


def run_benchmark(pack_path: str) -> BenchmarkResult:
    result = validate_pack(pack_path)
    rows = export.build_rag_rows(pack_path)

    okpf_metrics = AlternativeMetrics(
        name="OKPF pack",
        attribution_completeness=_ratio(rows, _row_has_attribution),
        lineage_completeness=_ratio(rows, _row_has_lineage),
        ingestion_questions_answered=_okpf_ingestion_answered(pack_path),
        ingestion_questions_total=len(INGESTION_QUESTIONS),
        validator_note=f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)",
    )

    with tempfile.TemporaryDirectory(prefix="okpf_benchmark_") as tmp:
        from okpf.cli import _compare_layout  # local import: avoid a cli<->benchmark import cycle

        output_dir = Path(tmp)
        with contextlib.redirect_stdout(io.StringIO()):
            _compare_layout(pack_path, str(output_dir))

        alternatives = [
            _markdown_folder_metrics(output_dir / "markdown-folder"),
            _jsonl_only_metrics(output_dir / "jsonl-only" / "records.jsonl"),
        ]

    return BenchmarkResult(
        pack_path=pack_path,
        okpf=okpf_metrics,
        alternatives=alternatives,
        validator_errors=len(result.errors),
        validator_warnings=len(result.warnings),
    )


def _ratio(rows: list[dict[str, Any]], predicate) -> float:
    if not rows:
        return 0.0
    return round(100 * sum(1 for row in rows if predicate(row)) / len(rows), 1)


def _row_has_attribution(row: dict[str, Any]) -> bool:
    license_present = bool(row.get("license"))
    citation_present = bool(row.get("citation"))
    return license_present and citation_present


def _row_has_lineage(row: dict[str, Any]) -> bool:
    return bool(row.get("provenance"))


def _okpf_ingestion_answered(pack_path: str) -> int:
    manifest, _ = _load_manifest_only(pack_path)
    if manifest is None:
        return 0
    checks = (
        bool(manifest.get("package_id") or manifest.get("id")),
        bool(isinstance(manifest.get("license"), dict) and manifest["license"]),
        bool(manifest.get("domain")),
        bool(manifest.get("version")),
        isinstance(manifest.get("usage_policy"), dict) and "allow_rag" in manifest["usage_policy"],
    )
    return sum(1 for check in checks if check)


def _load_manifest_only(pack_path: str):
    from okpf_validate import load_manifest

    return load_manifest(pack_path)


def _markdown_folder_metrics(folder: Path) -> AlternativeMetrics:
    files = sorted(folder.glob("*.md")) if folder.is_dir() else []

    def pct(predicate) -> float:
        if not files:
            return 0.0
        return round(100 * sum(1 for f in files if predicate(f)) / len(files), 1)

    # _front_matter_has_key already implies YAML front matter is present, so
    # no separate has-front-matter filter is needed first.
    attribution = pct(lambda f: _front_matter_has_key(f, ("author", "creator", "license")))
    lineage = pct(lambda f: _front_matter_has_key(f, ("source", "provenance")))

    # A flat folder of Markdown files carries no package-level manifest, so
    # none of the ingestion questions are answered by inspection alone --
    # even where a single file has its own YAML front matter, there is no
    # single declared source of truth for the whole folder.
    return AlternativeMetrics(
        name="Plain Markdown folder",
        attribution_completeness=attribution,
        lineage_completeness=lineage,
        ingestion_questions_answered=0,
        ingestion_questions_total=len(INGESTION_QUESTIONS),
    )


def _front_matter_has_key(path: Path, keys: tuple[str, ...]) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end == -1:
        return False
    front_matter = text[4:end]
    return any(f"{key}:" in front_matter for key in keys)


def _jsonl_only_metrics(records_path: Path) -> AlternativeMetrics:
    if not records_path.is_file():
        return AlternativeMetrics(
            name="JSONL-only",
            attribution_completeness=0.0,
            lineage_completeness=0.0,
            ingestion_questions_answered=0,
            ingestion_questions_total=len(INGESTION_QUESTIONS),
        )

    records = []
    for line in records_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    attribution = _ratio(records, lambda r: any(k in r for k in ("creator", "author", "license", "attribution")))
    lineage = _ratio(records, lambda r: any(k in r for k in ("provenance", "source", "source_id")))

    # A bare JSONL file has no package manifest, so identity/license/version/
    # usage permission are unanswerable by inspection. `domain` is the one
    # exception: it's a required field on every OKPF record, so it survives
    # even a naive JSONL-only export.
    domain_present = bool(records) and all("domain" in r for r in records)

    return AlternativeMetrics(
        name="JSONL-only",
        attribution_completeness=attribution,
        lineage_completeness=lineage,
        ingestion_questions_answered=1 if domain_present else 0,
        ingestion_questions_total=len(INGESTION_QUESTIONS),
    )


def format_report(result: BenchmarkResult) -> str:
    lines = [
        f"OKPF Benchmark: {result.pack_path}",
        "Comparing against naive alternatives generated by `okpf compare-layout`.",
        "See docs/benchmark-plan.md for methodology (Q1, Q3, Q7) and docs/rag-export.md",
        "for how attribution/lineage are computed per row. Retrieval accuracy and",
        "hallucination-rate benchmarks (Q4, Q5) require a RAG/eval harness and are not",
        "measured here.",
        "",
    ]

    columns = [result.okpf, *result.alternatives]
    header = f"{'Metric':<42}" + "".join(f"{c.name:>22}" for c in columns)
    lines.append(header)
    lines.append("-" * len(header))

    def row(label: str, values: list[str]) -> str:
        return f"{label:<42}" + "".join(f"{v:>22}" for v in values)

    lines.append(row("attribution completeness", [f"{c.attribution_completeness}%" for c in columns]))
    lines.append(row("source lineage completeness", [f"{c.lineage_completeness}%" for c in columns]))
    lines.append(row("ingestion decisions requiring guessing", [str(c.ingestion_questions_requiring_guessing) for c in columns]))

    # Validator notes are free text (not a short number), so they get their
    # own section rather than breaking the fixed-width table above.
    lines.append("")
    lines.append("validator-caught structural issues:")
    for c in columns:
        lines.append(f"  {c.name}: {c.validator_note}")

    return "\n".join(lines)


def to_json(result: BenchmarkResult) -> dict[str, Any]:
    def metrics_dict(m: AlternativeMetrics) -> dict[str, Any]:
        return {
            "name": m.name,
            "attribution_completeness_pct": m.attribution_completeness,
            "source_lineage_completeness_pct": m.lineage_completeness,
            "ingestion_questions_answered": m.ingestion_questions_answered,
            "ingestion_questions_total": m.ingestion_questions_total,
            "ingestion_questions_requiring_guessing": m.ingestion_questions_requiring_guessing,
            "validator_note": m.validator_note,
        }

    return {
        "pack_path": result.pack_path,
        "okpf": metrics_dict(result.okpf),
        "alternatives": [metrics_dict(a) for a in result.alternatives],
        "validator_errors": result.validator_errors,
        "validator_warnings": result.validator_warnings,
    }
