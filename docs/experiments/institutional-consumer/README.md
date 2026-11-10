<!-- SPDX-License-Identifier: Apache-2.0 -->

# Institutional evidence consumer experiment

This bounded experiment asks whether one consumer can retrieve and use qualified
institutional evidence, disagreement, source attribution, and corrections from
the existing `examples/institutional-evidence-npm` pack. The implementation and
answer assessments are AI-authored and unreviewed. There is no independent human
gold standard. Neither structural validity nor availability of a relationship
proves that an answer preserves its epistemic limits.

## Setup and reproducibility

The plain-JSONL integration pattern in `docs/rag-integrations.md` is sufficient;
no vector database, new model installation, provider, or exporter change is
needed. The adapter lives outside Core at `tools/institutional_consumer.py`.
It consumes the actual `okpf.rag_export.v0.1` output of the unchanged exporter.

From the repository root:

```bash
PYTHONPATH=reference/python python3 -m okpf export-rag \
  examples/institutional-evidence-npm /tmp/institutional-rag.jsonl
python3 tools/institutional_consumer.py \
  --export /tmp/institutional-rag.jsonl \
  --evaluations examples/institutional-evidence-npm/evals/questions.json \
  --out /tmp/institutional-consumer-run
```

The preparation command produces exact prompts, admitted context, every expansion
attempt and reason, limit decisions, and post-hoc coverage. It does not generate
or grade answers. Expected answers/references are accessed only for the separate
coverage report after context construction; question IDs are labels, never
retrieval features. Only question text drives retrieval.

To run generation against an already-installed model on an already-authorized
loopback Ollama service:

```bash
python3 tools/institutional_consumer_generate.py \
  --inputs /tmp/institutional-consumer-run/inputs.json \
  --output /tmp/institutional-consumer-run/answers.json \
  --model phi3.5:latest
```

The generator uses the configured `OLLAMA_API_BASE`/`OLLAMA_HOST` (otherwise
localhost:11434), rejects non-loopback endpoints, checks that the named model is
installed, and never pulls a model. It refuses to overwrite an existing answer
file. There is no credential capture, payment setup, or external source fetch.
Network permissions may be needed to reach an existing local service. If it is
unavailable, retain the preparation artifacts and mark generation/behavioral
assessment not run; do not fabricate replacement answers.

## Fixed design

Initial retrieval uses length-normalized, inverse-document-frequency-weighted
word overlap over record body text, with a fixed general stopword list. No
question-specific mapping, stemming, synonym inference, expected answers,
expected references, rubric items, or provenance index text enters the lexical
index. Exact algorithm and fixed settings are in the source. There is no tuning
to the seven question IDs after seeing their outcomes.

Both conditions use the same two initial hits and identical question, system
instructions, model settings, and maximum serialized context budget:

- **A — text only:** IDs and body text of the selected records. Inline reference
  strings remain as authored, but no targets are automatically supplied.
- **B — relationships:** the same initial hits with their own annotations,
  then breadth-first expansion through qualifications, supersession/correction,
  related/contrary/supporting records, outcomes, and cited evidence metadata.

Limits are six admitted records, ten successful additions beyond initial
retrieval (citation objects count), depth two, and 9,000 Unicode characters for
the exact serialized evidence-context JSON. Complete items are admitted or
rejected; no silent text clipping occurs. Prompt instructions and question are
outside that evidence budget but identical between conditions. There is a
separate model output cap. Metadata overhead consumes B's budget; this and the
additional selected content are inherent differences between conditions.

A logs relationships deliberately not expanded. B logs admitted, repeated,
unresolved, and limit-rejected targets. Cycles terminate via visited targets.
A metadata-only reference does not count as a retrieved record: the body must
be present. Likewise, globally available evidence metadata is not counted as
selected unless its citation object is admitted. Full primary source bodies
are absent in both conditions, so citation coverage is not independent evidence
verification.

The repeated whole provenance index is available to the adapter, but never
wholesale placed in a generation prompt. Only annotations of admitted records
and explicitly admitted citation entries appear in B. The index's availability
and the actually supplied IDs are retained separately. Inline references may
still tempt a model to cite absent records: this is measured as a possible
failure, not treated as successful retrieval.

## Run artifacts and assessment

The [2026-11-08 run](run-2026-11-08/) retains:

- `inputs.json`: export/text fingerprints, both conditions' identical initial
  hits, context bundles, budgets, all expansion logs, and exact generation inputs.
- `coverage.json`: post-hoc expected-record and citation availability; no answer
  grading or accuracy score. Missing targets and truncation are explicit.
- `answers.json`: model/digest/service version, settings, raw answers, response
  metadata (including completion reason), timing, and errors. Expectations are
  not embedded in this measured-output file.
- `assessment.json`: separate AI-authored rubric judgments and supporting raw
  answer excerpts. These judgments are not independent human review.
- `results.md`: question-by-question findings and limitations.

The inputs fingerprint the export without retaining sixteen copies of its full
provenance index in an extra file. Re-export the unchanged pack to reproduce the
input bytes. Exact model output may vary despite the recorded seed and zero
temperature; all original answers are retained. Expected answers remain in the
original evaluation file and are never sent to generation.

The embedded record text in `inputs.json` retains the pack’s CC-BY-4.0 license
and attribution; experiment code and metadata are Apache-2.0.

The comparison tests this adapter on one small authored pack. It does not
isolate OKPF versus other formats, identify causal effects, measure general
retrieval performance, or establish reduced hallucination rates. Read failures
and answer-level judgments in [results.md](run-2026-11-08/results.md), not just
coverage counts.

## Reproduction audit

The [2026-11-09 audit](audit-2026-11-09.md) reproduces all saved prompts and
coverage from a fresh CLI export and checks every assessment excerpt against its
referenced answer. It retains the original model run without new inference or
post-hoc retrieval tuning. These checks establish artifact traceability, not
independent review or behavioral correctness.
