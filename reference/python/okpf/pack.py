# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
Pack — primary entry point for loading and interacting with OKPF knowledge packs.

Supports directory packs. ZIP (.kpack) archive support is planned.

    from okpf import Pack

    pack = Pack.load("examples/brewing/")
    print(pack.manifest.title)
    print(pack.capabilities)
    for ev in pack.evaluations:
        print(ev.question)
"""

from __future__ import annotations

import os
from pathlib import Path

from .manifest import ContentArtifact, EvaluationCase, Manifest
from .validate import ValidationResult, validate


class ArtifactContent:
    """Content read from a pack artifact."""

    def __init__(self, artifact: ContentArtifact, raw: bytes):
        self.artifact = artifact
        self._raw = raw

    @property
    def text(self) -> str:
        """Decoded text content. Raises UnicodeDecodeError for binary artifacts."""
        return self._raw.decode("utf-8")

    @property
    def bytes(self) -> bytes:
        return self._raw

    def __repr__(self) -> str:
        return (
            f"ArtifactContent(id={self.artifact.id!r}, "
            f"type={self.artifact.type!r}, size={len(self._raw)})"
        )


class Pack:
    """
    An OKPF knowledge pack loaded from a directory or archive.

    Usage:

        pack = Pack.load("examples/brewing/")

        # Manifest metadata
        print(pack.manifest.title)       # "Water Chemistry for Brewing"
        print(pack.manifest.domain)      # "brewing"
        print(pack.manifest.version)     # "0.1.0"

        # AI interoperability hints
        print(pack.capabilities)         # ["retrieval", "evaluation", ...]
        print(pack.manifest.ai.risk_level)

        # Content
        guide = pack.read("guide")
        print(guide.text)

        # Evaluations
        for ev in pack.evaluations:
            print(ev.question)

        # Validation
        result = pack.validate()
        print(result.valid)
    """

    def __init__(self, path: str, manifest: Manifest):
        self._path = str(Path(path).resolve())
        self._manifest = manifest

    @classmethod
    def load(cls, path: str) -> Pack:
        """
        Load a knowledge pack from a directory path.

        Reads manifest.json and resolves $ref pointers to sibling files.
        ZIP archive (.kpack) support is planned — see ROADMAP.md.

        Raises:
            FileNotFoundError: if the path or manifest.json does not exist.
            json.JSONDecodeError: if manifest.json or a referenced file is invalid JSON.
        """
        resolved = str(Path(path).resolve())

        if not os.path.isdir(resolved):
            raise FileNotFoundError(f"Pack path not found or not a directory: {path!r}")

        manifest_path = os.path.join(resolved, "manifest.json")
        if not os.path.isfile(manifest_path):
            raise FileNotFoundError(f"manifest.json not found in {path!r}")

        manifest = Manifest.from_file(manifest_path)
        return cls(path=resolved, manifest=manifest)

    @property
    def path(self) -> str:
        """Absolute path to the pack directory."""
        return self._path

    @property
    def manifest(self) -> Manifest:
        """The parsed manifest for this pack."""
        return self._manifest

    @property
    def capabilities(self) -> list[str]:
        """
        Declared capabilities of this pack.

        Examples: ["retrieval", "evaluation", "workflow-execution"]
        Use for capability negotiation before loading content.
        """
        return self._manifest.capabilities

    @property
    def evaluations(self) -> list[EvaluationCase]:
        """
        Evaluation test cases declared in this pack.

        Returns an empty list if no evaluations are present.
        Evaluations are sourced from the manifest's evaluations field
        (resolved from evaluations/$ref if necessary).
        """
        raw = self._manifest.evaluations
        if raw is None:
            return []
        if isinstance(raw, dict):
            cases = raw.get("evaluations", [])
        elif isinstance(raw, list):
            cases = raw
        else:
            return []
        return [EvaluationCase.from_dict(e) for e in cases]

    @property
    def content(self) -> list[ContentArtifact]:
        """All content artifacts declared in the manifest."""
        return self._manifest.content

    def get_artifact(self, artifact_id: str) -> ContentArtifact:
        """
        Look up a content artifact by its ID.

        Raises:
            KeyError: if no artifact with the given ID exists in this pack.
        """
        for artifact in self._manifest.content:
            if artifact.id == artifact_id:
                return artifact
        raise KeyError(f"No artifact with id {artifact_id!r} in pack {self._manifest.id!r}")

    def read(self, artifact_id: str) -> ArtifactContent:
        """
        Read the content of an artifact by ID.

        Returns an ArtifactContent object. For text artifacts, use .text.
        For binary artifacts (images, etc.), use .bytes.

        Raises:
            KeyError: if artifact_id does not exist.
            FileNotFoundError: if the artifact file is missing from the pack.
        """
        artifact = self.get_artifact(artifact_id)
        artifact_path = os.path.join(self._path, artifact.path)

        if not os.path.isfile(artifact_path):
            raise FileNotFoundError(
                f"Artifact file not found: {artifact.path!r} in pack {self._manifest.id!r}"
            )

        with open(artifact_path, "rb") as f:
            raw = f.read()

        return ArtifactContent(artifact=artifact, raw=raw)

    def read_by_role(self, role: str) -> list[ArtifactContent]:
        """
        Read all artifacts with a specific semantic role.

        Common roles: "guide", "transcript", "workflow", "evaluation", "data", "image".
        """
        return [
            self.read(artifact.id)
            for artifact in self._manifest.content
            if artifact.role == role
        ]

    def get_workflow(self, artifact_id: str) -> dict:
        """
        Load a workflow artifact as a parsed JSON dict.

        The workflow conforms to task.schema.json. Use for workflow execution.

        Raises:
            KeyError: if artifact_id does not exist.
            ValueError: if the artifact is not application/json.
        """
        import json as _json

        artifact = self.get_artifact(artifact_id)
        if artifact.type != "application/json":
            raise ValueError(
                f"Artifact {artifact_id!r} has type {artifact.type!r}, expected application/json"
            )
        content = self.read(artifact_id)
        return _json.loads(content.bytes)

    def validate(self) -> ValidationResult:
        """
        Validate this pack against the OKPF specification.

        Returns a ValidationResult with any errors or warnings found.
        Does not raise on validation failure — check result.valid instead.
        """
        return validate(self._path)

    def __repr__(self) -> str:
        return (
            f"Pack(id={self._manifest.id!r}, "
            f"version={self._manifest.version!r}, "
            f"domain={self._manifest.domain!r})"
        )
