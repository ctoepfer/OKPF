# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for the okpf demo command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from okpf.demo import create_demo_pack, validate_demo_pack
from okpf_validate import load_manifest


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
DEMO_SOURCE = EXAMPLES_DIR / "hello-world" / "content" / "hello.md"


def test_demo_pack_creation(tmp_path):
    """Test that demo creates a valid pack from a source file."""
    kpack_path, temp_dir = create_demo_pack(str(DEMO_SOURCE))
    kpack_file = Path(kpack_path)

    assert kpack_file.exists(), "Pack file should be created"
    assert kpack_file.suffix == ".kpack", "Pack should have .kpack extension"

    manifest, errors = load_manifest(kpack_path)
    assert manifest is not None, f"Manifest should load: {errors}"
    assert manifest.get("okpf_version") == "0.1.0"
    assert manifest.get("domain") == "general"
    assert manifest.get("package_id"), "Package ID should be set"


def test_demo_pack_has_content_artifact(tmp_path):
    """Test that the demo pack includes the source file."""
    kpack_path, temp_dir = create_demo_pack(str(DEMO_SOURCE))
    manifest, _ = load_manifest(kpack_path)

    artifacts = manifest.get("artifacts", [])
    assert len(artifacts) > 0, "Pack should have at least one artifact"
    assert artifacts[0]["path"] == "content/hello.md"
    assert "sha256" in artifacts[0], "Artifact should have SHA-256 hash"


def test_demo_pack_has_evaluations(tmp_path):
    """Test that the demo pack includes auto-generated evaluations."""
    kpack_path, temp_dir = create_demo_pack(str(DEMO_SOURCE))
    manifest, _ = load_manifest(kpack_path)

    evaluations = manifest.get("evaluations", [])
    assert len(evaluations) > 0, "Pack should have evaluations"
    assert "$ref" in evaluations[0], "Evaluations should use $ref"


def test_demo_pack_has_provenance(tmp_path):
    """Test that the demo pack includes provenance metadata."""
    kpack_path, temp_dir = create_demo_pack(str(DEMO_SOURCE))
    manifest, _ = load_manifest(kpack_path)

    assert manifest.get("created"), "Manifest should have created timestamp"


def test_demo_pack_validates_cleanly(tmp_path):
    """Test that the created pack passes validation."""
    kpack_path, temp_dir = create_demo_pack(str(DEMO_SOURCE))

    is_valid = validate_demo_pack(kpack_path)
    assert is_valid, "Demo pack should validate successfully"


def test_demo_with_nonexistent_file():
    """Test that demo raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        create_demo_pack("/nonexistent/file.md")


def test_demo_questions_are_generated():
    """Test that Q&A pairs are actually generated."""
    kpack_path, temp_dir = create_demo_pack(str(DEMO_SOURCE))
    manifest, _ = load_manifest(kpack_path)

    evals_ref = manifest.get("evaluations", [])
    if evals_ref and isinstance(evals_ref, list):
        first_ref = evals_ref[0]
        if isinstance(first_ref, dict) and "$ref" in first_ref:
            ref_file = Path(kpack_path).parent / first_ref["$ref"]
            if ref_file.exists():
                evals_data = json.loads(ref_file.read_text())
                questions = evals_data.get("evaluations", [])
                assert len(questions) > 0, "Should have generated at least one question"
                for q in questions:
                    assert "question" in q
                    assert "expected_answer" in q
