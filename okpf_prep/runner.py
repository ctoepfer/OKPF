from __future__ import annotations

import html
import logging
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable

ProgressCallback = Callable[[dict[str, Any]], None]

from .ai.base import BaseAIBackend
from .ai.mock import MockAIBackend
from .ai.ollama import OllamaBackend
from .chunking import chunk_text
from .extractors import extract_text
from .models import OKPFRecord, PrepResult, TextChunk
from .package_builder import build_output_package
from .profiles import TrainingProfile, load_profile, validate_profile
from .prompts import build_system_prompt, build_user_prompt
from .reports import build_conversion_report
from .validation import validate_records, validate_records_json

log = logging.getLogger(__name__)


class PrepCancelledError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.warnings = warnings or []
        self.errors = errors or []
        self.validation_status = "cancelled"


_PROMOTIONAL_PATTERNS = re.compile(
    r"\b(shop|shopping|buy now|click here|view chart|continue your education|"
    r"learn more|subscribe|newsletter|cart|checkout|order now|promo|promotion)\b",
    re.IGNORECASE,
)
_EQUIPMENT_NOTE_PATTERN = re.compile(r"\bequipment\b", re.IGNORECASE)


def _normalize_support_text(text: str) -> str:
    text = html.unescape(unicodedata.normalize("NFKC", text))
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"[^\w\s.-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", _normalize_support_text(text)))


def _support_tokens(text: str) -> set[str]:
    tokens = set()
    for token in _normalize_support_text(text).split():
        if len(token) >= 3:
            tokens.add(token)
    return tokens


def _record_source_text(record: OKPFRecord) -> str:
    metadata = record.metadata or {}
    okpf = metadata.get("okpf") if isinstance(metadata.get("okpf"), dict) else {}
    pieces: list[str] = []
    for value in (
        record.title,
        record.summary or "",
        record.content or "",
        okpf.get("source_row_text", ""),
    ):
        if value:
            pieces.append(str(value))
    return "\n".join(pieces)


def _ground_record(record: OKPFRecord, source_text: str) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []

    content_text = (record.content or record.summary or "").strip()
    if not content_text:
        errors.append(f"{record.title or record.type}: empty or near-empty content.")
        return warnings, errors

    if len(content_text) < 12:
        warnings.append(f"{record.title or record.type}: fragmentary content.")

    if _PROMOTIONAL_PATTERNS.search(content_text):
        errors.append(f"{record.title or record.type}: promotional/navigation text is not allowed.")

    if record.type == "equipment_note" and not _EQUIPMENT_NOTE_PATTERN.search(source_text):
        errors.append(f"{record.title or record.type}: equipment_note requires equipment knowledge in the source.")

    if source_text:
        source_numbers = _extract_numbers(source_text)
        content_numbers = _extract_numbers(content_text)
        unsupported_numbers = sorted(n for n in content_numbers if n not in source_numbers)
        if unsupported_numbers:
            errors.append(
                f"{record.title or record.type}: unsupported numerical claim(s): {', '.join(unsupported_numbers)}."
            )

        source_tokens = _support_tokens(source_text)
        content_tokens = _support_tokens(content_text)
        overlap = content_tokens & source_tokens
        if not overlap and content_tokens:
            errors.append(f"{record.title or record.type}: no meaningful lexical support in the source.")
        elif content_tokens:
            support_ratio = len(overlap) / max(len(content_tokens), 1)
            if support_ratio < 0.35:
                warnings.append(f"{record.title or record.type}: weak grounding in the source.")

    return warnings, errors


def _table_row_to_record(
    chunk: TextChunk,
    row: dict[str, Any],
    profile: TrainingProfile,
) -> OKPFRecord:
    columns = row.get("columns") if isinstance(row.get("columns"), list) else []
    normalized_columns: list[dict[str, Any]] = []
    for column in columns:
        if not isinstance(column, dict):
            continue
        normalized_columns.append(
            {
                "name": str(column.get("name") or ""),
                "value": column.get("value"),
                "links": list(column.get("links") or []),
            }
        )

    row_index = int(row.get("row_index") or 0)
    source_values = [str(col["value"]) for col in normalized_columns if col.get("value") not in (None, "")]
    first_value = source_values[0] if source_values else f"row {row_index}"
    title = first_value[:120]
    resolved_type = profile.resolve_record_type("reference_entry")
    row_text = " | ".join(
        f"{col['name']}: {col['value']}" if col.get("value") not in (None, "") else f"{col['name']}:"
        for col in normalized_columns
    )
    row_text = row_text.strip(" |")

    source_ref = dict(chunk.source_ref or {})
    source_ref.update(
        {
            "row_index": row_index,
            "table_headers": chunk.table_headers,
            "table_caption": chunk.table_caption,
            "source_row_text": row_text,
            "source_row_values": source_values,
            "row_links": [link for col in normalized_columns for link in col.get("links", [])],
        }
    )

    metadata = {
        "okpf": {
            "source_file": source_ref.get("source_file"),
            "chunk_id": source_ref.get("chunk_id"),
            "source_section": chunk.heading,
            "table_index": source_ref.get("table_index"),
            "table_caption": chunk.table_caption,
            "table_headers": chunk.table_headers,
            "row_index": row_index,
            "row_range": source_ref.get("row_range"),
            "source_row_text": row_text,
            "source_row_values": source_values,
            "row_links": source_ref.get("row_links", []),
            "raw_row": row,
        }
    }

    return OKPFRecord(
        type=resolved_type,
        title=title or f"Table row {row_index}",
        summary=row_text or title,
        content=row_text or title,
        source_refs=[source_ref],
        confidence=1.0,
        metadata=metadata,
    )


def _attach_grounding(record: OKPFRecord, source_text: str) -> OKPFRecord:
    warnings, errors = _ground_record(record, source_text)
    record.warnings.extend(warnings)
    record.errors.extend(errors)
    return record


def _make_backend(
    backend: str,
    model: str | None,
    ollama_url: str,
    profile: TrainingProfile | None = None,
    timeout: float | None = None,
) -> BaseAIBackend:
    if backend == "mock":
        record_type = (
            profile.allowed_record_types[0]
            if profile and profile.allowed_record_types
            else "knowledge"
        )
        return MockAIBackend(record_type=record_type)
    if backend == "ollama":
        kwargs: dict[str, Any] = {"base_url": ollama_url, "default_model": model or "llama3.1:8b"}
        if timeout is not None:
            kwargs["timeout"] = timeout
        return OllamaBackend(**kwargs)
    raise ValueError(f"Unknown backend '{backend}'. Supported: mock, ollama")


class PrepRunner:
    def __init__(self, profile: TrainingProfile, ai_backend: BaseAIBackend) -> None:
        self.profile = profile
        self.ai_backend = ai_backend

    def run(
        self,
        source: str | Path,
        output_dir: str | Path,
        source_url: str | None = None,
        source_content_type: str | None = None,
        progress_callback: ProgressCallback | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> PrepResult:
        source_path = Path(source)
        out_dir = Path(output_dir)
        warnings: list[str] = []
        errors: list[str] = []

        def _cancelled(stage: str) -> None:
            if cancel_check is None:
                return
            try:
                cancelled = bool(cancel_check())
            except Exception:
                cancelled = False
            if cancelled:
                raise PrepCancelledError(
                    f"Cancellation requested while {stage}. The current chunk may need to finish before the worker stops.",
                    warnings=list(warnings),
                    errors=list(errors),
                )

        def _report(event: dict[str, Any]) -> None:
            if progress_callback is None:
                _cancelled("processing progress")
                return
            try:
                progress_callback(event)
            except Exception:
                # Progress reporting is best-effort observability, never
                # allowed to interrupt the actual conversion.
                log.warning("progress_callback raised", exc_info=True)
            _cancelled("processing progress")

        # Validate profile
        profile_result = validate_profile(self.profile)
        if not profile_result.valid:
            return PrepResult(
                output_dir=out_dir,
                manifest_path=out_dir / "manifest.json",
                records_path=out_dir / "records.json",
                extracted_text_path=out_dir / "sources" / "extracted_text.md",
                report_path=out_dir / "reports" / "conversion_report.json",
                record_count=0,
                validation_status="fail",
                errors=[f"Profile invalid: {e}" for e in profile_result.errors],
            )
        warnings.extend(profile_result.warnings)
        _cancelled("starting extraction")

        # Extract text
        _report({"phase": "extracting"})
        extracted = extract_text(
            source_path,
            source_url=source_url,
            source_content_type=source_content_type,
        )
        warnings.extend(extracted.warnings)
        _cancelled("finishing extraction")

        all_records: list[OKPFRecord] = []
        chunks_processed = 0

        if extracted.source_type == "beerxml":
            # BeerXML: generate deterministic records directly, skip chunking/AI
            _report({"phase": "preparing", "total_chunks": 0})
            from .beerxml import parse_beerxml_file, beerxml_recipe_to_record
            try:
                recipes = parse_beerxml_file(source_path)
                for recipe in recipes:
                    rec_dict = beerxml_recipe_to_record(recipe, extracted.source_filename)
                    all_records.append(OKPFRecord(
                        type=rec_dict["type"],
                        title=rec_dict["title"],
                        summary=rec_dict.get("summary"),
                        content=rec_dict.get("content"),
                        source_refs=rec_dict.get("source_refs", []),
                        confidence=rec_dict.get("confidence"),
                        metadata=rec_dict.get("metadata"),
                    ))
            except Exception as exc:
                errors.append(f"BeerXML record generation error: {exc}")
        else:
            # Chunk
            _report({"phase": "chunking"})
            chunks = _build_chunks_for_extracted_source(extracted, self.profile)
            chunks_processed = len(chunks)
            total_chunks = len(chunks)
            _report({"phase": "preparing", "total_chunks": total_chunks})
            _cancelled("before starting chunk processing")

            seen_record_signatures: set[str] = set()

            # Build prompts and call AI backend
            system_prompt = build_system_prompt(self.profile)

            for chunk_index, chunk in enumerate(chunks):
                _cancelled(f"starting chunk {chunk.chunk_id}")
                _report({
                    "phase": "preparing",
                    "chunk_index": chunk_index,
                    "chunk_id": chunk.chunk_id,
                    "total_chunks": total_chunks,
                })

                if chunk.is_table_like and chunk.table_rows:
                    chunk_records: list[OKPFRecord] = []
                    chunk_warnings: list[str] = []
                    chunk_errors: list[str] = []
                    for row in chunk.table_rows:
                        record = _table_row_to_record(chunk, row, self.profile)
                        source_text = record.metadata["okpf"].get("source_row_text", "")
                        _attach_grounding(record, source_text)
                        chunk_warnings.extend(record.warnings)
                        chunk_errors.extend(record.errors)
                        signature = _normalize_support_text(
                            " | ".join(
                                [record.type, record.title, record.summary or "", record.content or ""]
                            )
                        )
                        if signature in seen_record_signatures:
                            chunk_warnings.append(f"{chunk.chunk_id}: duplicate table record detected for row {record.metadata['okpf'].get('row_index')}")
                        else:
                            seen_record_signatures.add(signature)
                        chunk_records.append(record)

                    if len(chunk_records) != len(chunk.table_rows):
                        chunk_errors.append(
                            f"{chunk.chunk_id}: deterministic table conversion produced {len(chunk_records)} records for {len(chunk.table_rows)} source rows."
                        )

                    warnings.extend(chunk_warnings)
                    errors.extend(chunk_errors)
                    warnings.append(f"{chunk.chunk_id}: deterministic table records generated; optional enrichment skipped.")
                    all_records.extend(chunk_records)
                    _report({
                        "phase": "preparing",
                        "chunk_index": chunk_index,
                        "chunk_id": chunk.chunk_id,
                        "total_chunks": total_chunks,
                        "chunk_status": "success",
                    })
                    continue

                user_prompt = build_user_prompt(self.profile, chunk, extracted.source_filename)
                chunk_started = time.monotonic()
                try:
                    raw_response = self.ai_backend.generate(
                        prompt=user_prompt,
                        system=system_prompt,
                        temperature=0.1,
                    )
                except Exception as exc:
                    log.warning(
                        "chunk generate failed: %s",
                        {
                            "chunk_id": chunk.chunk_id,
                            "backend": self.ai_backend.name,
                            "model": getattr(self.ai_backend, "default_model", None),
                            "error_type": type(exc).__name__,
                            "elapsed_s": round(time.monotonic() - chunk_started, 2),
                            "chunk_chars": len(chunk.text),
                        },
                    )
                    errors.append(f"AI backend error on {chunk.chunk_id}: {exc}")
                    _report({
                        "phase": "preparing",
                        "chunk_index": chunk_index,
                        "chunk_id": chunk.chunk_id,
                        "total_chunks": total_chunks,
                        "chunk_status": "failed",
                    })
                    continue

                _cancelled(f"after completing chunk {chunk.chunk_id}")

                chunk_records, chunk_validation = validate_records_json(
                    raw_response, self.profile
                )
                if not chunk_validation.valid:
                    # A response that doesn't end with a closing brace almost
                    # always means generation was cut off by the output-token
                    # limit (num_predict) rather than the model choosing to
                    # stop — surface that distinction rather than reporting
                    # it identically to a genuinely malformed response.
                    truncation_hint = ""
                    if not raw_response.rstrip().endswith("}"):
                        truncation_hint = (
                            " (response does not end with a closing brace — "
                            "likely truncated by the output token limit; "
                            "consider a smaller/more targeted chunk)"
                        )
                    log.warning(
                        "chunk validation failed: %s",
                        {
                            "chunk_id": chunk.chunk_id,
                            "backend": self.ai_backend.name,
                            "response_chars": len(raw_response),
                            "likely_truncated": bool(truncation_hint),
                            "error_count": len(chunk_validation.errors),
                        },
                    )
                    errors.extend(
                        f"{chunk.chunk_id}: {e}{truncation_hint}" for e in chunk_validation.errors
                    )
                    _report({
                        "phase": "preparing",
                        "chunk_index": chunk_index,
                        "chunk_id": chunk.chunk_id,
                        "total_chunks": total_chunks,
                        "chunk_status": "failed",
                    })
                else:
                    _report({
                        "phase": "preparing",
                        "chunk_index": chunk_index,
                        "chunk_id": chunk.chunk_id,
                        "total_chunks": total_chunks,
                        "chunk_status": "success",
                    })
                for record in chunk_records:
                    source_text = chunk.text
                    _attach_grounding(record, source_text)
                    warnings.extend(record.warnings)
                    errors.extend(record.errors)
                    signature = _normalize_support_text(
                        " | ".join([record.type, record.title, record.summary or "", record.content or ""])
                    )
                    if signature in seen_record_signatures:
                        warnings.append(f"{chunk.chunk_id}: duplicate record detected for {record.title!r}.")
                    else:
                        seen_record_signatures.add(signature)
                all_records.extend(chunk_records)
                _cancelled(f"after recording chunk {chunk.chunk_id}")

        # Final validation pass
        _report({"phase": "validating"})
        _cancelled("before validation")
        final_validation = validate_records(all_records, self.profile)
        if not final_validation.valid:
            errors.extend(final_validation.errors)

        # Build report
        _report({"phase": "writing_pack"})
        _cancelled("before writing the final pack")
        report = build_conversion_report(
            source_filename=extracted.source_filename,
            profile_id=self.profile.id,
            backend_name=self.ai_backend.name,
            model_name=getattr(self.ai_backend, "default_model", None),
            chunks_processed=chunks_processed,
            records_generated=len(all_records),
            validation_result=final_validation,
            warnings=warnings,
            errors=errors,
        )

        # Write output package
        paths = build_output_package(
            output_dir=out_dir,
            profile=self.profile,
            records=all_records,
            source_path=source_path,
            extracted_text=extracted.text,
            report=report,
        )

        validation_status = "pass" if not errors else "fail"

        return PrepResult(
            output_dir=out_dir,
            manifest_path=paths["manifest"],
            records_path=paths["records"],
            extracted_text_path=paths["extracted_text"],
            report_path=paths["report"],
            record_count=len(all_records),
            validation_status=validation_status,
            warnings=warnings,
            errors=errors,
        )


def prepare_training_pack(
    source_path: str | Path,
    profile_path: str | Path,
    output_dir: str | Path,
    backend: str = "mock",
    model: str | None = None,
    ollama_url: str = "http://localhost:11434",
    ollama_timeout: float | None = None,
    source_url: str | None = None,
    source_content_type: str | None = None,
    progress_callback: ProgressCallback | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> PrepResult:
    """Convenience function: load profile, create runner, run preparation.

    ollama_timeout is in seconds and only applies to the "ollama" backend;
    ignored otherwise. Falls back to OllamaBackend's own default when None.

    progress_callback, if given, is invoked with a dict at each phase/chunk
    boundary — see PrepRunner.run() for the event shape. Best-effort: any
    exception it raises is caught and logged, never allowed to interrupt
    the conversion.
    """
    profile = load_profile(profile_path)
    ai_backend = _make_backend(backend, model, ollama_url, profile, timeout=ollama_timeout)
    runner = PrepRunner(profile, ai_backend)
    return runner.run(
        source_path,
        output_dir,
        source_url=source_url,
        source_content_type=source_content_type,
        progress_callback=progress_callback,
        cancel_check=cancel_check,
    )


def _build_chunks_for_extracted_source(extracted, profile: TrainingProfile) -> list[TextChunk]:
    """Build chunks, honoring extractor-provided deterministic blocks.

    For HTML mixed content, extractor prechunked blocks keep native table rows
    bounded deterministically before AI normalization while prose still uses the
    standard chunk_text strategy.
    """
    if not extracted.prechunked_blocks:
        return chunk_text(
            extracted.text,
            max_chars=profile.chunking.max_chars,
            overlap_chars=profile.chunking.overlap_chars,
            source_filename=extracted.source_filename,
            strategy=profile.chunking.strategy,
        )

    chunks: list[TextChunk] = []
    chunk_index = 0
    prose_parts: list[str] = []

    def _flush_prose() -> None:
        nonlocal chunk_index
        if not prose_parts:
            return
        prose_text = "\n\n".join(p for p in prose_parts if p.strip())
        prose_parts.clear()
        if not prose_text.strip():
            return
        prose_chunks = chunk_text(
            prose_text,
            max_chars=profile.chunking.max_chars,
            overlap_chars=profile.chunking.overlap_chars,
            source_filename=extracted.source_filename,
            strategy=profile.chunking.strategy,
        )
        for pc in prose_chunks:
            chunk_id = f"chunk-{chunk_index:04d}"
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=pc.text,
                    start_char=pc.start_char,
                    end_char=pc.end_char,
                    heading=pc.heading,
                    source_ref={
                        "source_file": extracted.source_filename,
                        "chunk_id": chunk_id,
                    },
                    is_table_like=False,
                )
            )
            chunk_index += 1

    for block in extracted.prechunked_blocks:
        if block.is_table_like:
            _flush_prose()
            chunk_id = f"chunk-{chunk_index:04d}"
            src = {
                "source_file": extracted.source_filename,
                "chunk_id": chunk_id,
            }
            src.update(block.source_ref or {})
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=block.text,
                    start_char=0,
                    end_char=len(block.text),
                    heading=block.heading,
                    source_ref=src,
                    is_table_like=True,
                    table_headers=block.table_headers,
                    table_rows=block.table_rows,
                    table_caption=block.table_caption,
                )
            )
            chunk_index += 1
        else:
            prose_parts.append(block.text)

    _flush_prose()
    return chunks
