from __future__ import annotations

import json
from pathlib import Path

from okpf_prep.models import OKPFRecord
from okpf_prep.package_builder import build_output_package
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
    assert records_data["records"][0]["type"] == "ingredient_reference"


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
