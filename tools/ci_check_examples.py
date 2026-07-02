#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Release-gate check: validate, pack, unpack, and revalidate every example
and every built-in okpf init template. Also smoke-checks that `okpf
export-rag` produces contract-conformant rows for each of them.

Run locally:

    python3 tools/ci_check_examples.py

Exits non-zero if any example or template fails any step.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import export, scaffold  # noqa: E402
from okpf.cli import _pack, _unpack  # noqa: E402
from okpf_validate import validate_pack  # noqa: E402


def _check_rag_export(name: str, pack_dir: Path) -> list[str]:
    """Smoke-check that `okpf export-rag` produces contract-conformant rows."""
    errors: list[str] = []
    try:
        rows = export.build_rag_rows(str(pack_dir))
    except export.ExportError as exc:
        errors.append(f"{name}: export-rag failed: {exc}")
        return errors

    for index, row in enumerate(rows):
        where = f"{name}: rag row[{index}]"
        if row.get("schema_version") != export.SCHEMA_VERSION:
            errors.append(f"{where}: unexpected schema_version {row.get('schema_version')!r}")
        if not isinstance(row.get("chunk_id"), str) or not row["chunk_id"]:
            errors.append(f"{where}: chunk_id missing or empty")
        if not isinstance(row.get("text"), str) or not row["text"]:
            errors.append(f"{where}: text missing or empty")
        if not isinstance(row.get("package_id"), str) or not row["package_id"]:
            errors.append(f"{where}: package_id missing or empty")
        for dict_field in ("license", "usage_policy", "provenance"):
            if not isinstance(row.get(dict_field), dict):
                errors.append(f"{where}: {dict_field} must be an object")
        if not isinstance(row.get("citation"), str) or not row["citation"]:
            errors.append(f"{where}: citation missing or empty")
        expected_sha256 = hashlib.sha256(row.get("text", "").encode("utf-8")).hexdigest()
        if row.get("sha256") != expected_sha256:
            errors.append(f"{where}: sha256 does not match text content")

    return errors


def _round_trip(name: str, pack_dir: Path, work_dir: Path) -> list[str]:
    """Validate, pack, unpack, revalidate, and export-rag `pack_dir`. Returns error strings."""
    errors: list[str] = []

    result = validate_pack(str(pack_dir))
    if not result.valid:
        errors.append(f"{name}: initial validation failed")
        errors.extend(f"{name}:   {issue}" for issue in result.errors)
        return errors

    kpack_path = work_dir / f"{name}.kpack"
    if _pack(str(pack_dir), str(kpack_path)) != 0:
        errors.append(f"{name}: `okpf pack` failed")
        return errors

    unpacked_dir = work_dir / f"{name}-unpacked"
    if _unpack(str(kpack_path), str(unpacked_dir)) != 0:
        errors.append(f"{name}: `okpf unpack` failed")
        return errors

    revalidated = validate_pack(str(unpacked_dir))
    if not revalidated.valid:
        errors.append(f"{name}: revalidation after pack/unpack failed")
        errors.extend(f"{name}:   {issue}" for issue in revalidated.errors)
        return errors

    errors.extend(_check_rag_export(name, pack_dir))

    return errors


def check_examples(examples_dir: Path, work_dir: Path) -> list[str]:
    errors: list[str] = []
    example_dirs = sorted(
        d for d in examples_dir.iterdir() if d.is_dir() and (d / "manifest.json").is_file()
    )
    if not example_dirs:
        errors.append(f"No example packs found under {examples_dir}")
    for example_dir in example_dirs:
        errors.extend(_round_trip(f"example__{example_dir.name}", example_dir, work_dir))
    return errors


def check_templates(work_dir: Path) -> list[str]:
    errors: list[str] = []
    templates = scaffold.list_templates()
    if not templates:
        errors.append("No built-in okpf init templates found")
    for template in templates:
        dest = work_dir / f"template-{template.id}"
        dest.mkdir(parents=True, exist_ok=True)
        try:
            scaffold.render_template(template, dest, {})
        except scaffold.TemplateError as exc:
            errors.append(f"template__{template.id}: render failed: {exc}")
            continue
        errors.extend(_round_trip(f"template__{template.id}", dest, work_dir))
    return errors


def main() -> int:
    examples_dir = REPO_ROOT / "examples"

    with tempfile.TemporaryDirectory(prefix="okpf_ci_check_") as tmp:
        work_dir = Path(tmp)
        errors = check_examples(examples_dir, work_dir)
        errors.extend(check_templates(work_dir))

    if errors:
        print(f"FAILED ({len(errors)} issue(s)):")
        for error in errors:
            print(f"  {error}")
        return 1

    print("All examples and templates validated, packed, unpacked, and revalidated cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
