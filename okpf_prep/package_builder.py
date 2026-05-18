from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import OKPFRecord
from .profiles import TrainingProfile

OKPF_PREP_VERSION = "0.1.0"


def build_output_package(
    output_dir: Path,
    profile: TrainingProfile,
    records: list[OKPFRecord],
    source_path: Path,
    extracted_text: str,
    report: dict[str, Any],
) -> dict[str, Path]:
    """Write the OKPF output package to disk. Returns a dict of named file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sources").mkdir(exist_ok=True)
    (output_dir / "reports").mkdir(exist_ok=True)

    manifest_path = _write_manifest(output_dir, profile, records, source_path)
    records_path = _write_records(output_dir, records)
    extracted_text_path = _write_sources(output_dir, source_path, extracted_text)
    report_path = _write_report(output_dir, report)

    return {
        "manifest": manifest_path,
        "records": records_path,
        "extracted_text": extracted_text_path,
        "report": report_path,
    }


def _write_manifest(
    output_dir: Path,
    profile: TrainingProfile,
    records: list[OKPFRecord],
    source_path: Path,
) -> Path:
    manifest: dict[str, Any] = {
        "okpf_version": profile.output.okpf_version,
        "package_type": profile.output.package_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile_id": profile.id,
        "profile_name": profile.name,
        "domain": profile.domain,
        "target_brains": profile.target_brains,
        "source_files": [source_path.name],
        "record_count": len(records),
        "generator": {
            "tool": "okpf_prep",
            "version": OKPF_PREP_VERSION,
        },
    }
    path = output_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def _write_records(output_dir: Path, records: list[OKPFRecord]) -> Path:
    payload = {"records": [r.to_dict() for r in records]}
    path = output_dir / "records.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_sources(
    output_dir: Path, source_path: Path, extracted_text: str
) -> Path:
    sources_dir = output_dir / "sources"

    # Copy original source file
    dest_original = sources_dir / source_path.name
    if source_path.exists() and not dest_original.exists():
        shutil.copy2(source_path, dest_original)

    # Write extracted text as markdown
    extracted_path = sources_dir / "extracted_text.md"
    extracted_path.write_text(extracted_text, encoding="utf-8")
    return extracted_path


def _write_report(output_dir: Path, report: dict[str, Any]) -> Path:
    path = output_dir / "reports" / "conversion_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
