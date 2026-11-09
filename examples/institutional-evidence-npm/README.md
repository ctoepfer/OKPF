<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Institutional evidence: two npm release-authority episodes

This Native Mode pack contains source-grounded summaries of two real episodes,
not a representative empirical corpus or a governance model:

- **Event-stream:** the dependency addition on September 9, 2018 through the
  reported response of December 12, 2018. The unit is release-authority
  transition and containment, not the project's entire history.
- **Ua-parser-js:** the maintainer's October 22, 2021 response to suspected npm
  account hijack. The later-accessed advisory supplies bounded remediation
  context, not a frozen contemporaneous snapshot.

Start with [narratives](artifacts/episodes.md), the
[comparison](artifacts/comparison.md), and [selection note](artifacts/selection.md).
The machine-readable view is [records/evidence.jsonl](records/evidence.jsonl).
Source URLs, publication/access dates, precise locators, and limitations are in
[provenance/context.json](provenance/context.json). Full third-party sources are
not included: redistribution permission was not established. Source availability
and mutable web pages limit independent offline verification of the accounts.
Only original summaries and fixture content are licensed CC-BY-4.0; linked
materials retain their own rights.

The three `*-synthetic` records are a deliberately fabricated correction exercise,
not historical testimony or an actual human review. All pack text, competing
interpretations, and [evaluation expectations](evals/questions.json) were drafted
by one AI assistant; no independent human review or measured consumer evaluation
is documented. Multiple interpretations here do not represent multiple reviewers.

```bash
python3 reference/python/okpf_validate.py examples/institutional-evidence-npm
PYTHONPATH=reference/python python3 -m okpf export-rag examples/institutional-evidence-npm out/institutional-rag.jsonl
PYTHONPATH=reference/python python3 -m okpf export-citations examples/institutional-evidence-npm out/institutional-citations.jsonl
```

The exports preserve the example's evidence/qualification/correction index inside
`provenance`. Select the entry matching `record_id` under
`extensions["org.okpf.examples.institutional_evidence"].record_context`.
Evidence references resolve in `provenance.evidence_index`; record references
resolve in that context index and to the corresponding exported `record_id`.
This is example authoring, not a new Core relationship syntax or graph resolver.
RAG text also states essential caveats inline. Citation rows also retain concise qualification summaries in the index.
They omit the full record text, so retain
and consult their provenance. Narrative/evaluation artifacts are not separately
exported under the existing records-first rule. The repeated index is suitable
for this small fixture, not an asserted scalable export architecture.

A consumer that indexes only text and discards provenance can still lose linked
context. No retrieval system, evaluation runner, or predictive model was tested.
The fixtures specify seven manual rubrics, not measured model results. See
[the conventions](../../docs/institutional-evidence-packs.md) for promotion criteria
and remaining limitations. This suite declares only `okpf-core` and does not
adopt or expand the earlier `okpf.profile.institutional.v1` scaffold.
