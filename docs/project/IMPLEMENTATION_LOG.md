<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

This is the primary resume point for AI coding agents and humans picking
up this project. Read this before starting non-trivial work. Update it
after meaningful code or architecture changes — see the rule in
[`CLAUDE.md`](../../CLAUDE.md) / [`AGENTS.md`](../../AGENTS.md).

Last updated: 2026-07-07.

## Current Phase

Post-Core-freeze extension work. OKPF Core v0.1 required fields were
declared frozen in commit `18cadcc` (2026-07-03,
[docs/v0.1-core-freeze.md](../v0.1-core-freeze.md)). Current work is adding
**optional extensions** on top of the frozen Core — specifically the
selective-disclosure / encrypted-artifacts extension
(`okpf.encrypted_artifacts.v0`).

**Needs confirmation:** whether this maps to a specific numbered
milestone/phase beyond the six referenced in recent commit messages
("Phase 1" through "Phase 6" — see `git log --oneline` and
`docs/phase-1-roadmap.md`). No phase-7 document exists yet.

## Current Goal

Land the `okpf.encrypted_artifacts.v0` extension end-to-end: schema
support, spec/doc coverage, a conformance fixture, a full worked example
pack, and a how-to guide — then commit it. Broader background goal: keep
closing the gap between [ROADMAP.md](../../ROADMAP.md) Milestone 1's
remaining unchecked items (JS/TS SDK parity, canonical URN namespace,
content-hash-mismatch handling) without touching frozen Core fields.

## Where We Left Off

The working tree (as of 2026-07-07) has **complete, passing, but
uncommitted** changes finishing the encrypted-artifacts extension that
commits `a9305ec` and `3db4cd9` (2026-07-03) started:

- `README.md` — links to the new how-to guide and example pack.
- `docs/examples.md` — table row for the new example.
- `tests/test_okpf_validate.py` — new test
  `test_selective_disclosure_encrypted_source_example_validates`.
- `docs/how-to/encrypted-artifacts.md` (new, untracked) — full how-to
  guide for packaging encrypted artifacts.
- `examples/selective-disclosure-encrypted-source/` (new, untracked) — a
  complete worked example pack (public/redacted/encrypted layers,
  provenance, evals, records).

`pytest -q` passes in full (283 passed) with these changes present. This
looks done and ready to commit — see
[NEXT_ACTIONS.md](NEXT_ACTIONS.md) item 1.

> Next step: review `git diff README.md docs/examples.md
> tests/test_okpf_validate.py` plus the two new untracked paths above,
> confirm nothing else changed, and commit as one unit (it's one logical
> change: finishing the encrypted-artifacts extension).

Separately, this session (2026-07-07) added the `docs/project/` resume
system itself — this file and its siblings — per explicit user request.

## Completed

- OKPF Core v0.1.0 spec, schemas, and conformance docs
  (`SPEC.md`, `schemas/v0.1.0/manifest.schema.json`,
  `schemas/record.schema.json`, `docs/v0.1-conformance.md`).
- Core declared frozen for required fields (`docs/v0.1-core-freeze.md`,
  commit `18cadcc`).
- Reference validator and Python CLI/SDK
  (`reference/python/okpf_validate.py`, `reference/python/okpf/`) with
  `validate`, `inspect`/`info`, `pack`, `unpack`, `init`, `demo`,
  `export-rag`, `export-citations`, `explain`, `compare-layout`.
- `okpf-prep` package: `prepare`, `validate-profile`, `extract-text`,
  BeerXML support, mock + optional Ollama backends.
- Profiles: fermentation, physical-skill-evidence, human-correction-loop.
- A broad example-pack library under `examples/`.
- Selective-disclosure / encrypted-artifacts extension metadata, schema
  fields, spec text, and docs (commits `a9305ec`, `3db4cd9`).
- This resume system (`docs/project/`, plus the `CLAUDE.md`/`AGENTS.md`
  rule pointing to it).

Full history: `git log --oneline`.

## In Progress

- Selective-disclosure-encrypted-source example pack + how-to guide —
  functionally complete and tested, **not yet committed** (see "Where We
  Left Off" above).
- `docs/project/` resume system rollout (this change).

## Next Actions

See [NEXT_ACTIONS.md](NEXT_ACTIONS.md) for the full prioritized list.
Top of the list right now:

1. Commit the encrypted-artifacts example/how-to work described above.
2. Track down why `okpf demo` writes `.kpack` files into the repo root
   (`reference/python/okpf/demo.py:74`, `Path.cwd() / f"demo-{...}.kpack"`)
   instead of a gitignored or temp location — 108 stray files exist as of
   this writing.

## Known Issues

- **`demo-*.kpack` file leak at repo root.** Confirmed cause:
  `reference/python/okpf/demo.py:74` writes output to `Path.cwd()`
  instead of the caller-controlled temp dir it already creates. Not
  gitignored. 108 untracked files present as of 2026-07-07.
- **Duplicate AI manifest docs.** `ai-manifest.md` and `AI_MANIFEST.md`
  both exist at repo root with different content; only `AI_MANIFEST.md`
  has an SPDX header. Canonical file **needs confirmation**.
- **Stale root-level status docs.** `PROJECT_STATUS.md` is dated
  2026-05-27 and predates the Core freeze and the encrypted-artifacts
  extension. `HANDOFF.md` is an empty template. Both now overlap with
  `docs/project/`. Disposition **needs confirmation** — see
  `NEXT_ACTIONS.md` items 4–5.
- **`ROADMAP.md` / `tools/README.md` drift.** Some docs still describe
  `pack`/`unpack` as future work even though they're implemented; flagged
  previously in `PROJECT_STATUS.md`'s own "Recommended Next Development
  Steps" section and not yet fixed.

## Decisions Made

See [DECISIONS.md](DECISIONS.md) for project-process decisions and
[docs/adr/](../adr/) for formal spec/schema architecture decisions
(currently ADR 0001–0005, all `Accepted`, covering `.kpack` ZIP format,
optional blockchain, license/usage_policy separation, JSON Schema
validation, and "simple core, optional power").

## Files Touched Recently

From `git log --oneline -10` (most recent first):

- `3db4cd9` — Polish selective disclosure terminology
- `a9305ec` — Add selective disclosure extension metadata
- `18cadcc` — docs: declare OKPF Core v0.1 frozen (Phase 6); fix leaked
  local path in README
- `0051c80` — feat: fix SDK `Pack.load()`, prep packaging, TS scoped
  parity, adoption docs (Phase 4-5)
- `502c259` — feat: add RAG export contract, benchmark tooling,
  historical evidence example (Phases 2-3)
- `49c929f` — feat: add `okpf init/add/fix/explain`, starter templates,
  example CI (Phase 1)

Plus this session's uncommitted work (see "Where We Left Off").

## Testing / Verification

Last full run: 2026-07-07, `pytest -q` → **283 passed**, no failures, no
skips, including the working-tree changes described above.

Standard commands (see also `CLAUDE.md` § Test Commands):

```bash
pytest
python3 reference/python/okpf_validate.py examples/selective-disclosure-encrypted-source
```

## Notes For Next Session

> Next step: commit the selective-disclosure-encrypted-source example and
> how-to guide (tests already pass — this is a commit-and-move-on task,
> not a build task). Then decide, with the user, whether to clean up the
> stray `demo-*.kpack` files and fix `demo.py`'s output path before
> starting anything else, since they'll keep multiplying every time `okpf
> demo` runs from the repo root.

Do not re-derive "what's done" from scratch by re-reading the whole repo
— this file plus `CURRENT_STATUS.md` should be sufficient. Only fall back
to a full repo scan if this file's claims don't match what you observe in
the code (and if so, please fix the mismatch here).
