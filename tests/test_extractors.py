from __future__ import annotations

import socket
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


def test_extract_html_supported(tmp_path):
    f = tmp_path / "sample.html"
    f.write_text("<html><body><h1>Title</h1><p>Body text.</p></body></html>", encoding="utf-8")
    result = extract_text(f)
    assert result.source_type == "html"
    assert "Title" in result.text
    assert "Body text" in result.text


def test_extract_htm_supported(tmp_path):
    f = tmp_path / "sample.htm"
    f.write_text("<html><body><p>HTM works.</p></body></html>", encoding="utf-8")
    result = extract_text(f)
    assert result.source_type == "html"
    assert "HTM works" in result.text


def test_html_script_style_nav_removed(tmp_path):
    f = tmp_path / "doc.html"
    f.write_text(
        """
        <html><body>
          <nav>Site menu</nav>
          <header>Header chrome</header>
          <p>Keep this paragraph.</p>
          <script>alert('x')</script>
          <style>p{color:red}</style>
          <noscript>fallback</noscript>
          <footer>Footer chrome</footer>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = extract_text(f)
    assert "Keep this paragraph" in result.text
    assert "Site menu" not in result.text
    assert "Header chrome" not in result.text
    assert "Footer chrome" not in result.text
    assert "alert('x')" not in result.text
    assert "p{color:red}" not in result.text


def test_html_lists_preserved(tmp_path):
    f = tmp_path / "list.html"
    f.write_text(
        """
        <html><body>
          <ul><li>One</li><li>Two</li></ul>
          <ol><li>First</li><li>Second</li></ol>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = extract_text(f)
    assert "- One" in result.text
    assert "- Two" in result.text
    assert "1. First" in result.text
    assert "2. Second" in result.text


def test_html_table_header_and_row_boundaries_preserved(tmp_path):
    f = tmp_path / "table.html"
    f.write_text(
        """
        <html><body>
          <h2>Grains</h2>
          <table>
            <tr><th>Name</th><th>Color</th></tr>
            <tr><td>Pilsner</td><td>1.5</td></tr>
            <tr><td>Munich</td><td>9</td></tr>
          </table>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = extract_text(f)
    table_blocks = [b for b in result.prechunked_blocks if b.is_table_like]
    assert table_blocks
    first = table_blocks[0].text
    assert "| Name | Color |" in first
    assert "| Pilsner | 1.5 |" in first
    assert "| Munich | 9 |" in first
    assert "row_range=" in first


def test_html_repeated_table_batches_include_only_table_header(tmp_path):
        rows = "\n".join(
                f"<tr><td>Malt {i}</td><td>{i}</td></tr>" for i in range(1, 70)
        )
        f = tmp_path / "batches.html"
        f.write_text(
                f"""
                <html><body>
                    <p>Prose intro that should not be repeated in each table batch.</p>
                    <table>
                        <tr><th>Name</th><th>Color</th></tr>
                        {rows}
                    </table>
                </body></html>
                """,
                encoding="utf-8",
        )
        result = extract_text(f)
        table_blocks = [b.text for b in result.prechunked_blocks if b.is_table_like]
        assert len(table_blocks) > 1
        for block in table_blocks:
                assert "| Name | Color |" in block
                assert "Prose intro" not in block


def test_html_mixed_prose_and_table_extraction(tmp_path):
    f = tmp_path / "mixed.html"
    f.write_text(
        """
        <html><body>
          <h1>Guide</h1>
          <p>Paragraph before table.</p>
          <table>
            <tr><th>A</th><th>B</th></tr>
            <tr><td>1</td><td>2</td></tr>
          </table>
          <p>Paragraph after table.</p>
        </body></html>
        """,
        encoding="utf-8",
    )
    result = extract_text(f)
    prose = [b for b in result.prechunked_blocks if not b.is_table_like]
    tables = [b for b in result.prechunked_blocks if b.is_table_like]
    assert prose
    assert tables
    assert any("Paragraph before table" in b.text for b in prose)
    assert any("Paragraph after table" in b.text for b in prose)


def test_html_malformed_but_recoverable(tmp_path):
    f = tmp_path / "broken.html"
    f.write_text("<html><body><h1>Broken<p>Still readable<table><tr><th>A", encoding="utf-8")
    result = extract_text(f)
    assert "Broken" in result.text
    assert "Still readable" in result.text


def test_html_unicode_normalization(tmp_path):
    f = tmp_path / "unicode.html"
    # Includes compatibility ligature that should normalize to plain "fi"
    f.write_text("<html><body><p>ofﬁce malt guide</p></body></html>", encoding="utf-8")
    result = extract_text(f)
    assert "office" in result.text


def test_html_relative_link_provenance_only_when_source_url_available(tmp_path):
    f = tmp_path / "links.html"
    f.write_text(
        "<html><body><p>See <a href='/docs/malts'>malts</a>.</p></body></html>",
        encoding="utf-8",
    )
    with_url = extract_text(f, source_url="https://example.com/guide")
    no_url = extract_text(f)
    assert any(p.get("kind") == "link" and p.get("resolved_url") == "https://example.com/docs/malts" for p in with_url.provenance)
    assert not any(p.get("kind") == "link" for p in no_url.provenance)


def test_html_no_external_network_fetch(tmp_path, monkeypatch):
    f = tmp_path / "network.html"
    f.write_text(
        "<html><body><img src='https://example.com/x.png'><p>Local parse only</p></body></html>",
        encoding="utf-8",
    )

    def _deny_socket(*_args, **_kwargs):
        raise AssertionError("No network calls expected during HTML extraction")

    monkeypatch.setattr(socket, "create_connection", _deny_socket)
    result = extract_text(f)
    assert "Local parse only" in result.text


# ---------------------------------------------------------------------------
# PDF extraction — Unicode normalization
# ---------------------------------------------------------------------------

def _mock_pypdf_reader(page_texts):
    from unittest.mock import MagicMock

    pages = []
    for text in page_texts:
        page = MagicMock()
        page.extract_text.return_value = text
        pages.append(page)
    reader = MagicMock()
    reader.pages = pages
    return reader


def test_pdf_extraction_strips_replacement_characters(tmp_path, monkeypatch):
    # extractors.py imports pypdf lazily inside the function, so patch the
    # real module's PdfReader attribute directly.
    import pypdf as real_pypdf

    f = tmp_path / "damaged.pdf"
    f.write_bytes(b"%PDF-1.4 fake")

    reader = _mock_pypdf_reader(["Weyermann� Pilsner Malt", "Second page text"])
    monkeypatch.setattr(real_pypdf, "PdfReader", lambda *_a, **_k: reader)

    result = extract_text(f)
    assert "�" not in result.text
    assert "Weyermann" in result.text


def test_pdf_extraction_warns_about_replacement_character_damage(tmp_path, monkeypatch):
    import pypdf as real_pypdf

    f = tmp_path / "damaged.pdf"
    f.write_bytes(b"%PDF-1.4 fake")

    reader = _mock_pypdf_reader(["A�B�C�D"])
    monkeypatch.setattr(real_pypdf, "PdfReader", lambda *_a, **_k: reader)

    result = extract_text(f)
    assert any("unrecognized character" in w for w in result.warnings)


def test_pdf_extraction_no_warning_when_clean(tmp_path, monkeypatch):
    import pypdf as real_pypdf

    f = tmp_path / "clean.pdf"
    f.write_bytes(b"%PDF-1.4 fake")

    reader = _mock_pypdf_reader(["Perfectly clean extracted text."])
    monkeypatch.setattr(real_pypdf, "PdfReader", lambda *_a, **_k: reader)

    result = extract_text(f)
    assert not any("unrecognized character" in w for w in result.warnings)
