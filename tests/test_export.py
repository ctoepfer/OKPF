# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for the okpf.rag_export.v0.1 contract (export.py + CLI commands)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import export  # noqa: E402
from okpf.cli import _export_citations, _export_rag  # noqa: E402

CONTRACT_FIELDS = {
    "schema_version", "chunk_id", "text", "package_id", "package_version",
    "domain", "artifact_path", "artifact_role", "record_id", "source_path",
    "license", "usage_policy", "provenance", "citation", "sha256",
}


def _assert_row_is_contract_conformant(row: dict) -> None:
    assert set(row.keys()) == CONTRACT_FIELDS
    assert row["schema_version"] == "okpf.rag_export.v0.1"
    assert isinstance(row["chunk_id"], str) and row["chunk_id"]
    assert isinstance(row["text"], str) and row["text"]
    assert isinstance(row["package_id"], str) and row["package_id"]
    assert isinstance(row["license"], dict)
    assert isinstance(row["usage_policy"], dict)
    assert isinstance(row["provenance"], dict)
    assert isinstance(row["citation"], str) and row["citation"]
    assert row["sha256"] == hashlib.sha256(row["text"].encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# records-first chunking
# ---------------------------------------------------------------------------


def test_records_first_export_on_software_onboarding() -> None:
    rows = export.build_rag_rows(str(REPO_ROOT / "examples" / "software-onboarding"))

    assert len(rows) == 5
    for row in rows:
        _assert_row_is_contract_conformant(row)
        assert row["artifact_path"] == "records/onboarding-checklist.jsonl"
        assert row["artifact_role"] is None
        assert row["record_id"] is not None

    chunk_ids = [row["chunk_id"] for row in rows]
    assert len(chunk_ids) == len(set(chunk_ids)), "chunk_ids must be unique"


def test_chunk_id_is_deterministic_across_calls() -> None:
    rows_a = export.build_rag_rows(str(REPO_ROOT / "examples" / "software-onboarding"))
    rows_b = export.build_rag_rows(str(REPO_ROOT / "examples" / "software-onboarding"))
    assert [r["chunk_id"] for r in rows_a] == [r["chunk_id"] for r in rows_b]


def test_records_only_pack_still_exports() -> None:
    rows = export.build_rag_rows(str(REPO_ROOT / "examples" / "minimal"))
    assert len(rows) >= 1
    for row in rows:
        _assert_row_is_contract_conformant(row)


# ---------------------------------------------------------------------------
# whole-artifact fallback
# ---------------------------------------------------------------------------


def test_whole_artifact_fallback_on_hello_world() -> None:
    rows = export.build_rag_rows(str(REPO_ROOT / "examples" / "hello-world"))

    assert len(rows) == 1
    row = rows[0]
    _assert_row_is_contract_conformant(row)
    assert row["artifact_path"] == "content/hello.md"
    assert row["artifact_role"] == "guide"
    assert row["record_id"] is None
    assert row["chunk_id"] == "okpf-hello-world:content/hello.md"


def test_non_text_artifacts_are_skipped(tmp_path: Path) -> None:
    pack_dir = tmp_path / "binary-pack"
    pack_dir.mkdir()
    (pack_dir / "data.bin").write_bytes(b"\x00\x01\x02")
    manifest = {
        "okpf_version": "0.1.0",
        "package_id": "org.example.binary-pack",
        "name": "Binary Pack",
        "version": "0.1.0",
        "domain": "general",
        "license": {"type": "CC-BY-4.0"},
        "artifacts": [{"path": "data.bin", "type": "application/octet-stream"}],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    rows = export.build_rag_rows(str(pack_dir))
    assert rows == []


# ---------------------------------------------------------------------------
# provenance matching
# ---------------------------------------------------------------------------


def test_provenance_matched_by_path_for_whole_artifact_rows() -> None:
    rows = export.build_rag_rows(str(REPO_ROOT / "examples" / "hello-world"))
    # hello-world declares no provenance at all.
    assert rows[0]["provenance"] == {}
    assert rows[0]["source_path"] is None


def test_legacy_ref_style_provenance_falls_back_to_whole_object() -> None:
    rows = export.build_rag_rows(str(REPO_ROOT / "examples" / "brewing"))
    assert rows
    # examples/brewing uses {"$ref": "provenance.json"} with sources[] keyed by
    # id, not path -- no per-row match is possible, so the whole resolved
    # object should be carried instead of being silently dropped.
    assert rows[0]["provenance"]
    assert "sources" in rows[0]["provenance"] or "transformations" in rows[0]["provenance"]


# ---------------------------------------------------------------------------
# .kpack support
# ---------------------------------------------------------------------------


def test_export_reads_kpack_archives(tmp_path: Path) -> None:
    from okpf.cli import _pack

    kpack_path = tmp_path / "software-onboarding.kpack"
    assert _pack(str(REPO_ROOT / "examples" / "software-onboarding"), str(kpack_path)) == 0

    rows = export.build_rag_rows(str(kpack_path))
    assert len(rows) == 5


# ---------------------------------------------------------------------------
# citations
# ---------------------------------------------------------------------------


def test_citation_rows_match_rag_rows_minus_text() -> None:
    rag_rows = export.build_rag_rows(str(REPO_ROOT / "examples" / "software-onboarding"))
    citation_rows = export.build_citation_rows(rag_rows)

    assert len(citation_rows) == len(rag_rows)
    for rag_row, citation_row in zip(rag_rows, citation_rows):
        assert "text" not in citation_row
        assert citation_row["chunk_id"] == rag_row["chunk_id"]
        assert citation_row["citation"] == rag_row["citation"]
        assert set(citation_row.keys()) == CONTRACT_FIELDS - {"text"}


# ---------------------------------------------------------------------------
# errors
# ---------------------------------------------------------------------------


def test_missing_pack_raises_export_error() -> None:
    with pytest.raises(export.ExportError, match="Expected a package directory"):
        export.build_rag_rows("/tmp/definitely-does-not-exist-okpf-pack")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_export_rag_writes_valid_jsonl(tmp_path: Path) -> None:
    output = tmp_path / "rag.jsonl"
    assert _export_rag(str(REPO_ROOT / "examples" / "software-onboarding"), str(output)) == 0

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5
    for line in lines:
        row = json.loads(line)
        _assert_row_is_contract_conformant(row)


def test_cli_export_citations_writes_valid_jsonl_without_text(tmp_path: Path) -> None:
    output = tmp_path / "citations.jsonl"
    assert _export_citations(str(REPO_ROOT / "examples" / "software-onboarding"), str(output)) == 0

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5
    for line in lines:
        row = json.loads(line)
        assert "text" not in row
        assert row["schema_version"] == "okpf.rag_export.v0.1"


def test_cli_export_rag_missing_pack_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output = tmp_path / "rag.jsonl"
    exit_code = _export_rag(str(tmp_path / "does-not-exist"), str(output))
    assert exit_code == 1
    assert not output.exists()
    assert "[ERROR]" in capsys.readouterr().out
