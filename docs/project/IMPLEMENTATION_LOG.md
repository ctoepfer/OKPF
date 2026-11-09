<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

This is the primary resume point for AI coding agents and humans picking
up this project. Read this before starting non-trivial work. Update it
after meaningful code or architecture changes — see the rule in
[`CLAUDE.md`](../../CLAUDE.md) / [`AGENTS.md`](../../AGENTS.md).

Last updated: 2026-11-08.

## Current Phase

Post-Core-freeze example-driven evidence packaging. Core requirements and
export contracts are unchanged.

## Current Goal

Complete the narrowly scoped institutional-evidence example suite. The local
implementation is complete; the user subsequently authorized committing and
pushing this suite to origin.

## Where We Left Off

Added `examples/institutional-evidence-npm/`: two real bounded npm episodes
(event-stream 2018 and ua-parser-js 2021), narrative and comparison artifacts,
16 Core records, citation-only source context, and seven evaluation rubrics.
Three records are explicitly synthetic correction fixtures. All authoring is
identified as AI-generated draft work, without independent human review.

Added `docs/institutional-evidence-packs.md` and restrained README/example links.
No new profile, Core schema, validator, runtime, or exporter change was needed.
The earlier institutional profile is a separate opt-in scaffold (commit
`2d9f27e`, already pushed in the preceding task); this suite does not adopt it.

An example-local provenance index preserves evidence, qualifications, competing
interpretations, and supersession links in both exports. Limitation summaries
also survive citation export. Tests verify reference closure and projection
consistency, not consumer answer quality. Full third-party sources are not
redistributed; URL/locator/date metadata does not create an archival snapshot.

The user initially requested local-only work, then explicitly authorized a
commit and push to origin. Incoming prep-tool edits remain separate and untouched.

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
- A broad example-pack library under `examples/`, now including the local
  institutional-evidence suite with export-context checks.
- Selective-disclosure / encrypted-artifacts extension metadata, schema
  fields, spec text, and docs (commits `a9305ec`, `3db4cd9`).
- This resume system (`docs/project/`, plus the `CLAUDE.md`/`AGENTS.md`
  rule pointing to it).

Full history: `git log --oneline`.

## In Progress

No remaining implementation work for the requested evidence suite. Source and
rubric review by a human is not claimed and remains a future research step.
Incoming prep-tool edits remain uncommitted and outside this task.

## Next Actions

1. Review the institutional-evidence suite committed for the authorized origin push.
2. Before empirical expansion, arrange genuine source review and define selection
   criteria/denominators. Keep the synthetic correction exercise separate.
3. Resolve the existing prep-tool failures separately; do not mix that work into
   this example-only change.

## Known Issues

- **`demo-*.kpack` output at repo root.** Now ignored by commit `2d331cf`;
  output-location cleanup remains optional. Historical cause:
  `reference/python/okpf/demo.py:74` writes output to `Path.cwd()`
  instead of the caller-controlled temp dir it already creates. The July
  count of untracked output files is historical; generated packs are now ignored.
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

- `examples/institutional-evidence-npm/`: manifest, narratives, comparison,
  selection note, records, provenance index, and evaluation questions.
- `docs/institutional-evidence-packs.md`, `README.md`, `docs/examples.md`.
- `tests/test_institutional_evidence_example.py` and project resume notes.

Core schemas, runtime/export code, and incoming prep-tool changes are untouched.

## Testing / Verification

2026-11-08, institutional-evidence suite:

- `python3 -m pytest -q tests/test_institutional_evidence_example.py
  tests/test_export.py tests/test_local_history_example.py tests/test_pack_archive.py`
  — **74 passed**. Includes directory/archive validity, existing-schema checks,
  both export forms, evidence/qualification links, alternate assessments,
  synthetic supersession, and evaluation reference integrity.
- Standalone validator: **VALID**, 16 records. CLI `export-rag` and
  `export-citations`: 16 rows each, written under `/tmp` for inspection.
- `git diff --check` passes. No consumer evaluation or predictive test was run.

Earlier profile task: 71 focused checks passed. Its broad suite run had
381 passed and seven failures in incoming prep work (CLI prepare, two prompt
wording checks, four mock-runner checks). That full suite was not repeated for
this example/documentation-only task.

## Notes For Next Session

The user authorized committing and pushing the evidence suite to origin. Provisional conventions
remain example-scoped; the earlier strict institutional profile does not govern
these new records. Consumers must retain/resolve provenance; source URLs require
external access and rubric fixtures are not measured results.
