<!-- SPDX-License-Identifier: Apache-2.0 -->

# Fixed-content evidence-ordering protocol v1

2026-11-09. User-authorized local pilot and main experiment. AI-authored protocol
and assessment; **no independent human review credited**. No deployment approval.
This supersedes [v0](ordering-proposal-v0.md) before any new generation. V0 changed
admission under a context cap, so it did not meet the latest instruction that
only ordering change. It also lacked actual input-file hashes, repetitions and
a pilot. The latest user request authorizes execution and AI-only assessment;
the earlier requirement for human scoring before execution is superseded.

## Frozen inputs and hypothesis

Test whether ordering the **same admitted record objects** by lexical relevance
changes qualification, attribution, substantive accuracy and correction tracing
in returned answers. No claim about retrieval coverage is tested: coverage must
be identical between conditions. This cannot justify changing admission order.
Seven existing questions are development examples, not held-out evaluation.

Source: `examples/institutional-evidence-npm`, 16 records, at base commit 724e677.
Copy every pack file (including manifest, provenance and evaluations) into a
retained snapshot, and retain actual CLI export bytes. Required export SHA-256:
`2982f461b9aee755d5fba4cdd1d79e8480ffcca71325fd3bbe06cbeac913a85a`.
Evaluation-file SHA-256:
`0c44d5fddcc253b8e677d4994013db03dc8420c6f45268369333963c6388bb62`.
`freeze.json` lists SHA-256 for every snapshot file, exact prepared input,
protocol and both experiment/consumer scripts, with UTC timestamp. Verify before
every request. Retain attribution and CC-BY-4.0 terms in the snapshot/inputs.
The FLOSS draft pack is not part of these inputs and stays pending_dual_review.

## Conditions: only array order changes

Run the unchanged lexical retriever and relationship expansion once per question.
Use its existing top two initial hits, six-record cap, ten successful additions
including citations, depth two and 9,000 serialized-context-character cap. Preserve
its selection/expansion audit, including unavailable and truncated context.

- **O0:** records in existing admitted order.
- **O1:** the exact same complete records sorted by descending question/body
  lexical score, then record ID ascending. Score uses the existing tokenizer,
  stopwords, full-corpus IDF and length-normalized overlap formula, rounded to
  eight decimals. No expected answers, rubric, question IDs or metadata enter
  scoring. No records are added, dropped, clipped or merged.

Citation objects retain identical content and order. Annotations, JSON key order,
whitespace serialization, question, system message and instruction prefix stay
identical. Only the records array is permuted. Record/citation multisets and exact
context length must match in every pair. Prompt strings necessarily differ in
evidence order only; there are no condition names in model inputs. Record any
pair whose permutation is unchanged; retain it as a no-contrast control.
No product retriever, exporter, MCP endpoint or Core change is permitted.

## Local model and controls

Verified installed before preparation: `phi3.5:latest`, digest
`61819fb370a3c1a9be6694869331e5f85f867a079e9271d66cb223acb81d04ba`,
Ollama **0.18.0**. Recheck for pilot/main and stop on mismatch. Capture `/api/show`
(template, model metadata and default parameters), `/api/version` and model tag
metadata. Use only configured credential-free loopback; no download or paid API.

Generation: `temperature=0`, `num_predict=768`, **`num_ctx=16384`**, `stream=false`,
240-second timeout per request; no previous conversation/context passed.
Use the exact original `institutional_consumer.SYSTEM` (including under-250-word
request) and question/prefix. Exact system and prompts are frozen in `inputs.json`.
Other options remain server/model defaults and are retained via model metadata.
The larger context window is selected before pilot to avoid the previous
4096-window uncertainty; it is equal across arms, not comparable to old A/B runs.

Preflight requires UTF-8 bytes of system+prompt plus 2,048 template-overhead
allowance plus 768 output tokens to fit 16,384. This is a conservative byte-based
estimate, not a measured tokenizer count. Pilot/server prompt counts provide an
additional empirical check, not independent certification against silent truncation.
Never shrink one condition's content to fit. Save token counts and finish reasons.
GPU kernels, concurrency/cache and runtime behavior may remain nondeterministic;
seeds and temperature zero do not guarantee byte-identical results.

## Pilot and freeze

Run exactly two pilot requests (O0/O1) for the question with the longest serialized
context, ties resolved by existing question order. Pilot seed **17**. Save pilot
requests/responses separately from main data. Check identity, response completion,
reported prompt tokens plus output allowance versus context window and output
finish reasons. Pilot selection does not inspect expected answers or prior quality.

If transport fails or fit fails, stop and document a revised protocol before main.
If output reaches the cap, retain it and keep the predeclared budget; censorship
is a measured outcome, not grounds to selectively increase output. Do not inspect
pilot quality for tuning. Before main, `final-freeze.json` timestamps and hashes
the first freeze and pilot file, stating any protocol change. This protocol permits
no main-run changes after seeing results.

## Repeated main run

Two complete repetitions: seeds **42 and 43**, fourteen requests each (28 total).
For each seed use original question order. For repetition zero, run O0/O1 on
even zero-based question indices and O1/O0 on odd; invert for repetition one.
This counterbalances time/order exposure without claiming randomized sampling.
One request per question/arm/seed, no retry, best-of selection or answer replacement.
Errors remain explicit observations. A crash leaves the pending request and all
completed lines; do not silently resume or regenerate a partial run.

Persist exact requests before inference, complete returned response objects,
timestamps, elapsed seconds, eval/prompt tokens, server durations, finish reasons
and errors. Keep pilot separate. All requests refer to frozen inputs and code.
Do not run the old generator, which has different caps and no repeated schedule.

## Frozen rubric and assessment

Keep original seven question-specific rubrics unchanged in the snapshot. For each
returned answer assess every original item using `met`, `partial`, `not_met`, or
`not_assessable` (missing/error). Require exact answer excerpts and short reasons.
Also assess these four dimensions separately; no overall accuracy score:

- **Attribution:** met if substantive source/record attributions are correct and
  same-author interpretations are not called independent/community consensus;
  partial for vague/missing attribution; not_met for a false attribution.
- **Correction tracing:** for supersession, met requires candidate → correction →
  replacement IDs plus rationale and synthetic status; partial for an incomplete
  chain; not_met for adopting the superseded claim. Other questions: not_applicable.
- **Uncertainty:** met if relevant missing observations, bounds and lack of causal
  warrant are explicit; partial if incomplete; not_met for unsupported certainty,
  quantities or absence-of-evidence treated as contrary evidence.
- **Substantive accuracy:** met if material assertions are supported by supplied
  context; partial for vague/incomplete response without explicit false claims;
  not_met for incident conflation, invented facts or materially false statements.

For errors all dimensions are not_assessable except inapplicable correction.
For truncated responses assess only returned text and tag omissions as censored,
not an unlimited-generation inability. False assertions in a prefix remain
assessable. Report each condition's cutoff/error counts using all scheduled
responses; do not discard cutoffs or treat complete-only comparison as unbiased.

Blind answer presentation by a deterministic shuffle with seed **20261109**,
opaque IDs, and a separate key containing condition/repetition/seed. Assess against
common condition-independent evidence and original questions/rubrics; hide request
ordering and labels during the initial review. The implementing AI already knows
the design, so this is practical masking, not independent blinded human review.
Assessments are **AI-authored and unreviewed**. Report per-question/item outcomes,
seed agreement and descriptive differences, including ties, nulls and regressions.
Keep coverage, answer quality, truncation and causal claims separate.

Independent human review of raw answers and judgments remains required before
any adoption/approval claim. No results on this small authored pack generalize to
formats, institutions, safety, prediction or reduced hallucination rates.
