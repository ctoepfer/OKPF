# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
Manifest dataclass and loader for OKPF knowledge packs.

Parses manifest.json into structured Python objects. Resolves $ref pointers
to sibling files (license.json, contributors.json, provenance.json).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentArtifact:
    id: str
    path: str
    type: str
    title: str | None = None
    description: str | None = None
    sha256: str | None = None
    role: str | None = None
    language: str | None = None
    _raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> ContentArtifact:
        return cls(
            id=data["id"],
            path=data["path"],
            type=data["type"],
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
    type: str
    question: str
    difficulty: str | None = None
    expected_answer: Any = None
    choices: list[dict] | None = None
    source_artifacts: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    explanation: str | None = None
    _raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> EvaluationCase:
        return cls(
            id=data["id"],
            type=data["type"],
            question=data["question"],
            difficulty=data.get("difficulty"),
            expected_answer=data.get("expected_answer"),
            choices=data.get("choices"),
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
    id: str
    name: str
    version: str
    domain: str
    created: str
    content: list[ContentArtifact]

    description: str | None = None
    tags: list[str] = field(default_factory=list)
    language: str | None = None
    updated: str | None = None

    capabilities: list[str] = field(default_factory=list)
    ai: AiMetadata = field(default_factory=AiMetadata)
    trust: TrustMetadata = field(default_factory=TrustMetadata)

    # Raw resolved dicts for license, contributors, provenance
    license: dict = field(default_factory=dict)
    contributors: dict | list | None = None
    provenance: dict | None = None
    evaluations: dict | list | None = None

    _raw: dict = field(default_factory=dict, repr=False)

    @property
    def title(self) -> str:
        """Alias for name — convenience for AI system consumption."""
        return self.name

    @classmethod
    def from_dict(cls, data: dict, base_path: str | None = None) -> Manifest:
        """
        Parse a manifest dict into a Manifest instance.

        If base_path is provided, $ref values in license, contributors,
        provenance, and evaluations are resolved by loading sibling files.
        """
        content = [ContentArtifact.from_dict(a) for a in data.get("content", [])]

        def resolve_ref(value: Any) -> Any:
            if isinstance(value, dict) and "$ref" in value and base_path:
                ref_path = os.path.join(base_path, value["$ref"])
                with open(ref_path) as f:
                    return json.load(f)
            return value

        return cls(
            okpf_version=data["okpf_version"],
            id=data["id"],
            name=data["name"],
            version=data["version"],
            domain=data["domain"],
            created=data["created"],
            content=content,
            description=data.get("description"),
            tags=data.get("tags", []),
            language=data.get("language"),
            updated=data.get("updated"),
            capabilities=data.get("capabilities", []),
            ai=AiMetadata.from_dict(data["ai"]) if "ai" in data else AiMetadata(),
            trust=TrustMetadata.from_dict(data["trust"]) if "trust" in data else TrustMetadata(),
            license=resolve_ref(data.get("license", {})),
            contributors=resolve_ref(data.get("contributors")),
            provenance=resolve_ref(data.get("provenance")),
            evaluations=resolve_ref(data.get("evaluations")),
            _raw=data,
        )

    @classmethod
    def from_file(cls, path: str) -> Manifest:
        """Load a manifest.json from a file path, resolving $refs relative to its directory."""
        base_path = os.path.dirname(os.path.abspath(path))
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data, base_path=base_path)
