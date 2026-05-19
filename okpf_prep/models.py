from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ExtractedSource:
    source_path: Path
    source_filename: str
    source_type: str
    text: str
    page_count: int | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    start_char: int
    end_char: int
    heading: str | None = None
    source_ref: dict[str, Any] = field(default_factory=dict)


@dataclass
class OKPFRecord:
    type: str
    title: str
    summary: str | None = None
    content: str | None = None
    source_refs: list[dict[str, Any]] = field(default_factory=list)
    confidence: float | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": self.type, "title": self.title}
        if self.summary is not None:
            d["summary"] = self.summary
        if self.content is not None:
            d["content"] = self.content
        if self.source_refs:
            d["source_refs"] = self.source_refs
        if self.confidence is not None:
            d["confidence"] = self.confidence
        if self.metadata is not None:
            d["metadata"] = self.metadata
        return d


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PrepResult:
    output_dir: Path
    manifest_path: Path
    records_path: Path
    extracted_text_path: Path
    report_path: Path
    record_count: int
    validation_status: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
