from __future__ import annotations

import json

from .models import TextChunk
from .profiles import TrainingProfile

# Applied only to chunks flagged is_table_like (see chunking.is_table_like).
# Bounds how many records a single call is asked to produce — the model
# being asked to reconstruct every row of a large flattened table in one
# response (dozens of records, each with title/summary/content/source_refs)
# was the main driver of generations that ran past a 300s timeout without
# finishing. Table chunks are already batched small (~900 chars, roughly
# 5-15 flattened-table lines) by the chunker, so this is a backstop, not
# the primary mechanism.
MAX_RECORDS_PER_TABLE_CHUNK = 10


def build_system_prompt(profile: TrainingProfile) -> str:
    parts = [profile.prompt.system.strip()]

    domain_line = f"Domain: {profile.domain}"
    allowed = ", ".join(profile.allowed_record_types)
    allowed_line = f"Allowed record types: {allowed}"

    parts.extend([domain_line, allowed_line])
    parts.append(
        "You must respond with valid JSON only — no markdown fences, no explanation."
    )

    return "\n\n".join(p for p in parts if p)


def build_user_prompt(
    profile: TrainingProfile,
    chunk: TextChunk,
    source_filename: str,
) -> str:
    schema_example = _schema_example(profile, chunk, source_filename)

    lines = [
        profile.prompt.instructions.strip(),
        "",
        f"Source file: {source_filename}",
        f"Chunk ID: {chunk.chunk_id}",
    ]
    if chunk.heading:
        lines.append(f"Section heading: {chunk.heading}")

    if chunk.is_table_like:
        lines += [
            "",
            "This chunk contains fragmented table/reference data — columns "
            "were likely flattened into separate lines during text "
            "extraction, so row boundaries may be ambiguous or damaged. "
            f"Extract at most {MAX_RECORDS_PER_TABLE_CHUNK} distinct entries "
            "you can identify with reasonable confidence from this excerpt. "
            "Do not try to force every fragment into a record, and do not "
            "pad the response with uncertain or duplicate entries — a "
            "shorter, accurate response is better than an exhaustive one.",
        ]

    lines += [
        "",
        "Source text:",
        "---",
        chunk.text,
        "---",
        "",
        "Return a JSON object exactly matching this structure:",
        schema_example,
    ]

    return "\n".join(lines)


def _schema_example(
    profile: TrainingProfile,
    chunk: TextChunk,
    source_filename: str,
) -> str:
    record_type = profile.allowed_record_types[0] if profile.allowed_record_types else "knowledge"
    example: dict = {
        "records": [
            {
                "type": record_type,
                "title": "<concise title>",
                "summary": "<one or two sentence summary>",
                "content": "<detailed extracted content>",
                "source_refs": [
                    {
                        "source_file": source_filename,
                        "chunk_id": chunk.chunk_id,
                    }
                ],
                "confidence": 0.9,
            }
        ]
    }
    return json.dumps(example, indent=2)
