<!-- SPDX-License-Identifier: Apache-2.0 -->

# Proposed bounded related-edge ordering experiment

**Draft protocol — not executed or approved.** AI-assisted design, requiring
human sign-off before code changes, generation or scoring. This does not count
as human case coding. Keep the original 2026-11-08 run immutable.

## Question and hypothesis

Within the existing 16-record `institutional-evidence-npm` pack, does ordering
nonmandatory `related_refs` by question relevance admit more relevant substantive
context before the fixed limit, without reducing qualification/correction coverage?
Separately test whether returned answers preserve attribution and correction
chains. Improved coverage is not assumed to improve answers. The prior trace
question motivated this hypothesis; these seven questions are development data,
not a held-out test. No format-level or general causal claim is intended.

## Freeze before implementation

Human reviewers approve this protocol and record its content hash, repository
revision, actual export hash and evaluation-file hash. Use the original export
fingerprint `2982f461b9aee755d5fba4cdd1d79e8480ffcca71325fd3bbe06cbeac913a85a`;
stop if re-export differs. Keep all seven existing question strings and rubrics,
with no added corpus or labels entering retrieval/generation. Archive code,
inputs and outputs under a new run directory; never replace baseline artifacts.

## Two ordering conditions

Both arms use relationship-aware context, identical initial lexical top two
records, the existing tokenizer/stopwords/IDF/length normalization, breadth-first
queue, relation categories and citation placement. Limits remain six record
bodies, ten successful additions including citations, depth two and 9,000 Unicode
characters for the exact serialized context. Metadata overhead consumes budget.
No reranking of initial hits, extra retrieval, or change to admission rules.

- **O0, authored order:** current `Consumer.bundle` order within every relationship
  list, including `related_refs`.
- **O1, query order:** when processing each admitted parent's `related_refs`, sort
  that parent's existing target list by descending lexical score of the target
  body against the question, using exactly the initial-retriever scoring formula
  computed over the same full record collection. Do not truncate this list to
  initial_k. Break score ties by target ID; absent target bodies sort after known
  targets, then by ID. Keep duplicates for the existing visited/audit logic.
  All other relationship lists, category order and evidence-reference order stay
  identical. No expected refs, rubric text, question IDs or provenance text enters
  scoring. Do not move a target across relation categories or parents.

Qualification and supersession edges keep their existing per-parent priority.
This is not a new global guarantee that all qualifications fit: the current
breadth-first budget can still exclude them. Log scores, parent, relation,
original/reordered positions, every admission/rejection and reason. Require
focused synthetic tests of tie order, missing targets, cycles, unchanged
non-related edges and expectation isolation before any inference.

## Generation controls and budget

Use the already-authorized local Ollama model `phi3.5:latest` with recorded digest
`61819fb370a3c1a9be6694869331e5f85f867a079e9271d66cb223acb81d04ba` and Ollama
**0.18.0**. Verify both locally before starting; if unavailable or different, stop
and amend the protocol before observing results. Do not install models, switch
providers or purchase usage. This is a specification, not a claim that the model
or service was probed in this review.

Fix temperature 0, seed 42, `num_ctx=4096`, **`num_predict=768`**, 180-second timeout,
no conversation carry-over and the exact original system/question template.
Both arms receive the same output cap. Doubling the original 384-token cap is an
explicit censoring mitigation; comparisons with the old A/B answers are therefore
not controlled. The new inference comparison is O0 versus O1 only. Retain the
original under-250-word instruction unchanged.

Before inference, verify full prompt token counts with the matching local model
tokenizer if available: input plus 768 must fit 4096. If reliable counting is
unavailable, record that limitation and require human approval of the input-window
risk before running; do not silently shrink contexts. Inspect returned counts and
finish reasons, and flag any apparent input/output truncation. No selective retries,
truncated-answer replacement, best-of selection or handcrafted completion.

Exactly fourteen generation requests, one per question/arm. Use original question
order; for odd-numbered questions run O0 then O1 and even-numbered questions O1
then O0. This predetermined alternating schedule reduces one-sided ordering but
is not randomization or replication. Transport errors remain results, not retries.
Record model/digest/service, timing, exact prompts, selected contexts, raw answers,
finish reasons and errors. Do not consult expected answers during generation.

## Separate assessments

1. **Structural audit:** identical initial hits and settings; only specified edge
   order changes; budgets, paths and all expansion reasons retained. Stop for
   implementation/expectation leakage rather than interpret a broken comparison.
2. **Context coverage:** after contexts are frozen, count expected bodies and
   citation objects actually admitted, missing qualification/correction bodies,
   unresolved links and every rejected addition. Report per-question O0/O1 deltas,
   including regressions. The global index and inline mentions do not count as
   supplied bodies. Citation objects are not primary-source bodies.
3. **Answer rubric:** apply every existing question-specific rubric item separately
   as `met`, `partial`, `not_met`, or `not_assessable` for absent/error responses.
   Support each judgment with exact answer excerpts and supplied-context pointers.
   Add separate flags for unsupported attribution, incident conflation, invented
   IDs, implied consensus, synthetic/historical confusion, explicit correction
   chain and unsupported causal inference. Do not collapse these into accuracy.
4. **Censoring:** attach output-cutoff and possible input-truncation flags to every
   judgment. For cutoffs, classify missing rubric material as not observed in the
   returned prefix; do not infer what an unlimited answer would do. Explicit
   wrong assertions remain assessable. Report complete and censored responses
   separately without dropping either set. No causal estimate from the subset.

## Human review and interpretation

Two human reviewers independently assess all fourteen answers in shuffled,
condition-masked presentation, with the exact supplied context and rubrics.
Context content can reveal the arm, so masking is imperfect. Reviewers should be
independent of the implementation and record identities/roles, dates and conflicts.
Retain their separate judgments, excerpts, disagreements, reconciliation and
unresolved dissent. AI can prepare audit tables but cannot fill either human role.
The authored rubrics are not an independently validated gold standard.

Advance only if the reported coverage benefit survives human examination without
hiding lost qualifications/corrections or new unsupported claims. Mixed or null
results remain reportable. A decision to extend beyond this development set needs
new reviewed evidence and a separately specified study. This proposal establishes
no safety, effectiveness, generalization or reduced hallucination-rate result.
