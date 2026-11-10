# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Experimental checks of a declarative commitment against a separately retained baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from okpf.institutional import SCHEMA_ROOT

from .snapshot import MAX_FILE, MountError, parse_data


def read_document(path: Path) -> Any:
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE + 1)
    if len(raw) > MAX_FILE:
        raise MountError("Document exceeds 2 MiB limit")
    return parse_data(raw.decode("utf-8"), yaml_data=path.suffix.lower() in {".yaml", ".yml"})


def commitment_errors(value: Any) -> list[str]:
    schema = json.loads(
        (
            SCHEMA_ROOT / "extensions/semantic-invariants/draft-v0.1/commitment.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = [
        f"/{'/'.join(map(str, e.absolute_path))}: {e.message}"
        for e in Draft202012Validator(schema).iter_errors(value)
    ]
    if errors:
        return errors
    ids: set[str] = set()
    for binding in value["taxonomy_bindings"]:
        concept = binding["concept_id"]
        if concept in ids:
            errors.append(f"Duplicate concept_id: {concept}")
        ids.add(concept)
        actual = hashlib.sha256(binding["definition"].encode("utf-8")).hexdigest()
        if actual != binding["definition_sha256"]:
            errors.append(f"Definition digest mismatch: {concept}")
    for concept in value["operational_test"]["concept_ids"]:
        if concept not in ids:
            errors.append(f"Unbound operational concept: {concept}")
    return errors


def changes(before: Any, after: Any, pointer: str = "") -> list[str]:
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            path = pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in before or key not in after:
                result.append(path)
            else:
                result.extend(changes(before[key], after[key], path))
        return result
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return [
            p
            for i, (a, b) in enumerate(zip(before, after, strict=True))
            for p in changes(a, b, f"{pointer}/{i}")
        ]
    return [] if type(before) is type(after) and before == after else [pointer]


def check_semantics(document: Path, baseline: Path | None = None) -> dict[str, Any]:
    value = read_document(document)
    errors = commitment_errors(value)
    changed: list[str] = []
    baseline_digest = None
    if baseline is not None:
        original = read_document(baseline)
        errors += ["baseline: " + e for e in commitment_errors(original)]
        changed = changes(original, value)
        # This is only a receipt over the locally supplied baseline, not a signature.
        baseline_digest = hashlib.sha256(
            json.dumps(original, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
        ).hexdigest()
    return {
        "experimental": True,
        "valid": not errors and not changed,
        "errors": errors,
        "changed_pointers": changed,
        "baseline_checked": baseline is not None,
        "baseline_receipt_sha256": baseline_digest,
        "warnings": [
            (
                "Definition hashes detect byte changes only. Baseline authenticity and "
                "approval are not verified. Replacing both documents defeats comparison. "
                "No baseline means self-consistency only; semantic drift can exist even "
                "when bytes are unchanged. No operational test or fallback is executed."
            )
        ],
    }
