# OKPF Roadmap

This roadmap reflects the current thinking of the OKPF maintainers. Priorities may shift based on community feedback and contributions.

---

## Milestone 0 — Foundation

**Goal:** Establish the core format concept, initial specification, and working examples.

- [x] Initial repository structure
- [x] README and project philosophy
- [x] Specification draft (v0.1.0-draft)
- [x] JSON schemas for manifest, license, provenance, contributors, evaluations, tasks
- [x] Optional profile and facets convention
- [x] Draft fermentation profile as a domain-neutral extension example
- [x] Example pack: Brewing — Water Chemistry
- [x] Placeholder examples: Mechanic Diagnostics, Software Architecture
- [x] Documentation: concepts, licensing, provenance, blockchain, security, examples
- [x] Reference implementation stubs (Python, JavaScript)
- [ ] Community feedback on v0.1.0 spec draft

---

## Milestone 1 — Stable Core (v0.1.0) (Current)

**Goal:** Produce an OKPF Core v0.1.0 release candidate with a consistent draft specification, schema, examples, conformance fixtures, and working validator.

### Specification
- [ ] Finalize `manifest.json` schema based on feedback
- [ ] Finalize `license.json` schema with SPDX integration
- [ ] Finalize profile declaration and profile validation guidance
- [ ] Finalize import report counts for records, chunks, indexed units, record types, and facets
- [ ] Define canonical URN namespace for pack IDs
- [ ] Clarify handling of content hash mismatches
- [ ] Document upgrade/migration path from earlier drafts

### Tooling
- [x] `okpf validate <pack>` — validate a pack against the spec
- [x] `okpf info <pack>` — display pack summary
- [ ] `okpf init` — interactively scaffold a new pack
- [ ] Python reference library (`okpf-py`)
- [ ] JavaScript/Node reference library (`okpf-js`)

### Examples
- [ ] Complete brewing example (full guide + evaluations + provenance)
- [ ] Expand profile examples beyond fermentation to prove domain neutrality
- [ ] Complete mechanic diagnostics example
- [ ] Complete software architecture example

### Community
- [ ] Public discussion of v0.1.0 spec on GitHub Discussions
- [ ] First external contributors
- [ ] CONTRIBUTING guide refined

---

## Milestone 2 — Ecosystem (v0.2.0)

**Goal:** Enable practical sharing, discovery, and use of packs.

### Specification
- [ ] Embeddings schema finalized with multi-provider support
- [ ] Signatures schema finalized (GPG, SSH key, Verifiable Credentials)
- [ ] Dependency resolution between packs
- [ ] Pack bundle format (multi-pack archive)
- [ ] Domain registry proposal (community-managed namespace)

### Tooling
- [ ] `okpf pack` — create a `.kpack` archive from a directory
- [ ] `okpf unpack` — extract a `.kpack` archive
- [ ] `okpf sign` — sign a pack with a private key
- [ ] `okpf verify` — verify signatures
- [ ] `okpf diff` — compare two pack versions
- [ ] Plugin/extension API for custom content types

### Integrations (optional, community-driven)
- [ ] IPFS content addressing integration
- [ ] Git-based pack versioning workflow
- [ ] First blockchain anchor adapter (chain-agnostic interface defined in Milestone 1)

---

## Milestone 3 — Quality and Discovery (v0.3.0)

**Goal:** Make packs more trustworthy and findable.

### Specification
- [ ] Evaluation schema v2 with scoring rubrics
- [ ] Peer review workflow schema
- [ ] Pack registry protocol (open, self-hostable)
- [ ] Structured task schema for agent-compatible knowledge tasks

### Tooling
- [ ] `okpf eval` — run evaluations against a pack
- [ ] `okpf publish` — publish to a registry
- [ ] `okpf search` — search a registry
- [ ] Registry server reference implementation

### Community
- [ ] Public pack registry (hosted, community-governed)
- [ ] Pack submission and review process
- [ ] Example packs from 5+ domains

---

## Milestone 4 — Maturity (v1.0.0)

**Goal:** Declare the format stable and production-ready.

- [ ] Specification v1.0.0 — stable, no planned breaking changes
- [ ] Conformance test suite
- [ ] Third-party implementations (Go, Rust, other languages)
- [ ] Long-term governance model established
- [ ] At least 3 independent organizations using OKPF in production

---

## Non-Goals (by design)

The following are explicitly out of scope for OKPF core:

- Hosting or distributing knowledge packs (that's for registries to do)
- Defining how AI models use packs (that's for application layers)
- Mandating any specific blockchain or smart contract
- Building a marketplace or payment system
- Defining natural language processing pipelines
- Hard-coding domain-specific vocabularies into OKPF Core

---

## How to Influence the Roadmap

Open a GitHub Issue or Discussion with the label `roadmap`. The most impactful contributions are:

1. Real-world use cases that don't fit the current spec
2. Working example packs in new domains
3. Reference implementations in new languages
4. Concrete proposals for schema improvements

---

*Last updated: 2026-05-05*
