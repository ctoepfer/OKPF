# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
Validation logic for OKPF knowledge packs.

Validates a pack directory or .kpack archive against the OKPF specification.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from okpf_validate import DirectoryReader, PackageReader
from okpf_validate import ValidationResult as _ReaderValidationResult
from okpf_validate import ZipReader


@dataclass
class ValidationError:
    path: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.path}: {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    pack_id: str | None = None
    pack_version: str | None = None

    def __str__(self) -> str:
        lines = [f"ValidationResult(valid={self.valid})"]
        for e in self.errors:
            lines.append(f"  {e}")
        for w in self.warnings:
            lines.append(f"  {w}")
        return "\n".join(lines)

    @property
    def all_issues(self) -> list[ValidationError]:
        return self.errors + self.warnings


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_SCHEMA_PATH = REPO_ROOT / "schemas" / "v0.1.0" / "manifest.schema.json"
_BUNDLED_MANIFEST_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "v0.1.0" / "manifest.schema.json"

REQUIRED_MANIFEST_FIELDS = [
    "okpf_version", "name", "version", "domain", "license",
]

PAYLOAD_FIELDS = ("artifacts", "records", "content")
ARTIFACT_FIELDS = ("artifacts", "content")
REQUIRED_ARTIFACT_FIELDS = ["path"]


def validate(pack_path: str) -> ValidationResult:
    """
    Validate an OKPF pack (directory or .kpack archive) at pack_path.

    Checks:
    - manifest.json exists and is valid JSON
    - manifest.json conforms to the manifest JSON Schema when jsonschema is installed
    - Core compatibility requirements are present when schema validation is unavailable
    - referenced manifest $ref files exist and are valid JSON
    - declared artifact and record paths resolve within the pack
    - SHA-256 hashes match file contents where declared

    For deeper record/profile checks, see the standalone reference validator
    in reference/python/okpf_validate.py (also used by the `okpf` CLI).
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    reader = _open_reader(pack_path)
    if reader is None:
        errors.append(ValidationError("pack", "Expected a package directory or .kpack ZIP file"))
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    try:
        # Step 1: manifest.json must exist
        if not reader.exists("manifest.json"):
            errors.append(ValidationError("manifest.json", "File not found"))
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Step 2: manifest.json must be valid JSON
        try:
            manifest = json.loads(reader.read_text("manifest.json"))
        except json.JSONDecodeError as e:
            errors.append(ValidationError("manifest.json", f"Invalid JSON: {e}"))
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        if not isinstance(manifest, dict):
            errors.append(ValidationError("manifest.json", "Manifest must be a JSON object"))
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        pack_id = _string_or_none(manifest.get("package_id")) or _string_or_none(manifest.get("id"))
        pack_version = _string_or_none(manifest.get("version"))

        _run_schema_validation(manifest, errors, warnings)

        # Step 3: required fields
        for field_name in REQUIRED_MANIFEST_FIELDS:
            if field_name not in manifest:
                errors.append(ValidationError(
                    "manifest.json",
                    f"Missing required field: '{field_name}'"
                ))

        if "package_id" not in manifest and "id" not in manifest:
            errors.append(ValidationError("manifest.json", "Missing required field: 'package_id'"))

        if not any(field_name in manifest for field_name in PAYLOAD_FIELDS):
            errors.append(ValidationError(
                "manifest.json",
                "Expected at least one of: artifacts, records, content",
            ))

        for field_name in PAYLOAD_FIELDS:
            if field_name in manifest and not isinstance(manifest[field_name], list):
                errors.append(ValidationError(f"manifest.json#/{field_name}", "Must be an array"))
            elif isinstance(manifest.get(field_name), list) and not manifest[field_name]:
                errors.append(ValidationError(
                    f"manifest.json#/{field_name}",
                    "Must be a non-empty array",
                ))

        # Step 4: manifest $ref files must exist and be valid JSON.
        for field_name in ("license", "contributors", "provenance", "evaluations"):
            _check_ref(field_name, manifest.get(field_name), reader, errors)

        # Step 5: declared local paths must stay inside the pack and exist.
        for field_name in ARTIFACT_FIELDS:
            _check_artifact_paths(field_name, manifest.get(field_name), reader, errors, warnings)
        _check_file_entries("records", manifest.get("records"), reader, errors)

        valid = len(errors) == 0
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            pack_id=pack_id,
            pack_version=pack_version,
        )
    finally:
        reader.close()


def _open_reader(pack_path: str) -> PackageReader | None:
    resolved = Path(pack_path).resolve()
    if resolved.is_dir():
        return DirectoryReader(resolved)
    if resolved.is_file() and resolved.suffix == ".kpack":
        return ZipReader(resolved, _ReaderValidationResult(str(resolved)))
    return None


def _run_schema_validation(
    manifest: dict[str, Any],
    errors: list[ValidationError],
    warnings: list[ValidationError],
) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        warnings.append(ValidationError(
            "schema",
            "jsonschema is not installed; skipping manifest schema validation",
            severity="warning",
        ))
        return

    # Prefer the repo-relative schema (always freshest in a source checkout);
    # fall back to the copy bundled with this package for standalone installs.
    schema_path = MANIFEST_SCHEMA_PATH if MANIFEST_SCHEMA_PATH.is_file() else _BUNDLED_MANIFEST_SCHEMA_PATH
    if not schema_path.is_file():
        warnings.append(ValidationError(
            "schema",
            f"Manifest schema not found: {MANIFEST_SCHEMA_PATH}",
            severity="warning",
        ))
        return

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(ValidationError(
            "schema",
            f"Manifest schema is invalid JSON: {exc}",
            severity="warning",
        ))
        return

    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema)
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        path = "/".join(str(part) for part in error.absolute_path)
        location = f"manifest.json#/{path}" if path else "manifest.json"
        errors.append(ValidationError(location, f"Schema: {error.message}"))


def _check_ref(
    field_name: str,
    value: Any,
    reader: PackageReader,
    errors: list[ValidationError],
) -> None:
    if not isinstance(value, dict) or "$ref" not in value:
        return
    ref_path = value["$ref"]
    location = f"manifest.json#/{field_name}/$ref"
    if not isinstance(ref_path, str) or not ref_path:
        errors.append(ValidationError(location, "Referenced path must be a non-empty string"))
        return
    if not _resolve_pack_file(ref_path, reader, location, errors):
        return
    try:
        json.loads(reader.read_text(ref_path))
    except json.JSONDecodeError as exc:
        errors.append(ValidationError(ref_path, f"Invalid JSON: {exc}"))


def _check_artifact_paths(
    field_name: str,
    entries: Any,
    reader: PackageReader,
    errors: list[ValidationError],
    warnings: list[ValidationError],
) -> None:
    if not isinstance(entries, list):
        return

    seen_ids: set[str] = set()
    for index, artifact in enumerate(entries):
        prefix = f"manifest.json#/{field_name}[{index}]"
        if not isinstance(artifact, dict):
            continue

        for required in REQUIRED_ARTIFACT_FIELDS:
            if required not in artifact:
                errors.append(ValidationError(prefix, f"Missing required field: '{required}'"))

        artifact_id = artifact.get("id")
        if isinstance(artifact_id, str):
            if artifact_id in seen_ids:
                errors.append(ValidationError(prefix, f"Duplicate artifact id: '{artifact_id}'"))
            seen_ids.add(artifact_id)

        artifact_path = artifact.get("path")
        if not isinstance(artifact_path, str):
            continue
        if not _resolve_pack_file(artifact_path, reader, prefix, errors):
            continue

        declared_hash = artifact.get("sha256")
        if declared_hash:
            actual_hash = hashlib.sha256(reader.read_bytes(artifact_path)).hexdigest()
            if actual_hash != declared_hash:
                errors.append(ValidationError(
                    prefix,
                    f"SHA-256 mismatch for '{artifact_path}': "
                    f"declared={declared_hash[:16]}... actual={actual_hash[:16]}...",
                ))
        else:
            warnings.append(ValidationError(
                prefix,
                f"No SHA-256 hash declared for '{artifact_path}'; integrity unverifiable",
                severity="warning",
            ))


def _check_file_entries(
    field_name: str,
    entries: Any,
    reader: PackageReader,
    errors: list[ValidationError],
) -> None:
    if not isinstance(entries, list):
        return

    for index, entry in enumerate(entries):
        prefix = f"manifest.json#/{field_name}[{index}]"
        if not isinstance(entry, dict):
            continue
        file_path = entry.get("path")
        if isinstance(file_path, str):
            _resolve_pack_file(file_path, reader, prefix, errors)


def _resolve_pack_file(
    relative_path: str,
    reader: PackageReader,
    location: str,
    errors: list[ValidationError],
) -> bool:
    if not _is_safe_path(relative_path):
        errors.append(ValidationError(location, f"Unsafe path: '{relative_path}'"))
        return False

    if not reader.exists(relative_path):
        errors.append(ValidationError(location, f"File not found: '{relative_path}'"))
        return False
    return True


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
