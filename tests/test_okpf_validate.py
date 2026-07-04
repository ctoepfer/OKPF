from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_DIR = REPO_ROOT / "tests" / "fixtures" / "conformance"
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf_validate import validate_pack  # noqa: E402


def copy_example(tmp_path: Path, name: str) -> Path:
    src = REPO_ROOT / "examples" / name
    dst = tmp_path / name
    shutil.copytree(src, dst)
    return dst


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_valid_minimal_package() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "minimal"))
    assert result.valid
    assert result.records_checked == 1


def test_valid_conformance_fixtures_pass() -> None:
    fixture_names = [
        "minimal",
        "artifacts-only",
        "records-only",
        "legacy-content",
        "package-id",
        "legacy-id",
        "selective-disclosure",
        "unknown-fields",
    ]
    for fixture_name in fixture_names:
        result = validate_pack(str(CONFORMANCE_DIR / "valid" / fixture_name))
        assert result.valid, (fixture_name, [str(issue) for issue in result.issues])


def test_invalid_conformance_fixtures_fail() -> None:
    fixture_names = [
        "missing-manifest",
        "missing-payload",
        "unsafe-path-parent-traversal",
        "unsafe-path-absolute",
        "unsafe-path-backslash-traversal",
        "unsafe-path-windows-drive",
        "bad-okpf-version",
    ]
    for fixture_name in fixture_names:
        result = validate_pack(str(CONFORMANCE_DIR / "invalid" / fixture_name))
        assert not result.valid, fixture_name


def test_missing_manifest(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    (pack / "records").mkdir(parents=True)
    result = validate_pack(str(pack))
    assert not result.valid
    assert any(issue.location == "manifest.json" for issue in result.errors)


def test_invalid_manifest(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    del manifest["package_id"]
    write_json(pack / "manifest.json", manifest)

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("package_id" in issue.message for issue in result.errors)


def test_legacy_id_remains_valid() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "valid" / "legacy-id"))
    assert result.valid
    assert result.package_id == "org.example.conformance.legacy-id"


def test_legacy_id_without_package_id_warns() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "valid" / "legacy-id"))
    assert result.valid
    assert any("package_id" in issue.message for issue in result.warnings)


def test_legacy_content_remains_valid() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "valid" / "legacy-content"))
    assert result.valid


def test_legacy_content_without_artifacts_warns() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "valid" / "legacy-content"))
    assert result.valid
    assert any("content" in issue.location for issue in result.warnings)


def test_package_id_and_artifacts_do_not_trigger_legacy_warnings() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "hello-world"))
    assert result.valid
    assert not any("legacy" in issue.message.lower() for issue in result.warnings)


def test_missing_payload_rejected() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "invalid" / "missing-payload"))
    assert not result.valid
    assert any("artifacts, records, content" in issue.message for issue in result.errors)


def test_missing_records_file(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    (pack / "records" / "records.json").unlink()

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("File not found" in issue.message for issue in result.errors)


def test_invalid_json_record(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    (pack / "records" / "records.json").write_text("{bad json", encoding="utf-8")

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("Invalid JSON" in issue.message for issue in result.errors)


def test_jsonl_records() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "fermentation-bjcp-style"))
    assert result.valid
    assert result.records_checked == 3


def test_unsafe_zip_path(tmp_path: Path) -> None:
    pack = tmp_path / "unsafe.kpack"
    with zipfile.ZipFile(pack, "w") as zf:
        zf.writestr("../escape.txt", "nope")
        zf.writestr(
            "manifest.json",
            json.dumps(
                {
                    "okpf_version": "0.1",
                    "package_id": "unsafe",
                    "name": "Unsafe",
                    "version": "1.0.0",
                    "domain": "test",
                    "profiles": ["okpf-core"],
                    "records": [
                        {
                            "path": "records/records.json",
                            "format": "json",
                            "record_count": 0,
                        }
                    ],
                }
            ),
        )
        zf.writestr("records/records.json", "[]")

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("Unsafe ZIP path" in issue.message for issue in result.errors)


def test_unsafe_zip_path_stops_before_reading_manifest(tmp_path: Path) -> None:
    pack = tmp_path / "unsafe.kpack"
    with zipfile.ZipFile(pack, "w") as zf:
        zf.writestr("../escape.txt", "nope")
        zf.writestr("manifest.json", "{bad json")

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("Unsafe ZIP path" in issue.message for issue in result.errors)
    assert not any("Invalid JSON" in issue.message for issue in result.errors)


def test_optional_sources_and_provenance() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "fermentation-bjcp-style"))
    assert result.valid
    assert result.package_id == "bjcp-2021-beer-styles"


def test_fermentation_profile_example() -> None:
    result = validate_pack(
        str(REPO_ROOT / "examples" / "fermentation-bjcp-style"),
        profile="fermentation",
    )
    assert result.valid
    assert not result.errors


def test_core_accepts_record_with_facets(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    records = json.loads((pack / "records" / "records.json").read_text(encoding="utf-8"))
    records[0]["facets"] = {
        "subject": "example",
        "score": 1,
        "active": True,
        "labels": ["hello", 1, False],
        "nested": {"display": "ok"},
        "empty": None,
    }
    write_json(pack / "records" / "records.json", records)

    result = validate_pack(str(pack))
    assert result.valid


def test_core_accepts_record_without_facets() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "minimal"))
    assert result.valid


def test_profile_missing_recommended_facets_warns_not_core_error(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    records = json.loads((pack / "records" / "records.json").read_text(encoding="utf-8"))
    records[0]["domain"] = "fermentation"
    records[0]["record_type"] = "process_note"
    write_json(pack / "records" / "records.json", records)

    core = validate_pack(str(pack))
    assert core.valid
    assert not any("facets" in issue.location for issue in core.errors)

    profiled = validate_pack(str(pack), profile="fermentation")
    assert profiled.valid
    assert any("recommends" in issue.message for issue in profiled.warnings)


def test_unknown_fermentation_record_type_warns_not_core_error(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    records = json.loads((pack / "records" / "records.json").read_text(encoding="utf-8"))
    records[0]["domain"] = "fermentation"
    records[0]["record_type"] = "local_record_type"
    records[0]["facets"] = {
        "beverage_type": "general",
        "knowledge_role": "example"
    }
    write_json(pack / "records" / "records.json", records)

    result = validate_pack(str(pack), profile="fermentation")
    assert result.valid
    assert any("Unknown fermentation profile record_type" in issue.message for issue in result.warnings)


def test_strict_profile_turns_profile_warnings_into_errors(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "minimal")
    records = json.loads((pack / "records" / "records.json").read_text(encoding="utf-8"))
    records[0]["domain"] = "fermentation"
    records[0]["record_type"] = "local_record_type"
    write_json(pack / "records" / "records.json", records)

    result = validate_pack(str(pack), profile="fermentation", strict_profile=True)
    assert not result.valid
    assert any("Unknown fermentation profile record_type" in issue.message for issue in result.errors)


def test_import_report_with_record_type_and_facet_counts() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "fermentation-mixed-bundle"))
    assert result.valid

    report = json.loads(
        (REPO_ROOT / "examples" / "fermentation-mixed-bundle" / "import_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["source_files"][0]["record_type_counts"]["style_guideline"] == 1
    assert report["source_files"][0]["facet_counts"]["beverage_type"]["beer"] == 2


def test_mixed_bundle_validates_under_core_and_profile() -> None:
    core = validate_pack(str(REPO_ROOT / "examples" / "fermentation-mixed-bundle"))
    profiled = validate_pack(
        str(REPO_ROOT / "examples" / "fermentation-mixed-bundle"),
        profile="fermentation",
    )
    assert core.valid
    assert profiled.valid
    assert profiled.records_checked == 8


def test_import_report_with_partial_success() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "fermentation-bjcp-style"))
    assert result.valid

    report = json.loads(
        (REPO_ROOT / "examples" / "fermentation-bjcp-style" / "import_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["status"] == "partial_success"


def test_brewing_with_beerxml_example() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "brewing-with-beerxml"))
    assert result.valid
    assert result.records_checked == 2


def test_hello_world_example_validates() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "hello-world"))
    assert result.valid


def test_usage_policy_accepts_valid_values() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "hello-world"))
    assert result.valid
    manifest = json.loads(
        (REPO_ROOT / "examples" / "hello-world" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["usage_policy"]["allow_rag"] is True


def test_usage_policy_is_optional(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "hello-world")
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    del manifest["usage_policy"]
    write_json(pack / "manifest.json", manifest)

    result = validate_pack(str(pack))
    assert result.valid


def test_unknown_optional_manifest_fields_are_valid() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "valid" / "unknown-fields"))
    assert result.valid


def test_selective_disclosure_pack_validates_without_decryption() -> None:
    result = validate_pack(str(CONFORMANCE_DIR / "valid" / "selective-disclosure"))
    assert result.valid, [str(issue) for issue in result.issues]

    manifest = json.loads(
        (CONFORMANCE_DIR / "valid" / "selective-disclosure" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    disclosure_states = {
        artifact["id"]: artifact["disclosure"]
        for artifact in manifest["artifacts"]
    }
    assert disclosure_states["public-summary"] == "public"
    assert disclosure_states["redacted-source"] == "redacted"
    assert disclosure_states["encrypted-source"] == "encrypted"

    encrypted = next(
        artifact
        for artifact in manifest["artifacts"]
        if artifact["id"] == "encrypted-source"
    )
    assert encrypted["encryption"]["extension"] == "okpf.encrypted_artifacts.v0"
    assert encrypted["encryption"]["required_for_core_validation"] is False
    assert manifest["provenance"]["protected_artifacts"] == [
        "redacted-source",
        "encrypted-source",
    ]


def test_expert_notes_accepts_valid_entries() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "hello-world"))
    assert result.valid
    manifest = json.loads(
        (REPO_ROOT / "examples" / "hello-world" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert "rationale" in manifest["expert_notes"]


def test_dependencies_accept_valid_entries() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "brewing-with-beerxml"))
    assert result.valid
    manifest = json.loads(
        (REPO_ROOT / "examples" / "brewing-with-beerxml" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["dependencies"][0]["name"] == "BeerXML"


def test_unsafe_artifact_path_rejected(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "hello-world")
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    manifest["artifacts"][0]["path"] = "../outside.md"
    write_json(pack / "manifest.json", manifest)

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("Unsafe path" in issue.message for issue in result.errors)


def test_missing_artifact_path_rejected(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "hello-world")
    (pack / "content" / "hello.md").unlink()

    result = validate_pack(str(pack))
    assert not result.valid
    assert any("File not found" in issue.message for issue in result.errors)


def test_cli_validate_success_for_valid_example() -> None:
    result = run_okpf_cli("validate", "examples/hello-world")
    assert result.returncode == 0
    assert "valid" in result.stdout.lower()


def test_cli_validate_supports_profile_option() -> None:
    result = run_okpf_cli(
        "validate",
        "examples/fermentation-mixed-bundle",
        "--profile",
        "fermentation",
    )
    assert result.returncode == 0
    assert "valid" in result.stdout.lower()


def test_cli_validate_failure_for_invalid_fixture(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "hello-world")
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    manifest["artifacts"][0]["path"] = "content/missing.md"
    write_json(pack / "manifest.json", manifest)

    result = run_okpf_cli("validate", str(pack))
    assert result.returncode != 0
    assert "invalid" in result.stdout.lower()


def test_cli_info_alias_matches_inspect_summary() -> None:
    inspect_result = run_okpf_cli("inspect", "examples/hello-world")
    info_result = run_okpf_cli("info", "examples/hello-world")
    assert inspect_result.returncode == 0
    assert info_result.returncode == 0
    assert info_result.stdout == inspect_result.stdout
    assert "OKPF version:" in info_result.stdout
    assert "Legacy fields:" in info_result.stdout


def test_versioned_manifest_schema_exists() -> None:
    schema_path = REPO_ROOT / "schemas" / "v0.1.0" / "manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["$id"] == "https://okpf.org/schema/v0.1.0/manifest.schema.json"


def test_evaluation_result_example_validates_against_schema() -> None:
    import jsonschema

    schema = json.loads(
        (REPO_ROOT / "schemas" / "v0.1.0" / "evaluation-result.schema.json").read_text(
            encoding="utf-8"
        )
    )
    example = json.loads(
        (REPO_ROOT / "examples" / "evaluation-result-example.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(example, schema)


def run_okpf_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "reference" / "python")
    return subprocess.run(
        [sys.executable, "-m", "okpf", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
