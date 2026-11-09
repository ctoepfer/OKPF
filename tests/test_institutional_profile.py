# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Institutional profile conformance and offline pack validation."""
import json
import shutil
import zipfile
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from okpf.institutional import validate_institutional_pack
from okpf_validate import validate_pack

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/institutional"
FIXTURES = ROOT / "tests/fixtures/institutional"
SCHEMAS = ROOT / "schemas/profiles/institutional/v1"


@pytest.fixture
def pack(tmp_path):
    target = tmp_path / "pack"
    shutil.copytree(EXAMPLE, target)
    manifest = json.loads((target / "manifest.json").read_text())
    # Mutation tests target profile validity independently of content hashes.
    del manifest["artifacts"][0]["sha256"]
    (target / "manifest.json").write_text(json.dumps(manifest))
    return target


def write_case(pack, case):
    (pack / "cases/floss-node-event-stream.yaml").write_text(yaml.safe_dump(case))


def read_case(pack):
    return yaml.safe_load((pack / "cases/floss-node-event-stream.yaml").read_text())


def test_seed_and_archive_validate(tmp_path):
    assert validate_pack(str(EXAMPLE)).valid
    assert validate_institutional_pack(EXAMPLE).valid
    assert validate_pack(str(EXAMPLE), strict_profile=True).valid
    archive = tmp_path / "seed.kpack"
    with zipfile.ZipFile(archive, "w") as zf:
        for path in EXAMPLE.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(EXAMPLE))
    result = validate_institutional_pack(archive)
    assert result.valid, result.errors
    assert result.records_checked == 2


@pytest.mark.parametrize("name", ["missing-shadow_practice", "missing-unobserved_variables"])
def test_invalid_fixtures(pack, name):
    case = json.loads((FIXTURES / f"{name}.json").read_text())
    schema = json.loads((SCHEMAS / "case_record.json").read_text())
    assert list(Draft202012Validator(schema).iter_errors(case))
    write_case(pack, case)
    result = validate_institutional_pack(pack)
    assert not result.valid
    assert name.removeprefix("missing-") in str(result.errors)
    assert validate_pack(str(pack)).valid  # Domain requirements do not alter Core.


@pytest.mark.parametrize("field,value", [
    ("perspectives", {}), ("unobserved_variables", []),
    ("unobserved_variables", ["   "]), ("outcomes", {}),
    ("id", "contains-hyphen"),
    ("outcomes", {1: {"status": "x", "reporting_source": "y"}}),
    ("perspectives", {"formal_charter": " ", "shadow_practice": "x",
                      "post_mortem_consensus": "x"}),
])
def test_empty_or_malformed_required_fields(pack, field, value):
    case = read_case(pack)
    case[field] = value
    write_case(pack, case)
    assert not validate_institutional_pack(pack).valid


@pytest.mark.parametrize("mutation", ["block", "profile", "year", "coding"])
def test_manifest_constraints(pack, mutation):
    path = pack / "manifest.json"
    manifest = json.loads(path.read_text())
    if mutation == "block":
        del manifest["institutional_profile"]
    elif mutation == "profile":
        manifest["profile"] = "other"
    elif mutation == "year":
        manifest["institutional_profile"]["observation_window"]["start_year"] = 2019
    else:
        manifest["institutional_profile"]["coding_standard"] = "unknown"
    path.write_text(json.dumps(manifest))
    assert not validate_institutional_pack(pack).valid


def test_unlisted_nested_json_and_duplicate_ids(pack):
    nested = pack / "cases/nested"
    nested.mkdir()
    case = read_case(pack)
    (nested / "extra.json").write_text(json.dumps(case))
    assert "Duplicate institutional case id" in str(validate_institutional_pack(pack).errors)
    case["id"] = "secondCase"
    (nested / "extra.json").write_text(json.dumps(case))
    assert validate_institutional_pack(pack).valid
    del case["perspectives"]
    (nested / "extra.json").write_text(json.dumps(case))
    assert not validate_institutional_pack(pack).valid


def test_unknown_fields_and_core_aliases(pack):
    path = pack / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["id"] = manifest.pop("package_id")
    manifest["content"] = manifest.pop("artifacts")
    manifest["okpf_version"] = "0.1"
    manifest["profiles"].append("unknown-profile")
    manifest["institutional_profile"]["future_field"] = {"anything": True}
    path.write_text(json.dumps(manifest))
    case = read_case(pack)
    case["future_case_field"] = [1, 2, 3]
    write_case(pack, case)
    assert validate_institutional_pack(pack).valid


@pytest.mark.parametrize("text", ["[broken", "!!python/object/apply:os.system ['false']", "null"])
def test_invalid_yaml_is_reported(pack, text):
    (pack / "cases/floss-node-event-stream.yaml").write_text(text)
    assert not validate_institutional_pack(pack).valid


def test_missing_cases(pack):
    shutil.rmtree(pack / "cases")
    assert not validate_institutional_pack(pack).valid


def test_symlink_escape(pack, tmp_path):
    outside = tmp_path / "outside.yaml"
    outside.write_text("invalid: [")
    (pack / "cases/escape.yaml").symlink_to(outside)
    errors = str(validate_institutional_pack(pack).errors)
    assert "Unsafe or inaccessible case path" in errors
    assert "Cannot parse case" not in errors


@pytest.mark.parametrize("unsafe", ["../evil.json", "/evil.json", "C:/evil.json", "cases/..\\evil.json"])
def test_unsafe_archive_rejected_before_reading(tmp_path, unsafe):
    archive = tmp_path / "bad.kpack"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("manifest.json", "not JSON")
        zf.writestr(unsafe, "not JSON")
    result = validate_institutional_pack(archive)
    assert "Unsafe ZIP path" in str(result.errors)
    assert result.records_checked == 0


def test_schemas_are_valid():
    for path in SCHEMAS.glob("*.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
