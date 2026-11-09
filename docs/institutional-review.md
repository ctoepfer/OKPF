<!-- SPDX-License-Identifier: Apache-2.0 -->

# Experimental institutional review command

`okpf review` is an offline comparison aid separate from OKPF Core validation.
It compares explicit proposal declarations with validated institutional cases,
retains their evidence and uncertainty, and emits Markdown. It does not discover
institutional laws, identify causal effects, simulate governance, certify an
intervention, or establish predictive validity. A field shared by two records
is not evidence that the institutions are historical twins.

```bash
PYTHONPATH=reference/python python3 -m okpf review \
  --pack examples/institutional \
  --proposal examples/institutional/proposals/release-council.md

PYTHONPATH=reference/python python3 -m okpf pack examples/institutional out/institutional.kpack
PYTHONPATH=reference/python python3 -m okpf review \
  --pack out/institutional.kpack \
  --proposal examples/institutional/proposals/release-council.md --limit 3
```

No additional Python dependencies or remote services are required beyond the
reference package's existing JSON Schema and YAML dependencies. The command
validates the institutional profile strictly before reading cases for review.
Invalid records, missing perspectives, empty unobserved-variable lists, reversed
observation windows, and unsafe paths cause errors. Files under `cases/` must
be JSON or YAML; keep explanatory Markdown elsewhere. Plain Core validation
still does not impose institutional requirements. No pack content is executed.

## Proposal declarations

A Markdown proposal can begin with YAML front matter, as in this **synthetic**
example (the opening `---` must be the first line):

```yaml
---
resource_type: public_npm_package
authority_concentration: distributed_council
exit_barrier: costly_migration
credential_custody: multisig_threshold
feedback_cadence: monthly_review
boundary_conditions:
  - automated_execution
  - near_zero_distribution_cost
stakeholders:
  - group: release council
    discretion: approve releases
    residual_risk: accountability for approval decisions
  - group: downstream operators
    discretion: deployment timing
    residual_risk: remediation cost is unmeasured
---
```

Alternatively, unfenced lines such as `- credential_custody: multisig_threshold`
are parsed for the five scalar variables. Code examples are ignored. Use front
matter for boundary tags and stakeholder rows. Duplicate keys and malformed
values are rejected. Absent values and explicit `unknown`, `not_observed`,
`not_established`, or `not_yet_checked` are unmeasured, not matches.

The tool does not extract claims from arbitrary prose, infer custody from
maintainer counts, or translate synonyms automatically. Declare the same tokens
in proposal and case if they mean the same thing. Narrative interpretation is
left to the author; declarations are not evidence of implementation. Counts,
feedback periods, copying costs, and geographic enforcement are not inferred
when the evidence is missing.

## Matching and report scope

Five explicit scalar variables are compared: resource type, authority
concentration, exit barrier, credential custody, and feedback cadence. Cases
are ordered by count of exact matches, then count of comparable variables,
then case ID. The report shows matching fields and comparison coverage out of
five. Missing values neither agree nor disagree. With zero positive matches,
the command explicitly abstains; listed cases are context only. Results are not
probabilities, calibrated structural distances, or evidence of effectiveness.

The four report sections contain declarations, ranked records and their
interventions/outcomes, mismatches, and a stakeholder matrix. All perspectives,
unobserved variables, recorded divergences, review status, and source citations
remain visible. The matrix reproduces proposal assertions; it does not infer
stakeholder consent, benefits, losses, or completeness. Undeclared groups and
risk allocations are marked unknown.

The bundled [mismatch rule table](../reference/python/okpf/mismatch_rules.json)
is experimental, version-controlled data. It adds caution text when declared
values differ. Boundary-tag differences are reported separately: absence of a
tag means undocumented, not false. Speed of defection and geographic enforcement
remain unmeasured; no numerical delta is fabricated. Rules are loaded from the
installed package, not supplied or executed by the pack.

The sample contains the same 2018 event-stream episode in two serializations,
with distinct record IDs and explicit scope notes. Two rows are not two
independent observations. The new fixture deliberately records unknown counts,
custody, exit costs, feedback cadence, and long-run outcomes. The retained
sources do not establish maintainer burnout. The larger
[institutional-evidence suite](institutional-evidence-packs.md) remains a separate
Core-record example and is not silently converted into strict cases.

## Compatible experimental case layout

Existing `outcomes`, `credential_architecture`, `formal_safeguards_active`, and
`factor`/`analog_comparison`/`divergence_reason` cases remain valid.
Set `case_layout: review-v1` to opt into the new shape in the existing
[case schema](../schemas/profiles/institutional/v1/case_record.json):

- `topology`: resource type, actor distribution (`primary_decision_makers`,
  `active_participants`, `dependent_tier`), credential custody, and exit barrier.
  Counts are nonnegative integers or explicit `null` when unknown. Custody and
  exit enums include `unknown`. Authority concentration and feedback cadence
  are optional nonblank strings.
- `stressor`: category, event description, and onset (`acute`, `rapid`, `delayed`,
  `chronic`); `rapid` is retained for compatibility.
- `intervention`: type, mechanism, and `formal_safeguards` string array.
- `telemetry`: nonblank `t_immediate`, `t_stabilized`, `t_terminal` descriptions;
  explicitly state when a horizon is unobserved rather than asserting closure.
- Nonblank formal charter, shadow practice, and post-mortem synthesis fields;
  nonempty unobserved-variable list. Consensus must not be fabricated.
- Divergences with `parameter`, `historical_analog`, `divergence_rationale`.

A marked new case cannot pass via the old branch. Unknown optional fields remain
allowed. This is a provisional representation, not a promotion to a stable
institutional science profile.

The manifest keeps the established root `profile` and `institutional_profile`
block. Both `panel_consensus` and legacy `consensus_panel` are accepted coding
labels; neither establishes that review occurred. Setting
`institutional_profile.layout` to `review-v1` opts into the proposed domain enum
(`digital_infrastructure`, `common_pool_resources`, `mutual_credit_clearing`,
`municipal_cooperatives`, `platform_governance`) and at least one boundary tag.
Unmarked existing manifests retain open domain strings and optional empty tags.
This avoids retroactively invalidating already published packs.

## Optional packaging and signing test

The CLI has no built-in signer. The interoperability test uses OpenSSH's existing
SSH signature envelope with an Ed25519 key and a detached signature over the
exact `.kpack` bytes. It generates an ephemeral key in a test temporary directory,
verifies using an explicit allowed-signers file, then confirms tampering fails.
It runs when `ssh-keygen` is installed; otherwise only that optional test skips.
No example private key or asserted real author credential is committed.

For a user-managed signing key and trusted allowed-signers file:

```bash
ssh-keygen -Y sign -f "$SIGNING_KEY" -n okpf-review out/institutional.kpack
ssh-keygen -Y verify -f "$ALLOWED_SIGNERS" -I "$SIGNER_ID" \
  -n okpf-review -s out/institutional.kpack.sig < out/institutional.kpack
```

The `.sig` sits beside the archive so it does not change the bytes being signed;
this is an external distribution convention, not a new Core signature format.
Core validation and review do not require or verify it. Verification establishes
control of an accepted key and integrity of the supplied bytes, not identity,
trusted timestamps, source truth, independent review, or methodological validity.
Repacking changes the signed bytes even if logical content is unchanged.

## Verification limits

Tests exercise schema compatibility and rejection, safe proposal parsing,
explicit-variable ranking, mismatch warnings, unknown-value abstention,
stakeholder attribution, CLI output, directory/archive equivalence, and optional
signing/tamper rejection. They do not measure retrieval usefulness, causal
identification, or predictive accuracy. Source URLs are not fetched during
review. Human source review and evaluation on real proposals remain future work.

## Proposal linter (experimental)

```bash
PYTHONPATH=reference/python python3 -m okpf lint-proposal --proposal proposal.yaml
PYTHONPATH=reference/python python3 -m okpf lint-proposal \
  --proposal proposal.md --pack examples/institutional --json
```

`lint-proposal` reads UTF-8 JSON (`.json`), a single YAML document (`.yaml`,
`.yml`), or Markdown/plain text with YAML front matter. Duplicate mapping keys,
unsafe YAML constructors and malformed inputs are rejected. Arbitrary prose can
be linted, but prose promises and fenced examples do not satisfy structured
commitments. Files are read only; no network, LLM, rollback action or scraper is
invoked. Exit codes are **0** for structural success (warnings allowed), **1** for
schema errors, and **2** for unreadable/invalid input or an invalid supplied pack.
`--json` emits machine-readable diagnostics to stdout.

A synthetic proposal declaration:

```yaml
evasion_vectors:
  - tactic_category: nominal_compliance
    mechanism: Passive multisig signers approve without independent review.
    telemetry_impact: Approval counts overstate independent oversight.
    detection_signature: Repeated approvals without recorded review evidence.
pre_mortem_falsification:
  leading_indicator_failure: More than two unreviewed releases during six months.
  evaluation_horizon_months: 6
  automated_off_ramp:
    trigger_condition: More than two unreviewed releases at the month-six review.
    fallback_action: Suspend releases pending independent review.
```

The local Draft 2020-12 `proposal_lint.json` requires both blocks and validates
nonblank descriptions, six tactic categories, a positive integer horizon, and
trigger/action strings. Optional `secondary_stress_signals` contains nonblank
strings. Unknown optional fields are preserved. Historical `case_record.json`
validates these blocks **when present** in either supported layout; they are not
retroactively required of existing cases. This deliberately adapts the supplied
required-field sketch to preserve existing institutional v1 packs. There is no
new `case.json`, Core field, or profile identifier.

The Adversarial Gaming Audit recognizes lexical mentions of multisig, housing or
retention, thresholds, and audits or approvals. These include quoted and negated
mentions; they are inspection hints, not evidence that a policy adopts a safeguard.
With `--pack`, candidates require at least one exact declared topology match and
a corresponding tactic category. All qualifying vectors are reported with case
ID, source path, matching fields, review status, citations and unobserved variables.
No match means no evidence found, not safety. Repeated serializations are not
counted as independent historical precedents. Cases declaring a `tombstone` are
excluded conservatively; neither its signature nor replacement is verified.

Passing checks establishes structure only. It does not prove that a threshold is
measurable, that a commitment predates implementation, that a fallback executes,
or that evasion occurred. The linter does not compute hazard rates, implement a
cohort registry, verify cryptographic revocation, or ingest audit reports. Those
require separate designs and evidence. Human review remains necessary; these
checks do not establish deployment readiness.
