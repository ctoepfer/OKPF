from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from okpf_prep.cli import cli

PROFILES_DIR = Path(__file__).parent.parent / "profiles"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_prepare_command_exits_zero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, [
        "prepare",
        "--source", str(EXAMPLES_DIR / "brewing_notes.md"),
        "--profile", str(PROFILES_DIR / "brewing_recipe.yaml"),
        "--out", str(tmp_path / "out"),
        "--backend", "mock",
    ])
    assert result.exit_code == 0, result.output


def test_prepare_command_creates_files(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out"
    runner.invoke(cli, [
        "prepare",
        "--source", str(EXAMPLES_DIR / "brewing_notes.md"),
        "--profile", str(PROFILES_DIR / "brewing_recipe.yaml"),
        "--out", str(out),
        "--backend", "mock",
    ])
    assert (out / "manifest.json").exists()
    assert (out / "records.json").exists()
    assert (out / "sources" / "extracted_text.md").exists()
    assert (out / "reports" / "conversion_report.json").exists()


def test_prepare_command_missing_source_nonzero(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, [
        "prepare",
        "--source", str(tmp_path / "nonexistent.md"),
        "--profile", str(PROFILES_DIR / "brewing_recipe.yaml"),
        "--out", str(tmp_path / "out"),
        "--backend", "mock",
    ])
    assert result.exit_code != 0


def test_validate_profile_command_valid():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "validate-profile",
        str(PROFILES_DIR / "brewing_recipe.yaml"),
    ])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_validate_profile_command_missing_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-profile", "/nonexistent/profile.yaml"])
    assert result.exit_code != 0


def test_validate_profile_command_invalid_profile(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("id: x\nname: X\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-profile", str(bad)])
    assert result.exit_code != 0


def test_extract_text_command(tmp_path):
    out_file = tmp_path / "extracted.md"
    runner = CliRunner()
    result = runner.invoke(cli, [
        "extract-text",
        str(EXAMPLES_DIR / "brewing_notes.md"),
        "--out", str(out_file),
    ])
    assert result.exit_code == 0
    assert out_file.exists()
    assert "Cascade" in out_file.read_text()


def test_extract_text_missing_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["extract-text", "/nonexistent/file.md"])
    assert result.exit_code != 0


def test_extract_text_html_command(tmp_path):
    src = tmp_path / "doc.html"
    src.write_text("<html><body><h1>Doc</h1><p>Body</p></body></html>", encoding="utf-8")

    out_file = tmp_path / "extracted.md"
    runner = CliRunner()
    result = runner.invoke(cli, [
        "extract-text",
        str(src),
        "--out",
        str(out_file),
    ])
    assert result.exit_code == 0
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8")
    assert "Doc" in text
    assert "Body" in text
