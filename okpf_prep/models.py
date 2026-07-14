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
    is_table_like: bool = False


@dataclass
class OKPFRecord:
    """A single normalized knowledge unit.

    ``to_dict()`` emits the OKPF v0.1.0 Universal Record shape (see
    ``schemas/record.schema.json``): required fields ``id``, ``record_type``,
    ``title``, ``text``, ``domain``, ``metadata``, plus optional ``facets``.
    ``id`` and ``domain`` are normally filled in by
    ``package_builder._write_records`` (which knows the record's position and
    the profile's domain) rather than by callers constructing this dataclass.
    ``summary``, ``content``, ``source_refs``, and ``confidence`` are kept as
    additional (schema-permitted) fields for backward compatibility with
    existing consumers such as Lumina's training-prep bridge.
    """

    type: str
    title: str
    summary: str | None = None
    content: str | None = None
    source_refs: list[dict[str, Any]] = field(default_factory=list)
    confidence: float | None = None
    metadata: dict[str, Any] | None = None
    id: str = ""
    domain: str = ""
    facets: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "record_type": self.type,
            "title": self.title,
            "text": self.content or self.summary or "",
            "domain": self.domain,
            "metadata": self.metadata or {},
        }
        if self.summary is not None:
            d["summary"] = self.summary
        if self.content is not None:
            d["content"] = self.content
        if self.source_refs:
            d["source_refs"] = self.source_refs
        if self.confidence is not None:
            d["confidence"] = self.confidence
        if self.facets:
            d["facets"] = self.facets
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
