from __future__ import annotations

from pathlib import Path

import pytest

from okpf_prep.extractors import extract_text

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_extract_txt(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Hello, world!\nLine two.", encoding="utf-8")
    result = extract_text(f)
    assert result.source_type == "txt"
    assert result.source_filename == "sample.txt"
    assert "Hello" in result.text
    assert result.page_count is None
    assert result.warnings == []


def test_extract_md(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("# Title\n\nSome text.", encoding="utf-8")
    result = extract_text(f)
    assert result.source_type == "md"
    assert "Title" in result.text


def test_extract_md_example_file():
    result = extract_text(EXAMPLES_DIR / "brewing_notes.md")
    assert "Cascade" in result.text
    assert result.source_type == "md"


def test_extract_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/file.txt")


def test_extract_unsupported_type_raises(tmp_path):
    f = tmp_path / "doc.docx"
    f.write_bytes(b"fake docx content")
    with pytest.raises(ValueError, match="Unsupported source type"):
        extract_text(f)


def test_extract_txt_unicode(tmp_path):
    f = tmp_path / "unicode.txt"
    f.write_text("Schönes Bier! 🍺 Ñoño.", encoding="utf-8")
    result = extract_text(f)
    assert "Schönes" in result.text
