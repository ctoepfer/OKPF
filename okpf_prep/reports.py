from __future__ import annotations

from typing import Any

from .models import ValidationResult


def build_conversion_report(
    source_filename: str,
    profile_id: str,
    backend_name: str,
    model_name: str | None,
    chunks_processed: int,
    records_generated: int,
    validation_result: ValidationResult,
    warnings: list[str],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "source_filename": source_filename,
        "profile_id": profile_id,
        "backend_name": backend_name,
        "model_name": model_name,
        "chunks_processed": chunks_processed,
        "records_generated": records_generated,
        "validation_status": "pass" if validation_result.valid else "fail",
        "validation_errors": validation_result.errors,
        "validation_warnings": validation_result.warnings,
        "warnings": warnings,
        "errors": errors,
    }
