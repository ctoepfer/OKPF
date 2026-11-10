# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from okpf_mcp.operational_review import classification, compare, render, review_via_mcp
from okpf_mcp.snapshot import MountError

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "examples/floss-maintainer-succession"


def test_classification_never_promotes_prose_or_negation_to_invariants():
    result = classification("We reject multisig for this npm package.", {})
    assert result["declarations"] == {}
    assert result["resource_hints"] == ["public_npm_package"]
    assert "credential_custody" in result["missing_invariants"]
    assert classification("npm", {"credential_custody": "UNKNOWN"})["declarations"] == {}
    with pytest.raises(MountError):
        classification("npm", {"domain": ["not a string"]})


def test_mismatch_vs_unknown_and_untyped_legacy_fields():
    compared = compare(
        {"credential_custody": "multisig_threshold", "resource_type": "npm"},
        {
            "topology": {
                "credential_custody": "single_custody",
                "resource_type": "npm",
                "exit_barrier": {"free": True},
            }
        },
    )
    by_key = {row["variable"]: row for row in compared}
    assert by_key["credential_custody"]["status"] == "mismatch"
    assert by_key["resource_type"]["status"] == "match"
    assert by_key["exit_barrier"]["status"] == "unavailable"


def test_real_mcp_review_from_installed_consumer(tmp_path):
    async def run():
        report = await review_via_mcp(PACK / "proposals/npm-release-council.md", [str(PACK)], 5)
        assert report["valid"]
        assert not report["abstained"]
        assert report["candidate_count_in_received_results"] == 2
        assert {c["case_id"] for c in report["cases"]} == {"eventStream2018", "corejs2023"}
        assert all(c["evidence_sources"] for c in report["cases"])
        assert {v["data"]["epistemic_status"] for v in report["evasion_warnings"]} == {
            "source_reported_mechanism_analyst_category",
            "hypothetical_not_observed",
        }
        assert all(
            v["data"]["historical_precommitment"] is False for v in report["authored_criteria"]
        )
        assert {row["tool"] for row in report["retrieval_log"]} == {
            "okpf_list_mounted_packs",
            "okpf_find_structural_analogs",
            "okpf_inspect_case",
            "okpf_audit_evasion_vectors",
            "okpf_get_pre_mortem_benchmarks",
        }
        assert "hypothetical_not_observed" in render(report)
        raw = await review_via_mcp(PACK / "proposals/raw-npm-proposal.md", [str(PACK)], 1)
        assert not raw["valid"]
        assert raw["truncated"]
        assert raw["classification"]["declarations"] == {}
        assert raw["cases"]
        assert all(row["status"] == "unavailable" for row in raw["cases"][0]["comparisons"])
        no_hints = tmp_path / "proposal.md"
        no_hints.write_text("We should improve the institution.")
        abstention = await review_via_mcp(no_hints, [str(PACK)])
        assert abstention["abstained"]
        assert abstention["cases"] == []

    asyncio.run(run())


def test_cli_review_with_child_network_guard(tmp_path):
    # Install the audit hook before importing the CLI; the MCP server spawned by
    # it is also guarded by the dedicated SDK stdio test in test_stdio.py.
    script = """
import sys
def guard(event, args):
    if event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo', 'socket.sendto'}:
        raise RuntimeError('NETWORK ATTEMPT: ' + event)
sys.addaudithook(guard)
from okpf_mcp.tool_cli import main
raise SystemExit(main())
"""
    env = {**os.environ, "OKPF_PACK_PATHS": "[]"}
    command = [
        sys.executable,
        "-c",
        script,
        "review",
        "--pack",
        str(PACK),
        "--proposal",
        str(PACK / "proposals/raw-npm-proposal.md"),
        "--json",
    ]
    result = subprocess.run(
        command, cwd=tmp_path, env=env, check=False, capture_output=True, text=True, timeout=40
    )
    assert result.returncode == 1, result.stderr
    assert json.loads(result.stdout)["transport"] == "mcp_stdio"
    assert "NETWORK ATTEMPT" not in result.stderr
    executable = Path(sys.executable).with_name("okpf-tool")
    result = subprocess.run(
        [str(executable), "review", "--proposal", str(tmp_path / "missing"), "--pack", str(PACK)],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert not result.stdout


@pytest.mark.parametrize("value", [" UNKNOWN ", " not_observed ", "", "   "])
def test_blank_or_padded_unknown_case_values_are_unavailable(value):
    compared = compare({"feedback_cadence": "monthly"}, {"topology": {"feedback_cadence": value}})
    field = next(row for row in compared if row["variable"] == "feedback_cadence")
    assert field["status"] == "unavailable"
    assert field["case"] == value  # Preserve authored evidence in the report.
