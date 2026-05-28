<!-- SPDX-License-Identifier: Apache-2.0 -->

# Module Index

This repository is modular at the directory/package level. This index documents current ownership boundaries and integration points.

## `schemas/`
Owns:
- JSON Schema contracts for OKPF Core and related objects.
- Compatibility surface for manifest/record validation.

Does not own:
- Runtime execution logic.
- Domain profile policy details beyond schema representation.

Key interfaces/contracts:
- `schemas/v0.1.0/manifest.schema.json`
- `schemas/record.schema.json`
- Additional schema artifacts (`license`, `provenance`, `evaluation`, etc.)

Dependencies/boundaries:
- Consumed by `reference/python/okpf_validate.py` and docs.
- Must remain aligned with `SPEC.md`.

## `reference/python/`
Owns:
- Python reference validator and reference CLI behavior.
- Pack inspection/validation/packaging baseline implementation.

Does not own:
- Authoritative spec semantics (owned by `SPEC.md` + `schemas/`).
- Training-pack preparation pipeline (`okpf_prep/`).

Key interfaces/contracts:
- Standalone validator: `reference/python/okpf_validate.py`
- CLI entry via module: `python3 -m okpf ...` from `reference/python/okpf/cli.py`
- Commands: `validate`, `inspect`/`info`, `pack`, `unpack`, `compare-layout`

Dependencies/boundaries:
- Depends on local schemas and local filesystem/ZIP packs.
- Expected to remain offline-capable for core validation.

## `okpf_prep/`
Owns:
- Source extraction and preparation pipeline for OKPF-compatible outputs.
- `okpf-prep` CLI command behavior.
- Optional AI backend integration for extraction/record generation workflows.

Does not own:
- Canonical Core validation rules for general pack conformance.
- Registry/discovery/distribution infrastructure.

Key interfaces/contracts:
- CLI in `okpf_prep/cli.py`: `prepare`, `validate-profile`, `extract-text`
- Package entry point from `pyproject.toml`: `okpf-prep = "okpf_prep.cli:main"`
- Internal integration points: `runner.py`, `extractors.py`, `package_builder.py`, `profiles.py`, `validation.py`, `ai/base.py`

Dependencies/boundaries:
- Python runtime dependencies declared in `pyproject.toml`.
- Optional Ollama backend (`ai/ollama.py`) and default `mock` backend.

## `profiles/`
Owns:
- Optional domain-specific profile conventions and constraints.
- Profile documentation and schema/rules outside Core.

Does not own:
- Core manifest required fields or Core schema semantics.

Key interfaces/contracts:
- Profile directories and profile docs, for example:
  - `profiles/fermentation/v0.1.0/`
  - `profiles/physical-skill-evidence/v0.1.0/`
  - `profiles/human-correction-loop/v0.1.0/`

Dependencies/boundaries:
- Referenced by examples and optional profile-aware validation modes.
- Unknown profiles must not invalidate otherwise core-valid packs.

## `examples/`
Owns:
- Demonstration packs and fixtures for documentation and testing.
- Practical examples of native/envelope/hybrid packaging patterns.

Does not own:
- Normative core requirements.
- Tooling logic.

Key interfaces/contracts:
- Example pack directories consumed by validators and docs.
- Validation smoke-test targets (for example `examples/hello-world`).

Dependencies/boundaries:
- Must remain consistent with current schema/spec expectations.
- Used as compatibility evidence, not as normative source.

## `tests/`
Owns:
- Regression and behavior checks for reference tooling and prep pipeline.

Does not own:
- Product/runtime code paths.
- Specification authority.

Key interfaces/contracts:
- Pytest suites covering validator, CLI, profiles, pack building, extraction, chunking, and runner behavior.

Dependencies/boundaries:
- Depends on local repo files/examples and Python dev dependencies.

## `docs/`
Owns:
- Human-readable guidance, conformance narrative, security notes, profile authoring, architecture concepts.

Does not own:
- Executable behavior.
- Canonical schema enforcement.

Key interfaces/contracts:
- Conformance and architecture guidance, for example `docs/v0.1-conformance.md`, `docs/manifest.md`, `docs/package-structure.md`, `docs/security.md`.

Dependencies/boundaries:
- Should stay synchronized with implemented behavior in `reference/python/` and `okpf_prep/`.
- Planned/future sections should be explicitly labeled to avoid status ambiguity.

## `reference/javascript/`
Owns:
- JavaScript/TypeScript reference implementation track.

Does not own:
- Current canonical validation behavior parity (still partial/stub).

Key interfaces/contracts:
- Current source stubs in `reference/javascript/src/`.
- WIP status documented in `reference/javascript/README.md`.

Dependencies/boundaries:
- Should align with core schemas and reference CLI semantics as implementation matures.
