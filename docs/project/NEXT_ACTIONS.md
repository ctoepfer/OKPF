<!-- SPDX-License-Identifier: Apache-2.0 -->

# Next Actions

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

2026-11-09: sourced drafts and optional consumers are complete locally. The
previous MCP adapter was pushed as `9dfd0cd`; the current follow-up is uncommitted.

## Now

1. Review `docs/reviews/institutional-724e677.md` and the local corrections without
   promoting pending drafts. Two independent human coding passes remain required.
2. Complete the user-authorized separate ordering restart under the frozen v1
   protocol; preserve the original interrupted run and assess the new run separately.
3. Keep new changes local and uncommitted. Prior push authorization applied to 724e677.
4. Resolve seven known prep-tool failures in a separately scoped pass.

## Soon

3. **Reconcile `ai-manifest.md` vs. `AI_MANIFEST.md`.** Two files at the
   repo root cover similar ground with different content and only one has
   an SPDX header. Pick one as canonical (the more recently touched
   `AI_MANIFEST.md` is the likely candidate), fold in anything
   irreplaceable from the other, and remove the loser.
   > Next step: diff the two files side by side, confirm nothing in
   > `ai-manifest.md` is referenced elsewhere (`grep -rn "ai-manifest.md"`),
   > then remove it and update any links.

4. **Refresh or retire `PROJECT_STATUS.md`.** It's dated 2026-05-27 and
   predates both the Core freeze declaration and the encrypted-artifacts
   extension. Either regenerate it from current repo state or replace its
   body with a short pointer to `docs/project/CURRENT_STATUS.md` and
   `docs/project/IMPLEMENTATION_LOG.md`.
   > Next step: decide (with the user) whether `PROJECT_STATUS.md` stays
   > as a periodic human-written snapshot or becomes a redirect stub.

5. **Decide the fate of `HANDOFF.md`.** It's an unfilled template that
   now overlaps with `docs/project/IMPLEMENTATION_LOG.md`'s "Where We Left
   Off" section.
   > Next step: either delete it in favor of the log, or repurpose it as a
   > per-session scratch file that gets folded into the log at session end.

## Later (from ROADMAP.md, not yet scheduled)

6. **JS/TS SDK parity work** — bring `reference/javascript/src/` from
   stub to `Pack.load()`/`validate()` parity with the Python reference,
   per [ROADMAP.md](../../ROADMAP.md) Milestone 1. No `.kpack`, `ajv`, or
   builder support expected in this pass.
7. **Reconcile `ROADMAP.md` / `tools/README.md` "planned" language** with
   commands that are already implemented (`pack`/`unpack` are done but
   some docs still list them as future work) — flagged in
   `PROJECT_STATUS.md`'s existing "Recommended Next Development Steps."
