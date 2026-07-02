<!-- SPDX-License-Identifier: Apache-2.0 -->

# RAG export contract (`okpf.rag_export.v0.1`)

`okpf export-rag` and `okpf export-citations` turn an OKPF pack into a
predictable JSONL stream. This is a **stable contract**, not a convenience
command: field names, types, and the chunking rule below will not change
within `okpf.rag_export.v0.1`. A future breaking change would ship as
`okpf.rag_export.v0.2` with the old version still supported for a
deprecation window.

```bash
PYTHONPATH=reference/python python3 -m okpf export-rag examples/software-onboarding out/rag.jsonl
PYTHONPATH=reference/python python3 -m okpf export-citations examples/software-onboarding out/citations.jsonl
```

Both commands accept a pack directory or a `.kpack` file.

## Not to be confused with `okpf compare-layout`

`okpf compare-layout` (see [docs/benchmark-plan.md](benchmark-plan.md))
generates a deliberately **naive** `jsonl-only/records.jsonl` export — no
license, no provenance, no chunk IDs — because that's exactly the kind of
ad hoc export OKPF is meant to be compared *against* in benchmarks.
`export-rag`'s `rag.jsonl` is the opposite: the OKPF-native, fully
attributed output. Don't use `compare-layout`'s output as a RAG ingestion
source; it exists only for side-by-side comparison.

## Chunking rule

One rule, applied per pack:

- If the pack declares any `records`, **one row per record** (from every
  records file), using the record's own `id` and `text`. Records are
  treated as the authored, RAG-ready form of the pack's content.
- If the pack declares **no** records at all, **one row per text-ish
  artifact** (`type` of `text/markdown` or `text/plain`, or a
  `.md`/`.txt`/`.rst` path when `type` is absent), using the whole file as
  a single chunk. Non-text artifacts are skipped.

OKPF Core does not define a text-splitting/chunking algorithm — that's
squarely a RAG-pipeline concern, and inventing one here would just be a
different kind of guessing. If you want finer-grained RAG chunks than
"whole file," author `records` (see the `rag-source` template:
`okpf init --template rag-source`).

## Row schema

```json
{
  "schema_version": "okpf.rag_export.v0.1",
  "chunk_id": "string",
  "text": "string",
  "package_id": "string",
  "package_version": "string",
  "domain": "string",
  "artifact_path": "string",
  "artifact_role": "string|null",
  "record_id": "string|null",
  "source_path": "string|null",
  "license": {},
  "usage_policy": {},
  "provenance": {},
  "citation": "string",
  "sha256": "string"
}
```

| Field | Notes |
|-------|-------|
| `chunk_id` | Deterministic, identity-based, human-readable: `{package_id}:{file_path}:{record_id}` for record rows, `{package_id}:{file_path}` for whole-artifact rows. Stable across re-runs and across text edits — correct for upsert/dedup workflows. |
| `sha256` | Content hash of `text`. Changes when the text changes, even though `chunk_id` doesn't — use this to detect updates. |
| `artifact_path` | The records-file path or artifact path this row's content came from. |
| `artifact_role` | The matching `artifacts[]` entry's `role`, for whole-artifact rows only. `null` for record rows (the manifest schema has no `role` field on records entries). |
| `record_id` | The record's own `id`, for record rows only. `null` for whole-artifact rows. |
| `license` / `usage_policy` | The manifest's objects, verbatim. `{}` if the pack declares neither. **Check `usage_policy.allow_rag` before ingesting.** |
| `provenance` | Best-effort per-row match — see below. |
| `source_path` | The matched provenance entry's own `path`, when a per-row match was found; otherwise `null`. |
| `citation` | Constructed (not stored): pack name/version, the artifact or record title if present, joined creator names, and the license type. Degrades gracefully when fields are missing. |

## Provenance matching (scoped, not a full graph resolver)

Existing OKPF packs use genuinely different provenance shapes — for
example `{"$ref": "provenance.json"}` pointing at a `sources[]`/
`transformations[]` object keyed by source **id**, versus
`{"sources": "provenance/sources.json"}` pointing at a flat array keyed by
file **path**. Building a universal provenance-graph resolver is out of
scope for `okpf.rag_export.v0.1`. The actual rule:

1. Resolve the manifest's `provenance` field one level (follow a `$ref` or
   a named pointer to a sibling file, if present).
2. If the resolved value is, or contains, a list of objects with a `path`
   key, look for an entry whose `path` equals this row's `artifact_path`.
   If found, that single entry becomes the row's `provenance` and
   `source_path`.
3. Otherwise, if *any* provenance was resolved, embed the whole resolved
   object on the row — still satisfies "provenance travels with every
   row," without pretending to have solved exact per-chunk attribution.
4. If the pack declares no provenance at all, `provenance` is `{}`.

## Relationship to benchmarking

[docs/benchmark-plan.md](benchmark-plan.md) Q3 ("Does OKPF reduce ingestion
ambiguity?") and Q4 (hallucinated-source-citation rate) are exactly what
this contract is meant to serve: before `export-rag` existed, a RAG loader
had no documented field set to rely on at all. A future `okpf benchmark`
command can diff `export-rag`'s output against `compare-layout`'s naive
`jsonl-only/` baseline to make that comparison concrete.

## See also

- [docs/rag-integrations.md](rag-integrations.md) — short loader snippets for LangChain, LlamaIndex, a generic vector store, and plain JSONL.
- [docs/records.md](records.md) — the record shapes `export-rag` reads.
- [docs/five-minutes.md](five-minutes.md) — end-to-end walkthrough including `export-rag`.
