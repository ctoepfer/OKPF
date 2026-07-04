# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
Manifest dataclass and loader for OKPF knowledge packs.

Parses manifest.json into structured Python objects. Resolves $ref pointers
to sibling files (license.json, contributors.json, provenance.json).

Accepts current v0.1.0 manifests (`package_id`, `artifacts`) as well as
legacy `id`/`content` aliases, matching the same compatibility rule used by
`reference/python/okpf_validate.py`.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentArtifact:
    path: str
    id: str
    type: str | None = None
    format: str | None = None
    title: str | None = None
    description: str | None = None
    sha256: str | None = None
    role: str | None = None
    language: str | None = None
    _raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> ContentArtifact:
        path = data["path"]
        return cls(
            path=path,
            # `id` is optional on artifact/content entries in the current
            # schema (only `path` is required) -- fall back to the path
            # itself so every artifact has a stable, always-present id.
            id=data.get("id") or path,
            type=data.get("type"),
            format=data.get("format"),
            title=data.get("title"),
            description=data.get("description"),
            sha256=data.get("sha256"),
            role=data.get("role"),
            language=data.get("language"),
            _raw=data,
        )


@dataclass
class EvaluationCase:
    id: str
    question: str
    type: str | None = None
    difficulty: str | None = None
    expected_answer: Any = None
    choices: list[dict] | None = None
    record_ids: list[str] = field(default_factory=list)
    source_artifacts: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    explanation: str | None = None
    _raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> EvaluationCase:
        return cls(
            id=data.get("id", ""),
            question=data.get("question", ""),
            type=data.get("type"),
            difficulty=data.get("difficulty"),
            expected_answer=data.get("expected_answer"),
            choices=data.get("choices"),
            record_ids=data.get("record_ids", []),
            source_artifacts=data.get("source_artifacts", []),
            tags=data.get("tags", []),
            explanation=data.get("explanation"),
            _raw=data,
        )


@dataclass
class AiMetadata:
    recommended_use: list[str] = field(default_factory=list)
    safe_for_training: bool | None = None
    contains_pii: bool = False
    modalities: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    risk_level: str | None = None
    evaluation_available: bool | None = None
    workflow_capable: bool | None = None

    @classmethod
    def from_dict(cls, data: dict) -> AiMetadata:
        return cls(
            recommended_use=data.get("recommended_use", []),
            safe_for_training=data.get("safe_for_training"),
            contains_pii=data.get("contains_pii", False),
            modalities=data.get("modalities", []),
            domains=data.get("domains", []),
            risk_level=data.get("risk_level"),
            evaluation_available=data.get("evaluation_available"),
            workflow_capable=data.get("workflow_capable"),
        )


@dataclass
class TrustMetadata:
    signed: bool = False
    verified_contributors: bool = False
    provenance_complete: bool | None = None
    attestations: list[dict] = field(default_factory=list)
    verification_method: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> TrustMetadata:
        return cls(
            signed=data.get("signed", False),
            verified_contributors=data.get("verified_contributors", False),
            provenance_complete=data.get("provenance_complete"),
            attestations=data.get("attestations", []),
            verification_method=data.get("verification_method"),
        )


@dataclass
class Manifest:
    okpf_version: str
    package_id: str
    name: str
    version: str
    domain: str
    content: list[ContentArtifact]

    id: str | None = None  # legacy alias, preserved as-declared if present
    title: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    language: str | None = None
    created: str | None = None
    updated: str | None = None
    profiles: list[str] = field(default_factory=list)

    capabilities: list[str] = field(default_factory=list)
    ai: AiMetadata = field(default_factory=AiMetadata)
    trust: TrustMetadata = field(default_factory=TrustMetadata)

    # Raw resolved dicts for license, usage_policy, contributors, provenance
    license: dict = field(default_factory=dict)
    usage_policy: dict = field(default_factory=dict)
    contributors: dict | list | None = None
    provenance: dict | None = None
    evaluations: dict | list | None = None

    _raw: dict = field(default_factory=dict, repr=False)

    @property
    def display_name(self) -> str:
        """The manifest's `title` if declared, else `name`."""
        return self.title or self.name

    @classmethod
    def from_dict(
        cls,
        data: dict,
        base_path: str | None = None,
        read_ref_text: Any = None,
    ) -> Manifest:
        """
        Parse a manifest dict into a Manifest instance.

        Reads `artifacts` (falling back to legacy `content`) and
        `package_id` (falling back to legacy `id`) -- the same aliasing
        rule as `reference/python/okpf_validate.py`.

        $ref values in license, contributors, provenance, and evaluations
        are resolved by loading sibling files, either from a directory
        (`base_path`) or via `read_ref_text(relative_path) -> str` for
        non-directory sources such as a `.kpack` archive. At most one of
        `base_path`/`read_ref_text` should be given.
        """
        artifacts_data = data.get("artifacts")
        if not isinstance(artifacts_data, list):
            artifacts_data = data.get("content", [])
        content = [ContentArtifact.from_dict(a) for a in artifacts_data if isinstance(a, dict)]

        package_id = data.get("package_id") or data.get("id")
        if not package_id:
            raise KeyError("manifest.json must declare 'package_id' (or legacy 'id')")

        def resolve_ref(value: Any) -> Any:
            if not (isinstance(value, dict) and "$ref" in value):
                return value
            if read_ref_text is not None:
                return json.loads(read_ref_text(value["$ref"]))
            if base_path:
                ref_path = os.path.join(base_path, value["$ref"])
                with open(ref_path, encoding="utf-8") as f:
                    return json.load(f)
            return value

        evaluations = data.get("evaluations")
        if evaluations is None:
            evaluations = data.get("evals")  # common repo convention, see docs/five-minutes.md

        return cls(
            okpf_version=data["okpf_version"],
            package_id=package_id,
            name=data["name"],
            version=data["version"],
            domain=data["domain"],
            content=content,
            id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            tags=data.get("tags", []),
            language=data.get("language"),
            created=data.get("created"),
            updated=data.get("updated"),
            profiles=data.get("profiles", []),
            capabilities=data.get("capabilities", []),
            ai=AiMetadata.from_dict(data["ai"]) if isinstance(data.get("ai"), dict) else AiMetadata(),
            trust=TrustMetadata.from_dict(data["trust"]) if isinstance(data.get("trust"), dict) else TrustMetadata(),
            license=resolve_ref(data.get("license", {})) or {},
            usage_policy=data.get("usage_policy", {}) or {},
            contributors=resolve_ref(data.get("contributors")),
            provenance=resolve_ref(data.get("provenance")),
            evaluations=resolve_ref(evaluations),
            _raw=data,
        )

    @classmethod
    def from_file(cls, path: str) -> Manifest:
        """Load a manifest.json from a file path, resolving $refs relative to its directory."""
        base_path = os.path.dirname(os.path.abspath(path))
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, base_path=base_path)

    @classmethod
    def from_reader(cls, reader: Any) -> Manifest:
        """Load manifest.json via a PackageReader (directory or .kpack), resolving $refs through the same reader."""
        data = json.loads(reader.read_text("manifest.json"))
        return cls.from_dict(data, read_ref_text=reader.read_text)
