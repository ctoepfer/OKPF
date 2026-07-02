# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""AI/RAG export contract: `okpf export-rag` and `okpf export-citations`.

Produces `okpf.rag_export.v0.1` rows — see docs/rag-export.md for the
field-by-field contract. This module runs against packs presumed already
valid (`okpf validate` is the place for error reporting); parsing here is
best-effort and silently skips malformed entries rather than raising.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from okpf_validate import DirectoryReader, PackageReader, ValidationResult, ZipReader, _is_safe_path

SCHEMA_VERSION = "okpf.rag_export.v0.1"


class ExportError(Exception):
    """Raised when a pack can't be opened or has no usable manifest."""


def _open_pack(pack_path: str) -> tuple[dict[str, Any], PackageReader]:
    path = Path(pack_path)
    if path.is_dir():
        reader: PackageReader = DirectoryReader(path)
    elif path.is_file() and path.suffix == ".kpack":
        reader = ZipReader(path, ValidationResult(str(pack_path)))
    else:
        raise ExportError(f"Expected a package directory or .kpack ZIP file: {pack_path}")

    if not reader.exists("manifest.json"):
        reader.close()
        raise ExportError(f"manifest.json not found in {pack_path!r}")
    try:
        manifest = json.loads(reader.read_text("manifest.json"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        reader.close()
        raise ExportError(f"Could not read manifest.json: {exc}") from exc
    if not isinstance(manifest, dict):
        reader.close()
        raise ExportError("manifest.json must be an object")
    return manifest, reader


def build_rag_rows(pack_path: str) -> list[dict[str, Any]]:
    """Build okpf.rag_export.v0.1 rows for a pack (directory or .kpack).

    Chunking rule: if the pack declares any `records`, one row per record
    (records are the authored RAG-ready form). Otherwise, one row per
    text-ish artifact, using the whole file as a single chunk. See
    docs/rag-export.md.
    """
    manifest, reader = _open_pack(pack_path)
    try:
        package_id = str(manifest.get("package_id") or manifest.get("id") or "")
        package_version = str(manifest.get("version") or "")
        domain = str(manifest.get("domain") or "")
        license_obj = manifest.get("license") if isinstance(manifest.get("license"), dict) else {}
        usage_policy = manifest.get("usage_policy") if isinstance(manifest.get("usage_policy"), dict) else {}

        resolved_provenance = _resolve_provenance_object(reader, manifest)
        source_entries = _extract_source_entries(resolved_provenance)

        rows: list[dict[str, Any]] = []
        records_entries = manifest.get("records")
        if isinstance(records_entries, list) and records_entries:
            for entry in records_entries:
                rows.extend(
                    _rows_from_record_file(
                        reader, entry, package_id, package_version, domain,
                        manifest, license_obj, usage_policy, source_entries, resolved_provenance,
                    )
                )
        else:
            for entry in _artifact_entries(manifest):
                row = _row_from_artifact(
                    reader, entry, package_id, package_version, domain,
                    manifest, license_obj, usage_policy, source_entries, resolved_provenance,
                )
                if row is not None:
                    rows.append(row)
        return rows
    finally:
        reader.close()


def build_citation_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Same rows as build_rag_rows, with `text` removed for lighter citation metadata."""
    return [{key: value for key, value in row.items() if key != "text"} for row in rows]


def _artifact_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = manifest.get("artifacts")
    if not isinstance(entries, list):
        entries = manifest.get("content")
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _rows_from_record_file(
    reader: PackageReader,
    entry: Any,
    package_id: str,
    package_version: str,
    domain: str,
    manifest: dict[str, Any],
    license_obj: dict[str, Any],
    usage_policy: dict[str, Any],
    source_entries: list[dict[str, Any]] | None,
    resolved_provenance: Any,
) -> list[dict[str, Any]]:
    if not isinstance(entry, dict):
        return []
    path = entry.get("path")
    if not isinstance(path, str) or not _is_safe_path(path) or not reader.exists(path):
        return []
    record_format = str(entry.get("format", "")).lower()

    rows: list[dict[str, Any]] = []
    for record in _iter_records_in_file(reader, path, record_format):
        text = record.get("text")
        if not isinstance(text, str) or not text:
            continue
        record_id = record.get("id")
        rows.append(
            _build_row(
                package_id=package_id, package_version=package_version, domain=domain,
                file_path=path, artifact_role=None, record_id=str(record_id) if record_id else None,
                text=text, title=record.get("title"), manifest=manifest,
                license_obj=license_obj, usage_policy=usage_policy,
                source_entries=source_entries, resolved_provenance=resolved_provenance,
            )
        )
    return rows


def _row_from_artifact(
    reader: PackageReader,
    entry: dict[str, Any],
    package_id: str,
    package_version: str,
    domain: str,
    manifest: dict[str, Any],
    license_obj: dict[str, Any],
    usage_policy: dict[str, Any],
    source_entries: list[dict[str, Any]] | None,
    resolved_provenance: Any,
) -> dict[str, Any] | None:
    path = entry.get("path")
    if not isinstance(path, str) or not _is_safe_path(path) or not reader.exists(path):
        return None

    mime_type = str(entry.get("type") or "")
    is_text = mime_type in {"text/markdown", "text/plain"} or path.endswith((".md", ".txt", ".rst"))
    if not is_text:
        return None

    try:
        text = reader.read_text(path)
    except UnicodeDecodeError:
        return None
    if not text.strip():
        return None

    return _build_row(
        package_id=package_id, package_version=package_version, domain=domain,
        file_path=path, artifact_role=entry.get("role"), record_id=None,
        text=text, title=entry.get("title"), manifest=manifest,
        license_obj=license_obj, usage_policy=usage_policy,
        source_entries=source_entries, resolved_provenance=resolved_provenance,
    )


def _build_row(
    *,
    package_id: str,
    package_version: str,
    domain: str,
    file_path: str,
    artifact_role: Any,
    record_id: str | None,
    text: str,
    title: Any,
    manifest: dict[str, Any],
    license_obj: dict[str, Any],
    usage_policy: dict[str, Any],
    source_entries: list[dict[str, Any]] | None,
    resolved_provenance: Any,
) -> dict[str, Any]:
    chunk_id = f"{package_id}:{file_path}:{record_id}" if record_id else f"{package_id}:{file_path}"

    match = None
    if source_entries:
        match = next((e for e in source_entries if e.get("path") == file_path), None)

    if match is not None:
        provenance_value: Any = match
        source_path = match.get("path")
    elif resolved_provenance:
        provenance_value = resolved_provenance
        source_path = None
    else:
        provenance_value = {}
        source_path = None

    return {
        "schema_version": SCHEMA_VERSION,
        "chunk_id": chunk_id,
        "text": text,
        "package_id": package_id,
        "package_version": package_version,
        "domain": domain,
        "artifact_path": file_path,
        "artifact_role": artifact_role if isinstance(artifact_role, str) else None,
        "record_id": record_id,
        "source_path": source_path if isinstance(source_path, str) else None,
        "license": license_obj,
        "usage_policy": usage_policy,
        "provenance": provenance_value,
        "citation": _build_citation(manifest, title, license_obj),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def _build_citation(manifest: dict[str, Any], title: Any, license_obj: dict[str, Any]) -> str:
    name = manifest.get("name") or manifest.get("title") or manifest.get("package_id") or manifest.get("id") or "Untitled pack"
    version = manifest.get("version")

    parts = [f"{name} v{version}" if version else str(name)]
    if title:
        parts.append(str(title))

    creators = manifest.get("creators")
    if isinstance(creators, list):
        names = [c.get("name") for c in creators if isinstance(c, dict) and c.get("name")]
        if names:
            parts.append(", ".join(names))

    citation = ". ".join(parts)
    license_type = license_obj.get("type") if isinstance(license_obj, dict) else None
    citation += f". Licensed under {license_type}." if license_type else "."
    return citation


def _resolve_provenance_object(reader: PackageReader, manifest: dict[str, Any]) -> Any:
    """Best-effort resolution of manifest['provenance']. See docs/rag-export.md
    for why this doesn't attempt full provenance-graph resolution."""
    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        return {}

    ref = provenance.get("$ref")
    if isinstance(ref, str) and _is_safe_path(ref) and reader.exists(ref):
        try:
            return json.loads(reader.read_text(ref))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return provenance

    sources_path = provenance.get("sources")
    if isinstance(sources_path, str) and _is_safe_path(sources_path) and reader.exists(sources_path):
        try:
            return {"sources": json.loads(reader.read_text(sources_path))}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return provenance

    return provenance


def _extract_source_entries(resolved: Any) -> list[dict[str, Any]] | None:
    candidates = resolved if isinstance(resolved, list) else (
        resolved.get("sources") if isinstance(resolved, dict) else None
    )
    if isinstance(candidates, list) and all(isinstance(e, dict) and "path" in e for e in candidates):
        return candidates
    return None


def _iter_records_in_file(reader: PackageReader, path: str, record_format: str):
    if record_format == "jsonl" or path.endswith(".jsonl"):
        try:
            text = reader.read_text(path)
        except UnicodeDecodeError:
            return
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record
        return

    try:
        data = json.loads(reader.read_text(path))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("records"), list):
        records = data["records"]
    elif isinstance(data, dict):
        records = [data]
    else:
        return

    for record in records:
        if isinstance(record, dict):
            yield record
