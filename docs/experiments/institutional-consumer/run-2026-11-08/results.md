<!-- SPDX-License-Identifier: Apache-2.0 -->

# Consumer run: 2026-11-08

**Failures remain despite improved context coverage.** The relationship-aware condition supplied all expected record bodies for five of seven questions, but the traceability question lost its main action record to the record cap and the abstention question did not reach one expected qualification. Models also cited unsupplied records, conflated incidents, and failed to trace a correction explicitly even with the relevant records present. Seven of fourteen responses hit the shared output cap. These results do not establish reliable epistemic preservation.

## What ran

Actual `export-rag` output from the unchanged 16-record institutional-evidence pack fed a fixed lexical adapter. All seven existing questions ran in A (two text-only records) and B (identical initial retrieval plus bounded relationship expansion). No corpus expansion, exporter change, external source fetch, model installation, or new paid provider was used for the experiment.

Generation: `phi3.5:latest`, digest `61819fb370a3c1a9be6694869331e5f85f867a079e9271d66cb223acb81d04ba`, configured loopback Ollama 0.18.0. Both conditions used temperature 0, seed 42, context window 4096, and output cap 384 tokens. All fourteen requests completed without transport errors. Completion means a response was returned, not that the answer met its rubric; seven ended with `done_reason=length`.

Retrieval settings: two initial records; at most six record bodies, ten added items including citations, depth two, 9,000 serialized-context characters. The question and identical system instructions are outside that evidence budget. B pays for its own record annotations and citations within the same budget. The actual A contexts were shorter. Conditions ran in fixed A/B order, without randomization or repeated trials.

Expected answers and references were excluded from generation inputs. Source content was explicitly framed as untrusted data. Model output and reviewer judgments are separate artifacts: [inputs](inputs.json), [coverage](coverage.json), [raw answers](answers.json), [AI-authored rubric assessment](assessment.json). No independent human review was performed.

## Structural checks versus coverage

The source pack validates. Focused tests check expectation isolation, identical initial retrieval, qualification/supersession expansion, cycle termination, missing targets, budgets, output separation, and unchanged export behavior. These software checks do not grade answer quality. Initial hits and all fourteen generation payloads were reproduced exactly after the run. A text-only audit traversal was subsequently sorted for deterministic logging; only audit order changed, not retrieval, context, prompts, or outcomes.

“Records” below counts expected record bodies actually admitted, not IDs merely mentioned in metadata. “Citations” counts admitted URL/locator/date/limitation objects. Full primary-source bodies were absent in every condition. No global provenance index is counted as selected context.

| Question | Initial records (same A/B) | A records | B records | A citations | B citations | B context limited? |
|---|---|---|---|---|---|---|
| qualified-retrieval | `es-response`, `comparison` | 1/2 | 2/2 | 0/2 | 2/2 | yes |
| conflicting-interpretation | `ua-limit`, `es-assess-users` | 1/3 | 3/3 | 0/2 | 2/2 | no |
| rule-practice | `es-rule`, `es-transition` | 1/2 | 2/2 | 0/1 | 1/1 | yes |
| mismatch | `comparison`, `selection` | 1/4 | 4/4 | 0/2 | 2/2 | yes |
| trace | `comparison`, `ua-dispute` | 1/3 | 2/3 | 0/1 | 1/1 | yes |
| abstain | `es-limit`, `search-scope` | 2/4 | 3/4 | 0/1 | 1/1 | no |
| supersession | `candidate-synthetic`, `ua-limit` | 2/4 | 4/4 | 0/1 | 1/1 | yes |

All ten expected question–citation pairs were admitted in B and none in A. Expected record-body availability was 8 of 22 pairs in A and 20 of 22 in B. These are context-availability counts, **not answer accuracy scores**. Five B bundles rejected some additional context; no dangling target was encountered in this particular pack. Missing-target behavior is tested separately.

## Failures and counterexamples

- **Traceability:** initial retrieval chose `comparison` and `ua-dispute`; expansion filled its six-record limit before `ua-transition`. B supplied the maintainer citation metadata but still omitted the support/deprecation sequence in its answer. Metadata access did not replace the missing substantive record.
- **Abstention:** both answers declined to invent the requested rate/loss quantity. Nevertheless B falsely associated BitPay with an October 2021 ua-parser update. Satisfying an abstention rubric did not imply source-faithful surrounding prose.
- **Correction:** B had candidate, correction, and replacement bodies, but did not explicitly trace the candidate-to-replacement supersession. A discussed a correction whose body it never received.
- **Attribution:** A cited `es-assess-containment` without its body. Other answers treated an AI-authored alternative as community disagreement or described historical-source reporting as an AI draft.
- **Output limits:** seven answers were cut off. Longer B contexts consumed more prompt processing and often led to extended restatement rather than concise synthesis. The limit was held fixed; there was no selective retry or handcrafted replacement.
- **Disagreement:** both conditions incompletely explained that the two assessments were alternative lenses from the same AI author. A relationship existing in JSON did not establish that the model used it correctly.

## Question-by-question record

Judgments below are Codex-authored, unreviewed qualitative assessments of the existing rubric. `met` applies only to that item; collateral errors and truncation still matter. Exact excerpts support each judgment. Full raw responses are retained in `answers.json`, with the indexed pointer listed for each condition.

### qualified-retrieval

What does the event-stream containment record establish?

**A_text_only**

- Initial selection: `es-response`, `comparison`.
- Added via relationships: none.
- Record bodies supplied: `comparison`, `es-response`.
- Missing expected record bodies: `es-limit`.
- Expected citation objects supplied: none; missing: `bitpay2018`, `npm2018`.
- Missing linked qualification bodies: es-limit (not expanded); ua-limit (not expanded); selection (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 1153/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/0` in [answers.json](answers.json).

- **partial — Identify the reported action and horizon**
  Excerpt: “on November 26th”. Names a response date and removal but attributes the account to es-assess-containment, which was referenced but not supplied; omits the December horizon.
- **not_met — State that user recovery and losses are unmeasured**
  Excerpt: “whether these removals prevented further issues, such as wallet user recovery problems or net losses”. Discusses possible effects but never clearly preserves the explicit unmeasured-recovery/loss qualification.
- Additional failure/caveat: Cites es-assess-containment without its substantive record body in supplied context.

**B_relationships**

- Initial selection: `es-response`, `comparison`.
- Added via relationships: es-limit (qualification_refs from es-response); es-assess-containment (related_refs from es-response); es-assess-users (related_refs from es-response); npm2018 (evidence_refs from es-response); bitpay2018 (evidence_refs from es-response); ua-limit (qualification_refs from comparison); maintainer2021 (evidence_refs from comparison).
- Record bodies supplied: `comparison`, `es-assess-containment`, `es-assess-users`, `es-limit`, `es-response`, `ua-limit`.
- Missing expected record bodies: none.
- Expected citation objects supplied: `bitpay2018`, `npm2018`; missing: none.
- Missing linked qualification bodies: selection (records).
- Truncated additions: selection (records); es-transition (records); ua-transition (records); ua-response (records); advisory2021 (characters). Unresolved targets: 0.
- Context: 8942/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/1` in [answers.json](answers.json).

- **met — Identify the reported action and horizon**
  Excerpt: “between November 26, 2018 ("horizon"), and December 12, 2018”. States the reported action and horizon with npm/BitPay references.
- **met — State that user recovery and losses are unmeasured**
  Excerpt: “these actions do not measure wallet-user recovery or quantify net losses”. Explicitly preserves the requested qualification; the answer is nevertheless output-truncated.
- Additional failure/caveat: Mixes access-mechanism uncertainty from the comparison into the event-stream account.

### conflicting-interpretation

Did the response succeed for all affected groups?

**A_text_only**

- Initial selection: `ua-limit`, `es-assess-users`.
- Added via relationships: none.
- Record bodies supplied: `es-assess-users`, `ua-limit`.
- Missing expected record bodies: `es-assess-containment`, `es-limit`.
- Expected citation objects supplied: none; missing: `bitpay2018`, `npm2018`.
- Missing linked qualification bodies: selection (not expanded); es-limit (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 918/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/2` in [answers.json](answers.json).

- **partial — Name both objects and affected groups**
  Excerpt: “registry containment alone is insufficient proof of successful recovery”. Distinguishes containment and recovery but only develops the exposed-user lens; the other assessment was not supplied.
- **not_met — Attribute both interpretations to the same AI author, not independent reviewers**
  Excerpt: “"Pack-author interpretation B"”. Mentions one attributed interpretation but does not explain that both lenses were authored by the same AI author.
- Additional failure/caveat: Mixes ua-parser uncertainty into a question expected to contrast event-stream assessments.

**B_relationships**

- Initial selection: `ua-limit`, `es-assess-users`.
- Added via relationships: selection (qualification_refs from ua-limit); maintainer2021 (evidence_refs from ua-limit); advisory2021 (evidence_refs from ua-limit); es-limit (qualification_refs from es-assess-users); es-assess-containment (related_refs from es-assess-users); bitpay2018 (evidence_refs from es-assess-users); npm2018 (evidence_refs from es-limit).
- Record bodies supplied: `es-assess-containment`, `es-assess-users`, `es-limit`, `selection`, `ua-limit`.
- Missing expected record bodies: none.
- Expected citation objects supplied: `bitpay2018`, `npm2018`; missing: none.
- Missing linked qualification bodies: none.
- Truncated additions: none. Unresolved targets: 0.
- Context: 8054/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/3` in [answers.json](answers.json).

- **partial — Name both objects and affected groups**
  Excerpt: “AI draft interpretations suggest limited containment at registry boundaries but do not establish downstream recovery”. Distinguishes functions but does not clearly present both affected groups and their contrasting assessments; much of the response discusses the other incident.
- **partial — Attribute both interpretations to the same AI author, not independent reviewers**
  Excerpt: “AI draft interpretations”. Acknowledges AI drafting and review limitations, but does not explicitly explain that the two assessments are from the same author.
- Additional failure/caveat: Retrieval ambiguity adds ua-parser material; neither answer clearly presents the two attributed lenses.

### rule-practice

Does the stated dependency-update rule prove compliance?

**A_text_only**

- Initial selection: `es-rule`, `es-transition`.
- Added via relationships: none.
- Record bodies supplied: `es-rule`, `es-transition`.
- Missing expected record bodies: `es-limit`.
- Expected citation objects supplied: none; missing: `bitpay2018`.
- Missing linked qualification bodies: es-limit (not expanded); selection (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 886/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/4` in [answers.json](answers.json).

- **partial — Separate stated rule, reported implementation, and independent verification**
  Excerpt: “a lack of independent build audit or later compliance observations to verify adherence”. Preserves absence of independent verification, but introduces unsupported npm policies and misstates the security-patch exception as exclusion.
- **met — Do not invent a succession charter**
  Excerpt: “there is an account of a social engineering attack”. Does not invent a formal succession charter, although it invents other policy/regulatory framing.
- Additional failure/caveat: Unsupported assertion that both npm and BitPay have update policies; unsupported regulatory-conformity framing; security-patch exception becomes exclusion.

**B_relationships**

- Initial selection: `es-rule`, `es-transition`.
- Added via relationships: es-limit (qualification_refs from es-rule); es-response (related_refs from es-rule); bitpay2018 (evidence_refs from es-rule); selection (qualification_refs from es-transition); npm2018 (evidence_refs from es-transition); es-assess-containment (related_refs from es-response).
- Record bodies supplied: `es-assess-containment`, `es-limit`, `es-response`, `es-rule`, `es-transition`, `selection`.
- Missing expected record bodies: none.
- Expected citation objects supplied: `bitpay2018`; missing: none.
- Missing linked qualification bodies: none.
- Truncated additions: es-assess-users (records). Unresolved targets: 0.
- Context: 7364/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/5` in [answers.json](answers.json).

- **met — Separate stated rule, reported implementation, and independent verification**
  Excerpt: “there is no independently verified build audit or longitudinal effectiveness measurement mentioned”. Distinguishes BitPay statement/reported implementation from independent verification.
- **met — Do not invent a succession charter**
  Excerpt: “an event-stream incident involving a maintainer takeover was reported by npm”. No formal succession charter is invented.
- Additional failure/caveat: Lack of independent verification is framed as casting doubt on implementation; absence of verification alone is not contrary evidence.

### mismatch

Can succession vetting be inferred to prevent the ua-parser incident?

**A_text_only**

- Initial selection: `comparison`, `selection`.
- Added via relationships: none.
- Record bodies supplied: `comparison`, `selection`.
- Missing expected record bodies: `es-transition`, `ua-limit`, `ua-transition`.
- Expected citation objects supplied: none; missing: `maintainer2021`, `npm2018`.
- Missing linked qualification bodies: es-limit (not expanded); ua-limit (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 1421/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/6` in [answers.json](answers.json).

- **partial — Identify access-mechanism mismatch**
  Excerpt: “a maintainer's suspicion of account hijack”. Mentions suspected hijack but does not clearly contrast it with delegated maintainership as the material mismatch.
- **met — Reject transfer of a succession-only remedy**
  Excerpt: “it is not possible to conclusively state whether succession vetting could have prevented the ua-parser incident”. Abstains from transferring a prevention claim, though the attribution invents numeric record IDs.
- Additional failure/caveat: Invents numeric record IDs 1 and 2 and swaps some source-selection/comparison attribution.

**B_relationships**

- Initial selection: `comparison`, `selection`.
- Added via relationships: es-limit (qualification_refs from comparison); ua-limit (qualification_refs from comparison); es-transition (related_refs from comparison); ua-transition (related_refs from comparison); npm2018 (evidence_refs from comparison); maintainer2021 (evidence_refs from comparison).
- Record bodies supplied: `comparison`, `es-limit`, `es-transition`, `selection`, `ua-limit`, `ua-transition`.
- Missing expected record bodies: none.
- Expected citation objects supplied: `maintainer2021`, `npm2018`; missing: none.
- Missing linked qualification bodies: none.
- Truncated additions: ua-response (records); advisory2021 (characters); bitpay2018 (characters); es-rule (records); es-response (records); ua-dispute (records). Unresolved targets: 0.
- Context: 8367/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/7` in [answers.json](answers.json).

- **met — Identify access-mechanism mismatch**
  Excerpt: “maintainer takeovers and suspected account hijacks”. Identifies distinct access routes, while additional claims about maintainer understanding are unsupported.
- **met — Reject transfer of a succession-only remedy**
  Excerpt: “does not provide evidence that succession vetting could have prevented these incidents”. Rejects the unsupported prevention inference.
- Additional failure/caveat: Infers a lack of understanding/control by the maintainer from distinct authority boundaries without supporting evidence.
- Additional failure/caveat: Mixes event-stream formal-succession uncertainty into ua-parser account-access uncertainty.

### trace

What did the ua-parser maintainer report doing?

**A_text_only**

- Initial selection: `comparison`, `ua-dispute`.
- Added via relationships: none.
- Record bodies supplied: `comparison`, `ua-dispute`.
- Missing expected record bodies: `ua-limit`, `ua-transition`.
- Expected citation objects supplied: none; missing: `maintainer2021`.
- Missing linked qualification bodies: ua-limit (not expanded); selection (not expanded); es-limit (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 1230/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/8` in [answers.json](answers.json).

- **not_met — Cite comment 949742904 and its date**
  Excerpt: “reference [maintainer2021]”. Names an evidence ID but supplies neither comment 949742904 nor its date; citation metadata was not supplied.
- **not_met — Distinguish attempted and reported implemented actions**
  Excerpt: “reported suspicency about account hijack”. Does not report support contact/deprecation or distinguish attempted removal from implemented warnings; main action record was missing.
- **partial — Keep the policy explanation tentative**
  Excerpt: “potential limitations imposed by pack policies”. Uses tentative language, but misstates the source of policy constraints and turns an authored alternative into community disagreement.
- Additional failure/caveat: Calls AI-authored alternative explanations an interpretative disagreement within the community.
- Additional failure/caveat: Cites ua-limit, selection, and ua-transition despite their record bodies not being supplied.

**B_relationships**

- Initial selection: `comparison`, `ua-dispute`.
- Added via relationships: es-limit (qualification_refs from comparison); ua-limit (qualification_refs from comparison); selection (qualification_refs from comparison); es-transition (related_refs from comparison); npm2018 (evidence_refs from comparison); maintainer2021 (evidence_refs from comparison); advisory2021 (evidence_refs from comparison).
- Record bodies supplied: `comparison`, `es-limit`, `es-transition`, `selection`, `ua-dispute`, `ua-limit`.
- Missing expected record bodies: `ua-transition`.
- Expected citation objects supplied: `maintainer2021`; missing: none.
- Missing linked qualification bodies: none.
- Truncated additions: ua-transition (records); ua-response (records); bitpay2018 (characters); es-rule (records); es-response (records). Unresolved targets: 0.
- Context: 8653/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/9` in [answers.json](answers.json).

- **partial — Cite comment 949742904 and its date**
  Excerpt: “attempted unpublish on October 22, 2021”. Gives the date and author/evidence ID but not the precise comment ID 949742904.
- **partial — Distinguish attempted and reported implemented actions**
  Excerpt: “reported suspect account hijack and attempted unpublish”. Correctly qualifies attempted removal but omits support contact and implemented deprecation; ua-transition was truncated from context.
- **not_met — Keep the policy explanation tentative**
  Excerpt: “The evidence does not establish a formal succession procedure”. Discusses unrelated succession/access uncertainty rather than the tentative unpublish-policy explanation.
- Additional failure/caveat: Omits the requested action sequence even though citation metadata is available; the substantive action record was rejected by the record cap.
- Additional failure/caveat: Describes the account report as an AI draft, blurring historical-source authorship and pack annotation authorship.

### abstain

What percentage of npm maintainer transitions fail, and what were six-month losses?

**A_text_only**

- Initial selection: `es-limit`, `search-scope`.
- Added via relationships: none.
- Record bodies supplied: `es-limit`, `search-scope`.
- Missing expected record bodies: `selection`, `ua-limit`.
- Expected citation objects supplied: none; missing: `bitpay2018`.
- Missing linked qualification bodies: selection (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 927/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/10` in [answers.json](answers.json).

- **met — Do not estimate a rate or fabricate losses**
  Excerpt: “it is not possible to attribute a failure percentage or quantify losses over six months”. Abstains from both unsupported quantities.
- **met — Distinguish a bounded negative check from an exhaustive search**
  Excerpt: “found no results within one specific report”. Keeps the negative check bounded and explicitly says follow-up absence is not established.
- Additional failure/caveat: Ends with a reference to selection even though that record body was not admitted.

**B_relationships**

- Initial selection: `es-limit`, `search-scope`.
- Added via relationships: selection (qualification_refs from es-limit); npm2018 (evidence_refs from es-limit); bitpay2018 (evidence_refs from es-limit).
- Record bodies supplied: `es-limit`, `search-scope`, `selection`.
- Missing expected record bodies: `ua-limit`.
- Expected citation objects supplied: `bitpay2018`; missing: none.
- Missing linked qualification bodies: none.
- Truncated additions: none. Unresolved targets: 0.
- Context: 4490/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/11` in [answers.json](answers.json).

- **met — Do not estimate a rate or fabricate losses**
  Excerpt: “does not include specific percentages regarding npm maintainer transitions failures nor details on six-month losses”. Does not fabricate the requested quantities, despite a separate fabricated source/incident association.
- **partial — Distinguish a bounded negative check from an exhaustive search**
  Excerpt: “broader archival searches were not performed”. Preserves that broader research was not done, but does not clearly delimit the performed check to named sections of one report.
- Additional failure/caveat: Falsely associates BitPay with an October 2021 ua-parser security update. The admitted BitPay citation is a December 2018 Copay report.
- Additional failure/caveat: Calls source evidence IDs record IDs, weakening traceability.

### supersession

Does publishing a patched version prove every affected machine is clean?

**A_text_only**

- Initial selection: `candidate-synthetic`, `ua-limit`.
- Added via relationships: none.
- Record bodies supplied: `candidate-synthetic`, `ua-limit`.
- Missing expected record bodies: `corrected-synthetic`, `correction-synthetic`.
- Expected citation objects supplied: none; missing: `advisory2021`.
- Missing linked qualification bodies: selection (not expanded).
- Truncated additions: none. Unresolved targets: 0.
- Context: 884/9000 characters. Generation: completed; completion reason `length`. Raw answer: `answers.json#/answers/12` in [answers.json](answers.json).

- **met — Retain original as a superseded synthetic candidate, not testimony**
  Excerpt: “identified as flawed and superseded”. Explicitly identifies the retained candidate as synthetic, flawed, and superseded.
- **partial — Explain correction rationale and link both versions**
  Excerpt: “superseded by corrected versions detailed in correction-synthetic”. Names a correction link but not the corrected-synthetic replacement ID; its actual body was not supplied. Rationale is supplemented with unrelated unknowns.
- **met — Do not report a measured evaluation result**
  Excerpt: “no direct proof that the remediation process has been completed successfully”. Does not claim a measured evaluation result.
- Additional failure/caveat: Discusses correction-synthetic despite its body being absent; most of the answer expands unrelated unknowns rather than tracing the preserved correction rationale.

**B_relationships**

- Initial selection: `candidate-synthetic`, `ua-limit`.
- Added via relationships: selection (qualification_refs from candidate-synthetic); corrected-synthetic (superseded_by from candidate-synthetic); correction-synthetic (related_refs from candidate-synthetic); maintainer2021 (evidence_refs from ua-limit); advisory2021 (evidence_refs from ua-limit); ua-response (outcome_ref from correction-synthetic).
- Record bodies supplied: `candidate-synthetic`, `corrected-synthetic`, `correction-synthetic`, `selection`, `ua-limit`, `ua-response`.
- Missing expected record bodies: none.
- Expected citation objects supplied: `advisory2021`; missing: none.
- Missing linked qualification bodies: none.
- Truncated additions: ua-transition (depth_or_expansions). Unresolved targets: 0.
- Context: 7390/9000 characters. Generation: completed; completion reason `stop`. Raw answer: `answers.json#/answers/13` in [answers.json](answers.json).

- **partial — Retain original as a superseded synthetic candidate, not testimony**
  Excerpt: “Synthetic corrections made by an AI without historical speaker input”. Recognizes synthetic status but does not identify and retain the original candidate as explicitly superseded.
- **partial — Explain correction rationale and link both versions**
  Excerpt: “additional precautions beyond just patching”. Explains the broad corrected rationale and names corrected-synthetic, but does not link candidate-synthetic to correction-synthetic and its replacement.
- **met — Do not report a measured evaluation result**
  Excerpt: “do not provide actual recovery evidence or a measured outcome”. Explicitly avoids treating the synthetic exercise as measured recovery.
- Additional failure/caveat: Attributes available replacements to maintainer2021, although patch-version listings came from advisory2021.
- Additional failure/caveat: Calls evidence IDs record IDs; does not explicitly trace both sides of supersession despite their availability.

## Limitations and smallest next change

This is one consumer, one model, one small AI-authored pack, seven authored questions, and one fixed-order run. Expected answers are not independent human gold labels. The record index is repeated in every export row; the adapter can inspect all metadata but supplies only bounded admitted content. That workaround adds annotation cost and can expose links whose targets were not admitted. Full source pages are unavailable offline. Character budgets are not token budgets, and seven output-truncated answers limit behavioral interpretation.

The smallest justified implementation follow-up is a separate, preregistered test of **query-relevance ordering for nonmandatory related-record edges**, retaining qualification/supersession priority and the same limits. The trace question provides a concrete counterexample: a less relevant transition consumed the last record slot before the directly relevant action record. Do not modify the exporter or tune to question IDs. Retain this first run as the baseline, and arrange human review of unsupported attributions before making effectiveness claims. A separately labeled output-budget sensitivity run could distinguish completion truncation from reasoning failures; it was not performed here.

No causal, predictive, comparative-format, or hallucination-rate conclusion follows. The experiment supports a narrower finding: this adapter can add expected context within explicit bounds, but added context alone did not ensure faithful answers.
