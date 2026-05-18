from __future__ import annotations

import hashlib
import json
from typing import Any

from .base import BaseAIBackend


class MockAIBackend(BaseAIBackend):
    """Deterministic mock backend for tests — no AI model required."""

    name = "mock"

    def __init__(self, record_type: str = "knowledge") -> None:
        self.record_type = record_type

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        schema: dict[str, Any] | None = None,
        temperature: float = 0.1,
        model: str | None = None,
    ) -> str:
        # Derive a stable short fingerprint from the prompt so tests are reproducible
        fingerprint = hashlib.md5(prompt.encode()).hexdigest()[:8]

        # Extract chunk_id from prompt if present (line like "Chunk ID: chunk-0001")
        chunk_id = "chunk-0000"
        for line in prompt.splitlines():
            if line.startswith("Chunk ID:"):
                chunk_id = line.split(":", 1)[1].strip()
                break

        # Extract source_file from prompt if present
        source_file = "source.md"
        for line in prompt.splitlines():
            if line.startswith("Source file:"):
                source_file = line.split(":", 1)[1].strip()
                break

        record: dict[str, Any] = {
            "type": self.record_type,
            "title": f"Mock record [{fingerprint}]",
            "summary": f"Deterministic mock summary for chunk {chunk_id}.",
            "content": f"Mock content derived from input prompt hash {fingerprint}.",
            "source_refs": [{"source_file": source_file, "chunk_id": chunk_id}],
            "confidence": 0.95,
        }
        return json.dumps({"records": [record]})
