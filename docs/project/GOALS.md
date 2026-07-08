<!-- SPDX-License-Identifier: Apache-2.0 -->

# Goals

## Product / Project Goal

OKPF (Open Knowledge Pack Format) is an open, model-neutral, vendor-neutral,
infrastructure-neutral file format for packaging structured human expertise
— provenance, licensing, and usage intent included — so knowledge can move
between tools and teams without depending on a specific platform.

The reference implementation (Python CLI/SDK, JSON Schemas, JavaScript
stubs, example packs) exists to prove the spec is implementable, not as a
product in its own right.

## Current Direction

- OKPF Core v0.1 is **frozen** for required-field changes
  (see [docs/v0.1-core-freeze.md](../v0.1-core-freeze.md)).
- New capability now ships as **optional extensions** (e.g.
  `okpf.encrypted_artifacts.v0`, `okpf.selective_disclosure`) or as
  **profiles** (e.g. fermentation, physical-skill-evidence), not as new
  Core required fields.
- Tooling and docs continue to evolve under the frozen Core: reference CLI
  commands (`validate`, `inspect`, `pack`, `unpack`, `init`, `demo`,
  `export-rag`, `export-citations`), example packs, and adoption docs.
- The JavaScript/TypeScript SDK is intentionally behind the Python
  reference and is being brought toward scoped parity
  (`Pack.load()`/`validate()` first, no `.kpack`/`ajv`/builder yet).
- See [ROADMAP.md](../../ROADMAP.md) for the full milestone list; this file
  only summarizes current-cycle intent so it doesn't drift out of sync with
  the roadmap.

## Non-Goals

Explicitly out of scope for OKPF Core (see also
[ROADMAP.md § Non-Goals](../../ROADMAP.md)):

- Hosting or distributing knowledge packs — that is a registry's job, not
  Core's.
- Defining how AI models use packs — that is an application-layer concern.
- Mandating any specific blockchain, ledger, or anchoring scheme.
- A marketplace, payments, or royalty/DRM enforcement system.
- Hard-coding domain vocabularies (brewing, BJCP, fermentation, etc.) into
  OKPF Core — those belong in profiles, extensions, or examples.
- An executable agent runtime or server-side execution environment. Packs
  are data; they are never auto-executed.
- Proving factual accuracy of pack contents. Core validation checks
  structure, integrity, and policy metadata only.

## Important Constraints

- **Spec stability first.** Core priorities, in order: specification
  stability, schema correctness, provenance/attribution, license clarity,
  security, portability, long-lived interoperability.
- **Offline-capable validation.** Core validation must not fetch remote
  schemas, registries, models, or URLs unless a user explicitly asks for
  networked behavior.
- **Additive-only Core.** New required fields in v0.1.x are breaking in
  spirit and require prior discussion; compatibility aliases (`id`,
  `content`) must be preserved.
- **Packs are data, not code.** No auto-execution of pack content, ever.
- **License vs. usage policy stay separate.** `license` is legal
  permission; `usage_policy` is machine-readable operational intent. One
  does not override the other.
- **No secrets or local paths in tracked content.** Schemas, examples,
  tests, and docs must not contain credentials, API keys, private URLs, or
  local absolute user paths.
