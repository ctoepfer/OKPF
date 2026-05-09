#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
okpf_validate.py — standalone OKPF pack validator.

Validates an OKPF knowledge pack directory against the OKPF Core v0.1.0 spec.

Usage:
    python reference/python/okpf_validate.py <pack-directory>
    python reference/python/okpf_validate.py examples/basic-pack
    python reference/python/okpf_validate.py examples/homebrew-recipe-pack --verbose

Exit codes:
    0  — pack is valid (warnings may still be printed)
    1  — pack is invalid (one or more errors)
    2  — usage error

Dependencies:
    - Python 3.9+
    - jsonschema>=4.0  (pip install jsonschema)

If jsonschema is not installed, schema validation is skipped and a warning is
printed. All other checks (file existence, required fields, SHA-256 hashes)
still run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Locate the schema relative to this script
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_SCHEMA_PATH = _REPO_ROOT / "schemas" / "manifest.schema.json"


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

class Issue:
    def __init__(self, location: str, message: str, severity: str = "error"):
        self.location = location
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        icon = "✗" if self.severity == "error" else "⚠"
        return f"  {icon} [{self.severity.upper()}] {self.location}: {self.message}"


class ValidationResult:
    def __init__(self, pack_path: str):
        self.pack_path = pack_path
        self.issues: list[Issue] = []
        self.pack_id: Optional[str] = None
        self.pack_version: Optional[str] = None

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, location: str, message: str) -> None:
        self.issues.append(Issue(location, message, "error"))

    def warn(self, location: str, message: str) -> None:
        self.issues.append(Issue(location, message, "warning"))


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

REQUIRED_MANIFEST_FIELDS = [
    "okpf_version", "id", "name", "version", "domain",
    "created", "license", "content",
]

REQUIRED_ARTIFACT_FIELDS = ["id", "path", "type"]

SUPPORTED_OKPF_VERSIONS = {"0.1.0"}


def validate_pack(pack_path: str, verbose: bool = False) -> ValidationResult:
    """
    Validate an OKPF pack directory.

    Performs the following checks:
      1. manifest.json exists and is valid JSON
      2. JSON Schema validation (if jsonschema is installed)
      3. Required manifest fields are present
      4. okpf_version is a recognized value
      5. license.$ref resolves and contains spdx_expression
      6. content is a non-empty array
      7. Each artifact: required fields present, path exists, SHA-256 matches
      8. Artifact IDs are unique

    Returns a ValidationResult with errors and warnings.
    """
    result = ValidationResult(pack_path)
    pack_dir = Path(pack_path).resolve()

    if not pack_dir.exists():
        result.error("pack", f"Path does not exist: {pack_path}")
        return result

    if not pack_dir.is_dir():
        result.error("pack", f"Path is not a directory: {pack_path}")
        return result

    # Step 1: manifest.json
    manifest_file = pack_dir / "manifest.json"
    if not manifest_file.is_file():
        result.error("manifest.json", "File not found")
        return result

    try:
        with manifest_file.open(encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as exc:
        result.error("manifest.json", f"Invalid JSON: {exc}")
        return result

    result.pack_id = manifest.get("id")
    result.pack_version = manifest.get("version")

    # Step 2: JSON Schema validation
    _run_schema_validation(manifest, result, verbose)

    # Step 3: Required fields
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            result.error("manifest.json", f"Missing required field: '{field}'")

    # Step 4: okpf_version check
    okpf_ver = manifest.get("okpf_version", "")
    if okpf_ver and okpf_ver not in SUPPORTED_OKPF_VERSIONS:
        result.warn(
            "manifest.json#/okpf_version",
            f"Unrecognized okpf_version '{okpf_ver}'; "
            f"this validator supports {sorted(SUPPORTED_OKPF_VERSIONS)}",
        )

    # Step 5: license
    _check_license(manifest, pack_dir, result)

    # Step 6 + 7 + 8: content artifacts
    _check_content(manifest, pack_dir, result)

    # Recommended field hints (warnings only)
    _check_recommended(manifest, result)

    return result


def _run_schema_validation(
    manifest: dict, result: ValidationResult, verbose: bool
) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        result.warn(
            "schema",
            "jsonschema library not found — install it with 'pip install jsonschema' "
            "to enable full JSON Schema validation",
        )
        return

    if not _SCHEMA_PATH.is_file():
        result.warn("schema", f"Schema file not found at {_SCHEMA_PATH}; skipping schema validation")
        return

    try:
        with _SCHEMA_PATH.open(encoding="utf-8") as f:
            schema = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        result.warn("schema", f"Could not load schema: {exc}")
        return

    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema)

    schema_errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))
    for err in schema_errors:
        location = "manifest.json#/" + "/".join(str(p) for p in err.absolute_path)
        result.error(location or "manifest.json", f"Schema: {err.message}")

    if verbose and not schema_errors:
        print("  ✓ JSON Schema validation passed")


def _check_license(manifest: dict, pack_dir: Path, result: ValidationResult) -> None:
    license_val = manifest.get("license", {})
    if not isinstance(license_val, dict):
        result.error("manifest.json#/license", "Must be an object")
        return

    if "$ref" in license_val:
        ref_path = pack_dir / license_val["$ref"]
        if not ref_path.is_file():
            result.error(
                f"manifest.json#/license/$ref",
                f"Referenced file not found: '{license_val['$ref']}'",
            )
            return
        try:
            with ref_path.open(encoding="utf-8") as f:
                license_data = json.load(f)
        except json.JSONDecodeError as exc:
            result.error(license_val["$ref"], f"Invalid JSON: {exc}")
            return

        if "spdx_expression" not in license_data:
            result.error(license_val["$ref"], "Missing required field: 'spdx_expression'")
    elif "spdx_expression" not in license_val:
        result.error(
            "manifest.json#/license",
            "Inline license missing required field: 'spdx_expression'",
        )


def _check_content(manifest: dict, pack_dir: Path, result: ValidationResult) -> None:
    content = manifest.get("content")
    if not isinstance(content, list) or len(content) == 0:
        result.error("manifest.json#/content", "Must be a non-empty array")
        return

    seen_ids: set[str] = set()
    for i, artifact in enumerate(content):
        prefix = f"manifest.json#/content[{i}]"

        if not isinstance(artifact, dict):
            result.error(prefix, "Each artifact must be an object")
            continue

        for req in REQUIRED_ARTIFACT_FIELDS:
            if req not in artifact:
                result.error(prefix, f"Missing required field: '{req}'")

        art_id = artifact.get("id", f"<index {i}>")
        if art_id in seen_ids:
            result.error(prefix, f"Duplicate artifact id: '{art_id}'")
        seen_ids.add(art_id)

        art_path = artifact.get("path")
        if art_path:
            full_path = pack_dir / art_path
            if not full_path.is_file():
                result.error(prefix, f"File not found: '{art_path}'")
            else:
                declared_hash = artifact.get("sha256")
                if declared_hash:
                    actual_hash = _sha256_file(full_path)
                    if actual_hash != declared_hash:
                        result.error(
                            prefix,
                            f"SHA-256 mismatch for '{art_path}'\n"
                            f"    declared: {declared_hash}\n"
                            f"    actual:   {actual_hash}",
                        )
                else:
                    result.warn(prefix, f"No sha256 declared for '{art_path}' — integrity unverifiable")


def _check_recommended(manifest: dict, result: ValidationResult) -> None:
    for field in ("description", "contributors", "provenance", "tags", "language"):
        if field not in manifest:
            result.warn("manifest.json", f"Recommended field '{field}' is absent")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="okpf_validate",
        description="Validate an OKPF knowledge pack directory.",
    )
    parser.add_argument("pack_path", help="Path to the pack directory")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print additional detail"
    )
    parser.add_argument(
        "--hash-only", action="store_true",
        help="Print SHA-256 hashes for all declared artifact paths and exit",
    )
    args = parser.parse_args()

    pack_dir = Path(args.pack_path).resolve()

    # --hash-only mode: compute and print hashes for review
    if args.hash_only:
        manifest_file = pack_dir / "manifest.json"
        if not manifest_file.is_file():
            print(f"Error: manifest.json not found in {args.pack_path}", file=sys.stderr)
            return 1
        with manifest_file.open(encoding="utf-8") as f:
            manifest = json.load(f)
        for artifact in manifest.get("content", []):
            path = pack_dir / artifact["path"]
            if path.is_file():
                h = _sha256_file(path)
                print(f"{artifact['id']}: {h}")
            else:
                print(f"{artifact['id']}: FILE NOT FOUND ({artifact['path']})")
        return 0

    print(f"Validating: {args.pack_path}")
    if args.verbose:
        print(f"  Schema:    {_SCHEMA_PATH}")
    print()

    result = validate_pack(args.pack_path, verbose=args.verbose)

    # Print identity
    if result.pack_id:
        print(f"  Pack ID:      {result.pack_id}")
    if result.pack_version:
        print(f"  Pack version: {result.pack_version}")
    if result.pack_id or result.pack_version:
        print()

    # Print issues
    if result.errors:
        print(f"Errors ({len(result.errors)}):")
        for issue in result.errors:
            print(issue)
        print()

    if result.warnings:
        print(f"Warnings ({len(result.warnings)}):")
        for issue in result.warnings:
            print(issue)
        print()

    # Summary
    if result.valid:
        warn_suffix = f" ({len(result.warnings)} warning(s))" if result.warnings else ""
        print(f"✓ VALID{warn_suffix}")
        return 0
    else:
        print(f"✗ INVALID — {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
