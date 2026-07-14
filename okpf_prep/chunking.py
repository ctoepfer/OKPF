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
# boundary to split on) — a character budget tuned to land in a small
# handful of entries per request.
#
# Live verification against a real damaged grain-reference table found
# 900 still let a dense stretch (chunk-0018: ~8 distinct malt entries in
# 895 chars, ~112 chars/entry) hit the 1024-token output ceiling even
# with the "at most 5 records" prompt instruction, because the model
# doesn't reliably obey that cap when the source material itself has
# more distinct entries than that. 450 roughly halves entries-per-request
# for this extraction pattern (~4 entries), giving real margin under the
# 5-record instruction instead of relying on the model's compliance alone.
DEFAULT_TABLE_MAX_CHARS = 450
DEFAULT_TABLE_OVERLAP_CHARS = 80

# Window size used only to *detect* table-like content (the initial probe
# at each position, and the step size _find_table_transition scans ahead
# with) — deliberately kept larger than DEFAULT_TABLE_MAX_CHARS and NOT
# tied to it. Live verification found that when the detection window was
# shrunk to match a smaller DEFAULT_TABLE_MAX_CHARS (450), is_table_like's
# ratio heuristic started false-positiving on short, borderline runs
# scattered through ordinary prose (a real 21k-char document went from 24
# chunks to 245, mostly tiny bogus "table" fragments) — a small window is
# much more easily tipped over the 60% short-line ratio by a local burst
# than a large one, which dilutes it back into "mostly prose." Detection
# window and batch size are different concerns: this one only needs to be
# big enough to reliably tell table from prose; DEFAULT_TABLE_MAX_CHARS
# separately controls how much of a *confirmed* table region goes in one
# request once detection has already fired.
DEFAULT_TABLE_DETECT_CHARS = 900

# How much of the first table-like chunk in a run to keep as a "header"
# candidate, repeated at the top of every later chunk in that same run.
# Not true column-header parsing (the flattened extraction has no
# reliable delimiter to identify a header row from a data row) — a
# fixed-size leading snippet of the run's first chunk, which in practice
# tends to include the actual column-label text (verified against the
# real grain-table extraction, where the header row lands in the first
# ~150 chars of the first table chunk).
DEFAULT_TABLE_HEADER_CHARS = 200


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
    table_detect_chars: int = DEFAULT_TABLE_DETECT_CHARS,
) -> list[TextChunk]:
    if strategy == "section-aware":
        return _section_aware_chunks(
            text, max_chars, overlap_chars, source_filename,
            table_max_chars=table_max_chars, table_overlap_chars=table_overlap_chars,
            table_detect_chars=table_detect_chars,
        )
    return _flat_chunks(
        text, max_chars, overlap_chars, source_filename,
        table_max_chars=table_max_chars, table_overlap_chars=table_overlap_chars,
        table_detect_chars=table_detect_chars,
    )


def _section_aware_chunks(
    text: str,
    max_chars: int,
    overlap_chars: int,
    source_filename: str,
    table_max_chars: int = DEFAULT_TABLE_MAX_CHARS,
    table_overlap_chars: int = DEFAULT_TABLE_OVERLAP_CHARS,
    table_detect_chars: int = DEFAULT_TABLE_DETECT_CHARS,
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
                table_detect_chars=table_detect_chars,
            )
            chunks.extend(sub_chunks)
            chunk_index += len(sub_chunks)

    if not chunks:
        return _flat_chunks(
            text, max_chars, overlap_chars, source_filename,
            table_max_chars=table_max_chars, table_overlap_chars=table_overlap_chars,
            table_detect_chars=table_detect_chars,
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
    table_detect_chars: int = DEFAULT_TABLE_DETECT_CHARS,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    idx = 0
    chunk_index = start_index
    table_run_header: str | None = None

    while idx < len(text):
        # Is idx itself already inside table-like content? Check a
        # detection-sized window first (deliberately larger than
        # table_max_chars — see DEFAULT_TABLE_DETECT_CHARS docstring: a
        # window this small would false-positive on short prose bursts,
        # while a window spanning both prose and table content would
        # average out and misclassify the boundary the other way).
        immediate_end = min(idx + table_detect_chars, len(text))
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
            transition = _find_table_transition(text, idx, max_chars, table_detect_chars)
            effective_max = (transition - idx) if transition is not None else max_chars
            effective_overlap = overlap_chars

        end = min(idx + effective_max, len(text))

        if end < len(text):
            split = _find_paragraph_break(text, end)
            if split > idx:
                end = split

        chunk_text_slice = text[idx:end]
        is_table_chunk = is_table_like(chunk_text_slice)

        if is_table_chunk:
            if table_run_header is None:
                # First table chunk of a new run — its own leading text
                # becomes the header candidate reused by later chunks in
                # this run; nothing to inject into itself.
                table_run_header = chunk_text_slice[:DEFAULT_TABLE_HEADER_CHARS].strip()
                final_text = chunk_text_slice
            else:
                final_text = (
                    "Table header/context (repeated from the start of this "
                    "table, for column reference only — do not extract it "
                    "again as its own record):\n"
                    f"{table_run_header}\n"
                    "--- continued table data below ---\n"
                    f"{chunk_text_slice}"
                )
        else:
            final_text = chunk_text_slice
            table_run_header = None  # leaving the table run; next one starts fresh

        chunk_id = f"chunk-{chunk_index:04d}"
        chunks.append(
            TextChunk(
                chunk_id=chunk_id,
                text=final_text,
                start_char=idx,
                end_char=end,
                heading=heading,
                source_ref=_make_source_ref(source_filename, chunk_id),
                is_table_like=is_table_chunk,
            )
        )
        chunk_index += 1

        if end >= len(text):
            break
        idx = max(end - effective_overlap, idx + 1)

    return chunks


def _find_table_transition(
    text: str, idx: int, max_chars: int, table_detect_chars: int
) -> int | None:
    """Scan forward from idx in table_detect_chars-sized steps, up to
    max_chars ahead, for where table-like content begins. Returns the
    absolute offset where it starts, or None if the whole window stays
    prose (or the window is exhausted without finding a run long enough
    to trigger is_table_like)."""
    step = max(table_detect_chars, 1)
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
