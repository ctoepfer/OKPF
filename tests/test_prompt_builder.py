from __future__ import annotations

from pathlib import Path

from okpf_prep.models import TextChunk
from okpf_prep.profiles import load_profile
from okpf_prep.prompts import build_system_prompt, build_user_prompt

PROFILES_DIR = Path(__file__).parent.parent / "profiles"


def _brewing_profile():
    return load_profile(PROFILES_DIR / "brewing_recipe.yaml")


def _sample_chunk(chunk_id: str = "chunk-0001") -> TextChunk:
    return TextChunk(
        chunk_id=chunk_id,
        text="Cascade hops are floral and citrusy.",
        start_char=0,
        end_char=36,
        heading="Hop Selection",
        source_ref={"source_file": "brewing_notes.md", "chunk_id": chunk_id},
    )


def test_system_prompt_includes_domain():
    profile = _brewing_profile()
    system = build_system_prompt(profile)
    assert "brewing" in system.lower()


def test_system_prompt_includes_allowed_types():
    profile = _brewing_profile()
    system = build_system_prompt(profile)
    assert "recipe" in system


def test_system_prompt_instructs_json_only():
    profile = _brewing_profile()
    system = build_system_prompt(profile)
    assert "JSON" in system


def test_user_prompt_includes_chunk_id():
    profile = _brewing_profile()
    chunk = _sample_chunk("chunk-0042")
    prompt = build_user_prompt(profile, chunk, "brewing_notes.md")
    assert "chunk-0042" in prompt


def test_user_prompt_includes_source_filename():
    profile = _brewing_profile()
    chunk = _sample_chunk()
    prompt = build_user_prompt(profile, chunk, "brewing_notes.md")
    assert "brewing_notes.md" in prompt


def test_user_prompt_includes_chunk_text():
    profile = _brewing_profile()
    chunk = _sample_chunk()
    prompt = build_user_prompt(profile, chunk, "brewing_notes.md")
    assert "Cascade hops" in prompt


def test_user_prompt_includes_heading():
    profile = _brewing_profile()
    chunk = _sample_chunk()
    prompt = build_user_prompt(profile, chunk, "brewing_notes.md")
    assert "Hop Selection" in prompt


def test_user_prompt_includes_schema_example():
    profile = _brewing_profile()
    chunk = _sample_chunk()
    prompt = build_user_prompt(profile, chunk, "brewing_notes.md")
    assert "records" in prompt
    assert "confidence" in prompt
