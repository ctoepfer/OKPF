# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Experimental, offline comparison of explicitly declared institutional variables."""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from okpf.institutional import validate_institutional_pack
from okpf_validate import DirectoryReader, ValidationResult, ZipReader, _is_safe_path

VARIABLES = (
    "resource_type", "authority_concentration", "exit_barrier", "credential_custody",
    "feedback_cadence",
)
UNKNOWN = {"unknown", "not_observed", "not_established", "not_yet_checked"}


class ReviewError(ValueError):
    """Input cannot support a validated comparison."""


@dataclass(frozen=True)
class CaseMatch:
    path: str
    case: dict[str, Any]
    variables: dict[str, str | None]
    matching: tuple[str, ...]
    compared: tuple[str, ...]


def _value(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip() or value.strip().lower() in UNKNOWN:
        return None
    return value.strip()


def parse_proposal(text: str) -> dict[str, Any]:
    """Read a YAML front matter block or explicit `- variable: value` lines.

    Free prose is never treated as an assertion about authority or custody.
    Conflicting duplicate declarations are rejected, including in YAML.
    """
    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader: Any, node: Any, deep: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ReviewError("Proposal keys must be unique strings")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            raise ReviewError("Unclosed YAML front matter")
        try:
            proposal = yaml.load("\n".join(lines[1:end]), Loader=UniqueLoader)
        except yaml.YAMLError as exc:
            raise ReviewError(f"Invalid proposal YAML: {exc}") from exc
    else:
        proposal = {}
        fence: str | None = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("```", "~~~")):
                marker = stripped[:3]
                if fence is None:
                    fence = marker
                elif marker == fence:
                    fence = None
                continue
            if fence is not None:
                continue
            match = re.fullmatch(r"\s*-?\s*([a-z_]+):\s*(.*?)\s*", line)
            if match and match[1] in VARIABLES:
                if match[1] in proposal:
                    raise ReviewError(f"Duplicate proposal declaration: {match[1]}")
                proposal[match[1]] = match[2]
    if not isinstance(proposal, dict):
        raise ReviewError("Proposal front matter must be an object")
    for key in VARIABLES:
        if key in proposal and not isinstance(proposal[key], str):
            raise ReviewError(f"{key} must be a string (use 'unknown' for missing evidence)")
    tags = proposal.get("boundary_conditions")
    if tags is not None and (not isinstance(tags, list) or
                             any(not isinstance(tag, str) or not tag.strip() for tag in tags)):
        raise ReviewError("boundary_conditions must be an array of nonblank strings")
    stakeholders = proposal.get("stakeholders", [])
    if not isinstance(stakeholders, list):
        raise ReviewError("stakeholders must be an array")
    for row in stakeholders:
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip()
                                           for k in ("group", "discretion", "residual_risk")):
            raise ReviewError("Each stakeholder needs group, discretion, and residual_risk strings")
    return proposal


def _variables(case: dict[str, Any]) -> dict[str, str | None]:
    topology = case["topology"]
    # Do not infer concentration from a maintainer count, or custody from prose.
    return {key: _value(topology.get(key)) for key in VARIABLES}


def load_cases(pack_path: str | Path) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    result = validate_institutional_pack(pack_path)
    if not result.valid:
        raise ReviewError("Institutional pack is invalid:\n" + "\n".join(map(str, result.errors)))
    path = Path(pack_path)
    validation = ValidationResult(str(path))
    reader = DirectoryReader(path) if path.is_dir() else ZipReader(path, validation)
    try:
        if validation.errors:
            raise ReviewError("Unsafe archive")
        manifest = json.loads(reader.read_text("manifest.json"))
        cases = []
        for name in sorted(reader.iter_paths()):
            if not name.startswith("cases/") or Path(name).suffix.lower() not in {".json", ".yaml", ".yml"}:
                continue
            if not _is_safe_path(name) or not reader.exists(name):
                raise ReviewError(f"Unsafe case path: {name}")
            text = reader.read_text(name)
            case = json.loads(text) if Path(name).suffix.lower() == ".json" else yaml.safe_load(text)
            cases.append((name, case))
        return manifest, cases
    finally:
        reader.close()


def match_cases(proposal: dict[str, Any], cases: list[tuple[str, dict[str, Any]]]) -> list[CaseMatch]:
    matches = []
    for path, case in cases:
        variables = _variables(case)
        compared = tuple(key for key in VARIABLES if _value(proposal.get(key)) is not None
                         and variables[key] is not None)
        matching = tuple(key for key in compared if _value(proposal[key]) == variables[key])
        matches.append(CaseMatch(path, case, variables, matching, compared))
    # More explicit matches first, then coverage, then stable identity. Unknowns
    # neither match nor disagree. This is an unweighted count, not a probability.
    return sorted(matches, key=lambda m: (-len(m.matching), -len(m.compared), m.case["id"]))


def _md(value: Any) -> str:
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False)
    escaped = re.sub(r"([\\`*{}\[\]()#+!|])", r"\\\1", value.replace("\n", " "))
    return html.escape(escaped, quote=False)


def _detail_lines(label: str, value: Any) -> list[str]:
    lines = ["", f"**{label}**", ""]
    if isinstance(value, dict):
        lines.extend(f"- {_md(key)}: {_md(item)}" for key, item in value.items())
    elif isinstance(value, list):
        lines.extend(f"- {_md(item)}" for item in value)
        if not value:
            lines.append("None recorded.")
    else:
        lines.append(_md(value))
    return lines


def review_pack(pack_path: str | Path, proposal_path: str | Path, limit: int = 3) -> str:
    if not 1 <= limit <= 20:
        raise ReviewError("limit must be between 1 and 20")
    proposal = parse_proposal(Path(proposal_path).read_text(encoding="utf-8"))
    manifest, cases = load_cases(pack_path)
    ranked = match_cases(proposal, cases)
    lines = ["# Institutional review (experimental)", "",
             "Declared-input comparison only; not causal inference, prediction, or independent review.",
             f"Pack: {_md(manifest.get('package_id', manifest.get('id')))} v{_md(manifest['version'])}",
             "", "## Detected Topology & Invariants", "",
             "Explicit declarations only; invariance across settings is not established.", "",
             "| Variable | Proposal declaration |", "|---|---|"]
    for key in VARIABLES:
        lines.append(f"| {key} | {_md(_value(proposal.get(key)) or 'unknown / not declared')} |")
    lines += ["", "## Closest Structural Post-Mortems", "",
              "Ranking: exact matching fields, then compared-field coverage, then case ID. "
              "Unknowns never count as matches; no calibrated similarity score."]
    if not any(m.matching for m in ranked):
        lines += ["", "Abstain: no positive declared-variable match. Cases below are context only."]
    for match in ranked[:limit]:
        case = match.case
        lines += ["", f"### {_md(case['canonical_name'])} ({_md(case['id'])})",
                  f"Source file: {_md(match.path)}. Matches: {len(match.matching)}; "
                  f"compared: {len(match.compared)}/{len(VARIABLES)}.",
                  f"Matching fields: {_md(', '.join(match.matching) or 'none')}.",
                  f"Review status: {_md(case.get('review_status', 'not documented'))}",
                  f"Case scope: {_md(case.get('example_note', 'not supplied'))}"]
        for label, value in (
            ("Intervention", case["intervention"]),
            ("Telemetry / outcomes", case.get("telemetry", case.get("outcomes"))),
            ("Perspectives (source assertions)", case["perspectives"]),
            ("Unobserved variables", case["unobserved_variables"]),
            ("Recorded divergences", case.get("structural_divergences", [])),
            ("Evidence citations (not fetched)", case.get("evidence_sources", "not supplied")),
        ):
            lines.extend(_detail_lines(label, value))
    lines += ["", "## Boundary Condition Mismatch Warning", ""]
    for match in ranked[:limit]:
        for key in VARIABLES:
            target, prior = _value(proposal.get(key)), match.variables[key]
            if target is None or prior is None:
                lines.append(f"- {_md(match.case['id'])}: {key} comparison unavailable; "
                             "do not assume equivalence.")
            elif target != prior:
                lines.append(f"- {_md(match.case['id'])}: {key} differs: proposal {_md(target)}; "
                             f"precedent {_md(prior)}. Transfer requires separate justification.")
    rules = json.loads(Path(__file__).with_name("mismatch_rules.json").read_text(encoding="utf-8"))
    for rule in rules["rules"]:
        key = rule["variable"]
        if any(key in match.compared and key not in match.matching for match in ranked[:limit]):
            lines.append(f"- Rule {key}: {_md(rule['warning'])}")
    prior_tags = set(manifest["institutional_profile"]["boundary_conditions"])
    if "boundary_conditions" not in proposal:
        lines.append("- Proposal boundary conditions not declared; comparison unavailable.")
    else:
        target_tags = set(proposal["boundary_conditions"])
        lines.append(f"- Proposal-only tags: {_md(sorted(target_tags - prior_tags))}.")
        lines.append(f"- Pack-only tags: {_md(sorted(prior_tags - target_tags))}.")
        lines.append("- Absent tags mean undocumented conditions, not evidence that a condition is false.")
    lines += [f"- Pack sampling frame: {_md(manifest['institutional_profile']['sampling_frame'])}.",
              "- Speed of defection and geographic enforcement are not inferred from domain labels.",
              "", "## Distributional Stakeholder Matrix", "",
              "Proposal assertions only; completeness and distributional effects are not verified.", "",
              "| Group | Discretion | Residual risk |", "|---|---|---|"]
    rows = proposal.get("stakeholders", [])
    if not rows:
        lines.append("| Unknown | Not declared | Not declared; affected groups require investigation |")
    for row in rows:
        lines.append("| " + " | ".join(_md(row[k]) for k in
                                       ("group", "discretion", "residual_risk")) + " |")
    return "\n".join(lines) + "\n"
