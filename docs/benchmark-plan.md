<!-- SPDX-License-Identifier: Apache-2.0 -->

# OKPF Benchmark Plan — v0.1

This document defines how OKPF can be compared against simpler alternatives. Not every benchmark needs to be implemented immediately. The goal is to define the questions and methods so that comparisons can be run as the project matures.

---

## Alternatives Under Comparison

OKPF is compared against the following:

| Alternative | Description |
|-------------|-------------|
| **Plain Markdown folder** | A directory of `.md` files with no schema, no manifest, no explicit license |
| **Markdown + YAML front matter** | Markdown files with structured YAML headers (title, author, date, tags) |
| **JSONL records only** | A single `.jsonl` file of structured records with no surrounding package context |
| **RAG loader conventions** | The implicit schema used by LangChain, LlamaIndex, or similar frameworks when loading documents — typically just file content plus metadata dict |
| **Hugging Face dataset layout** | A directory with `dataset_info.json` and `train.jsonl` / `data/*.parquet`, structured for ML consumption |
| **RO-Crate / BagIt** | Archival packaging formats designed for research data with provenance and integrity metadata |

OKPF does not need to beat every alternative for every use case. It needs to be measurably better for at least a few workflows where provenance, validation, packaging, and reuse are important.

---

## Benchmark Questions

The following questions define what the benchmark is trying to answer. Each can be answered qualitatively (manual comparison) or quantitatively (automated measurement).

### Q1: Does OKPF preserve attribution better?

**Operationalization:** Count the number of records in each format that have a traceable author, organization, or contributor reference. Compare OKPF records (with `creators` in manifest and `metadata` in records) against alternatives.

**Success condition:** OKPF packs consistently carry attribution through the packaging layer that survives inspection without additional tooling.

---

### Q2: Does OKPF preserve source-to-record lineage better?

**Operationalization:** After ingesting a pack into a simulated RAG corpus, determine what percentage of records can be traced back to a specific source document, date, and transformation. Compare against plain folders and JSONL-only.

**Success condition:** OKPF provenance entries (`provenance/sources.json`) enable source tracing that is absent in plain alternatives.

---

### Q3: Does OKPF reduce ingestion ambiguity?

**Operationalization:** Count the number of loader decisions that require human judgment when ingesting each format. For example: What is the license? What is the domain? What records are present? What file format are records in?

**Success condition:** The OKPF manifest answers all standard ingestion questions without requiring the loader to guess or scan files.

---

### Q4: Does OKPF reduce hallucinated source claims?

**Operationalization:** Ask a RAG pipeline questions over an OKPF pack and over the equivalent plain folder. Count answers that cite a specific source vs. answers that fabricate a source. Compare rates.

**Success condition:** OKPF provenance metadata reduces hallucinated source citations by providing a structured ground truth the pipeline can reference.

**Note:** This benchmark requires a working RAG pipeline and an evaluation judge. It is not implementable with the current reference tooling alone. Marked for future work.

---

### Q5: Does OKPF improve retrieval accuracy?

**Operationalization:** For a fixed set of evaluation questions (from the `evals/` directories in example packs), compare the rate of correct answers retrieved from an OKPF-ingested corpus vs. a plain folder corpus.

**Success condition:** OKPF-structured records improve retrieval by providing cleaner domain signals (facets, record types) than unstructured Markdown.

**Note:** Requires a retrieval system and evaluation harness. Marked for future work.

---

### Q6: Does OKPF make versioned knowledge easier to audit?

**Operationalization:** Make a structured change to knowledge in each format. Count the number of lines in the diff that are meaningful (content changes) vs. noise (reformatting, metadata churn). Assess whether a non-technical reviewer can understand what changed.

**Success condition:** OKPF pack diffs (manifest version bump + specific record change) are more auditable than diff-over-directory for an equivalent change.

---

### Q7: Does OKPF make domain-specific validation easier?

**Operationalization:** Run the OKPF validator on each example pack. Run an equivalent check on a plain Markdown folder. Measure how many structural problems are caught before ingestion.

**Success condition:** The OKPF validator catches at least one class of ingestion problem (missing path, unsafe path, missing required field) that the plain-folder alternative would not catch.

**Current status:** This benchmark can be run today against the three Phase 2 example packs using `okpf_validate.py`.

---

### Q8: Does OKPF impose too much authoring overhead?

**Operationalization:** Time how long it takes to author an equivalent knowledge artifact in each format. Record the number of files, fields, and decisions required.

**Success condition:** OKPF authoring overhead is justified by the additional properties gained — if not, simplify the format.

**Current status:** Qualitative only. Needs user feedback from external adopters.

---

## Initial Test Corpora

All three Phase 2 example packs can serve as initial benchmark corpora. Each has an equivalent representation in the alternatives:

| OKPF pack | Plain Markdown equivalent |
|-----------|--------------------------|
| `examples/software-onboarding/` | Three `.md` files in a directory |
| `examples/local-organization-knowledge/` | Two `.md` files and one `.jsonl` file in a directory |
| `examples/field-repair-checklist/` | Three `.md` files and one `.jsonl` file in a directory |

The `okpf compare-layout` CLI command (see below) generates the plain-folder equivalent from an OKPF pack, making side-by-side comparison easier.

---

## Metrics

| Metric | How to measure | Automated today? |
|--------|---------------|-----------------|
| Pack validation pass/fail | `okpf_validate.py` | Yes |
| Number of source-backed records | Count records with non-empty `provenance` or `sources` entry | Partial |
| Number of unsupported answers | Requires RAG + eval judge | No |
| Retrieval precision/recall | Requires retrieval system | No |
| Citation/source trace completeness | Count records traceable to `provenance/sources.json` | Partial |
| Authoring time | Timed user study | No |
| Import time | `time okpf validate` | Yes (simple) |
| Schema error rate | Count validator errors per pack | Yes |
| Human review score | Structured reviewer rubric | No |

---

## What OKPF Must Beat

OKPF does not need to win every comparison. It needs to clearly win at least these:

1. **Attribution completeness vs. plain Markdown folder.** A plain `.md` file has no structured author field. OKPF manifests always have `creators` and records have `metadata`. This should be provably true.

2. **Path safety and integrity vs. zip-without-manifest.** A ZIP file with no manifest cannot tell a loader what it contains or whether files are safe to extract. OKPF adds that layer.

3. **Ingestion ambiguity vs. JSONL-only.** A bare JSONL file does not declare its license, domain, version, or source. An OKPF pack does. Any loader that needs to make decisions about rights, scope, or version benefits from the manifest.

4. **Auditable structure vs. opaque formats.** OKPF packs in a Git repo are fully diff-able. The manifest changes are visible. The records are inspectable. Compare against a Confluence page or an internal DB dump.

If OKPF cannot demonstrate superiority on these four points with real examples, the project should focus its scope.

---

## `okpf compare-layout` — Benchmark Helper

The `compare-layout` CLI command generates alternative layout exports from an OKPF pack directory. This makes it easier to run side-by-side comparisons.

```bash
PYTHONPATH=reference/python python3 -m okpf compare-layout examples/software-onboarding out/comparison/
```

Output structure:

```text
out/comparison/
  markdown-folder/       Text and Markdown artifacts, flat
  jsonl-only/            All records merged into a single JSONL file
  manifest-summary.json  Key manifest fields as a simple JSON summary
```

See [reference/python/okpf/cli.py](../reference/python/okpf/cli.py) for implementation.

---

## Future Work

The following benchmarks require tooling not yet in this repository:

- **Retrieval accuracy benchmark** — requires an embedding model and a vector retrieval system. Deliberately out of scope for OKPF Core.
- **RAG hallucination rate benchmark** — requires a RAG pipeline and an LLM judge. Out of scope.
- **User study for authoring overhead** — requires external participants.
- **Cross-tool interoperability test** — requires a second independent tool that reads OKPF packs.

These are the most important long-term benchmarks. Community contributions here are especially welcome. See `docs/adoption-strategy.md` for the broader adoption context.

---

## See Also

- [docs/adoption-strategy.md](adoption-strategy.md) — adoption thesis and success metrics
- [docs/when-not-to-use-okpf.md](when-not-to-use-okpf.md) — scope boundaries
- [docs/v0.1-conformance.md](v0.1-conformance.md) — conformance levels
