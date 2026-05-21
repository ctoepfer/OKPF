# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Command-line tools for the OKPF reference implementation."""

from __future__ import annotations

import argparse
from typing import Any

from okpf_validate import load_manifest, validate_pack


def main() -> int:
    parser = argparse.ArgumentParser(prog="okpf", description="OKPF reference CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate an OKPF package")
    validate_parser.add_argument("pack_path")
    validate_parser.add_argument("--profile", help="Run optional validation for a named profile")
    validate_parser.add_argument(
        "--strict-profile",
        action="store_true",
        help="Treat profile validation warnings as errors",
    )

    inspect_parser = subparsers.add_parser("inspect", help="Inspect an OKPF package manifest")
    inspect_parser.add_argument("pack_path")
    info_parser = subparsers.add_parser("info", help="Show an OKPF package summary")
    info_parser.add_argument("pack_path")

    args = parser.parse_args()
    if args.command == "validate":
        return _validate(args.pack_path, args.profile, args.strict_profile)
    if args.command in {"inspect", "info"}:
        return _inspect(args.pack_path)
    parser.error(f"Unknown command: {args.command}")
    return 2


def _validate(pack_path: str, profile: str | None = None, strict_profile: bool = False) -> int:
    result = validate_pack(pack_path, profile=profile, strict_profile=strict_profile)
    if result.valid:
        name = result.package_id or pack_path
        print(f"OKPF package is valid: {name}")
        for issue in result.warnings:
            print(issue)
        return 0

    print(f"OKPF package is invalid: {pack_path}")
    for issue in result.errors:
        print(issue)
    for issue in result.warnings:
        print(issue)
    return 1


def _inspect(pack_path: str) -> int:
    manifest, errors = load_manifest(pack_path)
    if manifest is None:
        print(f"Could not inspect OKPF package: {pack_path}")
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    artifacts = _as_list(manifest.get("artifacts")) + _as_list(manifest.get("content"))
    records = _as_list(manifest.get("records"))
    license_value = manifest.get("license", {})
    usage_policy = manifest.get("usage_policy", {})
    legacy_fields = [
        field_name for field_name in ("id", "content")
        if field_name in manifest and {"id": "package_id", "content": "artifacts"}[field_name] not in manifest
    ]

    print(f"Name: {manifest.get('title') or manifest.get('name') or '(untitled)'}")
    print(f"Package ID: {manifest.get('package_id') or manifest.get('id') or '(none)'}")
    print(f"Version: {manifest.get('version') or '(none)'}")
    print(f"OKPF version: {manifest.get('okpf_version') or '(none)'}")
    print(f"Domain: {manifest.get('domain') or '(none)'}")
    print(f"Description: {manifest.get('description') or '(none)'}")
    print(f"Artifact count: {len(artifacts)}")
    print(f"Record file count: {len(records)}")
    print(f"Legacy fields: {', '.join(legacy_fields) if legacy_fields else '(none)'}")
    print(f"License: {_summarize_license(license_value)}")
    print(f"Usage policy: {_summarize_usage_policy(usage_policy)}")
    return 0


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _summarize_license(value: Any) -> str:
    if not isinstance(value, dict):
        return "(none)"
    if "$ref" in value:
        return str(value["$ref"])
    parts = [str(value[key]) for key in ("type", "details") if value.get(key)]
    return "; ".join(parts) if parts else "(declared)"


def _summarize_usage_policy(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return "(none)"
    enabled = sorted(
        key for key, item in value.items()
        if key.startswith("allow_") and isinstance(item, bool) and item
    )
    disabled = sorted(
        key for key, item in value.items()
        if key.startswith("allow_") and isinstance(item, bool) and not item
    )
    parts: list[str] = []
    if enabled:
        parts.append("allow " + ", ".join(_usage_label(key) for key in enabled))
    if disabled:
        parts.append("disallow " + ", ".join(_usage_label(key) for key in disabled))
    if value.get("require_attribution") is True:
        parts.append("requires attribution")
    elif value.get("require_attribution") is False:
        parts.append("attribution not required")
    if value.get("notes"):
        parts.append(str(value["notes"]))
    return "; ".join(parts) if parts else "(declared)"


def _usage_label(key: str) -> str:
    return key.removeprefix("allow_").replace("_", " ")
