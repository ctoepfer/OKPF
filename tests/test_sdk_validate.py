# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for the Python reference SDK validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from okpf import validate


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_DIR = REPO_ROOT / "tests" / "fixtures" / "conformance"


@pytest.mark.parametrize(
    ("fixture_name", "expected_pack_id"),
    [
        ("package-id", "org.example.conformance.package-id"),
        ("legacy-id", "org.example.conformance.legacy-id"),
    ],
)
def test_sdk_validator_accepts_package_id_or_id(
    fixture_name: str,
    expected_pack_id: str,
) -> None:
    result = validate(str(CONFORMANCE_DIR / "valid" / fixture_name))

    assert result.valid, [str(issue) for issue in result.all_issues]
    assert result.pack_id == expected_pack_id


@pytest.mark.parametrize(
    "fixture_name",
    [
        "artifacts-only",
        "records-only",
        "legacy-content",
    ],
)
def test_sdk_validator_accepts_any_core_payload_field(fixture_name: str) -> None:
    result = validate(str(CONFORMANCE_DIR / "valid" / fixture_name))

    assert result.valid, [str(issue) for issue in result.all_issues]


def test_sdk_validator_rejects_missing_payload() -> None:
    result = validate(str(CONFORMANCE_DIR / "invalid" / "missing-payload"))

    assert not result.valid
    assert any("artifacts, records, content" in issue.message for issue in result.errors)
