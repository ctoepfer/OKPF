<!-- SPDX-License-Identifier: Apache-2.0 -->

# Next Actions

Short, prioritized, and scoped to roughly one coding session each. See
[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) for the full context behind
each item.

## Now

1. **Review the institutional-evidence suite.** See
   `docs/institutional-evidence-packs.md` and the implementation log. The user
   subsequently authorized committing and pushing it to origin. Keep it separate from incoming
   prep edits and the previously pushed institutional profile scaffold. Before
   corpus expansion, seek actual human source review and a defensible sampling
   frame; seven rubric fixtures are not measured model evaluations.
2. **Resolve prep-tool test failures in a separate pass.** Seven full-suite
   failures involve mock grounding, bounded prompt wording, and generated record
   expectations. Inspect the existing prep diff before deciding intended behavior.
   The encrypted-artifacts example/how-to is already tracked; generated demo
   packs are now ignored. Those July commit/cleanup instructions are superseded.

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
