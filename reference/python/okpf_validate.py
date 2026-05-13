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
import json
import posixpath
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST_FIELDS = (
    "okpf_version",
    "package_id",
    "name",
    "version",
    "domain",
    "profiles",
    "records",
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
    result.package_version = _string_or_none(manifest.get("version"))

    _check_manifest(manifest, result)
    if result.errors:
        return

    _check_manifest_paths(manifest, reader, result)
    _check_records(manifest, reader, result)
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

    if not isinstance(manifest.get("profiles"), list) or not manifest.get("profiles"):
        result.error("manifest.json#/profiles", "Must be a non-empty array")

    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        result.error("manifest.json#/records", "Must be a non-empty array")
    elif any(not isinstance(item, dict) for item in records):
        result.error("manifest.json#/records", "Each record file entry must be an object")


def _check_manifest_paths(
    manifest: dict[str, Any], reader: PackageReader, result: ValidationResult
) -> None:
    for section in ("records", "sources"):
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
            if "format" not in entry:
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


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an OKPF v0.1 package.")
    parser.add_argument("pack_path", help="Path to an OKPF directory or .kpack ZIP")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    result = validate_pack(args.pack_path, verbose=args.verbose)
    print(f"Validating: {args.pack_path}")
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


if __name__ == "__main__":
    sys.exit(main())
