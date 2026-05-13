#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
Standalone OKPF v0.1 validator.

Validates package directories and .kpack ZIP containers for the practical core:
manifest presence, required manifest fields, safe paths, record file presence,
JSON/JSONL record validity, optional provenance sources, and optional import reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA_PATH = REPO_ROOT / "schemas" / "manifest.schema.json"

REQUIRED_MANIFEST_FIELDS = (
    "okpf_version",
    "name",
    "version",
    "domain",
    "license",
)

REQUIRED_RECORD_FIELDS = (
    "id",
    "record_type",
    "title",
    "text",
    "domain",
    "metadata",
)

IMPORT_STATUSES = {"success", "partial_success", "failed"}
IMPORT_ITEM_STATUSES = {"success", "warning", "error", "skipped"}
USAGE_POLICY_FIELDS = {
    "allow_rag",
    "allow_fine_tuning",
    "allow_evaluation",
    "allow_commercial_use",
    "allow_derivatives",
    "allow_commercial_derivatives",
    "require_attribution",
    "notes",
}
USAGE_POLICY_BOOLEAN_FIELDS = USAGE_POLICY_FIELDS - {"notes"}


@dataclass
class Issue:
    location: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.location}: {self.message}"


@dataclass
class ValidationResult:
    pack_path: str
    issues: list[Issue] = field(default_factory=list)
    package_id: str | None = None
    package_version: str | None = None
    records_checked: int = 0

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def valid(self) -> bool:
        return not self.errors

    def error(self, location: str, message: str) -> None:
        self.issues.append(Issue(location, message))

    def warn(self, location: str, message: str) -> None:
        self.issues.append(Issue(location, message, "warning"))


class PackageReader:
    def exists(self, path: str) -> bool:
        raise NotImplementedError

    def read_text(self, path: str) -> str:
        raise NotImplementedError

    def read_bytes(self, path: str) -> bytes:
        raise NotImplementedError

    def close(self) -> None:
        pass


class DirectoryReader(PackageReader):
    def __init__(self, root: Path):
        self.root = root.resolve()

    def exists(self, path: str) -> bool:
        candidate = (self.root / path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            return False
        return candidate.is_file()

    def read_text(self, path: str) -> str:
        candidate = (self.root / path).resolve()
        with candidate.open(encoding="utf-8") as f:
            return f.read()

    def read_bytes(self, path: str) -> bytes:
        candidate = (self.root / path).resolve()
        with candidate.open("rb") as f:
            return f.read()


class ZipReader(PackageReader):
    def __init__(self, archive_path: Path, result: ValidationResult):
        self.zf = zipfile.ZipFile(archive_path)
        self.names = {info.filename for info in self.zf.infolist() if not info.is_dir()}
        for info in self.zf.infolist():
            if not _is_safe_path(info.filename):
                result.error(info.filename, "Unsafe ZIP path")

    def exists(self, path: str) -> bool:
        return path in self.names

    def read_text(self, path: str) -> str:
        with self.zf.open(path) as f:
            return f.read().decode("utf-8")

    def read_bytes(self, path: str) -> bytes:
        with self.zf.open(path) as f:
            return f.read()

    def close(self) -> None:
        self.zf.close()


def validate_pack(pack_path: str, verbose: bool = False) -> ValidationResult:
    result = ValidationResult(pack_path)
    path = Path(pack_path)

    if not path.exists():
        result.error("pack", f"Path does not exist: {pack_path}")
        return result

    reader: PackageReader
    if path.is_dir():
        reader = DirectoryReader(path)
    elif path.is_file() and path.suffix == ".kpack":
        try:
            reader = ZipReader(path, result)
        except zipfile.BadZipFile as exc:
            result.error("pack", f"Invalid ZIP container: {exc}")
            return result
    else:
        result.error("pack", "Expected a package directory or .kpack ZIP file")
        return result

    try:
        _validate_with_reader(reader, result, verbose)
    finally:
        reader.close()

    return result


def _validate_with_reader(reader: PackageReader, result: ValidationResult, verbose: bool) -> None:
    if not reader.exists("manifest.json"):
        result.error("manifest.json", "File not found")
        return

    manifest = _load_json(reader, "manifest.json", result)
    if not isinstance(manifest, dict):
        result.error("manifest.json", "Manifest must be a JSON object")
        return

    result.package_id = _string_or_none(manifest.get("package_id"))
    if result.package_id is None:
        result.package_id = _string_or_none(manifest.get("id"))
    result.package_version = _string_or_none(manifest.get("version"))

    _run_schema_validation(manifest, result)
    _check_manifest(manifest, result)
    if result.errors:
        return

    _check_manifest_paths(manifest, reader, result)
    _check_records(manifest, reader, result)
    _check_usage_policy(manifest, result)
    _check_dependencies(manifest, result)
    _check_integrity(manifest, reader, result)
    _check_import_report(reader, result)
    _check_provenance(manifest, reader, result)

    if verbose:
        result.warn("validator", f"Checked {result.records_checked} record(s)")


def _check_manifest(manifest: dict[str, Any], result: ValidationResult) -> None:
    for field_name in REQUIRED_MANIFEST_FIELDS:
        if field_name not in manifest:
            result.error("manifest.json", f"Missing required field: '{field_name}'")

    if manifest.get("okpf_version") not in {"0.1", "0.1.0"}:
        result.error("manifest.json#/okpf_version", "Expected '0.1' or '0.1.0'")

    if "package_id" not in manifest and "id" not in manifest:
        result.error("manifest.json", "Missing required field: 'package_id'")

    if "profiles" in manifest and not isinstance(manifest.get("profiles"), list):
        result.error("manifest.json#/profiles", "Must be an array when present")

    payload_fields = ("artifacts", "records", "content")
    if not any(field in manifest for field in payload_fields):
        result.error("manifest.json", "Expected at least one of: artifacts, records, content")

    for field in payload_fields:
        entries = manifest.get(field)
        if entries is None:
            continue
        if not isinstance(entries, list) or not entries:
            result.error(f"manifest.json#/{field}", "Must be a non-empty array")
        elif any(not isinstance(item, dict) for item in entries):
            result.error(f"manifest.json#/{field}", "Each entry must be an object")


def _check_manifest_paths(
    manifest: dict[str, Any], reader: PackageReader, result: ValidationResult
) -> None:
    for section in ("records", "sources", "artifacts", "content"):
        entries = manifest.get(section, [])
        if not isinstance(entries, list):
            result.error(f"manifest.json#/{section}", "Must be an array when present")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            location = f"manifest.json#/{section}[{index}]"
            entry_path = entry.get("path")
            if not isinstance(entry_path, str) or not entry_path:
                result.error(location, "Missing required field: 'path'")
                continue
            if not _is_safe_path(entry_path):
                result.error(location, f"Unsafe path: '{entry_path}'")
                continue
            if not reader.exists(entry_path):
                result.error(location, f"File not found: '{entry_path}'")
            if section in {"records", "sources"} and "format" not in entry:
                result.error(location, "Missing required field: 'format'")


def _check_records(
    manifest: dict[str, Any], reader: PackageReader, result: ValidationResult
) -> None:
    for index, entry in enumerate(manifest.get("records", [])):
        if not isinstance(entry, dict):
            continue
        record_path = entry.get("path")
        if not isinstance(record_path, str) or not _is_safe_path(record_path) or not reader.exists(record_path):
            continue

        record_format = str(entry.get("format", "")).lower()
        if record_format == "jsonl" or record_path.endswith(".jsonl"):
            _check_jsonl_records(reader, record_path, result)
        elif record_format == "json" or record_path.endswith(".json"):
            _check_json_records(reader, record_path, result)
        else:
            result.warn(
                f"manifest.json#/records[{index}]",
                f"Record format '{entry.get('format')}' is not validated by this validator",
            )


def _check_json_records(reader: PackageReader, path: str, result: ValidationResult) -> None:
    data = _load_json(reader, path, result)
    records: list[Any]
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("records"), list):
        records = data["records"]
    elif isinstance(data, dict):
        records = [data]
    else:
        result.error(path, "JSON record file must be an object, array, or object with records array")
        return

    for index, record in enumerate(records):
        _check_record(record, f"{path}#{index}", result)


def _check_jsonl_records(reader: PackageReader, path: str, result: ValidationResult) -> None:
    try:
        text = reader.read_text(path)
    except UnicodeDecodeError as exc:
        result.error(path, f"Record file is not UTF-8: {exc}")
        return

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            result.error(f"{path}:{line_number}", f"Invalid JSONL record: {exc}")
            continue
        _check_record(record, f"{path}:{line_number}", result)


def _check_record(record: Any, location: str, result: ValidationResult) -> None:
    if not isinstance(record, dict):
        result.error(location, "Record must be a JSON object")
        return
    result.records_checked += 1
    for field_name in REQUIRED_RECORD_FIELDS:
        if field_name not in record:
            result.error(location, f"Missing required record field: '{field_name}'")
    if "metadata" in record and not isinstance(record["metadata"], dict):
        result.error(location, "Record field 'metadata' must be an object")


def _check_usage_policy(manifest: dict[str, Any], result: ValidationResult) -> None:
    usage_policy = manifest.get("usage_policy")
    if usage_policy is None:
        return
    if not isinstance(usage_policy, dict):
        result.error("manifest.json#/usage_policy", "Must be an object")
        return
    for key, value in usage_policy.items():
        location = f"manifest.json#/usage_policy/{key}"
        if key not in USAGE_POLICY_FIELDS:
            result.error(location, "Unknown usage_policy field")
        elif key in USAGE_POLICY_BOOLEAN_FIELDS and not isinstance(value, bool):
            result.error(location, "Must be a boolean")
        elif key == "notes" and not isinstance(value, str):
            result.error(location, "Must be a string")


def _check_dependencies(manifest: dict[str, Any], result: ValidationResult) -> None:
    dependencies = manifest.get("dependencies")
    if dependencies is None:
        return
    if not isinstance(dependencies, list):
        result.error("manifest.json#/dependencies", "Must be an array")
        return
    for index, dependency in enumerate(dependencies):
        location = f"manifest.json#/dependencies[{index}]"
        if not isinstance(dependency, dict):
            result.error(location, "Dependency must be an object")
            continue
        for field_name in ("name", "version", "uri", "description"):
            if field_name in dependency and not isinstance(dependency[field_name], str):
                result.error(f"{location}/{field_name}", "Must be a string")
        if "optional" in dependency and not isinstance(dependency["optional"], bool):
            result.error(f"{location}/optional", "Must be a boolean")


def _check_integrity(
    manifest: dict[str, Any], reader: PackageReader, result: ValidationResult
) -> None:
    integrity = manifest.get("integrity")
    if integrity is None:
        return
    if not isinstance(integrity, dict):
        result.error("manifest.json#/integrity", "Must be an object")
        return
    algorithm = integrity.get("algorithm")
    if algorithm != "sha256":
        result.error("manifest.json#/integrity/algorithm", "Only sha256 is supported in v0.1.0")
    for field_name in ("manifest_sha256", "content_sha256"):
        if field_name in integrity and not _is_sha256(str(integrity[field_name])):
            result.error(f"manifest.json#/integrity/{field_name}", "Must be a SHA-256 hex digest")
    artifacts = integrity.get("artifacts", [])
    if artifacts is None:
        return
    if not isinstance(artifacts, list):
        result.error("manifest.json#/integrity/artifacts", "Must be an array")
        return
    for index, artifact in enumerate(artifacts):
        location = f"manifest.json#/integrity/artifacts[{index}]"
        if not isinstance(artifact, dict):
            result.error(location, "Integrity artifact entry must be an object")
            continue
        path = artifact.get("path")
        sha256 = artifact.get("sha256")
        if not isinstance(path, str) or not path:
            result.error(location, "Missing required field: 'path'")
            continue
        if not _is_safe_path(path):
            result.error(location, f"Unsafe path: '{path}'")
            continue
        if not reader.exists(path):
            result.error(location, f"File not found: '{path}'")
            continue
        if not isinstance(sha256, str) or not _is_sha256(sha256):
            result.error(location, "Missing or invalid SHA-256 digest")
            continue
        actual = hashlib.sha256(reader.read_bytes(path)).hexdigest()
        if actual.lower() != sha256.lower():
            result.error(location, f"SHA-256 mismatch for '{path}'")


def _check_import_report(reader: PackageReader, result: ValidationResult) -> None:
    if not reader.exists("import_report.json"):
        return

    report = _load_json(reader, "import_report.json", result)
    if not isinstance(report, dict):
        result.error("import_report.json", "Import report must be a JSON object")
        return
    if report.get("status") not in IMPORT_STATUSES:
        result.error("import_report.json#/status", "Expected success, partial_success, or failed")
    if not isinstance(report.get("items"), list):
        result.error("import_report.json#/items", "Must be an array")
        return
    for index, item in enumerate(report["items"]):
        location = f"import_report.json#/items[{index}]"
        if not isinstance(item, dict):
            result.error(location, "Import report item must be an object")
            continue
        for field_name in ("path", "stage", "status", "message"):
            if field_name not in item:
                result.error(location, f"Missing required field: '{field_name}'")
        if item.get("status") not in IMPORT_ITEM_STATUSES:
            result.error(location, "Invalid item status")


def _check_provenance(
    manifest: dict[str, Any], reader: PackageReader, result: ValidationResult
) -> None:
    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        return
    sources_path = provenance.get("sources")
    if not isinstance(sources_path, str):
        return
    if not _is_safe_path(sources_path):
        result.error("manifest.json#/provenance/sources", f"Unsafe path: '{sources_path}'")
        return
    if not reader.exists(sources_path):
        result.error("manifest.json#/provenance/sources", f"File not found: '{sources_path}'")
        return

    sources = _load_json(reader, sources_path, result)
    if not isinstance(sources, list):
        result.error(sources_path, "Provenance sources must be an array")
        return
    for index, source in enumerate(sources):
        location = f"{sources_path}#{index}"
        if not isinstance(source, dict):
            result.error(location, "Provenance source entry must be an object")
            continue
        for field_name in ("source_id", "path", "format"):
            if field_name not in source:
                result.error(location, f"Missing required field: '{field_name}'")
        source_path = source.get("path")
        if isinstance(source_path, str) and not _is_safe_path(source_path):
            result.error(location, f"Unsafe path: '{source_path}'")


def _load_json(reader: PackageReader, path: str, result: ValidationResult) -> Any:
    try:
        text = reader.read_text(path)
    except UnicodeDecodeError as exc:
        result.error(path, f"File is not UTF-8: {exc}")
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        result.error(path, f"Invalid JSON: {exc}")
        return None


def _run_schema_validation(manifest: dict[str, Any], result: ValidationResult) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        result.warn("schema", "jsonschema is not installed; skipping manifest schema validation")
        return

    if not MANIFEST_SCHEMA_PATH.is_file():
        result.warn("schema", f"Manifest schema not found: {MANIFEST_SCHEMA_PATH}")
        return

    try:
        schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.warn("schema", f"Manifest schema is invalid JSON: {exc}")
        return

    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema)
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        path = "/".join(str(part) for part in error.absolute_path)
        location = f"manifest.json#/{path}" if path else "manifest.json"
        result.error(location, f"Schema: {error.message}")


def _is_safe_path(path: str) -> bool:
    if not path or "\x00" in path or "\\" in path:
        return False
    if path.startswith("/") or path.startswith("~"):
        return False
    if len(path) >= 2 and path[1] == ":":
        return False
    normalized = posixpath.normpath(path)
    if normalized in {"", "."}:
        return False
    if normalized.startswith("../") or normalized == "..":
        return False
    return normalized == path


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value)


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def load_manifest(pack_path: str) -> tuple[dict[str, Any] | None, list[str]]:
    path = Path(pack_path)
    errors: list[str] = []

    if path.is_dir():
        reader: PackageReader = DirectoryReader(path)
    elif path.is_file() and path.suffix == ".kpack":
        result = ValidationResult(pack_path)
        try:
            reader = ZipReader(path, result)
        except zipfile.BadZipFile as exc:
            return None, [f"Invalid ZIP container: {exc}"]
        if result.errors:
            errors.extend(issue.message for issue in result.errors)
    else:
        return None, [f"Expected a package directory or .kpack ZIP file: {pack_path}"]

    try:
        if not reader.exists("manifest.json"):
            return None, ["manifest.json not found"]
        data = json.loads(reader.read_text("manifest.json"))
        if not isinstance(data, dict):
            return None, ["manifest.json must be an object"]
        return data, errors
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"Could not read manifest.json: {exc}"]
    finally:
        reader.close()


def _print_validation_result(result: ValidationResult) -> int:
    print(f"Validating: {result.pack_path}")
    if result.package_id:
        print(f"Package ID: {result.package_id}")
    if result.package_version:
        print(f"Version: {result.package_version}")
    if result.records_checked:
        print(f"Records checked: {result.records_checked}")

    for issue in result.issues:
        print(issue)

    if result.valid:
        print("VALID")
        return 0

    print(f"INVALID: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an OKPF v0.1.0 package.")
    parser.add_argument("pack_path", help="Path to an OKPF directory or .kpack ZIP")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    return _print_validation_result(validate_pack(args.pack_path, verbose=args.verbose))


if __name__ == "__main__":
    sys.exit(main())
