<!-- SPDX-License-Identifier: Apache-2.0 -->

# Current Status

Last verified: 2026-07-07 (`pytest -q` → 283 passed, on branch `main`).

This file is a snapshot, not a promise. When it and the code disagree,
trust the code and update this file.

## What Currently Works

- **Core spec and schemas** — `SPEC.md`, `schemas/v0.1.0/manifest.schema.json`,
  `schemas/record.schema.json`; declared frozen for required fields in
  [docs/v0.1-core-freeze.md](../v0.1-core-freeze.md).
- **Reference validator and CLI** — `reference/python/okpf_validate.py`
  (standalone) and `reference/python/okpf/cli.py`
  (`validate`, `inspect`/`info`, `pack`, `unpack`, `init`, `demo`,
  `export-rag`, `export-citations`, `compare-layout`, `explain`). Full
  suite passes (283 tests as of last verification).
- **`okpf-prep` pipeline** — `okpf_prep/` package with `prepare`,
  `validate-profile`, `extract-text` CLI commands, BeerXML support, and a
  mock backend plus optional local Ollama backend.
- **Profiles** — fermentation, physical-skill-evidence, and
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

- **108 untracked `demo-*.kpack` files at the repository root** (as of
  this writing). These look like output from the `okpf demo` CLI command
  writing into the working directory instead of `out/` (which is
  gitignored) or a temp directory. They are not gitignored and clutter
  `git status`. **Needs confirmation**: check `reference/python/okpf/cli.py`
  demo-command output path and either fix the default output location or
  add a `.gitignore` entry.
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
