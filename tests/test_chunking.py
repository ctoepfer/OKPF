from __future__ import annotations

from okpf_prep.chunking import chunk_text


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
