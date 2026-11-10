<!-- SPDX-License-Identifier: Apache-2.0 -->

# Authorized full restart — 10 November 2026

Status: pilot and all 28 main requests complete. See [completion](completion.md).
See `launch.json` and `main-console.log`; `main.jsonl` contains saved responses.
Both pilot inputs used 2,542 tokens; one response reached the output cap.
Final freeze records no post-pilot changes. Assessment remains pending. The user selected a separate full run following
power loss. The original partial run remains in `../ordering-run-2026-11-09/`.

`restart-authorization.json` documents this explicit recovery decision. All
original frozen inputs, scripts and protocol are byte-identical. The new freeze
includes the restart receipt. Repeat the two-request pilot, freeze main, then
execute all 28 requests with unchanged settings. Do not pool with the old run.
AI assessment remains unreviewed; no independent human review is credited.

## Execution and resume notes

Use the copied runner and this directory for every command. Pilot seed is 17;
main seeds are 42/43, with the original counterbalanced schedule. The runner
checks every frozen hash before each request and refuses to overwrite output.
Do not rerun an existing phase or retry an interrupted request. Record any
interruption and select a recovery explicitly, retaining measured files.

After pilot completes, run `freeze-main` to check both responses and their
reported context fit. Only then run `main`. After all 28 responses are recorded,
run `blind` with the copied runner and use
`tools/institutional_ordering_analyze.py --run` with this directory. Initial
answer assessment uses `blinded-answers.json` and `assessment-context.json`;
keep the separate key hidden until judgments are saved. The frozen protocol
requires exact answer excerpts and per-item judgments, not automatic grading.

The original interrupted run is not pooled with or replaced by this restart.
All original inputs and settings match; runtime nondeterminism can still change
answers. Tests for fixed-content ordering, hash verification and overwrite
protection passed (3 tests). No product code, schemas or Core requirements change.

The process runs outside the sandbox. Check its PID outside the sandbox; a
sandbox-only process lookup can falsely report that it has exited. Its continued
execution was verified outside the sandbox after launch. No second attempt ran.
