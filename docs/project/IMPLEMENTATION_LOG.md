<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

This is the primary resume point for AI coding agents and humans picking
up this project. Read this before starting non-trivial work. Update it
after meaningful code or architecture changes — see the rule in
[`CLAUDE.md`](../../CLAUDE.md) / [`AGENTS.md`](../../AGENTS.md).

Last updated: 2026-11-08.

## Current Phase

Post-Core-freeze application-profile work. Core v0.1 required fields remain
frozen; institutional requirements apply only when the profile is selected.

## Current Goal

Scaffold `okpf.profile.institutional.v1` with schemas, offline validation,
a sourced seed case, fixtures, tests, and documentation. This scope is complete;
a diagnostic runtime and larger curated corpus are future work.

## Where We Left Off

Implemented the institutional application profile on 2026-11-08. Explicit
`--profile okpf.profile.institutional.v1` or `--strict-profile` on a declaring
manifest runs its mandatory checks. Core-only validation is unchanged. The
Python entry point is `okpf.institutional.validate_institutional_pack()`.
Directories and `.kpack` archives are supported, with bundled offline schemas.

The event-stream seed cites npm and BitPay; it marks uncollected long-term
outcomes and unknown custody/funding facts explicitly. It claims single-coder
status and a purposive sample of one, not a representative cohort.

The incoming working tree already contained changes in `okpf_prep/`, the two
prep YAML profiles, and `tests/test_html_table_records.py`. Those changes were
preserved. Full-suite failures are in that prep-tool area; see verification.

The July resume notes were stale: the encrypted-artifacts guide and example
are now tracked, and commit `2d331cf` ignores generated demo packs.

The user requested committing and pushing the institutional changes to origin.
Incoming prep-tool work remains separate and uncommitted.

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
- Profiles: fermentation, physical-skill-evidence, human-correction-loop,
  and institutional reliability (schemas, validator, sourced seed, tests, docs).
- A broad example-pack library under `examples/`.
- Selective-disclosure / encrypted-artifacts extension metadata, schema
  fields, spec text, and docs (commits `a9305ec`, `3db4cd9`).
- This resume system (`docs/project/`, plus the `CLAUDE.md`/`AGENTS.md`
  rule pointing to it).

Full history: `git log --oneline`.

## In Progress

No remaining implementation work for the requested institutional scaffold.
Incoming prep-tool edits remain in the working tree and need their own review.

## Next Actions

1. Review the institutional scaffold and its documentation.
2. Resolve the seven prep-tool test failures separately, preserving the incoming
   work. See [NEXT_ACTIONS.md](NEXT_ACTIONS.md).
3. Before expanding the corpus, define a denominator and arrange source review;
   do not label this single-coder seed as dual-coded.

## Known Issues

- **`demo-*.kpack` output at repo root.** Now ignored by commit `2d331cf`;
  output-location cleanup remains optional. Historical cause:
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

- `schemas/profiles/institutional/v1/` and identical Python-bundled copies.
- `reference/python/okpf/institutional.py`, `okpf_validate.py`, and `pyproject.toml`.
- `examples/institutional/`, `tests/fixtures/institutional/`, and
  `tests/test_institutional_profile.py`.
- `docs/profiles/institutional-v1.md`, `docs/profiles.md`, and project resume notes.

Pre-existing prep-tool changes were not edited by this task.

## Testing / Verification

2026-11-08:

- Final focused run: `python3 -m pytest -q tests/test_institutional_profile.py
  tests/test_schema_bundle_in_sync.py tests/test_okpf_validate.py` — **71 passed**.
- Full suite before the final two edge-case tests: **381 passed, 7 failed**.
  Failures: `test_cli.py::test_prepare_command_exits_zero`; two prompt-builder
  bounded-instruction tests; four `test_runner_mock.py` tests (validation,
  prose records, table records, callback exception). These exercise incoming
  prep changes, not the reference profile validator.
- Standalone explicit-profile CLI and package CLI `--strict-profile` both
  validate the seed successfully.
- `git diff --check` passes.

Tests cover YAML/JSON, archives, missing/empty perspectives and unobserved
variables, duplicate IDs, manifest metadata, year ordering, unknown optional
fields, Core aliases, malformed YAML, unsafe archive paths, and symlink escapes.

## Notes For Next Session

Start with the institutional files listed above. Keep the incoming prep-tool
work separate when reviewing changes. The scaffold does not implement the
attached roadmap's proposal-analysis runtime, embeddings, or signatures.
