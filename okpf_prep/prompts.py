from __future__ import annotations

import json

from .models import TextChunk
from .profiles import TrainingProfile


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
