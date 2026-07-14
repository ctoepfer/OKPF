from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from okpf_prep.models import OKPFRecord
from okpf_prep.package_builder import build_kpack_archive, build_output_package
from okpf_prep.profiles import load_profile

PROFILES_DIR = Path(__file__).parent.parent / "profiles"


def _profile():
    return load_profile(PROFILES_DIR / "brewing_recipe.yaml")


def _records():
    return [OKPFRecord(
        type="ingredient_reference",
        title="Cascade Hops",
        summary="Classic American hop.",
        content="Floral and citrusy.",
        source_refs=[{"source_file": "notes.md", "chunk_id": "chunk-0000"}],
        confidence=0.9,
    )]


def test_output_files_are_created(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("# Notes\n\nContent.", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="# Notes\n\nContent.",
        report={"status": "pass"},
    )

    assert paths["manifest"].exists()
    assert paths["records"].exists()
    assert paths["extracted_text"].exists()
    assert paths["report"].exists()


def test_manifest_content(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    manifest = json.loads(paths["manifest"].read_text())
    assert manifest["profile_id"] == "brewing_recipe"
    assert manifest["record_count"] == 1
    assert "okpf_version" in manifest
    assert "created_at" in manifest
    assert "generator" in manifest


def test_manifest_is_okpf_v0_1_0_conformant(tmp_path):
    """Manifest must satisfy schemas/v0.1.0/manifest.schema.json's required fields."""
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    manifest = json.loads(paths["manifest"].read_text())
    for required in ("okpf_version", "name", "version", "domain", "license"):
        assert required in manifest, f"missing required field {required!r}"
    assert manifest["package_id"]
    assert manifest["okpf_version"] == "0.1.0"
    # at least one of artifacts/records/content must be present and non-empty
    assert manifest.get("records")
    assert manifest["records"][0]["path"] == "records.json"
    assert manifest["records"][0]["format"]
    assert manifest["license"]


def test_manifest_license_defaults_when_profile_has_none(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    manifest = json.loads(paths["manifest"].read_text())
    assert manifest["license"]["type"] == "proprietary"


def test_records_json_content(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    records_data = json.loads(paths["records"].read_text())
    assert "records" in records_data
    assert len(records_data["records"]) == 1
    record = records_data["records"][0]
    assert record["record_type"] == "ingredient_reference"
    # content is kept for backward compatibility, but is not part of the
    # OKPF v0.1.0 record schema — "text" is the required field.
    assert record["content"] == "Floral and citrusy."


def test_records_json_is_okpf_v0_1_0_conformant(tmp_path):
    """Records must satisfy schemas/record.schema.json's required fields."""
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    records_data = json.loads(paths["records"].read_text())
    record = records_data["records"][0]
    for required in ("id", "record_type", "title", "text", "domain", "metadata"):
        assert required in record, f"missing required field {required!r}"
    assert record["id"]
    assert record["domain"] == "brewing"
    assert isinstance(record["metadata"], dict)
    assert record["text"] == "Floral and citrusy."


def test_records_get_sequential_ids_when_unset(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")
    records = [
        OKPFRecord(type="ingredient_reference", title="Cascade", content="A"),
        OKPFRecord(type="ingredient_reference", title="Citra", content="B"),
    ]

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=records,
        source_path=source,
        extracted_text="content",
        report={},
    )

    records_data = json.loads(paths["records"].read_text())
    ids = [r["id"] for r in records_data["records"]]
    assert ids == [f"{profile.id}-0000", f"{profile.id}-0001"]
    assert len(set(ids)) == 2


def test_extracted_text_written(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("my extracted text", encoding="utf-8")

    paths = build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=[],
        source_path=source,
        extracted_text="my extracted text",
        report={},
    )

    assert "my extracted text" in paths["extracted_text"].read_text()


def test_build_kpack_archive_creates_zip_with_manifest(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    dest = build_kpack_archive(tmp_path / "out", tmp_path / "notes.kpack")

    assert dest == tmp_path / "notes.kpack"
    assert dest.is_file()
    with zipfile.ZipFile(dest) as zf:
        names = zf.namelist()
        assert "manifest.json" in names
        assert "records.json" in names
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["okpf_version"] == "0.1.0"


def test_build_kpack_archive_rejects_missing_manifest(tmp_path):
    empty_dir = tmp_path / "empty_out"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        build_kpack_archive(empty_dir, tmp_path / "bad.kpack")


def test_build_kpack_archive_contains_only_safe_paths(tmp_path):
    profile = _profile()
    source = tmp_path / "notes.md"
    source.write_text("content", encoding="utf-8")

    build_output_package(
        output_dir=tmp_path / "out",
        profile=profile,
        records=_records(),
        source_path=source,
        extracted_text="content",
        report={},
    )

    dest = build_kpack_archive(tmp_path / "out", tmp_path / "notes.kpack")
    with zipfile.ZipFile(dest) as zf:
        for name in zf.namelist():
            assert not name.startswith("/")
            assert ".." not in name.split("/")
