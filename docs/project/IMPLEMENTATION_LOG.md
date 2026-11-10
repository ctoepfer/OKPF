<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

## Completed generation and authorized publication

Main generation completed: 28/28 responses retained, no request errors. Output-cap counts: O0 8/14; O1 7/14. All frozen hashes, request identities, paired content and context-fit checks pass. These are descriptive metrics, not answer-quality judgments. Masked answers and common assessment contexts are prepared; rubric assessment and independent human review remain pending. The interrupted original run remains separate. Verification before publication: 77 focused reference/experiment tests and 57 installed MCP tests passed; MCP lint, formatting and strict typing passed. Seven previously recorded prep-tool failures remain outside this change. User authorized commit and push after generation; earlier local-only notes are historical.


2026-11-10 publication authorized: the user requests commit and push to origin
after the background run finishes. This supersedes previous local-only notes.
A guarded completion task will verify all 28 responses, frozen hashes and tests
before committing the reviewed changes; unexpected edits or failures stop it.
Answer-quality assessment and independent human review remain pending.

2026-11-10 restart authorized: user selected a separate full run under the same
settings. New directory: `docs/experiments/institutional-consumer/ordering-run-2026-11-10-restart/`.
Original partial run preserved. New pilot completed (2/2); final freeze saved.
Separate 28-request main run launched in the background; see `launch.json`,
`main-console.log`, `main.jsonl` and `main-pending-request.json` in the new directory.
No main-run results or answer-quality assessment are final yet.
Runtime 0.18.0 and pinned phi3.5 digest verified. Execution is now authorized;
this supersedes the recovery-choice-pending notes below. Keep changes local.




2026-11-10 recovery: the authorized ordering experiment was interrupted by a
reported power outage after 2 pilot and 3/28 main responses. Request index 3
is pending without a saved response. All frozen input hashes verify unchanged;
3 ordering tests pass. Preserve the partial run. The user subsequently chose a separate full run; see the restart entry above. See
`docs/experiments/institutional-consumer/ordering-run-2026-11-09/recovery-2026-11-10.md`.
This supersedes older statements below that experiment execution is unauthorized
or has not begun. Keep changes local and preserve pending_dual_review.


2026-11-09 ordering experiment in progress: the latest user authorizes a local
pilot and repeated main run, superseding the prior no-inference restriction.
V1 changes presentation order only, freezing identical evidence content; v0 is
retained separately. New runner is outside product code. Snapshot, input hashes,
protocol and scripts are frozen under
`docs/experiments/institutional-consumer/ordering-run-2026-11-09/`.
Pilot uses the longest context, seed 17; main uses seeds 42/43 (28 requests).
Model/runtime identity verified locally. No independent human review credited.
Preserve prior uncommitted source-review/MCP fixes and pending_dual_review.

2026-11-09 review of `724e677`: latest user instruction keeps this review local
and uncommitted, superseding the previous push authorization for new work.
All six primary-source pages were accessible. Five case drafts retain
`pending_dual_review`; this AI-assisted review adds no independent human coding.
See `docs/reviews/institutional-724e677.md` and the unexecuted ordering proposal.


2026-11-09 publication authorization: the user requested pushing **all changes**
to origin, superseding earlier local-only restrictions. This includes the existing
prep-tool/table-extraction changes and tests as well as the institutional drafts,
MCP consumer, semantic draft and consumer audit. Full root suite: 450 passed and
seven known prep-tool failures; these failures are retained and disclosed.
Generated ignored `out/` artifacts are not source changes and remain local.

2026-11-09 consumer audit: the renewed attachment requests the already-completed
institutional evidence consumer experiment. Reproduced its fresh CLI export,
all fourteen generation inputs and post-hoc coverage; added replay and rubric
excerpt traceability tests (76 relevant checks passed). Retained the original
`phi3.5:latest` measurements without new inference or rewriting outputs. See
`docs/experiments/institutional-consumer/audit-2026-11-09.md`. Keep changes local.

2026-11-09 follow-up: five primary-source-cited FLOSS drafts, an optional MCP
review consumer, and a draft semantic commitment checker are complete locally.
The user selected sourced drafts pending independent dual review. No human coding
or reconciliation is claimed. Earlier MCP work was pushed as `9dfd0cd`; this
follow-up has not been committed or pushed. Preserve unrelated prep-tool edits.

This is the primary resume point for AI coding agents and humans picking
up this project. Read this before starting non-trivial work. Update it
after meaningful code or architecture changes — see the rule in
[`CLAUDE.md`](../../CLAUDE.md) / [`AGENTS.md`](../../AGENTS.md).

Last updated: 2026-11-10.

## Current Phase

Post-Core-freeze optional profile tooling and bounded consumer experiments.
Core requirements and export contracts remain unchanged.

## Current Goal

Recover the interrupted fixed-content ordering experiment transparently.
Preserve the original partial run and execute the documented separate full restart.

## Where We Left Off

Main generation completed: 28/28 responses retained, no request errors. Output-cap counts: O0 8/14; O1 7/14. All frozen hashes, request identities, paired content and context-fit checks pass. These are descriptive metrics, not answer-quality judgments. Masked answers and common assessment contexts are prepared; rubric assessment and independent human review remain pending. The interrupted original run remains separate. Verification before publication: 77 focused reference/experiment tests and 57 installed MCP tests passed; MCP lint, formatting and strict typing passed. Seven previously recorded prep-tool failures remain outside this change. User authorized commit and push after generation; earlier local-only notes are historical.

## Completed

- Source-grounded review of five drafts and raw consumer answers; narrow prose
  corrections, false-mismatch fix, and unexecuted experiment proposal.
- Five sourced pending-dual-review drafts, review ledger, hashed pack and source
  attribution; operational MCP consumer and optional semantic draft checker.
- 53 adapter/consumer tests and 187 focused reference regressions passed.
- Optional MCP adapter, bounded mount/query layer, 39 tests including real stdio,
  isolated distribution verification, docs and a separate optional CI job.

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
- A broad example-pack library including institutional evidence with export
  context checks; now exercised by a bounded actual consumer experiment.
- Experimental compatible institutional review command and optional detached
  signing interoperability tests (local follow-up).
- Selective-disclosure / encrypted-artifacts extension metadata, schema
  fields, spec text, and docs (commits `a9305ec`, `3db4cd9`).
- This resume system (`docs/project/`, plus the `CLAUDE.md`/`AGENTS.md`
  rule pointing to it).

Full history: `git log --oneline`.

## In Progress

Masked rubric assessment and independent human review remain pending.
Generation is complete.

## Next Actions

1. Confirm publication status in `out/ordering-publication/status.json` and origin.
2. Assess masked answers against the frozen rubric before opening the key.
3. Keep human review pending and preserve the interrupted run separately.

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

- Ordering-run README and recovery note; four project continuity files.

- `docs/reviews/institutional-724e677.md`.
- `docs/experiments/institutional-consumer/ordering-proposal.md`, audit and results addenda.
- Five FLOSS case YAML files and manifest artifact hashes.
- MCP `operational_review.py` and its four unknown-value regression cases.
- Project continuity files. Core, schemas, semantic checker and raw measurements unchanged.

## Testing / Verification

2026-11-10 recovery: original and restart frozen hashes intact; ordering tests
3 passed; diff whitespace check passed. Fresh pilot completed and context checks
passed. Runtime 0.18.0 and pinned phi3.5 digest match; main request 0 persisted.

2026-11-09 review:

- Four new unknown-value regressions failed against committed comparison behavior;
  all pass after the narrow fix.
- Focused reference/consumer/export/profile/schema checks: 78 passed.
- Full root suite: 450 passed, seven failures, exactly the prior prep failures:
  CLI prepare, two bounded prompt checks, mock-runner validation, prose/table
  records and callback-exception checks. No new root-suite failures.
- MCP adapter suite: 57 passed, installed updated local wheel, including guarded
  real stdio tests outside the sandbox (sandbox transport stalls).
- Ruff check/format and strict mypy passed. Both institutional packs validate;
  corrected FLOSS archive/hash contracts covered by focused tests.
- No inference, retrieval ordering change, commit or push performed.

## Notes For Next Session

Read the restart README and inspect the background run before taking action. Do not treat this
AI-assisted review as either independent human coding pass. Keep pending_dual_review,
zero completed independent codings and release_ready false. Preserve the original
consumer measurement; amendments are explicit addenda, not overwritten answers.
