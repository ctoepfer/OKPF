# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for the okpf init/add/fix/explain CLI commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf.cli import _add, _explain, _fix, _init  # noqa: E402
from okpf_validate import validate_pack  # noqa: E402


def _init_defaults(dest: Path, *, template_id: str = "minimal", force: bool = False) -> int:
    return _init(
        str(dest),
        template_id=template_id,
        package_id=None,
        name=None,
        domain=None,
        license_type=None,
        creator_name=None,
        version=None,
        force=force,
    )


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def test_init_creates_a_valid_pack(tmp_path: Path) -> None:
    dest = tmp_path / "new-pack"
    assert _init_defaults(dest) == 0
    result = validate_pack(str(dest))
    assert result.valid


def test_init_refuses_non_empty_destination_without_force(tmp_path: Path) -> None:
    dest = tmp_path / "occupied"
    dest.mkdir()
    (dest / "existing.txt").write_text("hi", encoding="utf-8")

    assert _init_defaults(dest) == 1
    assert not (dest / "manifest.json").exists()


def test_init_writes_into_non_empty_destination_with_force(tmp_path: Path) -> None:
    dest = tmp_path / "occupied"
    dest.mkdir()
    (dest / "existing.txt").write_text("hi", encoding="utf-8")

    assert _init_defaults(dest, force=True) == 0
    assert (dest / "manifest.json").exists()


def test_init_unknown_template_fails_cleanly(tmp_path: Path) -> None:
    dest = tmp_path / "bad-template"
    assert _init_defaults(dest, template_id="does-not-exist") == 1
    assert not dest.exists() or not any(dest.iterdir())


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------


def test_add_appends_artifact_with_sha256_and_preserves_other_fields(tmp_path: Path) -> None:
    pack_dir = tmp_path / "pack"
    _init_defaults(pack_dir)

    manifest_before = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))

    extra_file = tmp_path / "extra.md"
    extra_file.write_text("# Extra", encoding="utf-8")

    assert _add(
        str(pack_dir), str(extra_file),
        role="reference", mime_type="text/markdown", title="Extra", description=None,
        section="artifacts", force=False,
    ) == 0

    manifest_after = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))

    # Unrelated top-level fields survive untouched.
    for key, value in manifest_before.items():
        if key != "artifacts":
            assert manifest_after[key] == value

    new_entry = next(e for e in manifest_after["artifacts"] if e["path"] == "artifacts/extra.md")
    assert new_entry["role"] == "reference"
    assert new_entry["type"] == "text/markdown"
    assert new_entry["title"] == "Extra"
    assert len(new_entry["sha256"]) == 64

    assert (pack_dir / "artifacts" / "extra.md").is_file()
    result = validate_pack(str(pack_dir))
    assert result.valid


def test_add_missing_file_fails(tmp_path: Path) -> None:
    pack_dir = tmp_path / "pack"
    _init_defaults(pack_dir)

    assert _add(
        str(pack_dir), str(tmp_path / "does-not-exist.md"),
        role=None, mime_type=None, title=None, description=None,
        section="artifacts", force=False,
    ) == 1


def test_add_duplicate_path_requires_force(tmp_path: Path) -> None:
    pack_dir = tmp_path / "pack"
    _init_defaults(pack_dir)

    extra_file = tmp_path / "guide.md"
    extra_file.write_text("# Guide v2", encoding="utf-8")

    # `minimal` template already declares artifacts/guide.md.
    assert _add(
        str(pack_dir), str(extra_file),
        role=None, mime_type=None, title=None, description=None,
        section="artifacts", force=False,
    ) == 1

    assert _add(
        str(pack_dir), str(extra_file),
        role=None, mime_type=None, title=None, description=None,
        section="artifacts", force=True,
    ) == 0


# ---------------------------------------------------------------------------
# fix
# ---------------------------------------------------------------------------


def _write_legacy_pack(pack_dir: Path) -> None:
    pack_dir.mkdir(parents=True)
    (pack_dir / "content").mkdir()
    (pack_dir / "content" / "hello.md").write_text("hello", encoding="utf-8")
    manifest = {
        "okpf_version": "0.1.0",
        "id": "legacy-pack",
        "name": "Legacy Pack",
        "version": "0.1.0",
        "domain": "general",
        "license": {"type": "CC-BY-4.0"},
        "content": [{"path": "content/hello.md", "type": "text/markdown"}],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def test_fix_is_additive_and_preserves_legacy_fields(tmp_path: Path) -> None:
    pack_dir = tmp_path / "legacy"
    _write_legacy_pack(pack_dir)

    assert _fix(str(pack_dir)) == 0

    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["id"] == "legacy-pack"
    assert manifest["package_id"] == "legacy-pack"
    assert manifest["content"]
    assert manifest["artifacts"]
    assert manifest["artifacts"][0]["sha256"]

    result = validate_pack(str(pack_dir))
    assert result.valid


def test_fix_dry_run_does_not_write(tmp_path: Path) -> None:
    pack_dir = tmp_path / "legacy"
    _write_legacy_pack(pack_dir)
    before = (pack_dir / "manifest.json").read_text(encoding="utf-8")

    assert _fix(str(pack_dir), dry_run=True) == 0

    after = (pack_dir / "manifest.json").read_text(encoding="utf-8")
    assert before == after


def test_fix_is_idempotent(tmp_path: Path) -> None:
    pack_dir = tmp_path / "legacy"
    _write_legacy_pack(pack_dir)

    assert _fix(str(pack_dir)) == 0
    first_pass = (pack_dir / "manifest.json").read_text(encoding="utf-8")

    assert _fix(str(pack_dir)) == 0
    second_pass = (pack_dir / "manifest.json").read_text(encoding="utf-8")

    assert first_pass == second_pass


def test_fix_no_changes_needed_once_already_fixed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pack_dir = tmp_path / "modern"
    _init_defaults(pack_dir)

    assert _fix(str(pack_dir)) == 0  # first pass: backfills missing sha256
    capsys.readouterr()

    assert _fix(str(pack_dir)) == 0  # second pass: nothing left to fix
    captured = capsys.readouterr()
    assert "No fixes needed" in captured.out


# ---------------------------------------------------------------------------
# explain
# ---------------------------------------------------------------------------


def test_explain_valid_pack_reports_no_issues(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pack_dir = tmp_path / "pack"
    _init_defaults(pack_dir)

    assert _explain(str(pack_dir)) == 0
    captured = capsys.readouterr()
    assert "valid with no issues" in captured.out


def test_explain_surfaces_known_and_unknown_issues(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pack_dir = tmp_path / "legacy"
    _write_legacy_pack(pack_dir)

    exit_code = _explain(str(pack_dir))
    captured = capsys.readouterr()

    assert exit_code == 0  # legacy fields are warnings, not errors
    assert "package_id" in captured.out
    assert "->" in captured.out  # every issue gets an explanation line


def test_explain_missing_manifest_is_an_error(tmp_path: Path) -> None:
    pack_dir = tmp_path / "empty"
    pack_dir.mkdir()

    assert _explain(str(pack_dir)) == 1
