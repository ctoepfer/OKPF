<!-- SPDX-License-Identifier: Apache-2.0 -->

# Current Status

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

2026-11-09: five FLOSS source drafts and a built reference archive are complete,
marked `pending_dual_review` (zero independent reviews). Optional MCP proposal
review and semantic draft checking are implemented locally. Verification: 53
adapter tests, 187 focused regressions; full root suite 448 passed with seven
pre-existing prep-tool failures. Earlier MCP adapter was pushed as `9dfd0cd`;
this follow-up is not committed or pushed.

This file is a snapshot, not a promise. When it and the code disagree,
trust the code and update this file.

## What Currently Works

- **724e677 source-grounded review** — all five cases and fourteen saved answers
  inspected; draft status preserved. Narrow evidence qualifications and MCP
  unknown-value comparison fixed; 57 adapter and 78 focused tests pass, full root
  450 pass/seven unchanged prep failures. No new inference or semantic code change.

- **Consumer reproduction audit** — `docs/experiments/institutional-consumer/audit-2026-11-09.md`:
  fresh export reproduces fourteen retained generation inputs and coverage;
  rubric excerpts resolve to raw answers. 76 relevant tests passed. Original
  `phi3.5:latest` run retained; no new inference or independent review claimed.

- **FLOSS reference drafts** — `examples/floss-maintainer-succession/`: five
  primary-source-cited cases, explicit uncertainty and independent review ledger.
  No dual coding, population hazard estimates or release readiness claimed.
- **Optional operational consumer** — `okpf-tool review` calls existing MCP tools
  for proposal linting, structural comparisons and qualified evasion warnings.
- **Semantic commitment draft** — `okpf-tool check-semantics` checks definitions,
  metric boundaries and local baseline changes; no signature or trust verification.

- **Optional MCP stdio adapter** — `packages/okpf-mcp/`, official SDK FastMCP,
  bounded offline snapshots and five read-only tools. Supports original/review-v1
  institutional cases; provisional Core evidence is catalog-only. Setup and
  limitations: `docs/mcp-setup.md`. Core unchanged; the reference package now bundles the optional semantic draft schema.

- **Experimental proposal linting** — `okpf lint-proposal` checks required evasion
  and pre-mortem blocks, reports heuristic metric mentions, and optionally
  cross-references validated directory/archive cases. Existing case layouts keep
  these fields optional. No execution, hazard estimation, signature verification
  or audit ingestion is implied. See `docs/institutional-review.md`.

- **Institutional follow-ups (pushed as `1189b2e`)** — compatible institutional
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
