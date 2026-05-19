from __future__ import annotations

import json
from typing import Any

from .models import OKPFRecord, ValidationResult
from .profiles import TrainingProfile


def validate_records_json(
    raw_json: str,
    profile: TrainingProfile,
) -> tuple[list[OKPFRecord], ValidationResult]:
    """Parse and validate a JSON string of OKPF records against a profile."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return [], ValidationResult(valid=False, errors=[f"Invalid JSON: {exc}"])

    if not isinstance(data, dict) or "records" not in data:
        return [], ValidationResult(
            valid=False,
            errors=["Response must be a JSON object with a 'records' key."],
        )

    raw_records = data["records"]
    if not isinstance(raw_records, list):
        return [], ValidationResult(
            valid=False, errors=["'records' must be a JSON array."]
        )

    records: list[OKPFRecord] = []
    for i, rec in enumerate(raw_records):
        rec_errors = _validate_single_record(rec, i, profile)
        if rec_errors:
            errors.extend(rec_errors)
        else:
            records.append(_parse_record(rec))

    return records, ValidationResult(
        valid=len(errors) == 0, errors=errors, warnings=warnings
    )


def validate_records(
    records: list[OKPFRecord],
    profile: TrainingProfile,
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    for i, rec in enumerate(records):
        errors.extend(_validate_single_record(rec.to_dict(), i, profile))

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def _validate_single_record(
    rec: Any, index: int, profile: TrainingProfile
) -> list[str]:
    errors: list[str] = []
    label = f"Record[{index}]"

    if not isinstance(rec, dict):
        return [f"{label}: must be a JSON object."]

    rec_type = rec.get("type", "")
    if not rec_type:
        errors.append(f"{label}: missing 'type'.")
    elif profile.validation.record_type_policy == "strict":
        if rec_type not in profile.allowed_record_types:
            errors.append(
                f"{label}: type '{rec_type}' is not in allowed_record_types "
                f"{profile.allowed_record_types}."
            )

    if not rec.get("title"):
        errors.append(f"{label}: missing 'title'.")

    has_content = bool(rec.get("content")) or bool(rec.get("summary"))
    if not has_content:
        errors.append(f"{label}: must have at least one of 'content' or 'summary'.")

    if profile.conversion.require_source_refs:
        refs = rec.get("source_refs", [])
        if not refs:
            errors.append(f"{label}: 'source_refs' required by profile but not present.")

    if profile.conversion.confidence_required:
        conf = rec.get("confidence")
        if conf is None:
            errors.append(f"{label}: 'confidence' required by profile but not present.")
        elif not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
            errors.append(f"{label}: 'confidence' must be a number between 0 and 1.")

    return errors


def _parse_record(rec: dict[str, Any]) -> OKPFRecord:
    return OKPFRecord(
        type=rec["type"],
        title=rec["title"],
        summary=rec.get("summary"),
        content=rec.get("content"),
        source_refs=rec.get("source_refs", []),
        confidence=rec.get("confidence"),
        metadata=rec.get("metadata"),
    )
