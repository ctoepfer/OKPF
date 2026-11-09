# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Offline institutional application-profile validation for directories and archives."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from okpf_validate import PackageReader, ValidationResult, _is_safe_path, validate_pack

PROFILE = "okpf.profile.institutional.v1"
SCHEMA_ROOT = Path(__file__).resolve().parent / "schemas"


def validate_institutional_pack(pack_path: str | Path) -> ValidationResult:
    """Run Core checks and mandatory institutional checks; never fetch sources."""
    return validate_pack(str(pack_path), profile=PROFILE)


def validate_institutional_reader(
    reader: PackageReader, manifest: dict[str, Any], result: ValidationResult,
) -> None:
    try:
        import yaml
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError:
        result.error("profile", "Institutional validation requires jsonschema and PyYAML")
        return

    def schema(name: str) -> dict[str, Any]:
        return json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))

    core = schema("v0.1.0/manifest.schema.json")
    # An explicit registry resolves the sole external reference offline.
    registry = Registry().with_resource(
        "https://okpf.org/schemas/v0.1.0/manifest.schema.json", Resource.from_contents(core),
    )
    manifest_validator = Draft202012Validator(
        schema("profiles/institutional/v1/profile_manifest.json"), registry=registry,
    )
    case_validator = Draft202012Validator(schema("profiles/institutional/v1/case_record.json"))

    def check(value: Any, validator: Any, location: str) -> bool:
        errors = list(validator.iter_errors(value))
        for error in errors:
            path = "/".join(str(part) for part in error.absolute_path)
            result.error(f"{location}#/{path}", f"Institutional schema: {error.message}")
        return not errors

    if check(manifest, manifest_validator, "manifest.json"):
        window = manifest["institutional_profile"]["observation_window"]
        if window["start_year"] > window["end_year"]:
            result.error("manifest.json#/institutional_profile/observation_window", "start_year exceeds end_year")

    for path in reader.iter_paths():
        if path.startswith("cases/") and Path(path).suffix.lower() not in {".json", ".yaml", ".yml"}:
            result.error(path, "Institutional cases must be JSON or YAML files")
    paths = sorted(p for p in reader.iter_paths() if p.startswith("cases/")
                   and Path(p).suffix.lower() in {".json", ".yaml", ".yml"})
    if not paths:
        result.error("cases/", "At least one institutional case is required")
    seen: set[str] = set()
    for path in paths:
        if not _is_safe_path(path) or not reader.exists(path):
            result.error(path, "Unsafe or inaccessible case path")
            continue
        try:
            text = reader.read_text(path)
            value = json.loads(text) if Path(path).suffix.lower() == ".json" else yaml.safe_load(text)
        except (ValueError, OSError, yaml.YAMLError, RecursionError) as exc:
            result.error(path, f"Cannot parse case: {exc}")
            continue
        result.records_checked += 1
        try:
            valid = check(value, case_validator, path)
        except (RecursionError, TypeError) as exc:
            result.error(path, f"Case must use JSON-compatible values: {exc}")
            continue
        if valid:
            if value["id"] in seen:
                result.error(path, f"Duplicate institutional case id: {value['id']}")
            seen.add(value["id"])
