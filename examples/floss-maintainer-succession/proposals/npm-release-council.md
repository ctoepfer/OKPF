---
resource_type: public_npm_package
authority_concentration: distributed_council
credential_custody: multisig_threshold
exit_barrier: costly_migration
feedback_cadence: monthly_review
domain: digital_infrastructure
boundary_conditions:
  - near_zero_distribution_cost
evasion_vectors:
  - tactic_category: nominal_compliance
    mechanism: Hypothetical signers approve releases without independent review.
    telemetry_impact: Approval counts could overstate actual review coverage.
    epistemic_status: hypothetical_proposal_risk
pre_mortem_falsification:
  leading_indicator_failure: At least one release lacks a recorded independent review at the three-calendar-month checkpoint.
  evaluation_horizon_months: 3
  automated_off_ramp:
    trigger_condition: An unreviewed release or missing evidence exists at the checkpoint.
    fallback_action: Pause delegated publishing pending independent review and recorded authorization to resume.
  epistemic_status: synthetic_proposal
---
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Synthetic npm release-council proposal

Use multisig approvals and record the review that each approval attests to.
The declared topology is a proposal assertion, not an observed organizational fact.
No release action is executed by OKPF. Independent signers and a complete release
cohort must be established through separately reviewed operational evidence.
