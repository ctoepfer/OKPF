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
    discretion: approve releases under the proposed threshold
    residual_risk: accountability for approvals; magnitude unknown
  - group: downstream operators
    discretion: choose deployment timing
    residual_risk: remediation costs; magnitude unknown
---
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Synthetic release council proposal

These explicit declarations describe a synthetic proposed design, not observed
implementation. Risk allocations and exit costs require investigation. The
stakeholder rows are proposal assertions, not measurements or a complete census.

Narrative alone is not used to infer custody or authority. See
`docs/institutional-review.md` for the YAML front matter and minimal Markdown
scalar-declaration forms understood by the experimental reviewer.
