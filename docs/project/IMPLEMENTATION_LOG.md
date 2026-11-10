<!-- SPDX-License-Identifier: Apache-2.0 -->

# Implementation Log

2026-11-09 publication update: the user explicitly authorized committing and
pushing the completed MCP adapter, documentation, CI and project notes to origin.
This supersedes the local-only restrictions recorded below. Unrelated prep-tool
edits remain excluded. Verification: 39 adapter tests and 185 regression tests
passed; the existing full suite has 446 passes and seven pre-existing failures.

2026-11-09: the optional `okpf-mcp` adapter is implemented and verified locally.
Do not commit, publish or push this follow-up. Prior institutional work was
committed and pushed as `1189b2e`; unrelated prep-tool edits remain excluded.

This is the primary resume point for AI coding agents and humans picking
up this project. Read this before starting non-trivial work. Update it
after meaningful code or architecture changes — see the rule in
[`CLAUDE.md`](../../CLAUDE.md) / [`AGENTS.md`](../../AGENTS.md).

Last updated: 2026-11-09.

## Current Phase

Post-Core-freeze optional profile tooling and bounded consumer experiments.
Core requirements and export contracts remain unchanged.

## Current Goal

Complete the optional repository-maintained MCP stdio adapter. Implementation,
tests, distributions, client setup docs and verification are complete locally.
Core schemas and the reference package are unchanged.

## Where We Left Off

`packages/okpf-mcp/` provides the official SDK FastMCP server (`mcp>=1.30,<2`,
verified with 1.30.0) and five read-only tools. Install the local reference and
adapter distributions together; never let an unpublished `okpf` dependency be
resolved accidentally from a public registry. Schemas remain in the reference
wheel. Tools operate on validated bounded startup snapshots, using the reference
reader-validation hooks plus adapter guards for sizes, duplicate ZIP entries,
symlinks, structured parsing, and all declared per-file hashes.

Original and review-v1 institutional cases are supported only with the declared
profile and its actual validation contract. Provisional institutional evidence
Core records are catalog-only. Unknown layouts are not reinterpreted. Signature
verification, decryption, external lookups, reloads and recommendations are not
implemented. POSIX directory mounts use descriptor-relative no-follow reads;
other operating systems use `.kpack` archives. No client GUI was exercised.

Actual SDK client tests launch the installed executable outside the checkout,
including a child-process network-denial audit hook. Sandbox subprocess transport
stalled; these tests passed outside the sandbox with network guards retained.
Both wheel and sdist builds succeeded; installed modules and schemas resolve
inside `/tmp/okpf-mcp-venv`, not the checkout. See `docs/mcp-setup.md` for contracts,
installation, client configuration sources and Inspector instructions.

Earlier institutional review, proposal linting and the fourteen-answer consumer
experiment were pushed as `1189b2e`. Their raw inputs, outputs and qualified
assessments remain under `docs/experiments/institutional-consumer/`. No new model
runs or case evidence were added. The new MCP work is local-only per the latest
request. Incoming prep-tool edits and `tests/test_html_table_records.py` remain
untouched.

## Completed

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

No remaining implementation work for the MCP request. Human evidence review,
native Windows directory support, GUI testing and actual CI execution are not
claimed. Incoming prep-tool edits remain outside this task.

## Next Actions

1. Review the local MCP adapter changes; do not commit, publish or push.
2. Exercise actual client GUIs and CI Python 3.11/3.12 when available. This session
   tested Linux Python 3.13 and SDK 1.30.0; no GUI or Inspector process was run.
3. Retain bounded evidence/uncertainty semantics in future consumer work; do not
   conflate provisional Core evidence records with institutional case profiles.
4. Resolve seven existing prep-tool failures separately. Human review of the
   earlier experiment's attributions and judgments remains future work.

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

- `packages/okpf-mcp/`: packaging, snapshot/catalog/query/server modules and tests.
- `docs/mcp-setup.md`, `docs/agent-rules.md`, README discovery link.
- `.github/workflows/ci.yml`: separate optional MCP test/build/lint job.
- Project resume/status/decision notes. No Core, schema, reference package,
  example-pack, exporter or unrelated prep-tool edits in this follow-up.

## Testing / Verification

2026-11-09, Python 3.13.13, official SDK 1.30.0:

- `/tmp/okpf-mcp-venv/bin/python -m pytest -q packages/okpf-mcp/tests`:
  **39 passed**, including all five actual stdio tool calls and offline guards.
  This command required execution outside the sandbox because subprocess stdio
  stalled inside it; network denial remained active in tests and the audited child.
- `python3 -m pytest -q tests/test_institutional_profile.py
  tests/test_institutional_review.py tests/test_proposal_lint.py
  tests/test_schema_bundle_in_sync.py tests/test_okpf_validate.py
  tests/test_pack_archive.py tests/test_export.py
  tests/test_institutional_evidence_example.py`: **185 passed**.
- `python3 -m pytest -q --tb=no`: **446 passed, 7 failed**, the same incoming
  prep failures: CLI prepare; two bounded prompt checks; mock-runner validation,
  prose records, table records and callback-exception checks.
- `/tmp/okpf-mcp-venv/bin/ruff check packages/okpf-mcp`, `ruff format --check
  packages/okpf-mcp`, and `mypy --config-file packages/okpf-mcp/pyproject.toml
  packages/okpf-mcp/src`: passed. `pip check`: no broken requirements.
- `/tmp/okpf-mcp-venv/bin/python -m build --no-isolation --outdir
  /tmp/okpf-mcp-dist ./reference/python` and the same for `./packages/okpf-mcp`:
  wheels and sdists built. Installed both explicit wheels with `pip install
  --no-index --no-deps --force-reinstall`; dependencies were previously installed
  in the fresh isolated venv. Build backend emitted existing-style license-table
  deprecation warnings; builds succeeded.
- Installed console executable tested with working directory outside the checkout;
  bundled schema imports verified. No PYTHONPATH or sys.path modifications.
- Current Claude Desktop/Cursor/Inspector setup conventions checked against
  official documentation and linked in setup docs; GUIs/Inspector not run.
- `git diff --check` passes. No commit, push or publication in this follow-up.

## Notes For Next Session

Read `docs/mcp-setup.md` and the package tests first. Maintain separation between
case-profile tools and provisional Core evidence records. Directory mounts require
POSIX; archives are the portable path. Signature status is not hash status or
signer trust. Preserve unrelated prep-tool work, and do not publish this adapter
without a new instruction.
