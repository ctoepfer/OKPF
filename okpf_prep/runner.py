from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from .ai.base import BaseAIBackend
from .ai.mock import MockAIBackend
from .ai.ollama import OllamaBackend
from .chunking import chunk_text
from .extractors import extract_text
from .models import OKPFRecord, PrepResult
from .package_builder import build_output_package
from .profiles import TrainingProfile, load_profile, validate_profile
from .prompts import build_system_prompt, build_user_prompt
from .reports import build_conversion_report
from .validation import validate_records, validate_records_json

log = logging.getLogger(__name__)


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

    def run(self, source: str | Path, output_dir: str | Path) -> PrepResult:
        source_path = Path(source)
        out_dir = Path(output_dir)
        warnings: list[str] = []
        errors: list[str] = []

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

        # Extract text
        extracted = extract_text(source_path)
        warnings.extend(extracted.warnings)

        all_records: list[OKPFRecord] = []
        chunks_processed = 0

        if extracted.source_type == "beerxml":
            # BeerXML: generate deterministic records directly, skip chunking/AI
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
            chunks = chunk_text(
                extracted.text,
                max_chars=self.profile.chunking.max_chars,
                overlap_chars=self.profile.chunking.overlap_chars,
                source_filename=extracted.source_filename,
                strategy=self.profile.chunking.strategy,
            )
            chunks_processed = len(chunks)

            # Build prompts and call AI backend
            system_prompt = build_system_prompt(self.profile)

            for chunk in chunks:
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
                    continue

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
                all_records.extend(chunk_records)

        # Final validation pass
        final_validation = validate_records(all_records, self.profile)
        if not final_validation.valid:
            errors.extend(final_validation.errors)

        # Build report
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
) -> PrepResult:
    """Convenience function: load profile, create runner, run preparation.

    ollama_timeout is in seconds and only applies to the "ollama" backend;
    ignored otherwise. Falls back to OllamaBackend's own default when None.
    """
    profile = load_profile(profile_path)
    ai_backend = _make_backend(backend, model, ollama_url, profile, timeout=ollama_timeout)
    runner = PrepRunner(profile, ai_backend)
    return runner.run(source_path, output_dir)
