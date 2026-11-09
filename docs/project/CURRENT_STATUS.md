<!-- SPDX-License-Identifier: Apache-2.0 -->

# Current Status

2026-11-08 publication update: the user explicitly authorized committing and
pushing the completed institutional review, consumer experiment, and proposal
linter to origin. This supersedes local-only restrictions below. Unrelated
prep-tool edits remain excluded. Verification: 207 focused tests passed; full
suite 446 passed with seven pre-existing prep-tool failures.

Last verified: 2026-11-08. Focused review/consumer/regression tests: 207 passed.
Full suite: 446 passed, seven pre-existing prep-tool failures.

This file is a snapshot, not a promise. When it and the code disagree,
trust the code and update this file.

## What Currently Works

- **Experimental proposal linting** — `okpf lint-proposal` checks required evasion
  and pre-mortem blocks, reports heuristic metric mentions, and optionally
  cross-references validated directory/archive cases. Existing case layouts keep
  these fields optional. No execution, hazard estimation, signature verification
  or audit ingestion is implied. See `docs/institutional-review.md`.

- **Local experimental follow-ups (do not push)** — compatible institutional
  case layouts and `okpf review`; actual fourteen-answer consumer run on the
  existing evidence pack using installed `phi3.5:latest`. Exact inputs, coverage,
  raw outputs, and AI-authored assessments are retained under
  `docs/experiments/institutional-consumer/`. Seven responses hit the output cap;
  increased context availability did not ensure faithful attribution/correction.

- **Institutional evidence suite** —
  `examples/institutional-evidence-npm/`, two real episodes, separate synthetic
  correction fixtures, 16 Core records, seven AI-authored rubrics, and export
  context tests. No new profile or runtime; no measured consumer results.
  See `docs/institutional-evidence-packs.md`. The user subsequently authorized
  committing and pushing that earlier suite to origin. The current follow-ups
  are explicitly local-only.

- **Core spec and schemas** — `SPEC.md`, `schemas/v0.1.0/manifest.schema.json`,
  `schemas/record.schema.json`; declared frozen for required fields in
  [docs/v0.1-core-freeze.md](../v0.1-core-freeze.md).
- **Reference validator and CLI** — `reference/python/okpf_validate.py`
  (standalone) and `reference/python/okpf/cli.py`
  (`validate`, `inspect`/`info`, `pack`, `unpack`, `init`, `demo`,
  `export-rag`, `export-citations`, `compare-layout`, `explain`). Institutional profile checks support explicit selection and strict declared-profile validation.
- **`okpf-prep` pipeline** — `okpf_prep/` package with `prepare`,
  `validate-profile`, `extract-text` CLI commands, BeerXML support, and a
  mock backend plus optional local Ollama backend.
- **Institutional reliability profile** — `okpf.profile.institutional.v1`: schemas
  under `schemas/profiles/institutional/v1/`, bundled offline validator, sourced
  seed, and docs at `docs/profiles/institutional-v1.md`. Scaffold complete;
  diagnostic runtime and broader curated corpus are not implemented.
- **Other profiles** — fermentation, physical-skill-evidence, and
  human-correction-loop profiles exist under `profiles/` with examples.
- **Example packs** — a broad set under `examples/` (hello-world,
  brewing, homebrew-recipe-pack, zymurgy-recipe-correction,
  local-organization-knowledge, field-repair-checklist,
  local-history-lost-electric-sign, selective-disclosure-encrypted-source,
  and more), used as both documentation and CI fixtures.
- **Extension: encrypted artifacts / selective disclosure**
  (`okpf.encrypted_artifacts.v0`) — schema support, docs
  (`docs/extensions/encrypted-artifacts.md`,
  `docs/how-to/encrypted-artifacts.md`), a conformance fixture under
  `tests/fixtures/conformance/valid/selective-disclosure/`, and a full
  example pack — see `docs/project/IMPLEMENTATION_LOG.md` for the exact
  commit/working-tree state.

## Partially Implemented

- **JavaScript/TypeScript SDK** (`reference/javascript/src/`) — stub-level
  only. Has `Pack.load()`/type definitions but no `.kpack` archive
  support, no `ajv`-based validation, and no builder. Tracked in
  [ROADMAP.md](../../ROADMAP.md) Milestone 1.
- **Status documentation** — `PROJECT_STATUS.md` (repo root) is a useful
  point-in-time snapshot but is dated 2026-05-27, predates the Core freeze
  declaration and the encrypted-artifacts extension work, and now
  overlaps with this file. Treat `docs/project/` as canonical going
  forward; `PROJECT_STATUS.md` needs a refresh or a redirect note.
  **Needs confirmation** on whether to keep updating it or retire it in
  favor of this file.
- **`HANDOFF.md`** (repo root) — an empty session-handoff template, not
  currently filled in. Overlaps in purpose with
  `docs/project/IMPLEMENTATION_LOG.md`. **Needs confirmation** on whether
  it should be retired or kept as a lighter-weight per-session scratch
  form.

## What Appears Broken Or Incomplete

- **Incoming prep-tool changes have seven failing tests** in CLI prepare,
  prompt wording, and mock-runner validation. See the implementation log.
- **Demo packs still write to the repo root**, but are now gitignored by
  commit `2d331cf`; the old untracked-file warning no longer applies.
- **Duplicate AI manifest files** — `ai-manifest.md` (383 lines, no SPDX
  header, "persona/operating mode" framing) and `AI_MANIFEST.md` (110
  lines, has SPDX header, plain project-purpose framing) both exist at
  the repo root with different content. **Needs confirmation** on which
  is canonical; the other should likely be removed or merged.

## Important Files / Components

| Area | Path |
|---|---|
| Spec | `SPEC.md` |
| Core manifest schema | `schemas/v0.1.0/manifest.schema.json` |
| Record schema | `schemas/record.schema.json` |
| Standalone validator | `reference/python/okpf_validate.py` |
| Python SDK / CLI | `reference/python/okpf/` |
| JS/TS SDK (stub) | `reference/javascript/src/` |
| Prep pipeline | `okpf_prep/` |
| Profiles | `profiles/` |
| Examples | `examples/` |
| Tests | `tests/` |
| ADRs (formal decisions) | `docs/adr/` |
| Resume system (this system) | `docs/project/` |
