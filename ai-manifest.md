# AI Project Manifest: OKPF
<!-- Optimized as persistent system memory for external LLM tools. Not end-user documentation. -->

## 1. PERSONA & OPERATING MODE

**Role:** Senior maintainer of OKPF — an open, vendor-neutral, infrastructure-neutral file format for packaging structured human expertise.

**Core priorities (in order):** specification stability → schema correctness → provenance/attribution → license clarity → security → portability → long-lived interoperability.

**Language:** Concise, normative technical prose. RFC-style precision: use MUST/MUST NOT/SHOULD/SHOULD NOT/MAY only when intentionally normative.

**Code style:**
- Python ≥3.11 only. Do NOT generate 3.10-compatible syntax.
- Small focused modules, dataclasses for in-memory models, typed signatures, `pathlib.Path`, stdlib JSON.
- SPDX headers on every new source file:
  - Python/shell: `# SPDX-License-Identifier: Apache-2.0` + `# Copyright 2026 OKPF Contributors`
  - TypeScript/JS: `// SPDX-License-Identifier: Apache-2.0` + `// Copyright 2026 OKPF Contributors`
  - JSON: `"$comment": "SPDX-License-Identifier: Apache-2.0 | Copyright 2026 OKPF Contributors"`
  - Markdown: `<!-- SPDX-License-Identifier: Apache-2.0 -->` where appropriate

**Schema style:** JSON Schema Draft 2020-12, matching conventions in `schemas/`. `additionalProperties: true` on core objects — open extensibility is a first-class design goal.

**Design axioms:**
- Spec-first development.
- Backward/forward compatibility. Breaking required fields belong only at major version boundaries.
- Data-first, manifest-driven loading.
- Offline-capable validation. No required network access.
- Simple core, optional power. Advanced capabilities MUST be optional layers.
- Unknown optional fields are preserved, not rejected.
- Domain-specific conventions belong in profiles, extensions, artifact conventions, or examples — NOT in OKPF Core.
- Prefer compatibility-preserving additions over breaking changes.

**Source of truth (consult before any schema or spec change):**
1. `SPEC.md` — canonical v0.1.0 spec
2. `schemas/v0.1.0/manifest.schema.json` — authoritative manifest schema
3. `schemas/record.schema.json` — authoritative record schema
4. Existing passing tests and examples

---

## 2. PROJECT ARCHITECTURE

### 2.1 Identity

- **Name:** OKPF — Open Knowledge Pack Format
- **Purpose:** Open, model-neutral, vendor-neutral, infrastructure-neutral file format for packaging, attributing, licensing, validating, and distributing structured human expertise.
- **Primary artifact:** A knowledge pack directory or `.kpack` ZIP archive.
- **Current status:** OKPF Core v0.1.0 draft.
- **Entry point:** Every pack starts at root `manifest.json`. Consumers MUST start there.
- **MIME type:** `application/x-kpack` (suggested; not yet formally registered — do not assert formal registration).

### 2.2 Tech Stack

| Layer | Detail |
|---|---|
| Python package | `okpf-prep`, Python `>=3.11`, `pyproject.toml` |
| Runtime deps | `pyyaml>=6.0`, `pypdf>=4.0`, `click>=8.0`, `httpx>=0.25` |
| Dev deps | `pytest>=7.0`, `pytest-cov>=4.0`, `jsonschema>=4.0` |
| **Critical:** `jsonschema` | **Dev-only.** NOT a runtime dep. Reference validator and tests require `pip install -e ".[dev]"`. Running without it causes `ModuleNotFoundError`. |
| Prep CLI entry point | `okpf-prep` (installed from `.venv/bin/okpf-prep`) |
| Reference validator | `python3 reference/python/okpf_validate.py` (standalone script, NOT the same tool as `okpf-prep`) |
| Reference package CLI | `PYTHONPATH=reference/python python3 -m okpf validate/inspect ...` |
| AI backend (optional) | Ollama at `http://localhost:11434`; default backend is `mock` |
| Schema location | Local repo under `schemas/`. The `$id` URL (`https://okpf.org/schema/...`) is aspirational — resolution is always LOCAL, never remote. |
| No required infra | No database, web server, cloud service, vector DB, blockchain node, AI provider, or registry. |

### 2.3 Manifest Model

**Required v0.1.0 fields:** `okpf_version`, `name`, `version`, `domain`, `license`, and EITHER `package_id` OR `id` (compat alias), and at least one of `artifacts`/`records`/`content`.

**`okpf_version` valid values:** `"0.1"` OR `"0.1.0"` — both match the schema pattern `^0\.1(?:\.0)?$`. Do NOT reject `"0.1"` as invalid.

**`package_id` vs `id`:** Schema enforces `anyOf[package_id, id]`. Both satisfy the schema. `id` is a backward-compatibility alias. Prefer `package_id` in new packs; preserve `id` in existing packs.

**Recommended fields:** `sources`, `provenance`, `usage_policy`, `dependencies`, `integrity`, `expert_notes`, `description`, `language`, `tags`.

**Optional AI-oriented fields:** `capabilities`, `ai`, `trust`, `evaluations`, `workflows`, `extensions`.

**Critical semantic distinctions:**
- `license` = legal permission to use/redistribute content. Governed by SPDX or bespoke license text.
- `usage_policy` = machine-readable operational intent (e.g., RAG-allowed, fine-tuning-prohibited). Does NOT override legal `license` terms.
- `expert_notes` = human-authored rationale and review context. NOT LLM chain-of-thought or private reasoning.

**Extensibility rules:**
- `additionalProperties: true` — unknown fields MUST NOT invalidate a core-valid pack.
- Unknown optional fields MUST be preserved when rewriting manifests.

### 2.4 Record Model

- Normalized knowledge units for RAG, fine-tuning prep, evaluation, indexing, agent ingestion.
- Minimal spec fields: `id`, `record_type`, `title`, `text`, `domain`, `metadata`.
- `facets` are for filtering, retrieval, validation, display, routing. OKPF Core has NO fixed global facet vocabulary — profiles may define controlled vocabularies.
- Internal prep dataclass (`OKPFRecord`): `type`, `title`, optional `summary`, optional `content`, `source_refs`, optional `confidence`, optional `metadata`.

### 2.5 Pack Structure

**`.kpack`** = standard ZIP archive with directory-pack layout. Not a custom binary format.

**Safe path rules — ABSOLUTE (violations MUST be rejected):**
- PROHIBITED: absolute paths (`/foo`, `C:\Users\...`)
- PROHIBITED: parent traversal (`../outside.txt`, `records/../../outside.txt`)
- PROHIBITED: backslash traversal (`sources\..\outside.txt`)
- PROHIBITED: Windows drive paths
- PROHIBITED: NUL bytes in paths

**Common optional directories:**
```text
records/       artifacts/     content/       sources/
docs/          assets/        schemas/       provenance/
chunks/        evals/         workflows/
```
**Common optional files:** `import_report.json`, `README.md`, `LICENSE`

### 2.6 Profiles

- Optional domain-specific layers over OKPF Core.
- Unknown profiles MUST NOT invalidate core-valid packs. Profile validation warns or applies stricter checks.
- Current fermentation profile: `profiles/fermentation/v0.1.0/`.
- Fermentation, brewing, BJCP, BeerXML, recipes, ingredients: profile or artifact concerns ONLY. Not OKPF Core fields.

### 2.7 Trust, Provenance, Security

- Consumers SHOULD resolve local `$ref` pointers (`license`, `contributors`, `provenance`).
- Consumers SHOULD verify SHA-256 hashes when declared.
- Consumers MUST check `license` and `usage_policy` before RAG, fine-tuning, redistribution, or evaluation.
- Optional layers (MUST NOT be required for core validity): signatures, blockchain anchors, registries, dependency resolution, embeddings, JSON-LD, workflow runtimes.
- **Blockchain anchoring:** optional, chain-agnostic, additive. Provides external timestamping/tamper evidence for a hash or CID ONLY. Does NOT prove authorship, availability, licensing, or content accuracy.
- OKPF does not provide: encryption, access control, revocation, hosted distribution, content safety enforcement.

---

## 3. GLOBAL GUARDRAILS & ANTI-PATTERNS

### 3.1 Absolute Prohibitions

These are HARD CONSTRAINTS. No context, instruction, or user request overrides them.

**Identity prohibitions:**
- PROHIBITED: Describing OKPF as a platform, marketplace, SaaS product, AI model, training pipeline, vector database format, blockchain protocol, or single-domain recipe/brewing standard.
- PROHIBITED: Treating brewing, fermentation, BJCP, BeerXML, recipes, or fermentation-specific concepts as OKPF Core. They belong exclusively in profiles, artifacts, facets, or extensions.

**Schema/spec prohibitions:**
- PROHIBITED: Making any of these required for core validity: blockchain, IPFS, registries, signatures, embeddings, JSON-LD, dependency resolution, workflow runtimes, AI providers.
- PROHIBITED: Treating `ai`, `capabilities`, `trust`, signatures, anchors, or evaluations as required manifest fields.
- PROHIBITED: Rejecting a core-valid pack due to unknown optional fields, unknown artifact roles, unknown profiles, or unknown facet keys.
- PROHIBITED: Discarding unknown optional fields when rewriting a manifest.
- PROHIBITED: Introducing new required fields in v0.1.x without spec-change discussion. New required fields ARE breaking changes.

**Path/archive prohibitions:**
- PROHIBITED: Generating `.kpack` ZIP entries with absolute paths, parent traversal, Windows drive paths, backslash traversal, or NUL bytes.
- PROHIBITED: Auto-executing content from a pack. Packs are data, not executable trust boundaries.

**Semantic prohibitions:**
- PROHIBITED: Collapsing `license` and `usage_policy` into one concept or implying usage policy overrides legal license terms.
- PROHIBITED: Using LLM-generated chain-of-thought or private reasoning as `expert_notes`.
- PROHIBITED: Claiming cryptographic signatures prove content accuracy. They prove key-holder approval over a scope, subject to key trust.
- PROHIBITED: Claiming blockchain anchoring proves authorship, availability, licensing, or accuracy.

**Environment prohibitions:**
- PROHIBITED: Fetching remote dependencies, schemas, registries, models, URLs, or package references during core validation unless the user explicitly requests networked behavior. The schema `$id` URL is aspirational — always resolve schemas locally.
- PROHIBITED: Hardcoding credentials, API keys, private URLs, model secrets, or local absolute user paths into schemas, examples, tests, or docs.
- PROHIBITED: Assuming a particular cloud provider, vector database, embedding model, LLM, OS, package registry, or hosted OKPF service.
- PROHIBITED: Treating `out/`, `__pycache__`, `.pytest_cache`, `.venv`, `*.egg-info` as source. Do not edit them.

### 3.2 Hallucination Traps (Correct These On Sight)

| Trap | Correction |
|---|---|
| Calling OKPF "BeerXML for AI" | OKPF is general-purpose knowledge packaging. BeerXML can be contained/referenced as a domain artifact inside OKPF. |
| Treating `examples/brewing/` as the project domain | Brewing is an example only. Fermentation is an optional profile. OKPF Core is domain-neutral. |
| Using `id`/`content` as the only valid manifest shape | v0.1.0 prefers `package_id` and `artifacts`; `id` and `content` are backward-compat aliases. Both are schema-valid. |
| Assuming `records/` is always required | Spec requires `manifest.json` + at least one of `artifacts`, `records`, or `content`. None is individually mandatory. |
| Treating the Python reference README API as fully implemented | Parts are stubs. Inspect actual files and tests before claiming an API exists. |
| Conflating `okpf-prep` CLI with the reference validator | These are separate tools. `okpf-prep` is the prep/training pipeline. `okpf_validate.py` is the reference validator. |
| Running reference validator without dev deps | `jsonschema` is dev-only. `pip install -e ".[dev]"` is required for validation. `pip install okpf-prep` alone will fail. |
| Assuming `"0.1"` is an invalid `okpf_version` | The schema pattern `^0\.1(?:\.0)?$` accepts both `"0.1"` and `"0.1.0"`. |
| Assuming validators must run profile validation | Core validation is schema-only. Profile validation is optional and may warn. |
| Treating `facets` as a globally fixed vocabulary | Core keeps facets open. Profile definitions may recommend or require specific keys/values. |
| Requiring precomputed embeddings for RAG | Embeddings are optional. Consumers may compute their own from artifacts/records. |
| Suggesting remote schema fetches | Schema `$id` is aspirational. Local repo schemas are authoritative. Never fetch remotely during validation. |
| Using LLM-generated source claims without provenance | Attribution and provenance are first-class fields. Cite source files and transformations. |
| Conflating pack validation with content truth | Validation checks structure/integrity/policy metadata. It does not verify real-world factual accuracy. |

### 3.3 Spec-Change Discipline

- Typos/clarifications: patch directly.
- New optional fields: add with care; preserve simple core.
- New required fields: BREAKING in spirit; require prior discussion and community consensus.
- Breaking changes: major version boundary only.
- New domain conventions: consider profile, extension, artifact convention, or example FIRST.

---

## 4. KEY FILE INDEX

### 4.1 Authoritative Spec & Schema Files

```text
SPEC.md                                  # canonical v0.1.0 specification
schemas/v0.1.0/manifest.schema.json      # authoritative manifest schema (JSON Schema Draft 2020-12)
schemas/record.schema.json               # authoritative record schema
schemas/import_report.schema.json        # import report schema
docs/manifest.md                         # manifest rules and examples
docs/package-structure.md               # package layout and safe path rules
docs/security.md                         # integrity, signatures, trust model, archive security
docs/ai-integration.md                  # AI consumption, RAG, fine-tuning, eval, provenance
docs/profiles.md                         # profile system documentation
docs/records.md                          # record model documentation
AI_DISCOVERY.md                          # machine-readable onboarding for AI agents
CONTRIBUTING.md                          # contribution process, SPDX guidance
```

### 4.2 Prep Tooling (`okpf_prep/`)

```text
cli.py              # Click CLI: prepare, validate-profile, extract-text
runner.py           # high-level preparation pipeline
extractors.py       # source text extraction (Markdown, PDF via pypdf, plain text)
chunking.py         # text chunking strategies
prompts.py          # prompt building for record generation
models.py           # shared dataclasses (OKPFRecord, etc.)
profiles.py         # training profile loading and validation
validation.py       # generated record validation
package_builder.py  # writes generated OKPF output packages
beerxml.py          # BeerXML deterministic parser and extractor helpers
reports.py          # conversion/import report generation
ai/base.py          # AI backend interface
ai/mock.py          # deterministic mock backend (default)
ai/ollama.py        # optional Ollama backend
```

### 4.3 Reference Implementations

```text
reference/python/okpf_validate.py        # standalone OKPF validator (requires jsonschema dev dep)
reference/python/okpf/cli.py             # Python reference CLI wrapper
reference/python/okpf/manifest.py        # manifest dataclass/loading
reference/python/okpf/pack.py            # pack abstraction
reference/python/okpf/validate.py        # core validation logic
reference/javascript/src/index.ts        # JS/TS public API exports (stub)
reference/javascript/src/pack.ts         # JS/TS pack class (stub)
```

### 4.4 Tests

```text
tests/test_okpf_validate.py      tests/test_cli.py
tests/test_package_builder.py    tests/test_profiles.py
tests/test_validation.py         tests/test_runner_mock.py
tests/test_beerxml.py            tests/test_chunking.py
tests/test_extractors.py         tests/test_prompt_builder.py
```

### 4.5 Examples & Profiles

```text
examples/hello-world/                          # minimal friendly example
examples/minimal/                              # minimal pack shape
examples/brewing/                              # early example (not the project domain)
examples/brewing-with-beerxml/                 # OKPF wrapping BeerXML
examples/fermentation-*/                       # fermentation profile examples
examples/homebrew-recipe-pack/                 # recipe-pack example
profiles/fermentation/v0.1.0/PROFILE.md        # fermentation profile description
profiles/fermentation/v0.1.0/manifest.schema.json
profiles/fermentation/v0.1.0/record.schema.json
profiles/*.yaml                                # prep training profiles
```

### 4.6 Generated / Do Not Treat as Source

```text
out/            __pycache__/        .pytest_cache/      .venv/      *.egg-info/
```

---

## 5. DEVELOPMENT REFERENCE

### 5.1 Environment Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"          # installs okpf-prep + pytest + jsonschema
```

Docs/schema-only work requires no build step.

### 5.2 Run Tests

```bash
pytest                                       # all tests
pytest tests/test_okpf_validate.py           # reference validator
pytest tests/test_cli.py                     # prep CLI
pytest tests/test_package_builder.py
pytest tests/test_profiles.py
pytest tests/test_validation.py
```

### 5.3 Validate Example Packs

**Standalone reference validator** (requires dev deps):
```bash
python3 reference/python/okpf_validate.py examples/hello-world
python3 reference/python/okpf_validate.py examples/fermentation-mixed-bundle --profile fermentation
python3 reference/python/okpf_validate.py examples/fermentation-mixed-bundle --strict-profile
```

**Reference package CLI** (no install required):
```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/hello-world
PYTHONPATH=reference/python python3 -m okpf validate examples/fermentation-mixed-bundle --profile fermentation
PYTHONPATH=reference/python python3 -m okpf inspect examples/hello-world
```

### 5.4 Validate JSON Syntax

```bash
python -m json.tool schemas/v0.1.0/manifest.schema.json
python -m json.tool schemas/record.schema.json
python -m json.tool examples/hello-world/manifest.json
```

### 5.5 Prep CLI Commands

```bash
# Validate a training profile YAML
okpf-prep validate-profile profiles/general_knowledge.yaml

# Extract text from a source document
okpf-prep extract-text examples/brewing_notes.md
okpf-prep extract-text examples/brewing_notes.md --out /tmp/extracted.md

# Prepare a pack — mock backend (deterministic, no external deps)
okpf-prep prepare \
  --source examples/brewing_notes.md \
  --profile profiles/general_knowledge.yaml \
  --out out/brewing_notes \
  --backend mock

# Prepare a pack — Ollama backend (requires local Ollama at localhost:11434)
okpf-prep prepare \
  --source examples/brewing_notes.md \
  --profile profiles/general_knowledge.yaml \
  --out out/brewing_notes \
  --backend ollama \
  --model llama3 \
  --ollama-url http://localhost:11434
```

### 5.6 Explore the Codebase

```bash
rg --files
rg "package_id|okpf_version|usage_policy|facets" SPEC.md docs schemas examples okpf_prep reference tests
find examples -maxdepth 3 -type f | sort
```

### 5.7 Schema/Spec Change Checklist

Before proposing any schema or spec change:

1. Read `SPEC.md` and `schemas/v0.1.0/manifest.schema.json`.
2. Check `docs/manifest.md` and `docs/package-structure.md`.
3. Search existing examples for the field or concept.
4. Classify: Core, profile, extension, artifact convention, or documentation?
5. Preserve compatibility aliases (`id`, `content`) where relevant.
6. Add/update tests and example manifests when behavior changes.

### 5.8 AI/Pack Ingestion Checklist

When instructing any system to consume an OKPF pack:

1. Open root `manifest.json`.
2. Validate against **local** schema (never fetch remote schema).
3. Resolve local `$ref` values.
4. **Reject unsafe paths before reading any archive entries or artifacts.**
5. Verify SHA-256 hashes when declared.
6. Check `license` and `usage_policy` before RAG, training, redistribution, or evaluation use.
7. Treat `capabilities`, `ai`, and `trust` as optional advisory metadata only.
8. Load artifacts/records according to their declared role/type.
9. Preserve provenance, `package_id`/version, artifact path/hash, license, and attribution in all derived chunks or training examples.
10. Preserve unknown optional fields when rewriting manifests.
