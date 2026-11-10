# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Validated startup catalog; no filesystem access after construction."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from okpf.institutional import PROFILE, SCHEMA_ROOT
from okpf_validate import ValidationResult, _validate_with_reader

from .snapshot import MountError, Snapshot, parse_data, snapshot

MAX_MOUNTS = 16
MAX_CATALOG_BYTES = 128 * 1024 * 1024


def case_schema() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(
            (SCHEMA_ROOT / "profiles/institutional/v1/case_record.json").read_text(encoding="utf-8")
        ),
    )


@dataclass(frozen=True)
class Case:
    pack_ref: str
    package_id: str
    version: str
    path: str
    data: dict[str, Any]
    artifact_metadata: list[dict[str, Any]]

    def located(self, pointer: str, data: Any) -> dict[str, Any]:
        return {
            "pack_ref": self.pack_ref,
            "package_id": self.package_id,
            "version": self.version,
            "case_id": self.data["id"],
            "artifact_path": self.path,
            "pointer": pointer,
            "data": data,
            "evidence_sources": self.data.get("evidence_sources", []),
            "context": {
                k: v
                for k, v in self.data.items()
                if k
                not in {
                    "topology",
                    "stressor",
                    "intervention",
                    "outcomes",
                    "telemetry",
                    "evasion_vectors",
                    "pre_mortem_falsification",
                    "evidence_sources",
                }
            },
            "artifact_metadata": self.artifact_metadata,
        }


@dataclass
class Mount:
    summary: dict[str, Any]
    cases: list[Case]
    unsupported: list[dict[str, Any]]
    size: int


def verify_hashes(manifest: dict[str, Any], reader: Snapshot) -> int:
    integrity = manifest.get("integrity") or {}
    if any(k in integrity for k in ("manifest_sha256", "content_sha256")):
        raise MountError(
            "Aggregate manifest/content hashes have no supported verification convention"
        )
    entries = list(integrity.get("artifacts") or [])
    for key in ("artifacts", "content", "records", "sources"):
        entries += manifest.get(key, [])
    checked = 0
    for entry in entries:
        if "sha256" not in entry:
            continue
        digest = entry["sha256"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise MountError("Invalid artifact SHA-256")
        if hashlib.sha256(reader.read_bytes(entry["path"])).hexdigest() != digest.lower():
            raise MountError(f"SHA-256 mismatch: {entry['path']!r}")
        checked += 1
    return checked


def load_mount(path: Path) -> Mount:
    reader = snapshot(path)
    if not reader.exists("manifest.json"):
        raise MountError("Missing manifest.json")
    manifest = parse_data(reader.read_text("manifest.json"))
    if not isinstance(manifest, dict):
        raise MountError("Manifest must be an object")
    profiles = manifest.get("profiles", [])
    if not isinstance(profiles, list):
        raise MountError("profiles must be an array")
    declared = list(profiles)
    if "profile" in manifest and manifest["profile"] not in declared:
        declared.append(manifest["profile"])
    institutional = PROFILE in declared
    # Preflight files consumed by reference validation to bound structured parsing.
    protected = {
        entry.get("path")
        for key in ("artifacts", "content", "records", "sources")
        for entry in manifest.get(key, [])
        if isinstance(entry, dict) and entry.get("disclosure") == "encrypted"
    }
    parsed: dict[str, Any] = {}
    for name in reader.iter_paths():
        if name in protected:
            continue
        suffix = Path(name).suffix.lower()
        if suffix == ".json":
            parsed[name] = parse_data(reader.read_text(name))
        elif suffix == ".jsonl":
            for line in reader.read_text(name).splitlines():
                if line.strip():
                    parse_data(line)
        elif institutional and name.startswith("cases/") and suffix in {".yaml", ".yml"}:
            parsed[name] = parse_data(reader.read_text(name), yaml_data=True)
    result = ValidationResult(str(path))
    _validate_with_reader(reader, result, False, PROFILE if institutional else None)
    if not result.valid:
        raise MountError("; ".join(str(issue) for issue in result.errors[:5]))
    checked = verify_hashes(manifest, reader)
    identity = str(manifest.get("package_id", manifest.get("id")))
    # Stable across process restarts for the same explicit absolute mount path.
    ref = "pack-" + hashlib.sha256(str(path).encode()).hexdigest()[:24]
    artifact_entries = [
        entry
        for key in ("artifacts", "content", "records", "sources")
        for entry in manifest.get(key, [])
    ]
    cases: list[Case] = []
    unsupported = []
    if institutional:
        for name, data in sorted(parsed.items()):
            if not name.startswith("cases/"):
                continue
            entries = [entry for entry in artifact_entries if entry["path"] == name]
            reason = None
            if data.get("case_layout") not in (None, "review-v1"):
                reason = "Unsupported explicit case_layout"
            if any(entry.get("disclosure") == "encrypted" for entry in entries):
                reason = "Encrypted artifact is not exposed"
            if reason:
                unsupported.append({"case_id": data["id"], "artifact_path": name, "reason": reason})
            else:
                cases.append(Case(ref, identity, manifest["version"], name, data, entries))
    signatures = any(k in manifest for k in ("signature", "signatures"))
    integrity = manifest.get("integrity") or {}
    signatures |= any(k in integrity for k in ("signature", "signatures"))
    signatures |= any(n.endswith((".sig", ".asc")) for n in reader.files)
    # Trust/extensions may describe unknown signing systems; do not call them verified.
    state = (
        "unsupported"
        if signatures
        else ("not_checked" if manifest.get("trust") or manifest.get("extensions") else "absent")
    )
    summary = {
        "pack_ref": ref,
        "package_id": identity,
        "identity_fields": {k: manifest[k] for k in ("package_id", "id") if k in manifest},
        "name": manifest.get("name"),
        "version": manifest["version"],
        "profiles": declared,
        "institutional_profile": manifest.get("institutional_profile"),
        "validation": {
            "core": "valid",
            "institutional": "valid" if institutional else "not_applicable",
        },
        "integrity": {
            "status": "verified" if checked else "absent",
            "hash_entries_checked": checked,
            "scope": "Declared artifact SHA-256 only; unhashed files are not authenticated",
        },
        "signature": {
            "status": state,
            "signer_trust": "not_checked",
            "scope": "No cryptographic verifier; external detached files are not read",
        },
        "case_count": len(cases),
        "unsupported_cases": unsupported,
        "metadata": {
            k: v
            for k, v in manifest.items()
            if k
            not in {
                "package_id",
                "id",
                "name",
                "version",
                "profiles",
                "profile",
                "institutional_profile",
                "artifacts",
                "content",
                "records",
                "sources",
            }
        },
        "artifact_metadata": artifact_entries,
        "warnings": [str(w) for w in result.warnings]
        + (
            []
            if institutional
            else [
                "Catalog only: no supported institutional profile declared; Core records are not cases."
            ]
        ),
    }
    return Mount(summary, cases, unsupported, reader.size)


class Catalog:
    def __init__(self, paths: list[str]) -> None:
        self.mounts: list[Mount] = []
        self.errors: list[str] = []
        self.cases: list[Case] = []
        seen: set[Path] = set()
        total = 0
        if len(paths) > MAX_MOUNTS:
            raise MountError(f"At most {MAX_MOUNTS} configured mounts are supported")
        for source in paths:
            try:
                path = Path(source).resolve(strict=True)
                if path in seen:
                    continue
                seen.add(path)
                mount = load_mount(path)
                if total + mount.size > MAX_CATALOG_BYTES:
                    raise MountError("Catalog exceeds total byte limit")
                total += mount.size
                self.mounts.append(mount)
                self.cases.extend(mount.cases)
            except Exception as exc:  # noqa: BLE001 -- isolate malformed mounts at the trust boundary
                # Malformed untrusted inputs must not suppress other valid mounts.
                self.errors.append(f"{source!r}: {type(exc).__name__}: {str(exc)[:500]}")
        self.mounts.sort(
            key=lambda m: (m.summary["package_id"], m.summary["version"], m.summary["pack_ref"])
        )
        self.cases.sort(key=lambda c: (c.package_id, c.version, c.pack_ref, c.data["id"], c.path))
