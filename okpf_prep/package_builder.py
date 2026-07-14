from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import OKPFRecord
from .profiles import TrainingProfile

OKPF_PREP_VERSION = "0.1.0"

# Default license used when a profile does not declare output.license.
# These are personal/internal prep packages by default, not public releases.
_DEFAULT_LICENSE: dict[str, str] = {
    "type": "proprietary",
    "details": (
        "No license declared by the source profile. Not cleared for "
        "redistribution; prepared for internal training-data use only."
    ),
}

# Directories/suffixes excluded when zipping an output directory into a .kpack
# archive, mirroring the OKPF reference CLI's `okpf pack` exclusions.
_KPACK_EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
_KPACK_EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


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

    records_path = _write_records(output_dir, records, profile)
    manifest_path = _write_manifest(output_dir, profile, records, source_path)
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
    created_at = datetime.now(timezone.utc).isoformat()
    package_id = f"local.okpf-prep.{profile.id}.{uuid4().hex[:12]}"

    manifest: dict[str, Any] = {
        "$schema": "https://okpf.org/schema/v0.1.0/manifest.schema.json",
        "okpf_version": profile.output.okpf_version,
        "package_id": package_id,
        "name": f"{profile.name}: {source_path.stem}",
        "version": profile.output.version,
        "domain": profile.domain,
        "license": profile.output.license or dict(_DEFAULT_LICENSE),
        "created": created_at,
        "records": [
            {
                "path": "records.json",
                "format": "json",
                "record_count": len(records),
            }
        ],
        "sources": [
            {
                "path": f"sources/{source_path.name}",
                "format": (source_path.suffix.lstrip(".").lower() or "txt"),
            }
        ],
        # Additional fields, not part of OKPF Core, kept for Lumina/okpf_prep
        # bookkeeping. additionalProperties is true at the manifest root, so
        # these do not affect schema conformance.
        "package_type": profile.output.package_type,
        "created_at": created_at,
        "profile_id": profile.id,
        "profile_name": profile.name,
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


def _write_records(
    output_dir: Path, records: list[OKPFRecord], profile: TrainingProfile
) -> Path:
    for index, record in enumerate(records):
        if not record.id:
            record.id = f"{profile.id}-{index:04d}"
        if not record.domain:
            record.domain = profile.domain

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


def build_kpack_archive(output_dir: Path, dest_path: Path) -> Path:
    """Zip an okpf_prep output directory into a `.kpack` archive per SPEC.md's
    packaging-mode rules: a ZIP file using safe relative paths, no absolute
    paths, and no parent-directory traversal.

    ``output_dir`` must already contain a ``manifest.json`` (i.e. it must be
    the result of `build_output_package`). Returns ``dest_path``.
    """
    output_dir = Path(output_dir)
    dest_path = Path(dest_path)

    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"No manifest.json found in {output_dir}")

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(dest_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(output_dir.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(output_dir)
            parts = rel.parts
            if any(part in _KPACK_EXCLUDE_DIRS for part in parts):
                continue
            if file_path.suffix in _KPACK_EXCLUDE_SUFFIXES:
                continue

            entry_name = "/".join(parts)
            if not _is_safe_archive_entry(entry_name):
                raise ValueError(f"Unsafe path would be included in .kpack: {entry_name!r}")

            zf.write(file_path, entry_name)

    return dest_path


def _is_safe_archive_entry(entry_name: str) -> bool:
    """Reject absolute paths, parent traversal, and other unsafe archive entries."""
    if not entry_name or entry_name.startswith("/"):
        return False
    if "\\" in entry_name or ":" in entry_name or "\x00" in entry_name:
        return False
    parts = entry_name.split("/")
    return ".." not in parts and "" not in parts
