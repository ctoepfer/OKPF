# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
Validation logic for OKPF knowledge packs.

Validates a pack directory or .kpack archive against the OKPF specification.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path


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


REQUIRED_MANIFEST_FIELDS = [
    "okpf_version", "id", "name", "version", "domain", "created",
    "license", "content",
]

REQUIRED_ARTIFACT_FIELDS = ["id", "path", "type"]


def validate(pack_path: str) -> ValidationResult:
    """
    Validate an OKPF knowledge pack at pack_path.

    Checks:
    - manifest.json exists and is valid JSON
    - All required manifest fields are present
    - license.json exists and is valid JSON
    - All content artifact paths resolve within the pack
    - SHA-256 hashes match file contents where declared

    Does NOT (yet) validate against the full JSON Schema — that requires
    the jsonschema library and will be added in a future release.
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []
    pack_path = str(Path(pack_path).resolve())

    # Step 1: manifest.json must exist
    manifest_path = os.path.join(pack_path, "manifest.json")
    if not os.path.isfile(manifest_path):
        errors.append(ValidationError("manifest.json", "File not found"))
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    # Step 2: manifest.json must be valid JSON
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(ValidationError("manifest.json", f"Invalid JSON: {e}"))
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    pack_id = manifest.get("id")
    pack_version = manifest.get("version")

    # Step 3: required fields
    for field_name in REQUIRED_MANIFEST_FIELDS:
        if field_name not in manifest:
            errors.append(ValidationError(
                "manifest.json",
                f"Missing required field: '{field_name}'"
            ))

    # Step 4: license.json must exist (if $ref) and be valid
    license_value = manifest.get("license", {})
    if isinstance(license_value, dict) and "$ref" in license_value:
        license_path = os.path.join(pack_path, license_value["$ref"])
        if not os.path.isfile(license_path):
            errors.append(ValidationError(
                f"license ({license_value['$ref']})",
                "Referenced license file not found"
            ))
        else:
            try:
                with open(license_path) as f:
                    license_data = json.load(f)
                if "spdx_expression" not in license_data:
                    errors.append(ValidationError(
                        license_value["$ref"],
                        "Missing required field: 'spdx_expression'"
                    ))
            except json.JSONDecodeError as e:
                errors.append(ValidationError(license_value["$ref"], f"Invalid JSON: {e}"))
    elif isinstance(license_value, dict) and "spdx_expression" not in license_value:
        if license_value:
            errors.append(ValidationError(
                "manifest.json#/license",
                "Inline license missing required field: 'spdx_expression'"
            ))

    # Step 5: content artifact paths
    content = manifest.get("content", [])
    if not isinstance(content, list) or len(content) == 0:
        errors.append(ValidationError("manifest.json#/content", "Must be a non-empty array"))
    else:
        seen_ids: set[str] = set()
        for i, artifact in enumerate(content):
            prefix = f"manifest.json#/content[{i}]"

            for req in REQUIRED_ARTIFACT_FIELDS:
                if req not in artifact:
                    errors.append(ValidationError(prefix, f"Missing required field: '{req}'"))

            art_id = artifact.get("id", f"<index {i}>")
            if art_id in seen_ids:
                errors.append(ValidationError(prefix, f"Duplicate artifact id: '{art_id}'"))
            seen_ids.add(art_id)

            art_path = artifact.get("path")
            if art_path:
                full_path = os.path.join(pack_path, art_path)
                if not os.path.isfile(full_path):
                    errors.append(ValidationError(
                        prefix,
                        f"Content file not found: '{art_path}'"
                    ))
                else:
                    # Step 6: SHA-256 hash verification
                    declared_hash = artifact.get("sha256")
                    if declared_hash:
                        actual_hash = _sha256_file(full_path)
                        if actual_hash != declared_hash:
                            errors.append(ValidationError(
                                prefix,
                                f"SHA-256 mismatch for '{art_path}': "
                                f"declared={declared_hash[:16]}… actual={actual_hash[:16]}…"
                            ))
                    else:
                        warnings.append(ValidationError(
                            prefix,
                            f"No SHA-256 hash declared for '{art_path}' — integrity unverifiable",
                            severity="warning"
                        ))

    valid = len(errors) == 0
    return ValidationResult(
        valid=valid,
        errors=errors,
        warnings=warnings,
        pack_id=pack_id,
        pack_version=pack_version,
    )


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
