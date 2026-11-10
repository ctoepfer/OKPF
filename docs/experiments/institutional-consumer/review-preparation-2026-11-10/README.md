<!-- SPDX-License-Identifier: Apache-2.0 -->

# Evaluation scope and review preparation

Status: unscored. No condition-quality comparison or external review performed.
The user requested strict scoring-before-comparison and independent expert review.
Evaluation-scope clarification and reviewer identification are pending. The user
explicitly selected documentation-only work for the later RAG and boundary-transition
proposals, separate from and without changes to the frozen evaluation.

## Retained study versus requested study

| Property | Retained frozen study | Newly requested study |
|---|---|---|
| Conditions | Existing evidence order and lexical relevance order, identical admitted content | No-context baseline, static/few-shot ingestion, MCP retrieval |
| Questions | Seven authored development questions, repeated for two seeds | Not yet specified or sampled |
| Criteria | Exact question rubrics; attribution, correction tracing, uncertainty, substantive accuracy | Failure topology, evasion/gaming, boundary mismatch, primary-source attribution |
| Data | 28 retained answers; original interrupted run excluded | No corresponding three-arm dataset |

The new criteria cannot be described as pre-committed for these retained answers.
No-context and static/few-shot arms cannot be inferred from the ordering labels.
The prior consumer A/B study is also a different design and cannot supply missing
arms as a controlled comparison. Neither study supports a three-arm effect size.
Select the existing frozen evaluation or preregister a separate study before
scoring under a changed rubric. No new generation is implied by packet creation.

## Neutral evaluator packet

`prepare_packet.py` produced `out/institutional-review-packet-2026-11-10.zip`.
Archive SHA-256: `9fd9950c5b01354192ae8a333d91d0c5de7e481523094bde56506050c954c4e1`.
It contains verbatim masked responses, output token/character/byte lengths,
completion flags, common evidence context, exact frozen question criteria and
assessment dimensions, an empty scoring worksheet and reconciliation template.
A per-file hash manifest records packet contents. Generation checks all 28 answer
texts against the retained responses; it does not grade answers.

The script is an organizer tool: it reads the key to associate token counts, but
its evaluator output contains no key, condition label, request prompt, seed,
generation order, timing or prior judgments. Do not give the organizer script or
repository to the evaluator as part of the blinded first pass. The packet is not
an immutable primary-source archive; source access and disagreements should be
recorded by the reviewer rather than treated as already verified.

True access isolation cannot be claimed: keys and raw requests already exist in
the published repository, and response content may reveal treatment clues. Ask
an independent evaluator to disclose prior exposure and avoid those resources
until scoring is locked. The implementing assistant has seen the design and
condition-level operational counts; it is not an independent blinded evaluator.
No independent scoring has been credited.

## Ordered review procedure

1. Identify the evaluator, scope, conflicts, and prior exposure. Deliver only the
   evaluator packet for the first pass. Preserve original texts and frozen rubric.
2. Record every item/dimension, exact excerpts and reasons. No stylistic grading.
   Treat missing text at cutoff as censored; do not infer unseen content. Record
   completion lengths separately. Resolve rubric ambiguities before unmasking.
3. Lock/hash judgments before revealing labels. Keep independent passes separate
   until both are locked; retain disagreements, amendments and unresolved issues.
4. Join labels only after locking. Report per-item condition counts, denominators,
   paired differences, seed agreement, ties and regressions. No invented aggregate
   score. Full-versus-truncated strata are descriptive sensitivity analyses:
   completion is affected by treatment, so conditioning on it can introduce bias.
   Output-cap truncation alone does not prove input-window pressure or format utility.
5. Provide full raw data and reconciliation records to the independent expert
   after the locked pass, separately from any author interpretation. Record their
   review and unresolved concerns before any adoption or release-readiness claim.

No reviewer has been contacted or secured. Name/contact or an existing reviewer
arrangement is needed. Prior technical publication is not approval of findings.
The seven prep-tool failures are tracked separately in
[the technical-debt record](../../../project/PREP_TOOL_DEBT.md).
