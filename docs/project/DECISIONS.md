<!-- SPDX-License-Identifier: Apache-2.0 -->

# Decisions

2026-11-10 evaluation/design preparation: no scoring or condition-quality
comparison performed. The user's requested three-arm study and four criteria
differ from the completed two-order study's frozen protocol. Scope selection
and independent reviewer identity/contact are pending. A neutral, unscored
28-answer packet with completion lengths, exact frozen criteria, empty worksheets
and per-file hashes is prepared under `out/institutional-review-packet-2026-11-10`.
Published keys prevent any guarantee of access-isolated blinding; prior exposure
must be disclosed. See `docs/experiments/institutional-consumer/review-preparation-2026-11-10/`.
Seven prep-tool failures have a separate `docs/project/PREP_TOOL_DEBT.md` record.
The user explicitly selected documentation-only compatible designs for the
RAG/boundary-transition proposals, with the frozen evaluation unchanged.
Implementation is outside this pass. Existing `okpf.semantic_retrieval.v0` overlaps
the proposed RAG namespace. Core, schemas, raw outputs and frozen rubric unchanged.


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


2026-11-09 publication authorization: the user requested pushing **all changes**
to origin, superseding earlier local-only restrictions. This includes the existing
prep-tool/table-extraction changes and tests as well as the institutional drafts,
MCP consumer, semantic draft and consumer audit. Full root suite: 450 passed and
seven known prep-tool failures; these failures are retained and disclosed.
Generated ignored `out/` artifacts are not source changes and remain local.

2026-11-09 publication update: the user explicitly authorized committing and
pushing the completed MCP adapter, documentation, CI and project notes to origin.
This supersedes the local-only restrictions recorded below. Unrelated prep-tool
edits remain excluded. Verification: 39 adapter tests and 185 regression tests
passed; the existing full suite has 446 passes and seven pre-existing failures.

2026-11-08 publication update: the user explicitly authorized committing and
pushing the completed institutional review, consumer experiment, and proposal
linter to origin. This supersedes local-only restrictions below. Unrelated
prep-tool edits remain excluded. Verification: 207 focused tests passed; full
suite 446 passed with seven pre-existing prep-tool failures.

This file tracks **project-process** decisions: how the project is run,
organized, and kept resumable. It intentionally does not duplicate
[docs/adr/](../adr/), which holds formal architecture decision records for
spec- and schema-level design choices (ZIP-based `.kpack` archives,
optional blockchain, license/usage_policy separation, JSON Schema
validation, simple-core-optional-power). Check `docs/adr/` first for
"why does the format work this way" questions; use this file for "why is
the project organized this way" questions.

## 2026-07-07 — Adopt a `docs/project/` resume system

**Decision:** Add `docs/project/IMPLEMENTATION_LOG.md`,
`CURRENT_STATUS.md`, `GOALS.md`, `NEXT_ACTIONS.md`, and this file as the
canonical way for AI coding agents (and humans) to resume work across
sessions, and require `CLAUDE.md`/`AGENTS.md` to point agents at
`IMPLEMENTATION_LOG.md` before non-trivial implementation work.

**Reasoning:** The repo already had partial, overlapping mechanisms —
`PROJECT_STATUS.md` (a point-in-time snapshot, last refreshed 2026-05-27),
`HANDOFF.md` (an unfilled session-handoff template), and `ROADMAP.md` (a
long-lived milestone roadmap, not a session-resume tool). None of them was
being kept current, and none was referenced from `CLAUDE.md`/`AGENTS.md`
as something agents must read first. This mirrors the exact
"documentation drift" risk `PROJECT_STATUS.md` itself already flagged
under "Open Questions, Risks, And Pending Decisions."

**Consequences:**

- `docs/project/IMPLEMENTATION_LOG.md` becomes the source of truth for
  "where did we leave off," ahead of chat history or memory.
- `PROJECT_STATUS.md` and `HANDOFF.md` at the repo root now overlap with
  the new system and have not yet been reconciled — tracked in
  [NEXT_ACTIONS.md](NEXT_ACTIONS.md) items 4–5. They were left in place
  rather than deleted, since removing them wasn't requested and they may
  still hold useful history.
- Formal spec/schema decisions stay in `docs/adr/`; this file stays
  scoped to process so it doesn't become a second, competing ADR log.

## 2026-11-08 — Scope institutional work to the profile scaffold

Implement the requested schemas, Python validator integration, sourced seed,
fixtures, and documentation. Treat the attachment's diagnostic runtime and
larger corpus as future work. Preserve the pre-existing prep-tool edits and
report their failing tests separately. Profile semantics live in
[`docs/profiles/institutional-v1.md`](../profiles/institutional-v1.md); no Core
schema change or new Core requirement was introduced.

## 2026-11-08 — Keep institutional evidence example-driven and local

The new request supersedes the earlier runtime-oriented direction for this task:
use two bounded source-grounded examples and provisional conventions; create no
new institutional-case profile. Keep the prior opt-in scaffold separate. Preserve
export context through existing provenance fields and example tests rather than
changing the exporter. Label synthetic correction exercises and AI authorship
explicitly. No independent human review or evaluation results are claimed.

The user initially prohibited pushing or publishing this suite, then explicitly
authorized committing and pushing it to origin. The later authorization governs. See [institutional evidence conventions](../institutional-evidence-packs.md).

## 2026-11-08 — Preserve both layouts; measure one bounded consumer locally

The user explicitly selected accepting both institutional case layouts and
keeping review tooling experimental. The optional reviewer is separate from
Core and from the newer provisional evidence pack. No existing layout was
removed. New institutional evidence authoring starts with provisional examples;
reconciliation requires reviewed examples and consumer experience.

The subsequent attachment requested one actual consumer experiment without
corpus expansion. Use fixed lexical retrieval plus bounded relationship
expansion, keep expectations out of generation, and run both conditions on the
already-installed local `phi3.5:latest`. Retain exact prompts, contexts, raw
answers, and separate AI-authored judgments. No selective retry or post-hoc
retrieval tuning hides the observed failures. See the
[run report](../experiments/institutional-consumer/run-2026-11-08/results.md).

The latest instruction requires keeping these follow-ups local. Earlier push
authorizations applied only to prior commits; do not push or publish this work.

## 2026-11-08 — Experimental proposal lint contract

Use the existing Python CLI's `lint-proposal` subcommand and canonical
`case_record.json` naming. The attached required-field sketch is enforced by a
separate proposal schema, while case fields remain optional to honor the user's
accepted dual-layout compatibility decision. Present fields are validated in
both layouts. Metric mentions are heuristic hints; matched vectors are sourced
assertions, not independent precedent counts. A tombstone declaration causes
conservative exclusion, not verified cryptographic revocation. Cohort statistics,
ingestion and execution are outside this linter. All current work remains local.

## 2026-11-09 — Optional offline MCP consumer adapter

Keep `okpf-mcp` a separate distribution using official SDK FastMCP 1.x, with
explicit local reference-package installation. Reuse reference validation hooks
on bounded startup snapshots instead of changing Core or duplicating schemas.
Adapter-only guards enforce path, expansion, parsing and per-artifact hash bounds.
Use POSIX descriptor-relative directory reads; require `.kpack` on other OSes.

Institutional case tools require declared/validated profile membership. Original
and review-v1 data retain authored structure; provisional Core evidence remains
catalog-only. No signature verifier exists in runtime, so report unsupported or
not_checked accurately; do not confuse hash checks with trust. Tools are read-only,
exact-match, source-located and explicitly non-predictive. No cloud/LLM requests,
external dependency resolution, decryption, reloads or recommendations.

The user explicitly prohibited commits, pushes and publication for this MCP task.
Earlier institutional work was pushed as `1189b2e`; that authorization does not
apply to the adapter. Leave unrelated prep-tool changes alone.


## 2026-11-09 — Sourced drafts and optional consumers

The user selected sourced drafts for independent dual review. Use
`pending_dual_review`, empty independent coding records and `release_ready: false`;
never represent an AI drafting pass as independent reconciliation. Retain primary
source locators, unknown observations, hypothetical evasion labels and explicitly
retrospective pre-mortem examples. The five episodes are a purposive heterogeneous
sample, not a denominator or five verified succession failures.

Implement `okpf-tool review` in the optional MCP package using its existing five
read-only tools. Prose resource hints remain tentative, explicit proposal fields
supply asserted invariants, and missing values do not become matches. Keep
existing Core/reference review behavior compatible.

Semantic invariants are an optional draft extension, not required Core/profile
fields. Hashes check exact definition bytes; a separately trusted baseline is
needed to detect unapproved changes. No signature verification, operational test
execution or semantic immunity is claimed. The earlier MCP work was subsequently
published as `9dfd0cd`; this new follow-up remains uncommitted and unpushed.


## 2026-11-09 — Reproduce the existing consumer measurement

The renewed consumer-experiment attachment matches the existing implementation
and actual fourteen-answer run. Audit and retain that measurement rather than
replace it or conflate it with the newer FLOSS/MCP draft work. Fresh export replay
and rubric/excerpt integrity tests check traceability, not reviewer correctness.
No new inference, corpus expansion, Core/export change or publication is part of
this audit. Human review and a separately specified edge-ordering experiment
remain next steps.


## 2026-11-09 — Source review remains AI-assisted and local

The latest request supersedes push authorization for new review work. Inspect
primary sources and raw answers directly; qualify chronology/horizon labels and
retain source-reported versus analyst/proposed distinctions. Preserve all draft
and zero-human-coding flags. Correct only the reproduced unknown-value mismatch
bug; do not alter retrieval ordering, raw results or semantic trust claims.
Retain original AI judgments with an explicit narrower attribution addendum.
The new ordering proposal requires human approval and independent human scoring
before any effectiveness interpretation; it has not been executed.
