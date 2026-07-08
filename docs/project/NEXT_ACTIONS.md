<!-- SPDX-License-Identifier: Apache-2.0 -->

# Next Actions

Short, prioritized, and scoped to roughly one coding session each. See
[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) for the full context behind
each item.

## Now

1. **Commit the encrypted-artifacts example and how-to guide.** The
   working tree already has a complete, passing `selective-disclosure-encrypted-source`
   example pack, `docs/how-to/encrypted-artifacts.md`, README/`docs/examples.md`
   links, and a new test (`tests/test_okpf_validate.py::test_selective_disclosure_encrypted_source_example_validates`).
   `pytest -q` passes (283 passed). Nothing further to build here —
   just review the diff and commit it.
   > Next step: `git diff --stat` the four touched files, confirm the
   > diff is what's described in `IMPLEMENTATION_LOG.md`, then commit.

2. **Track down the `demo-*.kpack` file leak.** Over 100 untracked
   `.kpack` files are accumulating at the repo root. Find where
   `okpf demo` (or another CLI path) decides its output location in
   `reference/python/okpf/cli.py`, and either default it to `out/`
   (already gitignored) or add a scoped `.gitignore` entry if root output
   is intentional.
   > Next step: `grep -rn "\.kpack" reference/python/okpf/cli.py` to find
   > the demo command's output path, then decide default vs. gitignore.

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
