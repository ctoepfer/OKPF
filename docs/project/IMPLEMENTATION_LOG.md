<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

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

Last updated: 2026-11-09.

## Current Phase

Post-Core-freeze optional profile tooling and bounded consumer experiments.
Core requirements and export contracts remain unchanged.

## Current Goal

Audit the existing institutional evidence consumer experiment against the renewed
request, preserving the original run and all unrelated local work. Audit complete;
independent human review and a separately specified follow-up experiment remain
future work.

## Where We Left Off

The original consumer experiment already meets the renewed attachment's scope.
The new audit documents requirement coverage and adds two regression tests:
actual export/preparation replay and complete rubric/excerpt traceability. All
fourteen prompts and contexts match; four text-only audit lists differ only in
previously documented event order. The original results remain AI-reviewed and
human-unreviewed. No new model run was performed in this audit.

Earlier local work, preserved:

`examples/floss-maintainer-succession/` contains Event-Stream, Heartbleed,
Log4j, Core-JS and urllib3 drafts with primary source URLs and locators. Manifest,
cases and review ledger use `pending_dual_review`, zero completed independent
reviews and `release_ready: false`. These are heterogeneous episodes, not five
succession failures. Hypothetical evasion and retrospective pre-mortem examples
are explicitly distinguished from historical evidence. No population denominator
or statistical baseline is claimed.

`out/floss-maintainer-succession.kpack` was built and strictly validated; it is a
local generated artifact. The optional installed `okpf-tool review` consumer uses
all five existing MCP tools, tentative prose resource hints and explicit invariant
comparisons. Raw incomplete proposals remain invalid. It preserves evidence
status and reports missing data, mismatches, evasion warnings and truncation.
`out/floss-maintainer-succession-review.json` is an installed CLI archive smoke
result. No new MCP endpoints or network/model calls were added.

`okpf-tool check-semantics` validates the optional draft extension and compares
against an explicit local baseline. Exact definition hashes and document changes
are detectable; authenticity, approval and semantic immunity are not provided.
The pack's synthetic baseline is demonstration data, not a trusted commitment.
The new schema is bundled in the reference distribution; Core schemas are unchanged.

Both distributions were rebuilt and installed from explicit local wheels in
`/tmp/okpf-mcp-venv`. Actual SDK subprocess tests required execution outside the
sandbox due to stdio stalls, retaining network guards. No client GUI was tested.
Incoming prep-tool changes and `tests/test_html_table_records.py` remain untouched.

## Completed

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

No implementation work remains for this follow-up. Independent human coding,
reconciliation and release approval remain pending; these cannot be replaced by
another automated pass. Existing unrelated prep-tool failures remain unresolved.

## Next Actions

1. Assign two independent human coding passes using the pack review ledger;
   preserve source locators, uncertainty and dissent before changing draft status.
2. Review optional operational and semantic draft contracts before promotion.
   Keep the baseline independently trusted if using comparison operationally.
3. Exercise desktop clients and CI Python 3.11/3.12 when available.
4. Resolve the seven pre-existing prep-tool failures separately.

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

- `tests/test_institutional_consumer.py`: CLI replay and judgment traceability.
- `docs/experiments/institutional-consumer/README.md` and `audit-2026-11-09.md`.

Previous follow-up files, preserved:

- `examples/floss-maintainer-succession/` and `tests/test_floss_reference_draft.py`.
- `packages/okpf-mcp/`: consumer CLI, semantic checks, tests, packaging and README.
- `schemas/extensions/semantic-invariants/draft-v0.1/` and its reference bundle;
  `reference/python/pyproject.toml` includes the new optional schema package data.
- `docs/operational-institutional-review.md`,
  `docs/extensions/semantic-invariants-draft.md`, `docs/mcp-setup.md` and project notes.

## Testing / Verification

Consumer audit: 76 tests passed across consumer, evidence-example, export,
institutional profile/review and schema-bundle checks; evidence pack validates.
Fresh export fingerprint, generation payloads and coverage match the retained run.
No new generation or behavioral assessment performed.

Previous follow-up verification:

2026-11-09, Linux Python 3.13.13, official MCP SDK 1.30.0:

- Adapter suite: **53 passed**, including installed stdio consumer and offline guards.
- Focused institutional/profile/archive/export/schema regressions: **187 passed**.
- Full root suite: **448 passed, 7 failed**. Same pre-existing prep failures:
  CLI prepare; two bounded prompt checks; mock-runner validation, prose records,
  table records and callback-exception checks.
- Ruff check/format and strict mypy passed (15 formatted files, 8 source modules).
- Reference and MCP wheels/sdists rebuilt under `/tmp/okpf-operational-dist` and
  installed together with `--no-index --no-deps --force-reinstall`.
- Installed pack command built 12 files; archive strict profile validation passed.
- Installed `okpf-tool review` against the archive passed from outside the checkout;
  installed semantic checker validated and matched the demonstration baseline.
- Generated output remains under ignored `out/`. No commit or push in this follow-up.

## Notes For Next Session

Start with the reference pack README and `review/dual-coding-status.json`, then
`docs/operational-institutional-review.md` and the semantic draft document. Do not
promote AI-authored source drafts to independently reviewed evidence. Preserve
both institutional layouts and the distinction between case profiles and Core
evidence records. Keep unrelated prep work separate.
