<!-- SPDX-License-Identifier: Apache-2.0 -->

# Fixed-content ordering run (prepared 9 November, main begun 10 November 2026)

Status: interrupted by a reported power outage; 3 of 28 main responses saved.
See [recovery notes](recovery-2026-11-10.md). Recovery choice pending; no results
or recommendation finalized yet.
AI-authored protocol and forthcoming assessment; no independent human review.
This is a presentation-order experiment, not a test of changed evidence admission.

## Artifacts

- `snapshot/`: frozen original evidence pack, CC-BY-4.0, attribution retained.
- `export.jsonl`: actual reference CLI export, including repeated provenance index.
- `inputs.json`: fourteen prompts, selected contexts, identical-content pair audits,
  preflight bounds and ordering scores. Expectations are absent from generation.
- `protocol.md`, scripts, `freeze.json`: pre-pilot protocol/code/input hashes.
- `pilot.jsonl`, `pilot-environment.json`: two pilot requests and raw responses.
- `final-freeze.json`: pilot hash and main freeze, no post-pilot changes.
- `main.jsonl`, `main-environment.json`: raw main requests/responses, identity,
  timings, token counts and finish reasons. JSONL writes flush after each request.
- While executing, `main-pending-request.json` records the current request before
  inference; this file is removed after normal completion, not used for retries.

Pilot: both requests completed; reported input length was 2,542 tokens. O0 used
619 output tokens and stopped; O1 reached 768 and was truncated. Both fit the
16,384-token context. No quality-driven adjustments were made. Main uses the
same 768-token cap and two seeds, 42/43. Original baseline run remains untouched.

## Exact reproduction commands

From repository root, use a **new** output directory; measured files are never
overwritten. These commands perform local inference and require the pinned
already-installed model and runtime described in `protocol.md`.

```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/institutional-evidence-npm
PYTHONPATH=reference/python python3 -m okpf export-rag \
  examples/institutional-evidence-npm /tmp/ordering-export.jsonl
python3 tools/institutional_ordering.py prepare \
  --export /tmp/ordering-export.jsonl --out /tmp/okpf-ordering-replay
python3 /tmp/okpf-ordering-replay/institutional_ordering.py pilot \
  --out /tmp/okpf-ordering-replay
python3 /tmp/okpf-ordering-replay/institutional_ordering.py freeze-main \
  --out /tmp/okpf-ordering-replay
python3 /tmp/okpf-ordering-replay/institutional_ordering.py main \
  --out /tmp/okpf-ordering-replay
python3 /tmp/okpf-ordering-replay/institutional_ordering.py blind \
  --out /tmp/okpf-ordering-replay
python3 tools/institutional_ordering_analyze.py --run /tmp/okpf-ordering-replay
```

For the retained run the `--out` path was
`docs/experiments/institutional-consumer/ordering-run-2026-11-09` in every command.
Its copied scripts were used for pilot and main. The run directory retains its
preparation date even though execution spans client-calendar dates. Exact UTC
timestamps are in the raw files. Local loopback access required sandbox escalation;
no external provider, download or paid usage was used.

The prepare command checks the original export hash. A byte-identical source
snapshot and script copies are retained for later inspection; current repository
changes must not silently replace frozen files. New runs get new timestamped
receipts. Even pinned seeds/model/runtime do not guarantee identical answers.
