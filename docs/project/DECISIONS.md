<!-- SPDX-License-Identifier: Apache-2.0 -->

# Decisions

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
