# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Guard against the bundled schema copy drifting from the canonical one.

reference/python/okpf/schemas/ is a bundled copy of the canonical
top-level schemas/ directory, needed so validation still works when `okpf`
is pip-installed without a full repo checkout (see
reference/python/okpf/schemas/__init__.py). The top-level schemas/
directory remains authoritative (CLAUDE.md) -- this test fails loudly if
someone edits one copy and forgets the other, rather than letting them
silently diverge.
"""

from __future__ import annotations

import filecmp
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SCHEMAS_DIR = REPO_ROOT / "schemas"
BUNDLED_SCHEMAS_DIR = REPO_ROOT / "reference" / "python" / "okpf" / "schemas"


def _relative_schema_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*.json")
    }


def test_bundled_schema_files_match_canonical_set() -> None:
    canonical = _relative_schema_files(CANONICAL_SCHEMAS_DIR)
    bundled = _relative_schema_files(BUNDLED_SCHEMAS_DIR)
    assert bundled == canonical, (
        f"Bundled schemas out of sync with canonical schemas/.\n"
        f"Only in canonical: {canonical - bundled}\n"
        f"Only in bundled: {bundled - canonical}\n"
        f"Fix: re-sync reference/python/okpf/schemas/ from schemas/."
    )


def test_bundled_schema_files_are_byte_identical_to_canonical() -> None:
    mismatches = []
    for relative_path in _relative_schema_files(CANONICAL_SCHEMAS_DIR):
        canonical_file = CANONICAL_SCHEMAS_DIR / relative_path
        bundled_file = BUNDLED_SCHEMAS_DIR / relative_path
        if not bundled_file.is_file():
            continue  # covered by the file-set test above
        if not filecmp.cmp(canonical_file, bundled_file, shallow=False):
            mismatches.append(str(relative_path))

    assert not mismatches, (
        f"Bundled schema files differ from canonical schemas/: {mismatches}\n"
        f"Fix: re-copy the listed files from schemas/ to reference/python/okpf/schemas/."
    )
