from __future__ import annotations

import json
from pathlib import Path

import pytest

from okpf_prep.ai.mock import MockAIBackend
from okpf_prep.profiles import load_profile
from okpf_prep.runner import PrepRunner, prepare_training_pack

PROFILES_DIR = Path(__file__).parent.parent / "profiles"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _brewing_profile():
    return load_profile(PROFILES_DIR / "brewing_recipe.yaml")


def test_runner_produces_output_files(tmp_path):
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="ingredient_reference")
    runner = PrepRunner(profile, backend)
    result = runner.run(EXAMPLES_DIR / "brewing_notes.md", tmp_path / "out")

    assert result.manifest_path.exists()
    assert result.records_path.exists()
    assert result.extracted_text_path.exists()
    assert result.report_path.exists()


def test_runner_record_count_positive(tmp_path):
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="ingredient_reference")
    runner = PrepRunner(profile, backend)
    result = runner.run(EXAMPLES_DIR / "brewing_notes.md", tmp_path / "out")

    assert result.record_count > 0


def test_runner_validation_passes(tmp_path):
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="recipe")
    runner = PrepRunner(profile, backend)
    result = runner.run(EXAMPLES_DIR / "brewing_notes.md", tmp_path / "out")

    assert result.validation_status == "pass"
    assert result.errors == []


def test_runner_records_json_valid(tmp_path):
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="ingredient_reference")
    runner = PrepRunner(profile, backend)
    result = runner.run(EXAMPLES_DIR / "brewing_notes.md", tmp_path / "out")

    data = json.loads(result.records_path.read_text())
    assert "records" in data
    assert len(data["records"]) == result.record_count


def test_prepare_training_pack_convenience(tmp_path):
    result = prepare_training_pack(
        source_path=EXAMPLES_DIR / "brewing_notes.md",
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        output_dir=tmp_path / "out",
        backend="mock",
    )
    assert result.record_count > 0
    assert result.manifest_path.exists()


def test_runner_with_txt_source(tmp_path):
    source = tmp_path / "notes.txt"
    source.write_text("Water chemistry affects hop perception.\nSulfate accentuates bitterness.",
                      encoding="utf-8")
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="process_note")
    runner = PrepRunner(profile, backend)
    result = runner.run(source, tmp_path / "out")
    assert result.record_count > 0


def test_runner_missing_source_raises(tmp_path):
    profile = _brewing_profile()
    backend = MockAIBackend()
    runner = PrepRunner(profile, backend)
    with pytest.raises(FileNotFoundError):
        runner.run(tmp_path / "nonexistent.md", tmp_path / "out")


def test_runner_invalid_backend_raises():
    with pytest.raises(ValueError, match="Unknown backend"):
        prepare_training_pack(
            source_path=EXAMPLES_DIR / "brewing_notes.md",
            profile_path=PROFILES_DIR / "brewing_recipe.yaml",
            output_dir="/tmp/should_not_matter",
            backend="invalid_backend",
        )


def test_make_backend_threads_timeout_to_ollama_backend():
    """prepare_training_pack's ollama_timeout must actually reach the
    constructed OllamaBackend, not just be accepted and dropped."""
    from okpf_prep.runner import _make_backend

    backend = _make_backend("ollama", None, "http://localhost:11434", timeout=222.0)
    assert backend.timeout == 222.0


def test_make_backend_omits_timeout_uses_backend_default():
    from okpf_prep.ai.ollama import DEFAULT_TIMEOUT
    from okpf_prep.runner import _make_backend

    backend = _make_backend("ollama", None, "http://localhost:11434")
    assert backend.timeout == DEFAULT_TIMEOUT


def test_make_backend_timeout_ignored_for_mock_backend():
    """Mock backend has no timeout concept; passing one must not raise."""
    from okpf_prep.runner import _make_backend

    backend = _make_backend("mock", None, "http://localhost:11434", timeout=222.0)
    assert backend.name == "mock"


# ---------------------------------------------------------------------------
# Truncated-response diagnostics
# ---------------------------------------------------------------------------

class _FixedResponseBackend:
    """Minimal fake AI backend returning a fixed raw response, for testing
    validation/error-classification paths without mocking httpx."""

    name = "fixed"
    default_model = "fake-model"

    def __init__(self, response: str) -> None:
        self._response = response

    def generate(self, prompt, system=None, schema=None, temperature=0.1, model=None):
        return self._response


def test_truncated_json_response_gets_truncation_hint(tmp_path):
    # No closing brace — simulates a response cut off by num_predict.
    truncated = '{"records": [{"type": "recipe", "title": "T", "content": "unterminated'
    profile = _brewing_profile()
    backend = _FixedResponseBackend(truncated)
    runner = PrepRunner(profile, backend)
    result = runner.run(EXAMPLES_DIR / "brewing_notes.md", tmp_path / "out")
    assert result.validation_status == "fail"
    assert any("output token limit" in e for e in result.errors)


def test_malformed_but_complete_json_response_has_no_truncation_hint(tmp_path):
    # Valid-looking JSON structurally (ends with a closing brace) but the
    # record itself fails schema validation — not a truncation case.
    complete_but_invalid = '{"records": [{"type": "not_allowed_type", "title": "T"}]}'
    profile = _brewing_profile()
    backend = _FixedResponseBackend(complete_but_invalid)
    runner = PrepRunner(profile, backend)
    result = runner.run(EXAMPLES_DIR / "brewing_notes.md", tmp_path / "out")
    assert result.validation_status == "fail"
    assert not any("output token limit" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Generic record shapes — prose, recipe, and table/reference content all
# produce plain OKPF records; nothing in the runner forces a recipe shape.
# ---------------------------------------------------------------------------

def test_prose_source_produces_generic_records(tmp_path):
    source = tmp_path / "prose.txt"
    source.write_text(
        "Base malts form the fermentable backbone of most beer recipes. "
        "They are kilned lightly to preserve enzymatic potential.",
        encoding="utf-8",
    )
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="process_note")
    runner = PrepRunner(profile, backend)
    result = runner.run(source, tmp_path / "out")
    assert result.record_count > 0
    assert result.validation_status == "pass"


def test_table_like_source_produces_ingredient_reference_records(tmp_path):
    rows = "\n".join(f"Malt{i}\nMaltster\nRegion\n{i}L\nBase" for i in range(60))
    source = tmp_path / "table.txt"
    source.write_text(rows, encoding="utf-8")
    profile = _brewing_profile()
    backend = MockAIBackend(record_type="ingredient_reference")
    runner = PrepRunner(profile, backend)
    result = runner.run(source, tmp_path / "out")
    assert result.record_count > 0
    assert result.validation_status == "pass"
    data = json.loads(result.records_path.read_text())
    assert all(r["record_type"] == "ingredient_reference" for r in data["records"])
