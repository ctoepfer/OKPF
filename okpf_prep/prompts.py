from __future__ import annotations

import json

from .models import TextChunk
from .profiles import TrainingProfile

# Bounds how many records a single call is asked to produce. Applies to
# both table and prose chunks — live verification originally used a
# higher ceiling (10) for table chunks on the theory that flattened rows
# are smaller/more self-contained than prose records, but a real 893-char
# table batch asking for "at most 10" records still got cut off by
# DEFAULT_NUM_PREDICT (each record's title/summary/content/source_refs/
# confidence costs more tokens than 10-fits-in-1024 assumed). 5 is the
# value actually proven to complete reliably (a real prose chunk with
# this cap finished in 143s of a 300s budget, no truncation) — kept as
# one shared constant rather than two now that evidence doesn't support
# treating them differently.
MAX_RECORDS_PER_CHUNK = 5


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
            f"Extract at most {MAX_RECORDS_PER_CHUNK} distinct entries you "
            "can identify with reasonable confidence from this excerpt. "
            "Do not try to force every fragment into a record, and do not "
            "pad the response with uncertain or duplicate entries — a "
            "shorter, accurate response is better than an exhaustive one. "
            "Keep each entry's content brief (a short phrase or sentence, "
            "not a restatement of the whole row).",
        ]
    else:
        lines += [
            "",
            f"Extract at most {MAX_RECORDS_PER_CHUNK} distinct records "
            "from this chunk — the most clearly-supported, useful points, "
            "not an exhaustive restatement of everything in the text. Keep "
            "each record's content concise rather than reproducing long "
            "passages verbatim.",
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
