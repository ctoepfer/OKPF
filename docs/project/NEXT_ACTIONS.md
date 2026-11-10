<!-- SPDX-License-Identifier: Apache-2.0 -->

# Next Actions

2026-11-09 publication authorization: the user requested pushing **all changes**
to origin, superseding earlier local-only restrictions. This includes the existing
prep-tool/table-extraction changes and tests as well as the institutional drafts,
MCP consumer, semantic draft and consumer audit. Full root suite: 450 passed and
seven known prep-tool failures; these failures are retained and disclosed.
Generated ignored `out/` artifacts are not source changes and remain local.

2026-11-09: sourced drafts and optional consumers are complete locally. The
previous MCP adapter was pushed as `9dfd0cd`; the current follow-up is uncommitted.

## Now

- Consumer audit is complete. Review retained answers and AI assessments with a
  human reviewer; if continuing measurement, separately specify query-relevance
  ordering for nonmandatory related edges under unchanged initial retrieval and
  budgets. Preserve the original run; do not interpret coverage as answer quality.

1. Independently code and reconcile the five cases using
   `examples/floss-maintainer-succession/review/dual-coding-status.json`.
   Keep `pending_dual_review` until the documented promotion checks are satisfied.
2. Review the experimental operational consumer and semantic commitment draft.
   Use an independently trusted baseline for meaningful tamper detection;
   the included baseline is only a demonstration. GUI and CI matrix checks remain.
3. Resolve the seven existing prep-tool test failures in a separate pass,
   preserving and inspecting the incoming prep changes before changing behavior.

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
