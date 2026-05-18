from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from okpf_prep.profiles import load_profile, validate_profile

PROFILES_DIR = Path(__file__).parent.parent / "profiles"


def test_load_brewing_recipe_profile():
    profile = load_profile(PROFILES_DIR / "brewing_recipe.yaml")
    assert profile.id == "brewing_recipe"
    assert "md" in profile.input_types
    assert "recipe" in profile.allowed_record_types
    assert profile.chunking.max_chars == 12000
    assert profile.conversion.require_source_refs is True
    assert profile.conversion.confidence_required is True


def test_load_general_knowledge_profile():
    profile = load_profile(PROFILES_DIR / "general_knowledge.yaml")
    assert profile.id == "general_knowledge"
    assert "fact" in profile.allowed_record_types


def test_validate_valid_profile_passes():
    profile = load_profile(PROFILES_DIR / "brewing_recipe.yaml")
    result = validate_profile(profile)
    assert result.valid
    assert result.errors == []


def test_load_missing_profile_raises():
    with pytest.raises(FileNotFoundError):
        load_profile("/nonexistent/profile.yaml")


def test_load_profile_missing_required_field(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        textwrap.dedent("""\
        id: incomplete
        name: Missing Fields
        """),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required fields"):
        load_profile(bad)


def test_validate_profile_invalid_chunking(tmp_path):
    data = {
        "id": "test",
        "name": "Test",
        "description": "Test profile",
        "domain": "test",
        "input_types": ["txt"],
        "allowed_record_types": ["fact"],
        "chunking": {"max_chars": 50, "overlap_chars": 60},
    }
    p = tmp_path / "p.yaml"
    p.write_text(yaml.dump(data), encoding="utf-8")
    profile = load_profile(p)
    result = validate_profile(profile)
    assert not result.valid
    assert any("overlap_chars" in e for e in result.errors)


def test_validate_profile_warns_on_missing_prompts(tmp_path):
    data = {
        "id": "test",
        "name": "Test",
        "description": "Test profile",
        "domain": "test",
        "input_types": ["txt"],
        "allowed_record_types": ["fact"],
    }
    p = tmp_path / "p.yaml"
    p.write_text(yaml.dump(data), encoding="utf-8")
    profile = load_profile(p)
    result = validate_profile(profile)
    assert result.valid
    assert any("system" in w for w in result.warnings)
