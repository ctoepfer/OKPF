# OKPF Phase 1 Roadmap

**Phase 1: OKPF Core v0.1.0**

This document describes what Phase 1 includes, what it intentionally excludes, and what comes next.

---

## Phase 1 Deliverables

Phase 1 establishes the minimum viable foundation for OKPF. It is deliberately narrow so the core is stable before optional layers are added.

### Included in Phase 1

- [x] **Core manifest schema** — `manifest.json` with required and recommended fields
- [x] **JSON Schema validation** — `schemas/manifest.schema.json` (Draft 2020-12)
- [x] **Supporting schemas** — license, contributor, provenance, evaluation, task/workflow
- [x] **Artifact roles** — defined set covering both human-readable and AI-workflow use cases
- [x] **Pack types** — `reference_pack`, `training_pack`, `workflow_pack`, `evaluation_pack`, `mixed_pack`
- [x] **Intended uses** — advisory `intended_uses` and `not_intended_for` fields
- [x] **License metadata** — SPDX expressions with granular `ai_training` permission field
- [x] **Provenance metadata** — sources and transformations model
- [x] **Contributor attribution** — first-class contributor records with ORCID support
- [x] **Integrity metadata** — SHA-256 hash verification for content artifacts
- [x] **AI interoperability hints** — `capabilities`, `ai`, and `trust` optional manifest blocks
- [x] **Example packs** — `basic-pack` (minimal) and `homebrew-recipe-pack` (multi-artifact)
- [x] **Profiles and facets** — optional profile declarations plus open-ended record facets
- [x] **Fermentation profile example** — domain-specific recommendations outside OKPF Core
- [x] **Import report counts** — optional record, chunk, indexed unit, record type, and facet counts
- [x] **Reference validator** — `reference/python/okpf_validate.py` with JSON Schema + file checks
- [x] **Python SDK** — `reference/python/okpf/` — `Pack.load()`, `validate()`, manifest types
- [x] **JavaScript/TypeScript SDK** — `reference/javascript/src/` — `Pack.load()`, type definitions
- [x] **Specification** — `SPEC.md` with all required and optional fields documented
- [x] **Concepts documentation** — `docs/concepts.md`
- [x] **Governance** — `GOVERNANCE.md`, `CODE_OF_CONDUCT.md`, `AUTHORS.md`

---

## Phase 1 Exclusions

The following are explicitly out of scope for Phase 1. They may become optional extensions in later phases.

### Infrastructure and Platform Features

- Blockchain ownership or on-chain pack registration
- Marketplace, payments, or commerce features
- Royalty enforcement or micropayment systems
- Hosted registry or discovery service
- Executable agent runtime or server-side execution
- Model training service
- Domain-specific core fields for brewing, fermentation, recipes, AI training, RAG, or vector databases

### Security and Privacy

- Content encryption (at-rest or in-transit)
- Zero-knowledge proofs or verifiable credentials
- Trusted execution environments (TEEs)
- Access control or DRM

### Advanced Tooling

- Pack bundling/unbundling CLI (`okpf pack`, `okpf unpack`)
- Dependency resolution
- Pack signing workflow (`okpf sign`)
- Registry push/pull commands

---

## What Phase 2 Might Include

These are candidate items for Phase 2, based on community feedback and early adoption patterns. None are committed.

| Candidate | Description |
|-----------|-------------|
| CLI tool | `okpf validate`, `okpf pack`, `okpf info` commands |
| Pack registry spec | Standard API for hosting and discovering packs |
| Signing workflow | `okpf sign` and `okpf verify` with GPG/SSH/ed25519 |
| Dependency resolution | Fetching and verifying dependent packs |
| `.kpack` archive tooling | ZIP creation and extraction utilities |
| Streaming/chunked content | Large content artifacts with chunked manifests |
| Multi-language SDKs | Go, Rust, Java reference implementations |

---

## Stability Commitment

Phase 1 fields marked **required** in `SPEC.md` will not be renamed or removed without a major version bump and a migration guide.

Phase 1 fields marked **optional** may change semantics in minor versions if they have low adoption and the change is clearly backward compatible. High-adoption optional fields will be treated with the same stability guarantee as required fields.

New optional fields will be added additively in minor versions. Tools that ignore unknown fields are forward-compatible by design.

---

## Getting Involved

- Read [CONTRIBUTING.md](../CONTRIBUTING.md) for how to contribute
- Read [GOVERNANCE.md](../GOVERNANCE.md) for how decisions are made
- Open a [GitHub Discussion](https://github.com/ctoepfer/OKPF/discussions) for design questions
- Open a [GitHub Issue](https://github.com/ctoepfer/OKPF/issues) for bugs or concrete proposals
