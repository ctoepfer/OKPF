<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

2026-11-08 publication update: the user explicitly authorized committing and
pushing the completed institutional review, consumer experiment, and proposal
linter to origin. This supersedes local-only restrictions below. Unrelated
prep-tool edits remain excluded. Verification: 207 focused tests passed; full
suite 446 passed with seven pre-existing prep-tool failures.

This is the primary resume point for AI coding agents and humans picking
up this project. Read this before starting non-trivial work. Update it
after meaningful code or architecture changes — see the rule in
[`CLAUDE.md`](../../CLAUDE.md) / [`AGENTS.md`](../../AGENTS.md).

Last updated: 2026-11-08.

## Current Phase

Post-Core-freeze optional profile tooling and bounded consumer experiments.
Core requirements and export contracts remain unchanged.

## Current Goal

Complete the compatible experimental review tooling, actual institutional
evidence consumer experiment, and proposal linter. All are complete locally. Do not push or publish.

## Where We Left Off

Three related follow-ups are implemented but uncommitted:

1. Compatible `review-v1` case layout in the existing institutional profile;
   experimental offline `okpf review`, bundled mismatch rules, an alternate
   serialization of the existing event-stream episode, synthetic proposal, and
   packaging/SSH Ed25519 signing tests. The user explicitly chose accepting both
   layouts and keeping review tooling experimental. Unknown historical fields
   remain unknown; this is not another empirical episode.
2. An actual consumer experiment on the unchanged 16-record institutional-evidence
   pack. `tools/institutional_consumer.py` ingests actual RAG export, retrieves
   without expectations, and compares text-only selection against bounded
   relationship expansion. `tools/institutional_consumer_generate.py` ran all
   fourteen prepared prompts on already-installed `phi3.5:latest` through the
   configured loopback Ollama service. No model installation, new provider,
   corpus expansion, Core change, or exporter change was made for this experiment.

3. Experimental `okpf lint-proposal --proposal FILE [--pack PACK] [--json]`
   validates structured evasion vectors and pre-mortem commitments in JSON,
   YAML or Markdown front matter. Metric mentions generate heuristic warnings;
   optional validated packs supply matching case vectors. Declared tombstones
   are excluded without claiming signature verification. New case fields are
   optional for existing layouts; the separate proposal lint contract requires
   them. No cohort registry, cryptographic revocation or scraping runtime added.

Exact inputs, context/audits, post-hoc coverage, raw answers, and AI-authored
unreviewed rubric judgments are under
`docs/experiments/institutional-consumer/run-2026-11-08/`. The report records
failures prominently: B supplied all expected record bodies for five of seven
questions, but dropped the trace question's action record and missed one
abstention qualification. Source/incident conflations and incomplete correction
tracing persisted. Seven of fourteen answers hit the output cap. Availability
is not faithful use, and no general effectiveness claim is justified.

The latest user instruction is local-only. Earlier pushes (`2d9f27e`, `c44488b`)
applied to earlier work, not these follow-ups. Incoming prep-tool edits and
`tests/test_html_table_records.py` were preserved unchanged.

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

No remaining implementation or model calls for these requests. Human review of
the AI-authored assessments is not claimed and remains future work. Incoming
prep-tool edits remain outside this task.

## Next Actions

1. Review the local diffs and experiment report; do not push or publish.
2. Arrange human review of source attributions and rubric judgments before
   making effectiveness claims.
3. If extending the experiment, test query-relevance ordering for nonmandatory
   related edges while retaining qualification/supersession priority and limits.
   Keep this failed trace example and first run as a baseline. An output-budget
   sensitivity run would be separate; it was not performed.
4. Resolve the seven existing prep-tool failures separately.

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

- `reference/python/okpf/proposal_lint.py`, CLI wiring, canonical/bundled
  `proposal_lint.json`, optional case fields, `tests/test_proposal_lint.py`,
  and proposal-linter documentation.

- `reference/python/okpf/review.py`, `mismatch_rules.json`, `cli.py`,
  `institutional.py`, package data configuration, and institutional schemas/copies.
- `examples/institutional/` alternate serialization and synthetic proposal;
  institutional profile tests/fixtures and `tests/test_institutional_review.py`.
- `tools/institutional_consumer.py`, `tools/institutional_consumer_generate.py`,
  `tests/test_institutional_consumer.py`.
- `docs/experiments/institutional-consumer/`, `docs/institutional-review.md`,
  institutional evidence/profile guidance, README, and project resume notes.

`examples/institutional-evidence-npm/`, Core schemas, exporter code, and incoming
prep-tool edits are unchanged by these follow-ups.

## Testing / Verification

2026-11-08 final verification:

- Focused review, consumer, export, archive, schema bundle, validator, and CLI
  tests: **207 passed**.
- Full suite: **446 passed, 7 failed**. The same incoming prep failures remain:
  CLI prepare; two prompt-builder bounded-instruction checks; mock-runner
  validation, prose records, table records, and callback-exception checks.
- Both institutional packs validate: 16 Core records in the evidence pack and
  two representations of one case in the opt-in profile pack.
- Directory/archive review equivalence and Ed25519 sign/verify/tamper rejection
  passed; signing uses an ephemeral test key and external OpenSSH.
- Reference wheel built offline with review module, mismatch rules, and schemas.
- Fourteen actual generation calls completed using `phi3.5:latest`, temperature
  0, seed 42, context window 4096, output cap 384. Seven were output-truncated;
  no transport errors. Model digest/service version/raw responses are retained.
- All generation prompts and initial retrieval results reproduced exactly.
  Text-only audit order was sorted for future reproducibility; audit contents
  and all model inputs stayed the same. Attribution metadata was added separately.
- `git diff --check` passes. Nothing committed or pushed in these follow-ups.

## Notes For Next Session

Start with `docs/experiments/institutional-consumer/run-2026-11-08/results.md`.
Keep the bounded consumer findings distinct from the experimental case-review
command. Neither provides causal or predictive validation. Preserve the earlier
profile's functionality and both layouts; new evidence authoring starts with
provisional examples. Do not treat the previous push authorization as permission
to publish the current local work.
