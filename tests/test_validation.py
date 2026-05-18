from __future__ import annotations

import json
from pathlib import Path

from okpf_prep.models import OKPFRecord
from okpf_prep.profiles import load_profile
from okpf_prep.validation import validate_records, validate_records_json

PROFILES_DIR = Path(__file__).parent.parent / "profiles"


def _profile():
    return load_profile(PROFILES_DIR / "brewing_recipe.yaml")


def _valid_record_json(record_type: str = "ingredient_reference") -> str:
    return json.dumps({
        "records": [{
            "type": record_type,
            "title": "Cascade Hops",
            "summary": "Classic American hop.",
            "content": "Floral, citrusy.",
            "source_refs": [{"source_file": "notes.md", "chunk_id": "chunk-0000"}],
            "confidence": 0.9,
        }]
    })


def test_valid_records_json_passes():
    profile = _profile()
    records, result = validate_records_json(_valid_record_json(), profile)
    assert result.valid
    assert len(records) == 1
    assert records[0].type == "ingredient_reference"


def test_invalid_json_fails():
    profile = _profile()
    _, result = validate_records_json("not json", profile)
    assert not result.valid
    assert any("JSON" in e for e in result.errors)


def test_missing_records_key_fails():
    profile = _profile()
    _, result = validate_records_json(json.dumps({"data": []}), profile)
    assert not result.valid


def test_disallowed_record_type_fails():
    profile = _profile()
    _, result = validate_records_json(_valid_record_json("forbidden_type"), profile)
    assert not result.valid
    assert any("forbidden_type" in e for e in result.errors)


def test_missing_title_fails():
    profile = _profile()
    raw = json.dumps({"records": [{"type": "recipe", "summary": "ok", "confidence": 0.8,
                                   "source_refs": [{"source_file": "f", "chunk_id": "c"}]}]})
    _, result = validate_records_json(raw, profile)
    assert not result.valid
    assert any("title" in e for e in result.errors)


def test_missing_confidence_fails():
    profile = _profile()
    raw = json.dumps({"records": [{"type": "recipe", "title": "t", "summary": "s",
                                   "source_refs": [{"source_file": "f", "chunk_id": "c"}]}]})
    _, result = validate_records_json(raw, profile)
    assert not result.valid
    assert any("confidence" in e for e in result.errors)


def test_missing_source_refs_fails():
    profile = _profile()
    raw = json.dumps({"records": [{"type": "recipe", "title": "t", "summary": "s",
                                   "confidence": 0.9}]})
    _, result = validate_records_json(raw, profile)
    assert not result.valid
    assert any("source_refs" in e for e in result.errors)


def test_validate_records_objects():
    profile = _profile()
    records = [OKPFRecord(
        type="recipe",
        title="My IPA",
        summary="A nice IPA.",
        source_refs=[{"source_file": "notes.md", "chunk_id": "chunk-0000"}],
        confidence=0.9,
    )]
    result = validate_records(records, profile)
    assert result.valid


def test_validate_records_rejects_bad_type():
    profile = _profile()
    records = [OKPFRecord(type="bad_type", title="t", summary="s", confidence=0.9,
                          source_refs=[{"source_file": "f", "chunk_id": "c"}])]
    result = validate_records(records, profile)
    assert not result.valid
