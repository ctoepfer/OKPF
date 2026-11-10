<!-- SPDX-License-Identifier: Apache-2.0 -->

# Institutional evidence review of 724e677

Reviewed 2026-11-09. **AI-assisted, not independent human review or approval.**
The five cases, manifest and coding ledger remain `pending_dual_review`, with
zero independent codings and no reconciliation. This report reviews the committed
files against accessible primary sources and the retained consumer inputs/answers,
not against previous completion claims. Corrections are local and uncommitted.

Severity: **high** would materially misstate evidence or permit false assurance;
**medium** can mislead interpretation or comparison; **low** is a precision or
traceability weakness; **informational** records a supported claim or explicit
limit. “Supported” means the named source says it, not independently verified truth.
No cited source was inaccessible in this pass. GitHub's Core-JS page and its raw
view were both readable. These live pages are not frozen contemporaneous snapshots;
publication labels do not prove that every sentence existed on publication day.

## Case-level source checks

Pointers below refer to the named YAML files under
[`examples/floss-maintainer-succession/cases`](../../examples/floss-maintainer-succession/cases/).
Source links plus section names identify claim-level evidence; no external source
bodies are redistributed. No conflicting primary testimony was collected. That
means no verified dispute was found, not that the accounts are uncontested.

### Event-Stream — event-stream-2018.yaml

Source E: [npm, 27 November 2018](https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident), opening response account, “The attack” and technical details.

| Pointer / claim | Classification and severity | Correction or open question |
| --- | --- | --- |
| `/stressor/event_description`: deceptive maintainer takeover | Source-reported, informational; E, “The attack”. | Retain attribution to npm; private delegation records are absent. |
| `/intervention/mechanism`, `/telemetry/t_immediate`: removal and ownership response on 26 November | Directly supported report, informational; E opening. | Registry action does not establish endpoint recovery. |
| `/perspectives/shadow_practice`: dependency change and environment-sensitive activation | Supported report, informational; E opening/technical account. | Dependency introduction date is not proof of when the malicious payload first shipped; do not infer that chronology. |
| `/telemetry/t_stabilized`: affected Copay releases but no measured recovery | Medium: horizon label suggests stabilization without evidence. | Added report date and explicit non-stabilization caveat. |
| `/evasion_vectors/0`: nominal compliance | Analyst category attached to reported deception; no observed compliance-metric manipulation. | Preserve mixed epistemic label. Detection task and three-month pre-mortem are proposals. |

Formal succession rules remain unknown. The divergence from accidental defects is
an analytic comparison, not a causal estimate. No independently established
consensus, loss magnitude or safeguard effectiveness follows from E.

### Heartbleed — openssl-heartbleed-2014.yaml

Sources H1: [OpenSSL advisory, 7 April 2014](https://openssl-library.org/news/secadv/20140407.txt), CVE-2014-0160 and affected-user advice; H2: [Mark Cox, 8 August 2023](https://openssl-corporation.org/blog/2023-08-08-finances.html), paragraph beginning “The Heartbleed vulnerability in 2014”.

| Pointer / claim | Classification and severity | Correction or open question |
| --- | --- | --- |
| `/stressor/event_description`, `/telemetry/t_immediate`: heartbeat bounds-check defect and advisory date | Directly supported by H1, informational. | Fix/rebuild advice is historical, not deployment verification. |
| `/intervention/mechanism`: 1.0.1g; two workers, three years, audit | H1 supports fix; H2 explicitly supports funding quantities, informational. | Quantities are attributed retrospective claims, not independently audited staffing data. |
| `/perspectives/shadow_practice`, `/telemetry/t_stabilized`: temporary capacity support | Organizational retrospective, medium horizon ambiguity. | 2023 is reporting date, not demonstrated stabilization nine years after disclosure. Added general horizon caveat. |
| `/structural_divergences/0`: parser defect versus handoff | Low terminology imprecision. | Replaced “parser defect” with “heartbeat bounds-check defect”. |
| `/evasion_vectors/0`, `/pre_mortem_falsification` | Explicit hypothetical reporting bias and retrospective proposal. | No audit suppression or historical review-board policy established. |

H1 is advice, not a governance charter. H2 does not identify staffing's causal
effect on vulnerability incidence. Missing custody, longitudinal outcomes and
counterfactuals remain appropriately uncoded.

### Log4j — log4j-2021.yaml

Source L: [ASF, 14 December 2021](https://news.apache.org/foundation/entry/apache-log4j-cves), opening, CVE-2021-45046, impact FAQ and “How can I get help?”.

| Pointer / claim | Classification and severity | Correction or open question |
| --- | --- | --- |
| `/stressor/event_description`: incomplete initial fix in some non-default configurations | Directly supported by L, informational. | Retain historical scope; this is not a full later vulnerability chronology. |
| `/intervention/mechanism`: 2.16.0 after 2.15.0 and Java 7 path | Supported by L opening, informational. | Source states 13 December release and 2.12.2 Java 7 advice; draft prudently avoids current remediation claims. |
| `/perspectives/formal_charter`: advice/private reporting channel | Supported documentation, low category ambiguity. | Added source-scope caveat: published instructions are not demonstrated succession rules. |
| `/perspectives/shadow_practice`: no defensible population count | Supported by L impact FAQ, informational. | Unknown impact population is not zero impact. |
| `/telemetry`, `/structural_divergences` | Missing downstream outcomes and analyst distinction, informational. | No terminal success, staffing effect or succession equivalence established. |
| `/evasion_vectors/0`, `/pre_mortem_falsification` | Hypothetical definition dilution and retrospective verification proposal. | No evidence of intentional metric gaming; preserve labels and empty source list. |

“Delayed” is an analyst code, not an estimated detection interval. No consensus
or independently observed compliance is supplied by this single organizational report.

### Core-JS — core-js-2023.yaml

Source C: [maintainer's account](https://github.com/zloirock/core-js/blob/master/docs/2023-02-14-so-whats-next.md), [raw view](https://raw.githubusercontent.com/zloirock/core-js/master/docs/2023-02-14-so-whats-next.md), opening, support request, “Roadmap”, and signed date at end.

| Pointer / claim | Classification and severity | Correction or open question |
| --- | --- | --- |
| `/stressor/event_description`, `/telemetry/t_immediate`: exhaustion/support appeal dated 14 February 2023 | Supported self-report and signed date, informational. | Not a diagnosis, financial audit or independently verified collapse. |
| `/intervention/mechanism`: appeal plus roadmap | Directly supported by C, informational. | Appeal/plan does not establish funded delivery. |
| `/perspectives/shadow_practice`: maintenance pressure/indirect dependence | Attributed first-person account, informational. | Keep hours, finances and control records unverified. No adoption percentages are imported. |
| `/perspectives/post_mortem_consensus`, `/structural_divergences` | Explicit analyst inference and rejection of collapse/succession classification. | No consensus or causal evidence; retain. |
| `/evasion_vectors/0`, `/pre_mortem_falsification` | Hypothetical ticket manipulation and proposed funding criterion. | No misconduct allegation or historical three-month threshold supported. |

Low reproducibility limitation: `master` is mutable. Independent reviewers should
retain an authorized snapshot or reviewed revision before promotion. Later outcome
and independent testimony remain missing, not negative observations.

### Urllib3 — urllib3-migration-2023.yaml

Source U: [versioned 2.0.7 migration guide](https://urllib3.readthedocs.io/en/2.0.7/v2-migration-guide.html), timeline, package-maintainer migration, security fixes for 1.26.x, and upgrading issues.

| Pointer / claim | Classification and severity | Correction or open question |
| --- | --- | --- |
| `/stressor/event_description`: compatibility migration/testing guidance | Supported by U, informational. | Guidance is not measured execution. |
| `/intervention/mechanism`: dual-version support and Tidelift | Supported historical statement, medium temporal ambiguity. | Qualified as then-planned support, not a current commitment. |
| `/perspectives/formal_charter`: deprecation timeline | Medium: U uses future-tense planned release dates even in versioned documentation. | Added distinction between planned and verified completion dates; no release chronology inferred. |
| `/perspectives/shadow_practice`, `/telemetry`: issues listed, adoption unmeasured | Appropriately qualified, informational. | Neither actual universal smoothness nor workload reduction follows. |
| `/structural_divergences`, `/perspectives/post_mortem_consensus` | Analyst contrast, informational. | Version migration is not evidence of leadership succession. |
| `/evasion_vectors/0`, `/pre_mortem_falsification` | Hypothetical denominator exclusion and retrospective migration criterion. | No documented gaming or historical three-month commitment. |

The 2023 observation window does not establish a year of follow-up. Added a general
horizon caveat; historic guidance contains plans originating before that window.

## Cross-case findings and changes

- **Medium — misleading schema labels:** `post_mortem_consensus`, `formal_charter`
  and `t_stabilized` can overstate evidence when extracted without the surrounding
  text. Added `classification_notes` to all five cases explicitly identifying
  analyst synthesis, source scope and non-measured horizon labels. Preserved both
  schema layouts and every pending-review flag. No schema changes.
- **Medium — arbitrary precision in exercises:** all three-calendar-month horizons
  and any-event triggers are uncalibrated examples. Existing retrospective labels
  are accurate; added an explicit shared note. Time origin, metric ownership,
  feasibility and decision authority need human design work before use. These are
  not historical precommitments or validated falsification tests.
- **Low — case title and sample:** the pack identifier suggests succession, but
  four episodes are not succession studies. The README already explains this;
  retain the identifier for compatibility. This purposive sample cannot yield
  baseline hazards. `claim_sources` covers only selected pointers; this report
  supplies field-specific checks, not a complete provenance graph.
- **Unresolved:** “delayed/chronic” remain qualitative analyst labels, not measured
  latency; no examined source supports numeric headcounts/custody at event time.
  Empty safeguards mean not coded, not absent. No independent human codings,
  consensus panels or causal estimates have been created. Artifact hashes were
  refreshed after edits; they verify bytes, not truth or source immutability.

## Retained consumer experiment: direct answer review

Evidence: [raw answers](../experiments/institutional-consumer/run-2026-11-08/answers.json),
[exact inputs](../experiments/institutional-consumer/run-2026-11-08/inputs.json),
[coverage](../experiments/institutional-consumer/run-2026-11-08/coverage.json),
[AI judgments](../experiments/institutional-consumer/run-2026-11-08/assessment.json).
All fourteen answers were read. No new inference or ordering change was made.

**Medium — censoring is unequal.** A answers 4 and 12, and B answers 1, 3, 5, 7,
9 (zero-based indices) have `done_reason=length`, each at 384 output tokens.
Thus A is truncated 2/7 and B 5/7. Missing content in those responses is an
observed omission in the returned prefix, not proof it would remain absent with
more output. Explicit false statements within a prefix remain observable errors.
Prompt counts range 372–2542 tokens; these and the output cap fit within the
configured 4096 window, but server counters alone do not independently certify
absence of input truncation. Character budgets are not tokenizer budgets.

| Question / raw answer index | Evidence-based assessment |
| --- | --- |
| qualified-retrieval, 0/1 | A cites `es-assess-containment`, whose body was absent; inline mention is not retrieved evidence. B states recovery/loss limits but also says “no evidence of a succession event”, mixing episode qualifications. B is truncated; the positive qualification does not erase the false generalization. |
| conflicting-interpretation, 2/3 | A discusses one lens; B says “AI draft interpretations” but does not clearly attribute both to one author. Both mix ua-parser and Event-Stream. B's final list is cut off, limiting omission claims. |
| rule-practice, 4/5 | Both truncated. A inflates reported practice into “strict regulatory conformity”; B says absent verification is “casting doubt on the actual implementation”. Missing verification is not contrary evidence. |
| mismatch, 6/7 | Both reject unsupported prevention inference. A invents numeric record labels; B infers “lack of understanding or control” from distinct authority boundaries. B is truncated; those express claims can still be assessed. |
| trace, 8/9 | A calls same-author alternatives “disagreement within the community”. B gives date/author but omits comment ID and action sequence; `ua-transition` was excluded by the six-record cap and B ends mid-reference. Neither metadata coverage nor the returned prefix supports successful traceability. |
| abstain, 10/11 | Both complete and decline unsupported rates/losses. B falsely calls an October 2021 ua-parser update a BitPay report; supplied BitPay metadata concerns 2018 Copay. This error is not an output-cutoff artifact. |
| supersession, 12/13 | A identifies the synthetic superseded candidate using its supplied text but lacks replacement bodies and is cut off. B completes, names the replacement but does not trace candidate → correction → replacement; it wrongly assigns replacement listings to the maintainer account. This failure persists without output truncation. |

**Low — reviewer overstatement corrected by addendum:** the original assessment
of trace B says it describes the account “as an AI draft”. The actual wording is
“This account report is part of an AI draft”, following explicit attribution to
the GitHub commenter. That is ambiguous but can correctly describe packaging;
it does not establish that the model thought the historical speaker was AI.
Treat this item as ambiguous, not a confirmed authorship substitution. Similarly,
A's reference to `correction-synthetic` is available inline: mentioning it alone
is not invented evidence. Its missing full chain and unrelated rationale remain
observable. Original judgments and raw measurements are retained; this report
and linked addendum record the narrower review interpretation.

Coverage counts (A 8/22, B 20/22 expected body pairs; B complete for five questions)
are reproducible availability counts, not accuracy or causal effects. A/B differ
in annotations, citations, admitted bodies, length and processing burden. One
fixed-order run on seven authored questions cannot isolate relationships versus
additional text, establish a format advantage, or measure a general hallucination
rate. No claim of epistemic preservation is justified by reference resolution.

## Operational MCP review and semantic checks

**Medium, fixed — false mismatch on unknown values.**
`packages/okpf-mcp/src/okpf_mcp/operational_review.py::compare` used `prior.lower()`
without stripping or rejecting blanks. Padded unknown values in free-text fields
could be reported as mismatches. Four regression cases failed before the fix and
pass afterward. The fix treats blanks/padded unknowns as unavailable while
preserving the authored value in output. Known-value exact comparison is unchanged.

Other inspected behavior: explicit proposal declarations supply invariants;
regex mentions only select resource candidates and can be negated. Candidate
ordering is deterministic by package/version/mount/case, not relevance or causal
similarity. All five MCP tools are used, labels and source context are retained,
and `valid` means structural lint only. Global optional-data queries cap at 100;
a selected case can be omitted there, though complete case inspection still
contains its authored fields. Truncation is visible. This is a documented
limitation, not evidence that no evasion occurred. No review-ranking change made.

The semantic checker validates local schema, unique/bound concept IDs and exact
UTF-8 definition hashes; it compares full parsed documents, including unknown
fields, to an explicit baseline. Tests cover changed thresholds/denominators,
rehashed definitions and replacement of both files. **No defect requiring a
semantic implementation change found in this bounded review.** Passing without
a baseline proves only consistency. The co-located example baseline is not an
independently authenticated commitment. Signature verification, time attestation,
measurement execution and resistance to unchanged-text gaming remain absent.
Calendar-month end handling and zero-release interpretation need operational
agreement; schema validity does not settle them. No claim of semantic immunity.

## Verification and disposition

Checks: 78 focused reference tests and 57 installed MCP tests pass; lint/format
and strict type checks pass; both packs validate. Full root suite: 450 passed,
seven failures identical to the prior prep-tool set, with no new failures.
The four new unknown-value tests failed before the fix and pass afterward.
Details are recorded in the project implementation log.
Review is AI-assisted and unapproved; changes remain local. No independent coding
ledger entries were added. The [bounded ordering proposal](../experiments/institutional-consumer/ordering-proposal.md)
is a future experiment requiring human review, not an executed result.

## Subsequent execution and publication authorization

The user subsequently authorized the v1 fixed-content ordering experiment, then
a separate full restart after power loss, and commit/push after background work
finishes. These instructions supersede the earlier local-only disposition and
pre-execution human-review requirement above. Human review of the drafts and
answer-quality judgments remains pending; no release-readiness claim is added.
