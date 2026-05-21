<!-- SPDX-License-Identifier: Apache-2.0 -->

# CLAUDE.md

Guidance for Claude and other AI assistants working in this repository.

## Project Identity

OKPF is the Open Knowledge Pack Format: an open, model-neutral, vendor-neutral, infrastructure-neutral file format for packaging structured human expertise.

Treat OKPF as a file format specification and reference implementation. Do not describe it as a platform, marketplace, SaaS product, AI model, training pipeline, vector database format, blockchain protocol, or brewing standard.

Core priorities, in order:

1. Specification stability
2. Schema correctness
3. Provenance and attribution
4. License clarity
5. Security
6. Portability
7. Long-lived interoperability

## Authoritative Sources

Consult these before changing spec, schema, validation, examples, or docs:

1. `SPEC.md` - canonical v0.1.0 specification
2. `schemas/v0.1.0/manifest.schema.json` - authoritative manifest schema
3. `schemas/record.schema.json` - authoritative record schema
4. Existing passing tests and examples

Useful supporting docs:

- `AI_DISCOVERY.md`
- `docs/manifest.md`
- `docs/package-structure.md`
- `docs/security.md`
- `docs/ai-integration.md`
- `docs/profiles.md`
- `docs/records.md`
- `CONTRIBUTING.md`

## Development Style

- Use concise, normative technical prose in docs.
- Use RFC keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) only when intentionally normative.
- Python is `>=3.11`; do not add Python 3.10 compatibility workarounds.
- Prefer small focused modules, dataclasses for in-memory models, typed signatures, `pathlib.Path`, and stdlib JSON.
- JSON Schema is Draft 2020-12.
- Keep core schema objects extensible with `additionalProperties: true` unless the spec explicitly says otherwise.
- Preserve unknown optional fields when reading or rewriting manifests.

Add SPDX headers to new source files:

- Python/shell: `# SPDX-License-Identifier: Apache-2.0` and `# Copyright 2026 OKPF Contributors`
- TypeScript/JavaScript: `// SPDX-License-Identifier: Apache-2.0` and `// Copyright 2026 OKPF Contributors`
- JSON: `"$comment": "SPDX-License-Identifier: Apache-2.0 | Copyright 2026 OKPF Contributors"`
- Markdown: `<!-- SPDX-License-Identifier: Apache-2.0 -->` where appropriate

## Core Compatibility Rules

- OKPF Core v0.1.0 accepts `okpf_version` values `"0.1"` and `"0.1.0"`.
- New packs should prefer `package_id`, but existing `id` aliases are schema-valid and must be preserved.
- A valid core pack needs `manifest.json` plus at least one of `artifacts`, `records`, or `content`; none of those is individually mandatory.
- `license` is legal permission. `usage_policy` is machine-readable operational intent. Do not collapse them or imply that usage policy overrides license terms.
- `expert_notes` are human-authored rationale and review context, not LLM chain-of-thought or private reasoning.
- Unknown profiles, artifact roles, optional fields, and facet keys must not invalidate an otherwise core-valid pack.
- New required fields in v0.1.x are breaking in spirit and require prior discussion.
- Domain conventions belong in profiles, extensions, artifact conventions, or examples, not in OKPF Core.

## Security Rules

Core validation is offline-capable. Do not fetch remote schemas, registries, models, URLs, package references, or dependencies during core validation unless the user explicitly asks for networked behavior.

Reject unsafe pack paths before reading archive entries or artifacts:

- Absolute paths
- Parent traversal
- Backslash traversal
- Windows drive paths
- NUL bytes

Do not auto-execute content from packs. Packs are data, not executable trust boundaries.

Do not hardcode credentials, API keys, private URLs, model secrets, or local absolute user paths into schemas, examples, tests, or docs.

## Common Traps

- OKPF is general-purpose knowledge packaging. BeerXML, brewing, recipes, BJCP, and fermentation are examples, profiles, or artifacts only.
- `okpf-prep` and `reference/python/okpf_validate.py` are separate tools.
- `jsonschema` is a dev dependency. The standalone validator and tests require `pip install -e ".[dev]"`.
- The schema `$id` URLs are aspirational. Resolve schemas locally.
- Core validation checks structure, integrity, and policy metadata. It does not prove factual accuracy.
- Facets are open in OKPF Core. Profiles may define controlled vocabularies.
- Embeddings, signatures, blockchain anchors, registries, JSON-LD, workflow runtimes, AI providers, and dependency resolution are optional layers, never required for core validity.

## Key Paths

- `okpf_prep/` - prep package and `okpf-prep` CLI
- `reference/python/okpf_validate.py` - standalone reference validator
- `reference/python/okpf/` - Python reference package CLI and helpers
- `reference/javascript/src/` - JavaScript/TypeScript reference stubs
- `schemas/` - core JSON Schemas
- `profiles/fermentation/v0.1.0/` - fermentation profile
- `examples/` - example packs and source material
- `tests/` - pytest suite

Generated or local-only paths such as `out/`, `__pycache__/`, `.pytest_cache/`, `.venv/`, and `*.egg-info` are not source.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Docs/schema-only work usually requires no build step.

## Test Commands

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

Use the reference package CLI without install:

```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/hello-world
PYTHONPATH=reference/python python3 -m okpf validate examples/fermentation-mixed-bundle --profile fermentation
PYTHONPATH=reference/python python3 -m okpf inspect examples/hello-world
```

Validate JSON syntax:

```bash
python -m json.tool schemas/v0.1.0/manifest.schema.json
python -m json.tool schemas/record.schema.json
python -m json.tool examples/hello-world/manifest.json
```

## Prep CLI Examples

```bash
okpf-prep validate-profile profiles/general_knowledge.yaml
okpf-prep extract-text examples/brewing_notes.md
okpf-prep prepare \
  --source examples/brewing_notes.md \
  --profile profiles/general_knowledge.yaml \
  --out out/brewing_notes \
  --backend mock
```

Ollama is optional and local-only:

```bash
okpf-prep prepare \
  --source examples/brewing_notes.md \
  --profile profiles/general_knowledge.yaml \
  --out out/brewing_notes \
  --backend ollama \
  --model llama3 \
  --ollama-url http://localhost:11434
```

## Change Discipline

Before schema or spec changes:

1. Read `SPEC.md` and `schemas/v0.1.0/manifest.schema.json`.
2. Check `docs/manifest.md` and `docs/package-structure.md`.
3. Search examples for the field or concept.
4. Classify the change as Core, profile, extension, artifact convention, or documentation.
5. Preserve compatibility aliases such as `id` and `content`.
6. Add or update tests and example manifests when behavior changes.

When consuming or generating OKPF packs:

1. Start at root `manifest.json`.
2. Validate against local schemas.
3. Resolve local `$ref` values.
4. Reject unsafe paths before reading archive contents.
5. Verify SHA-256 hashes when declared.
6. Check `license` and `usage_policy` before RAG, training, redistribution, or evaluation use.
7. Treat `capabilities`, `ai`, and `trust` as optional advisory metadata.
8. Preserve provenance, package/version, artifact path/hash, license, and attribution in derived records or chunks.
9. Preserve unknown optional fields.
