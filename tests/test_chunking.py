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
        # Tolerance covers both paragraph-break search slack and the
        # repeated-header text injected into every chunk after the first
        # in a table run (see test_table_header_is_repeated_in_later_chunks).
        assert len(c.text) <= 900 + 700
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
    # +700 tolerance: paragraph-break search slack plus the repeated-header
    # text injected into chunks after the first in a table run.
    assert all(len(c.text) <= 900 + 700 for c in table_chunks)


def test_real_damaged_extraction_produces_small_table_batches():
    """Regression test for the original failure: a document with mostly
    tabular content chunked at the default max_chars=12000 (the
    brewing_recipe profile's setting) must not produce one or two giant
    chunks the model can't process within a reasonable timeout."""
    text = _prose_text(paragraphs=15) + "\n\n" + _flattened_table_text(rows=300)
    chunks = chunk_text(text, max_chars=12000, overlap_chars=500, strategy="section-aware")
    assert len(chunks) > 5
    # +700 tolerance: paragraph-break search slack plus the repeated-header
    # text injected into chunks after the first in a table run.
    assert all(
        len(c.text) <= 900 + 700 or not c.is_table_like
        for c in chunks
    )


# ---------------------------------------------------------------------------
# Table header preservation across a table run
# ---------------------------------------------------------------------------

def test_first_table_chunk_of_a_run_has_no_injected_header():
    """The first table chunk in a run IS the header source — it should not
    have the "repeated header" preamble injected into itself."""
    text = _flattened_table_text(rows=200)
    chunks = chunk_text(
        text, max_chars=12000, overlap_chars=500, strategy="flat",
        table_max_chars=450, table_overlap_chars=80,
    )
    assert "Table header/context" not in chunks[0].text


def test_table_header_is_repeated_in_later_chunks():
    """Every table chunk after the first in a run should carry a repeated
    header snippet so the model has column context on every request, not
    just the first."""
    text = _flattened_table_text(rows=200)
    chunks = chunk_text(
        text, max_chars=12000, overlap_chars=500, strategy="flat",
        table_max_chars=450, table_overlap_chars=80,
    )
    table_chunks = [c for c in chunks if c.is_table_like]
    assert len(table_chunks) > 2
    for c in table_chunks[1:]:
        assert "Table header/context" in c.text
        assert "continued table data below" in c.text


def test_table_header_does_not_leak_across_separate_table_runs():
    """Two distinct table regions separated by prose must not share a
    header — the second run's header should come from its own start, not
    leftover state from the first."""
    table_a = _flattened_table_text(rows=100)
    prose = "\n\n" + _prose_text(paragraphs=10) + "\n\n"
    table_b = "Hop0\nBrewer\nOrigin\nAlpha0\nPellet\n" * 40
    text = table_a + prose + table_b

    chunks = chunk_text(
        text, max_chars=12000, overlap_chars=500, strategy="flat",
        table_max_chars=450, table_overlap_chars=80,
    )
    table_chunks = [c for c in chunks if c.is_table_like]
    # Chunks belonging to table_b must never quote table_a's header text
    # (e.g. "Malt0") inside their injected header preamble.
    b_chunks = [c for c in table_chunks if "Hop0" in c.text or "Brewer" in c.text]
    assert b_chunks
    for c in b_chunks:
        if "Table header/context" in c.text:
            preamble_end = c.text.index("--- continued table data below ---")
            assert "Malt0" not in c.text[:preamble_end]


def test_default_table_max_chars_gives_headroom_under_record_cap():
    """Regression guard for the chunk-0018 live-verification failure: a
    dense real-world table region (~112 chars/entry observed) chunked at
    the default table size should contain noticeably fewer raw entries
    than MAX_RECORDS_PER_CHUNK, not right up against it."""
    from okpf_prep.chunking import DEFAULT_TABLE_MAX_CHARS
    from okpf_prep.prompts import MAX_RECORDS_PER_CHUNK

    chars_per_entry_observed = 112
    entries_per_chunk = DEFAULT_TABLE_MAX_CHARS / chars_per_entry_observed
    assert entries_per_chunk < MAX_RECORDS_PER_CHUNK


def test_small_table_max_chars_does_not_fragment_prose():
    """Regression guard: a live-verification run found that shrinking
    DEFAULT_TABLE_MAX_CHARS also shrank the *detection* window (both the
    initial in_table probe and _find_table_transition's scan step), which
    made is_table_like's ratio heuristic false-positive on short bursts
    scattered through ordinary prose — a real ~21k-char document went from
    24 chunks to 245, almost all bogus tiny "table" fragments. Detection
    window size (DEFAULT_TABLE_DETECT_CHARS) must stay decoupled from
    table batch size (DEFAULT_TABLE_MAX_CHARS) so shrinking one doesn't
    silently make the other over-trigger."""
    # Prose interspersed with short lines (a bulleted nav-link style list,
    # like "Malt Overview | Base Malts | Caramel & Crystal Malts" broken
    # onto separate short lines) — realistic borderline content that must
    # not tip into table classification just because the scan window is
    # small.
    prose_with_short_bursts = "\n\n".join(
        "This is an ordinary paragraph explaining malts and their use "
        "in brewing beer, several sentences long, clearly prose."
        for _ in range(20)
    ) + "\n" + "\n".join(["Overview", "Base Malts", "Crystal Malts", "Adjuncts", "Roasted"]) * 3

    chunks = chunk_text(
        prose_with_short_bursts, max_chars=12000, overlap_chars=500,
        strategy="section-aware",
    )
    # A handful of chunks, not dozens — the old bug produced ~10x too many.
    assert len(chunks) <= 5
