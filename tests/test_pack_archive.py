# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for pack/unpack CLI commands and archive safety."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf.cli import _is_safe_archive_entry, _pack, _unpack  # noqa: E402
from okpf_validate import validate_pack  # noqa: E402


# ---------------------------------------------------------------------------
# _is_safe_archive_entry unit tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entry", [
    "manifest.json",
    "content/hello.md",
    "records/data.jsonl",
    "provenance/sources.json",
    "artifacts/deep/nested/file.txt",
])
def test_safe_archive_entries(entry: str) -> None:
    assert _is_safe_archive_entry(entry), f"Expected safe: {entry!r}"


@pytest.mark.parametrize("entry", [
    "../evil.txt",
    "../../root.txt",
    "content/../../../etc/passwd",
    "/absolute.txt",
    "/etc/passwd",
    "C:\\Users\\bad.txt",
    "C:/Users/bad.txt",
    "sources\\evil.txt",
    "",
    ".",
])
def test_unsafe_archive_entries(entry: str) -> None:
    assert not _is_safe_archive_entry(entry), f"Expected unsafe: {entry!r}"


def test_unsafe_archive_entry_nul_byte() -> None:
    assert not _is_safe_archive_entry("file\x00name.txt")


def test_unsafe_archive_entry_tilde_home() -> None:
    assert not _is_safe_archive_entry("~/secret.txt")


def test_unsafe_archive_entry_windows_drive_backslash() -> None:
    assert not _is_safe_archive_entry("C:\\evil.txt")


# ---------------------------------------------------------------------------
# pack command tests
# ---------------------------------------------------------------------------


def _make_minimal_pack(directory: Path) -> None:
    """Create a minimal valid pack directory in directory."""
    directory.mkdir(parents=True, exist_ok=True)
    manifest = {
        "okpf_version": "0.1.0",
        "package_id": "test-pack",
        "name": "Test Pack",
        "version": "0.1.0",
        "domain": "test",
        "license": {"type": "CC-BY-4.0"},
        "records": [{"path": "records/records.json", "format": "json"}],
    }
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    records_dir = directory / "records"
    records_dir.mkdir()
    record = [
        {
            "id": "rec-001",
            "record_type": "document_section",
            "title": "Test Record",
            "text": "This is a test record.",
            "domain": "test",
            "metadata": {},
        }
    ]
    (records_dir / "records.json").write_text(json.dumps(record), encoding="utf-8")


def test_pack_produces_valid_kpack(tmp_path: Path) -> None:
    source = tmp_path / "my-pack"
    _make_minimal_pack(source)
    output = tmp_path / "my-pack.kpack"

    result = _pack(str(source), str(output))

    assert result == 0
    assert output.is_file()

    # The produced archive must be a valid ZIP.
    assert zipfile.is_zipfile(output)

    # All entries must be safe relative paths.
    with zipfile.ZipFile(output) as zf:
        for info in zf.infolist():
            assert _is_safe_archive_entry(info.filename), f"Unsafe entry: {info.filename!r}"

    # manifest.json must be present.
    with zipfile.ZipFile(output) as zf:
        names = {info.filename for info in zf.infolist()}
    assert "manifest.json" in names


def test_pack_produces_validator_valid_kpack(tmp_path: Path) -> None:
    source = tmp_path / "my-pack"
    _make_minimal_pack(source)
    output = tmp_path / "my-pack.kpack"

    _pack(str(source), str(output))
    result = validate_pack(str(output))
    assert result.valid, [str(i) for i in result.issues]


def test_pack_hello_world_example(tmp_path: Path) -> None:
    source = REPO_ROOT / "examples" / "hello-world"
    output = tmp_path / "hello-world.kpack"

    result = _pack(str(source), str(output))

    assert result == 0
    assert output.is_file()
    assert zipfile.is_zipfile(output)

    result_v = validate_pack(str(output))
    assert result_v.valid, [str(i) for i in result_v.issues]


def test_pack_refuses_missing_manifest(tmp_path: Path) -> None:
    source = tmp_path / "no-manifest"
    source.mkdir()
    (source / "records").mkdir()
    (source / "records" / "records.json").write_text("[]", encoding="utf-8")

    output = tmp_path / "out.kpack"
    result = _pack(str(source), str(output))

    assert result != 0
    assert not output.exists()


def test_pack_refuses_nonexistent_directory(tmp_path: Path) -> None:
    result = _pack(str(tmp_path / "does-not-exist"), str(tmp_path / "out.kpack"))
    assert result != 0


def test_pack_excludes_cache_directories(tmp_path: Path) -> None:
    source = tmp_path / "my-pack"
    _make_minimal_pack(source)

    # Add files that should be excluded.
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "module.cpython-311.pyc").write_bytes(b"fake pyc")
    (source / ".pytest_cache").mkdir()
    (source / ".pytest_cache" / "v").mkdir()
    (source / ".pytest_cache" / "v" / "cache").write_bytes(b"cache")
    (source / ".venv").mkdir()
    (source / ".venv" / "bin").mkdir()
    (source / ".venv" / "bin" / "python").write_text("fake", encoding="utf-8")
    egg_dir = source / "my_pack.egg-info"
    egg_dir.mkdir()
    (egg_dir / "PKG-INFO").write_text("fake", encoding="utf-8")

    output = tmp_path / "out.kpack"
    result = _pack(str(source), str(output))

    assert result == 0
    with zipfile.ZipFile(output) as zf:
        names = {info.filename for info in zf.infolist()}

    assert not any("__pycache__" in n for n in names)
    assert not any(".pytest_cache" in n for n in names)
    assert not any(".venv" in n for n in names)
    assert not any(".egg-info" in n for n in names)


# ---------------------------------------------------------------------------
# unpack command tests
# ---------------------------------------------------------------------------


def test_unpack_produces_correct_files(tmp_path: Path) -> None:
    source = tmp_path / "my-pack"
    _make_minimal_pack(source)
    archive = tmp_path / "my-pack.kpack"
    _pack(str(source), str(archive))

    output = tmp_path / "unpacked"
    result = _unpack(str(archive), str(output))

    assert result == 0
    assert (output / "manifest.json").is_file()
    assert (output / "records" / "records.json").is_file()


def test_unpack_roundtrip_validates(tmp_path: Path) -> None:
    source = REPO_ROOT / "examples" / "hello-world"
    archive = tmp_path / "hello-world.kpack"
    _pack(str(source), str(archive))

    output = tmp_path / "unpacked"
    _unpack(str(archive), str(output))

    result = validate_pack(str(output))
    assert result.valid, [str(i) for i in result.issues]


def test_unpack_refuses_nonempty_output_without_force(tmp_path: Path) -> None:
    source = tmp_path / "my-pack"
    _make_minimal_pack(source)
    archive = tmp_path / "my-pack.kpack"
    _pack(str(source), str(archive))

    output = tmp_path / "existing"
    output.mkdir()
    (output / "existing-file.txt").write_text("existing", encoding="utf-8")

    result = _unpack(str(archive), str(output))
    assert result != 0


def test_unpack_accepts_nonempty_output_with_force(tmp_path: Path) -> None:
    source = tmp_path / "my-pack"
    _make_minimal_pack(source)
    archive = tmp_path / "my-pack.kpack"
    _pack(str(source), str(archive))

    output = tmp_path / "existing"
    output.mkdir()
    (output / "existing-file.txt").write_text("existing", encoding="utf-8")

    result = _unpack(str(archive), str(output), force=True)
    assert result == 0


def test_unpack_refuses_missing_file(tmp_path: Path) -> None:
    result = _unpack(str(tmp_path / "does-not-exist.kpack"), str(tmp_path / "out"))
    assert result != 0


def test_unpack_refuses_unsafe_zip_entries(tmp_path: Path) -> None:
    """Unpack must reject archives containing unsafe entry paths."""
    archive = tmp_path / "malicious.kpack"

    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("../evil.txt")
        zf.writestr(info, "malicious content")

    output = tmp_path / "out"
    result = _unpack(str(archive), str(output))
    assert result != 0
    # Output directory must NOT have been created with the evil file.
    assert not (tmp_path / "evil.txt").exists()


def test_unpack_refuses_absolute_path_zip_entries(tmp_path: Path) -> None:
    archive = tmp_path / "absolute.kpack"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("/absolute.txt")
        zf.writestr(info, "content")

    output = tmp_path / "out"
    result = _unpack(str(archive), str(output))
    assert result != 0


# ---------------------------------------------------------------------------
# New example pack validation tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("example_name", [
    "local-organization-knowledge",
    "software-onboarding",
    "field-repair-checklist",
])
def test_new_examples_validate(example_name: str) -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / example_name))
    assert result.valid, (example_name, [str(i) for i in result.issues])


@pytest.mark.parametrize("example_name", [
    "local-organization-knowledge",
    "software-onboarding",
    "field-repair-checklist",
])
def test_new_examples_pack_and_validate(tmp_path: Path, example_name: str) -> None:
    source = REPO_ROOT / "examples" / example_name
    archive = tmp_path / f"{example_name}.kpack"

    rc = _pack(str(source), str(archive))
    assert rc == 0, f"pack command failed for {example_name}"

    result = validate_pack(str(archive))
    assert result.valid, (example_name, [str(i) for i in result.issues])
