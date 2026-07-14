from __future__ import annotations

from okpf_prep.chunking import chunk_text, is_table_like


def test_short_text_single_chunk():
    text = "This is a short text."
    chunks = chunk_text(text, max_chars=12000, overlap_chars=500)
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].chunk_id == "chunk-0000"


def test_long_text_multiple_chunks():
    text = "word " * 3000  # ~15000 chars
    chunks = chunk_text(text, max_chars=5000, overlap_chars=200, strategy="flat")
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 5200  # slight tolerance for paragraph boundary


def test_chunk_ids_are_sequential():
    text = "x " * 5000
    chunks = chunk_text(text, max_chars=1000, overlap_chars=100, strategy="flat")
    ids = [c.chunk_id for c in chunks]
    expected = [f"chunk-{i:04d}" for i in range(len(ids))]
    assert ids == expected


def test_section_aware_splits_on_headings():
    text = "# Section One\n\nContent of section one.\n\n## Section Two\n\nContent of section two."
    chunks = chunk_text(text, max_chars=12000, overlap_chars=500, strategy="section-aware")
    assert len(chunks) >= 2
    headings = [c.heading for c in chunks if c.heading]
    assert any("Section One" in h for h in headings)
    assert any("Section Two" in h for h in headings)


def test_chunk_covers_all_text_flat():
    text = "abcdefghij" * 100  # 1000 chars
    chunks = chunk_text(text, max_chars=300, overlap_chars=50, strategy="flat")
    reconstructed = chunks[0].text
    for chunk in chunks[1:]:
        # Subsequent chunks overlap — just verify no chunk is empty
        assert len(chunk.text) > 0
    # First + last should cover start and end of text
    assert text[:10] in chunks[0].text
    assert text[-10:] in chunks[-1].text


def test_source_ref_included_in_chunk():
    text = "Some content here."
    chunks = chunk_text(text, source_filename="source.md")
    assert chunks[0].source_ref["source_file"] == "source.md"
    assert chunks[0].source_ref["chunk_id"] == "chunk-0000"


def test_empty_text_returns_one_chunk():
    chunks = chunk_text("")
    assert len(chunks) == 1
    assert chunks[0].text == ""


def test_overlap_does_not_skip_text():
    text = "A" * 200 + "B" * 200 + "C" * 200
    chunks = chunk_text(text, max_chars=250, overlap_chars=50, strategy="flat")
    full = "".join(c.text for c in chunks)
    assert "A" in full and "B" in full and "C" in full


# ---------------------------------------------------------------------------
# is_table_like — detection heuristic
# ---------------------------------------------------------------------------

def _flattened_table_text(rows: int = 30) -> str:
    """Simulates a PDF table whose columns were flattened to one value
    per line, e.g. "Pilsner\\nWeyermann\\nGermany\\n2L\\n..." repeated."""
    lines = []
    for i in range(rows):
        lines += [f"Malt{i}", "Maltster", "Region", f"{i}L", "Base"]
    return "\n".join(lines)


def _prose_text(paragraphs: int = 8) -> str:
    return "\n\n".join(
        "This is an ordinary paragraph of explanatory prose about base "
        "malts and how they contribute fermentable sugars to the mash. "
        "It reads like normal sentences, not a table."
        for _ in range(paragraphs)
    )


def test_flattened_table_is_detected():
    assert is_table_like(_flattened_table_text()) is True


def test_prose_is_not_detected_as_table():
    assert is_table_like(_prose_text()) is False


def test_short_text_never_flagged_as_table():
    """A handful of short lines (e.g. a short list) shouldn't trigger table
    mode — min_lines guards against false positives on small snippets."""
    assert is_table_like("A\nB\nC\nD\nE") is False


def test_single_long_line_is_not_a_table():
    assert is_table_like("word " * 3000) is False


# ---------------------------------------------------------------------------
# Table-aware chunk boundaries
# ---------------------------------------------------------------------------

def test_table_region_gets_smaller_chunks_than_max_chars():
    text = _flattened_table_text(rows=200)  # large flattened table
    chunks = chunk_text(
        text, max_chars=12000, overlap_chars=500, strategy="flat",
        table_max_chars=900, table_overlap_chars=80,
    )
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text) <= 900 + 200  # tolerance for paragraph-break search
        assert c.is_table_like is True


def test_prose_region_unaffected_by_table_chunking():
    """A pure-prose document must chunk exactly as before — table-awareness
    should not change behavior where the heuristic never fires."""
    text = _prose_text(paragraphs=200)
    chunks_with_table_awareness = chunk_text(
        text, max_chars=5000, overlap_chars=200, strategy="flat",
        table_max_chars=900, table_overlap_chars=80,
    )
    chunks_default = chunk_text(text, max_chars=5000, overlap_chars=200, strategy="flat")
    assert [c.text for c in chunks_with_table_awareness] == [c.text for c in chunks_default]
    assert all(not c.is_table_like for c in chunks_with_table_awareness)


def test_mixed_prose_then_table_does_not_bundle_table_into_prose_chunk():
    """A large max_chars window that starts as prose but runs into a table
    partway through must not swallow the table into one giant chunk."""
    prose = _prose_text(paragraphs=10)  # ~1000 chars
    table = _flattened_table_text(rows=100)  # large table region
    text = prose + "\n\n" + table

    chunks = chunk_text(
        text, max_chars=12000, overlap_chars=500, strategy="flat",
        table_max_chars=900, table_overlap_chars=80,
    )
    # The first chunk must not extend all the way to max_chars (12000) —
    # it should stop close to where the table begins.
    assert len(chunks[0].text) < len(prose) + 500
    assert chunks[0].is_table_like is False
    # At least one subsequent chunk must be table-flagged and small.
    table_chunks = [c for c in chunks if c.is_table_like]
    assert table_chunks
    assert all(len(c.text) <= 900 + 200 for c in table_chunks)


def test_real_damaged_extraction_produces_small_table_batches():
    """Regression test for the original failure: a document with mostly
    tabular content chunked at the default max_chars=12000 (the
    brewing_recipe profile's setting) must not produce one or two giant
    chunks the model can't process within a reasonable timeout."""
    text = _prose_text(paragraphs=15) + "\n\n" + _flattened_table_text(rows=300)
    chunks = chunk_text(text, max_chars=12000, overlap_chars=500, strategy="section-aware")
    assert len(chunks) > 5
    assert all(
        len(c.text) <= 900 + 200 or not c.is_table_like
        for c in chunks
    )
