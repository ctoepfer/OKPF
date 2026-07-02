# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for `okpf benchmark` (reference/python/okpf/benchmark.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import benchmark  # noqa: E402
from okpf.cli import _benchmark  # noqa: E402

FLAGSHIP = str(REPO_ROOT / "examples" / "software-onboarding")


def test_okpf_beats_naive_alternatives_on_attribution_and_lineage() -> None:
    result = benchmark.run_benchmark(FLAGSHIP)

    for alt in result.alternatives:
        assert result.okpf.attribution_completeness >= alt.attribution_completeness
        assert result.okpf.lineage_completeness >= alt.lineage_completeness
        assert result.okpf.ingestion_questions_requiring_guessing <= alt.ingestion_questions_requiring_guessing

    # The flagship pack is fully attributed and requires no ingestion guessing.
    assert result.okpf.attribution_completeness == 100.0
    assert result.okpf.ingestion_questions_requiring_guessing == 0


def test_naive_alternatives_have_no_validator() -> None:
    result = benchmark.run_benchmark(FLAGSHIP)
    for alt in result.alternatives:
        assert "not applicable" in alt.validator_note


def test_markdown_folder_and_jsonl_only_alternatives_present() -> None:
    result = benchmark.run_benchmark(FLAGSHIP)
    names = {alt.name for alt in result.alternatives}
    assert names == {"Plain Markdown folder", "JSONL-only"}


def test_jsonl_only_answers_domain_question_since_it_is_a_required_record_field() -> None:
    result = benchmark.run_benchmark(FLAGSHIP)
    jsonl_only = next(alt for alt in result.alternatives if alt.name == "JSONL-only")
    # domain is a required field on every OKPF record, so it survives even
    # a naive JSONL-only export -- this should not be 0/5 guessing.
    assert jsonl_only.ingestion_questions_answered >= 1


def test_run_benchmark_does_not_crash_on_records_only_pack() -> None:
    # examples/minimal has records but no artifacts -- exercises the
    # whole-artifact-fallback-vs-records-first boundary without erroring.
    result = benchmark.run_benchmark(str(REPO_ROOT / "examples" / "minimal"))
    assert result.okpf.attribution_completeness >= 0.0


def test_format_report_is_stable_shaped_text() -> None:
    result = benchmark.run_benchmark(FLAGSHIP)
    report = benchmark.format_report(result)

    assert "attribution completeness" in report
    assert "source lineage completeness" in report
    assert "ingestion decisions requiring guessing" in report
    assert "validator-caught structural issues" in report
    assert "docs/benchmark-plan.md" in report


def test_to_json_round_trips_through_json_dumps() -> None:
    result = benchmark.run_benchmark(FLAGSHIP)
    payload = benchmark.to_json(result)
    # Must be plain-JSON-serializable -- no dataclasses/Path objects leaking through.
    json.dumps(payload)
    assert payload["pack_path"] == FLAGSHIP
    assert len(payload["alternatives"]) == 2


def test_cli_benchmark_prints_report_and_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = _benchmark(FLAGSHIP, None)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "OKPF Benchmark" in captured.out


def test_cli_benchmark_writes_json_summary(tmp_path: Path) -> None:
    output = tmp_path / "benchmark.json"
    exit_code = _benchmark(FLAGSHIP, str(output))
    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["pack_path"] == FLAGSHIP


def test_cli_benchmark_missing_pack_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = _benchmark("/tmp/definitely-does-not-exist-okpf-pack", None)
    assert exit_code == 1
    assert "[ERROR]" in capsys.readouterr().out
