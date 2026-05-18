from __future__ import annotations

import re
from typing import Any

from .models import TextChunk

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def chunk_text(
    text: str,
    max_chars: int = 12000,
    overlap_chars: int = 500,
    source_filename: str = "",
    strategy: str = "section-aware",
) -> list[TextChunk]:
    if strategy == "section-aware":
        return _section_aware_chunks(text, max_chars, overlap_chars, source_filename)
    return _flat_chunks(text, max_chars, overlap_chars, source_filename)


def _section_aware_chunks(
    text: str,
    max_chars: int,
    overlap_chars: int,
    source_filename: str,
) -> list[TextChunk]:
    sections = _split_by_headings(text)
    chunks: list[TextChunk] = []
    chunk_index = 0

    for heading, section_text in sections:
        if len(section_text) <= max_chars:
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
            )
            chunks.extend(sub_chunks)
            chunk_index += len(sub_chunks)

    if not chunks:
        return _flat_chunks(text, max_chars, overlap_chars, source_filename)

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
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    idx = 0
    chunk_index = start_index

    while idx < len(text):
        end = min(idx + max_chars, len(text))

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
            )
        )
        chunk_index += 1

        if end >= len(text):
            break
        idx = max(end - overlap_chars, idx + 1)

    return chunks


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
