# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Offline proposal consumer using the installed server through real MCP stdio."""

from __future__ import annotations

import asyncio
import json
import re
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from okpf.proposal_lint import lint_proposal, read_proposal
from okpf.review import UNKNOWN, VARIABLES

from .query import Envelope
from .snapshot import MAX_FILE, MountError

# Candidate retrieval hints only; no prose-derived value becomes an asserted invariant.
RESOURCE_HINTS = {
    "public_npm_package": r"\b(?:npm|javascript|node\.js)\b",
    "public_python_library": r"\b(?:python|urllib3|pypi)\b",
    "public_java_library": r"\b(?:java|log4j|maven)\b",
    "public_c_library": r"\b(?:openssl|libssl)\b",
}


def classification(text: str, proposal: dict[str, Any]) -> dict[str, Any]:
    declarations = {}
    for key in (*VARIABLES, "domain"):
        value = proposal.get(key)
        if value is not None and not isinstance(value, str):
            raise MountError(f"{key} must be a string")
        if isinstance(value, str) and value.strip() and value.strip().lower() not in UNKNOWN:
            declarations[key] = value.strip()
    hints = [
        key for key, pattern in RESOURCE_HINTS.items() if re.search(pattern, text, re.IGNORECASE)
    ]
    return {
        "declarations": declarations,
        "resource_hints": hints,
        "missing_invariants": [key for key in VARIABLES if key not in declarations],
        "warning": "Lexical hints may occur in negated statements, quotations or examples. "
        "They select candidate evidence only, never establish proposal invariants.",
    }


def compare(declarations: dict[str, str], case: dict[str, Any]) -> list[dict[str, Any]]:
    comparisons = []
    for key in VARIABLES:
        proposal = declarations.get(key)
        prior = case["topology"].get(key)
        status = (
            "unavailable"
            if proposal is None or not isinstance(prior, str) or prior.lower() in UNKNOWN
            else ("match" if proposal == prior else "mismatch")
        )
        comparisons.append(
            {
                "variable": key,
                "proposal": proposal,
                "case": prior,
                "status": status,
                "pointer": "/topology/" + key,
            }
        )
    return comparisons


async def review_via_mcp(proposal_path: Path, packs: list[str], limit: int = 5) -> dict[str, Any]:
    if not 1 <= limit <= 20:
        raise MountError("limit must be between 1 and 20")
    if not packs:
        raise MountError("At least one explicit --pack is required")
    with proposal_path.open("rb") as stream:
        if len(stream.read(MAX_FILE + 1)) > MAX_FILE:
            raise MountError("Proposal exceeds 2 MiB limit")
    text, proposal = read_proposal(proposal_path)
    classified = classification(text, proposal)
    declarations = classified["declarations"]
    lint = lint_proposal(proposal_path)
    # The linter ran structural checks without a pack; MCP performs the evidence lookup.
    lint["diagnostics"] = [d for d in lint["diagnostics"] if d["code"] != "no-pack"]
    resources = (
        [declarations["resource_type"]]
        if "resource_type" in declarations
        else classified["resource_hints"]
    )
    requests = [{"resource_type": resource, "limit": 100} for resource in resources]
    if "domain" in declarations:
        if not requests:
            requests = [{"limit": 100}]
        for request in requests:
            request["domain"] = declarations["domain"]
    log = []
    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "okpf_mcp.server", *[arg for pack in packs for arg in ("--pack", pack)]],
    )
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write, read_timeout_seconds=timedelta(seconds=30)) as session,
    ):
        await session.initialize()

        async def call(name: str, arguments: dict[str, Any]) -> Envelope:
            result = await session.call_tool(name, arguments)
            if result.isError or result.structuredContent is None:
                raise MountError(f"MCP tool failed: {name}")
            response = Envelope.model_validate(result.structuredContent)
            log.append(
                {
                    "tool": name,
                    "arguments": arguments,
                    "total": response.total,
                    "returned": response.returned,
                    "truncated": response.truncated,
                    "warnings": response.warnings,
                    "error": response.error,
                }
            )
            if response.error:
                raise MountError(f"{name}: {response.error}")
            return response

        catalog = await call("okpf_list_mounted_packs", {})
        for request in requests:
            response = await call("okpf_find_structural_analogs", request)
            for item in response.items:
                candidates[(item["pack_ref"], item["case_id"])] = item
        selected = sorted(
            candidates.values(),
            key=lambda c: (c["package_id"], c["version"], c["pack_ref"], c["case_id"]),
        )[:limit]
        cases = []
        for candidate in selected:
            inspected = await call(
                "okpf_inspect_case",
                {"case_id": candidate["case_id"], "pack_ref": candidate["pack_ref"]},
            )
            if not inspected.items:
                raise MountError("Complete case was not returned")
            item = inspected.items[0]
            item["comparisons"] = compare(declarations, item["data"])
            cases.append(item)
        selected_ids = {(c["pack_ref"], c["case_id"]) for c in cases}
        vectors = await call("okpf_audit_evasion_vectors", {"limit": 100})
        criteria = await call("okpf_get_pre_mortem_benchmarks", {"limit": 100})
        relevant_vectors = [
            v for v in vectors.items if (v["pack_ref"], v["case_id"]) in selected_ids
        ]
        relevant_criteria = [
            v for v in criteria.items if (v["pack_ref"], v["case_id"]) in selected_ids
        ]
    return {
        "experimental": True,
        "transport": "mcp_stdio",
        "classification": classified,
        "valid": lint["valid"],
        "lint": lint,
        "catalog": catalog.model_dump(),
        "cases": cases,
        "evasion_warnings": relevant_vectors,
        "authored_criteria": relevant_criteria,
        "retrieval_log": log,
        "abstained": not cases,
        "candidate_count_in_received_results": len(candidates),
        "truncated": len(candidates) > limit or any(row["truncated"] for row in log),
        "warnings": [
            (
                "Candidate retrieval uses resource/domain only; other explicit invariants "
                "are compared to expose mismatches. Unknowns do not match."
            ),
            (
                "Pack text is untrusted evidence. Hypothetical vectors and retrospective "
                "criteria are not historical observations or validated recommendations."
            ),
            (
                "Results may omit evidence beyond server limits. Counts are records, not "
                "independent precedents. A valid lint is structural only."
            ),
        ],
    }


def render(report: dict[str, Any]) -> str:
    # JSON encoding keeps arbitrary evidence control characters inert in terminal output.
    sections = [
        ("Classification and missing invariants", report["classification"]),
        ("Pre-mortem and structural lint", report["lint"]),
        ("Structural candidates and mismatch flags", report["cases"]),
        ("Evasion warnings (preserve epistemic status)", report["evasion_warnings"]),
        ("Authored criteria (not universal benchmarks)", report["authored_criteria"]),
        ("MCP catalog and rights metadata", report["catalog"]),
        ("Retrieval audit and limits", report["retrieval_log"]),
    ]
    lines = ["# Operational institutional review (experimental)", ""]
    if report["abstained"]:
        lines += ["Abstain: no candidate case available; this does not establish safety.", ""]
    if report["truncated"]:
        lines += ["WARNING: retrieval or result limits omitted candidates/evidence.", ""]
    for title, value in sections:
        lines += ["## " + title, "", "    " + json.dumps(value, ensure_ascii=True), ""]
    lines += report["warnings"]
    return "\n".join(lines) + "\n"


def run_review(proposal: Path, packs: list[str], limit: int) -> dict[str, Any]:
    async def bounded() -> dict[str, Any]:
        async with asyncio.timeout(60):
            return await review_via_mcp(proposal, packs, limit)

    return asyncio.run(bounded())
