#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Release-gate check: validate, pack, unpack, and revalidate every example
and every built-in okpf init template.

Run locally:

    python3 tools/ci_check_examples.py

Exits non-zero if any example or template fails any step.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import scaffold  # noqa: E402
from okpf.cli import _pack, _unpack  # noqa: E402
from okpf_validate import validate_pack  # noqa: E402


def _round_trip(name: str, pack_dir: Path, work_dir: Path) -> list[str]:
    """Validate, pack, unpack, and revalidate `pack_dir`. Returns error strings."""
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
