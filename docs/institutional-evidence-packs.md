<!-- SPDX-License-Identifier: Apache-2.0 -->

# Institutional evidence packs: provisional conventions

Institutional evidence examples demonstrate packaging of sources, contested
interpretations, uncertainty, and limits on analogy. They do not validate causal
claims or certify institutional laws. The bounded
[npm example suite](../examples/institutional-evidence-npm/) contains two real
release-authority episodes and a separate, explicitly synthetic correction
exercise. It is an AI-authored draft, not an independently reviewed corpus.

## Which institutional approach to use

Start new institutional evidence authoring with these provisional examples.
The earlier `okpf.profile.institutional.v1` remains an experimental, opt-in
scaffold with compatible validation and review tooling; it is not removed or
silently deprecated. Neither approach establishes causal or predictive validity.
Reconciliation requires independently reviewed examples and observed consumer
behavior, not choosing a schema by assertion. The bounded
[consumer experiment](experiments/institutional-consumer/README.md) tests one
adapter against this example pack; it does not promote either approach to a
stable profile.

## Scope and packaging

Use the existing Core envelope and [historical evidence conventions](historical-evidence-packs.md).
Native Mode fits authored narratives, citations, and normalized records when
source reproduction is unavailable. Envelope Mode can retain lawfully
redistributable domain artifacts; Hybrid Mode can combine them with normalized
records. This suite uses Native Mode. Citation-only evidence is less independently
verifiable offline than a source snapshot; do not conceal that distinction.

The unit of analysis should be a bounded decision, transition, or response,
with actors, resources, authority, dependencies, dates, and observation limits.
Retain narrative context alongside structured records. Separate formal rules
from evidence of actual practice, announced interventions from attempts and
reported implementation, and reported implementation from independent checks.
Distinguish affected groups rather than requiring one institution-wide outcome.

Use open Core `record_type`, `facets`, and `metadata` fields. The suite borrows
`historical_claim`, `uncertainty_note`, `negative_search`, `counterargument`, and
`review_note` conventions and demonstrates `outcome_observation`,
`outcome_assessment`, and `comparison`. These are example vocabularies, not
required types. An assessment identifies its object/function, affected group,
baseline, observation, horizon, assessor, rationale, evidence, and uncertainty.
Multiple assessments may coexist without a mandatory failure/evolution taxonomy.

## Evidence and epistemic distinctions

| Distinction | Example treatment |
|---|---|
| Direct attestation | `source_attested`, with source ID and precise locator; an operator report remains a report |
| Inference | `inference`, with the AI pack author named as assessor and causal limitations |
| Disputed interpretation | `disputed`, with each position attributed; an authored alternative is not a second witness |
| Unknown | `unknown`, for information absent from this pack |
| Not yet checked | Named research tasks in `search-scope`; no claim of performed searches |
| Checked with no result | `checked_no_result`, restricted to named sections, date, and query purpose |
| Uncertain timing | Observation horizon and source-revision caveats; no invented exact handoff date |
| Weak causal attribution | No counterfactual, comparison group, or effect estimate |
| Uncertain transferability | Explicit material mismatches and analogy rejection conditions |

Collection-level selection notes state inclusion/exclusion, known omissions,
and whether a denominator exists. A purposive pair of public incidents cannot
establish historical failure rates. Preserve source title, author, publication
and access dates, revision date when known, precise locator, availability, and
redistribution limits. Do not infer permission from public accessibility.
Neither hashes nor signatures prove evidence quality, authorship trustworthiness,
privacy, peer review, or factual correctness.

Structural validity means the pack conforms to format requirements. Evidentiary
support means a particular source supports a particular qualified claim. Causal
inference requires a defensible account of alternatives and counterfactuals.
Predictive validity requires testing predictions on relevant unseen outcomes.
Passing these fixtures establishes only structure and reference preservation.

## Relationships, correction, and export

The suite's local namespace is `org.okpf.examples.institutional_evidence`.
Each record stores context under `metadata[namespace]`: `evidence_refs` address
source IDs and `qualification_refs`/`related_refs` address record IDs. Correction
records also use the existing `candidate_ref`, `corrected_ref`, `correction_type`,
and `feedback_summary` conventions; candidate/replacement records link through
`superseded_by`/`supersedes`. The synthetic exercise claims no actual human
review and does not declare the human-correction-loop profile. Original text,
rationale, author type, and supersession remain inspectable.

The current `export-rag` contract does not export arbitrary record metadata or
facets, and `export-citations` additionally removes text. This suite deliberately
uses its existing provenance fallback: manifest `provenance.$ref` points to
`provenance/context.json`, containing an `evidence_index` and an
`extensions[namespace].record_context` index. With no matching per-file `sources`
entries, the exporter includes this whole context object in every row. Each
context entry mirrors record metadata and supplies its record file path/title.
Limitation entries include concise `qualification_summary` text, so citation
exports retain substantive caveats as well as links.

Resolve the current row's `record_id` in `record_context`; follow record IDs to
other context entries and corresponding exported rows or original records; follow
evidence IDs to URLs and locators in `evidence_index`. This provides explicit
connections in both exports without changing their fields or inclusion rules.
Tests verify projection equality, reference closure, source locators, and
supersession in directory and archive exports. These are authoring constraints
for this fixture, not new Core validation rules.

Essential qualifications also occur in RAG text. Citation exports retain the
relationship context, not the complete narrative or evaluation artifacts.
The records-first rule omits standalone artifact chunks, so the comparison is
also a record. Consumers must resolve links and retain provenance; text-only
indexing or arbitrary rechunking may lose context. The repeated index is small
here but scales poorly. A consumer is not guaranteed to retrieve disagreement
merely because its link survived. No retrieval-quality or hallucination-reduction
claim is made.

## Evaluation fixtures, not evaluation results

`evals/questions.json` follows the existing `schemas/evaluation.schema.json`
and contains seven questions with expected evidence/record references and
manual rubrics. These test qualification retrieval, conflicting interpretations,
rule/practice separation, mismatches, traceability, abstention, and supersession.
The expected answers were authored by an AI assistant, not independent human
coders. No measured model answers, scores, or evaluation-result documents are
included. Human-authored expectations, if later supplied, should record their
actual author and review process separately from measured results.

The repository contains a heuristic demo quiz, not a general evaluator for these
reference-aware rubrics. Its keyword matching cannot establish the requested
consumer behavior. Core validation does not itself grade evaluations; focused
tests validate the evaluation schema and references, not answer quality. No
simulator, LLM service, embedding dependency, or governance runtime is added.

## Profile promotion is deferred

No new institutional-case profile is proposed. The earlier
[`okpf.profile.institutional.v1` scaffold](profiles/institutional-v1.md) remains a
separate opt-in experiment; this suite does not declare it, treat its shape as
settled, or change its validator. The examples here deliberately allow multiple
attributed assessments and do not mandate a single outcome taxonomy.

A future optional profile would need convergence across independently authored,
source-reviewed examples; documented consumer needs and export behavior; evidence
that the proposed fields preserve disagreement and corrections across domains;
and compatibility review under the Core freeze. Its recommendations should be
experimental and warning-first until justified by that practice. Two cases from
one ecosystem and one AI author do not meet that threshold.
