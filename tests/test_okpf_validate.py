from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
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


def test_optional_sources_and_provenance() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "fermentation-bjcp-style"))
    assert result.valid
    assert result.package_id == "bjcp-2021-beer-styles"


def test_fermentation_profile_example() -> None:
    result = validate_pack(str(REPO_ROOT / "examples" / "fermentation-bjcp-style"))
    assert result.valid
    assert not result.errors


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


def test_cli_validate_failure_for_invalid_fixture(tmp_path: Path) -> None:
    pack = copy_example(tmp_path, "hello-world")
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    manifest["artifacts"][0]["path"] = "content/missing.md"
    write_json(pack / "manifest.json", manifest)

    result = run_okpf_cli("validate", str(pack))
    assert result.returncode != 0
    assert "invalid" in result.stdout.lower()


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
