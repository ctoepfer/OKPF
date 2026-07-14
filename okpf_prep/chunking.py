from __future__ import annotations

import re
from typing import Any

from .models import TextChunk

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# A PDF table with columns flattened into one cell per line produces a run
# of many short lines with none of the sentence-length variation normal
# prose has. Tuned against a real damaged extraction (a 24-page grain
# reference table): 1701/1780 non-empty lines were <=40 chars (95.6%),
# vs. well under 10% for the prose pages of the same document.
DEFAULT_TABLE_SHORT_LINE_MAX_CHARS = 40
DEFAULT_TABLE_SHORT_LINE_RATIO = 0.6
DEFAULT_TABLE_MIN_LINES = 15

# Much smaller than the prose default (12000): a table-like region gets
# batched into groups small enough that (a) the prompt stays well under
# the model's usable context window even when OLLAMA_NUM_PARALLEL halves
# it, and (b) the model can't reasonably try to emit dozens of records in
# one response, which is what drove the original 300s timeouts. Not a
# precise "N rows" count (the flattened extraction has no reliable row
# boundary to split on) — a character budget tuned to land in roughly the
# 5-10-row range for this kind of extraction (~150-300 chars/row observed).
DEFAULT_TABLE_MAX_CHARS = 900
DEFAULT_TABLE_OVERLAP_CHARS = 80


def is_table_like(
    text: str,
    *,
    min_lines: int = DEFAULT_TABLE_MIN_LINES,
    short_line_max_chars: int = DEFAULT_TABLE_SHORT_LINE_MAX_CHARS,
    short_line_ratio: float = DEFAULT_TABLE_SHORT_LINE_RATIO,
) -> bool:
    """Heuristic: does this text look like a table whose columns were
    flattened into one value per line during extraction?

    Not a general table detector — specifically tuned for the "cell per
    line" damage pattern common in pypdf output for multi-column tables.
    A document with too few non-empty lines is never flagged (avoids
    misclassifying a short prose paragraph that happens to have a few
    short lines).
    """
    lines = [line for line in text.split("\n") if line.strip()]
    if len(lines) < min_lines:
        return False
    short = sum(1 for line in lines if len(line.strip()) <= short_line_max_chars)
    return (short / len(lines)) >= short_line_ratio


def chunk_text(
    text: str,
    max_chars: int = 12000,
    overlap_chars: int = 500,
    source_filename: str = "",
    strategy: str = "section-aware",
    table_max_chars: int = DEFAULT_TABLE_MAX_CHARS,
    table_overlap_chars: int = DEFAULT_TABLE_OVERLAP_CHARS,
) -> list[TextChunk]:
    if strategy == "section-aware":
        return _section_aware_chunks(
            text, max_chars, overlap_chars, source_filename,
            table_max_chars=table_max_chars, table_overlap_chars=table_overlap_chars,
        )
    return _flat_chunks(
        text, max_chars, overlap_chars, source_filename,
        table_max_chars=table_max_chars, table_overlap_chars=table_overlap_chars,
    )


def _section_aware_chunks(
    text: str,
    max_chars: int,
    overlap_chars: int,
    source_filename: str,
    table_max_chars: int = DEFAULT_TABLE_MAX_CHARS,
    table_overlap_chars: int = DEFAULT_TABLE_OVERLAP_CHARS,
) -> list[TextChunk]:
    sections = _split_by_headings(text)
    chunks: list[TextChunk] = []
    chunk_index = 0

    for heading, section_text in sections:
        # A short-but-table-like section (e.g. a table entirely under one
        # heading, smaller than max_chars) still needs table batching even
        # though it fits in a single normal-sized chunk.
        if len(section_text) <= max_chars and not is_table_like(section_text):
            chunk_id = f"chunk-{chunk_index:04d}"
            start = text.find(section_text)
            end = start + len(section_text)
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=section_text,
                    start_char=max(start, 0),
                    end_char=max(end, 0),
                    heading=heading or None,
                    source_ref=_make_source_ref(source_filename, chunk_id),
                )
            )
            chunk_index += 1
        else:
            sub_chunks = _flat_chunks(
                section_text,
                max_chars,
                overlap_chars,
                source_filename,
                start_index=chunk_index,
                heading=heading or None,
                table_max_chars=table_max_chars,
                table_overlap_chars=table_overlap_chars,
            )
            chunks.extend(sub_chunks)
            chunk_index += len(sub_chunks)

    if not chunks:
        return _flat_chunks(
            text, max_chars, overlap_chars, source_filename,
            table_max_chars=table_max_chars, table_overlap_chars=table_overlap_chars,
        )

    return chunks


def _split_by_headings(text: str) -> list[tuple[str, str]]:
    """Split text into (heading, section_text) pairs on Markdown headings."""
    positions = [m.start() for m in _HEADING_RE.finditer(text)]

    if not positions:
        return [("", text)]

    sections: list[tuple[str, str]] = []

    if positions[0] > 0:
        preamble = text[: positions[0]].strip()
        if preamble:
            sections.append(("", preamble))

    for i, pos in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        block = text[pos:end]
        first_line_end = block.index("\n") if "\n" in block else len(block)
        heading_line = block[:first_line_end].strip()
        heading_text = _HEADING_RE.match(heading_line)
        heading = heading_text.group(2).strip() if heading_text else heading_line
        sections.append((heading, block.strip()))

    return sections


def _flat_chunks(
    text: str,
    max_chars: int,
    overlap_chars: int,
    source_filename: str,
    start_index: int = 0,
    heading: str | None = None,
    table_max_chars: int = DEFAULT_TABLE_MAX_CHARS,
    table_overlap_chars: int = DEFAULT_TABLE_OVERLAP_CHARS,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    idx = 0
    chunk_index = start_index

    while idx < len(text):
        # Is idx itself already inside table-like content? Check a
        # table-sized window first (not a full max_chars probe — a large
        # probe spanning both prose and table content would average out
        # and misclassify the boundary).
        immediate_end = min(idx + table_max_chars, len(text))
        in_table = is_table_like(text[idx:immediate_end])

        if in_table:
            effective_max = table_max_chars
            effective_overlap = table_overlap_chars
        else:
            # Prose here — but scan ahead for where table-like content
            # starts within the normal chunk window, so a large prose
            # chunk doesn't swallow the start of a table. If no
            # transition is found, behavior is identical to the
            # pre-table-awareness chunker (full max_chars).
            transition = _find_table_transition(text, idx, max_chars, table_max_chars)
            effective_max = (transition - idx) if transition is not None else max_chars
            effective_overlap = overlap_chars

        end = min(idx + effective_max, len(text))

        if end < len(text):
            split = _find_paragraph_break(text, end)
            if split > idx:
                end = split

        chunk_text_slice = text[idx:end]
        chunk_id = f"chunk-{chunk_index:04d}"
        chunks.append(
            TextChunk(
                chunk_id=chunk_id,
                text=chunk_text_slice,
                start_char=idx,
                end_char=end,
                heading=heading,
                source_ref=_make_source_ref(source_filename, chunk_id),
                is_table_like=is_table_like(chunk_text_slice),
            )
        )
        chunk_index += 1

        if end >= len(text):
            break
        idx = max(end - effective_overlap, idx + 1)

    return chunks


def _find_table_transition(
    text: str, idx: int, max_chars: int, table_max_chars: int
) -> int | None:
    """Scan forward from idx in table_max_chars-sized steps, up to
    max_chars ahead, for where table-like content begins. Returns the
    absolute offset where it starts, or None if the whole window stays
    prose (or the window is exhausted without finding a run long enough
    to trigger is_table_like)."""
    step = max(table_max_chars, 1)
    pos = idx
    limit = min(idx + max_chars, len(text))
    while pos < limit:
        window_end = min(pos + step, limit)
        if is_table_like(text[pos:window_end]):
            return pos
        pos = window_end
    return None


def _find_paragraph_break(text: str, near: int) -> int:
    """Find the nearest paragraph break before or at `near`."""
    search_start = max(0, near - 200)
    segment = text[search_start:near]
    double_nl = segment.rfind("\n\n")
    if double_nl != -1:
        return search_start + double_nl + 2
    single_nl = segment.rfind("\n")
    if single_nl != -1:
        return search_start + single_nl + 1
    return near


def _make_source_ref(source_filename: str, chunk_id: str) -> dict[str, Any]:
    return {"source_file": source_filename, "chunk_id": chunk_id}
