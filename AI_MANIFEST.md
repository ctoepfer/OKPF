<!-- SPDX-License-Identifier: Apache-2.0 -->

# AI Manifest

## Project Purpose
OKPF (Open Knowledge Pack Format) is an open, model-neutral, vendor-neutral, infrastructure-neutral file format for packaging structured human expertise.

Problem addressed:
- Knowledge is often moved as loose files without durable provenance, attribution, licensing, integrity metadata, or machine-readable usage intent.
- OKPF provides a stable pack structure centered on `manifest.json` so tools and teams can validate and exchange knowledge packs without requiring a specific platform.

This repository contains both specification material and reference tooling.

## Architecture Snapshot
Core components:
- `SPEC.md`: canonical Core v0.1.0 specification.
- `schemas/`: JSON Schema definitions (Draft 2020-12), including `schemas/v0.1.0/manifest.schema.json` and `schemas/record.schema.json`.
- `reference/python/okpf_validate.py`: standalone reference validator.
- `reference/python/okpf/`: reference CLI and helpers (`validate`, `inspect`, `pack`, `unpack`, `compare-layout`).
- `okpf_prep/`: `okpf-prep` package/CLI for source extraction and training-pack preparation.
- `profiles/`: optional domain profiles (for example fermentation, physical-skill-evidence, human-correction-loop).
- `examples/`: example packs for conformance, docs, and implementation checks.
- `tests/`: pytest suite for validators, CLI behavior, prep pipeline, extractors, chunking, profiles, and package building.

Runtime and storage choices:
- Python `>=3.11`.
- Local file-system packs (directory-based packs and `.kpack` ZIP archives).
- No required database or service runtime for core validation.
- Optional Ollama backend for `okpf-prep`; default backend is deterministic `mock`.

## Boundaries And Ownership
Core boundary rules:
- Core format/spec ownership: `SPEC.md` + `schemas/`.
- Reference implementation ownership: `reference/python/` and `reference/javascript/`.
- Prep/conversion workflow ownership: `okpf_prep/`.
- Domain-specific conventions ownership: `profiles/` and profile docs, not OKPF Core.
- Demonstration content ownership: `examples/`.

What Core does not own:
- Hosted registries, marketplaces, training pipelines, vector databases, blockchain requirements, or runtime execution semantics.
- Domain-specific controlled vocabularies in Core.

Behavioral boundaries to preserve:
- Unknown optional fields are tolerated and preserved.
- `license` (legal permission) and `usage_policy` (operational intent) are distinct concepts.
- Core validation is local/offline-capable; do not require remote schema fetches.
- Packs are data, not executable trust boundaries.

## Common Development Commands
Environment setup:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
pytest tests/test_okpf_validate.py
pytest tests/test_cli.py
pytest tests/test_package_builder.py
pytest tests/test_profiles.py
pytest tests/test_validation.py
```

Validate example packs:
```bash
python3 reference/python/okpf_validate.py examples/hello-world
python3 reference/python/okpf_validate.py examples/fermentation-mixed-bundle --profile fermentation
python3 reference/python/okpf_validate.py examples/fermentation-mixed-bundle --strict-profile
```

Reference CLI from source checkout:
```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/hello-world
PYTHONPATH=reference/python python3 -m okpf inspect examples/hello-world
PYTHONPATH=reference/python python3 -m okpf pack examples/hello-world out/hello-world.kpack
PYTHONPATH=reference/python python3 -m okpf unpack out/hello-world.kpack out/hello-world-unpacked
```

Prep CLI:
```bash
okpf-prep validate-profile profiles/general_knowledge.yaml
okpf-prep extract-text examples/brewing_notes.md
okpf-prep prepare --source examples/brewing_notes.md --profile profiles/general_knowledge.yaml --out out/brewing_notes --backend mock
```

Formatting/lint/build/migrations/local server:
- No canonical repo-wide formatter or linter command is currently defined in `pyproject.toml`.
- No DB migrations are defined.
- No always-on local service startup is required for core development.
- JSON syntax checks can be done ad hoc with `python -m json.tool <file>`.

## AI Guardrails
When modifying this repository:
- Treat OKPF as a file format specification and reference implementation.
- Prioritize: spec stability, schema correctness, provenance/attribution, license clarity, security, portability.
- Prefer additive, compatibility-preserving changes.
- Keep profile/domain logic out of Core unless intentionally standardizing Core behavior.
- Preserve unknown optional manifest fields during read/rewrite operations.
- Reject unsafe paths (absolute paths, traversal, backslash traversal, drive paths, NUL bytes) before archive extraction.
- Do not claim content truth or safety from schema validity.
- Do not introduce network dependencies for core validation unless explicitly requested.

Anti-patterns:
- Presenting planned/stub capabilities as implemented.
- Blurring profile rules into Core requirements.
- Conflating legal license terms with usage policy hints.
- Adding required fields in v0.1.x without explicit compatibility discussion.
