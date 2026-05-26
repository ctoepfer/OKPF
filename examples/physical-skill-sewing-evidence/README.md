<!-- SPDX-License-Identifier: Apache-2.0 -->

# Physical Skill Sewing Evidence Example

This is a tiny, fictional OKPF example pack using the `physical-skill-evidence` profile.

It demonstrates Hybrid Mode: the pack preserves fictional physical-process evidence artifacts while adding OKPF records, provenance, limitations, non-claims, and evaluation metadata.

This example is illustrative. It is not an executable sewing policy. It is not robot-control guidance. It does not prove transfer to another machine or robot.

This example demonstrates how to package evidence, metadata, limitations, and evaluation context around a physical-process dataset.

The included files are small fabricated samples. They are not real robot data, real operator data, model weights, executable policies, safety instructions, or machine-control guidance.

## What It Shows

- Evidence artifacts: a fictional demonstration episode, control log, calibration bundle, and source embodiment description
- Representation artifacts: phase labels inside the episode sample
- Policy artifacts: non-executable policy metadata
- Validation artifacts: transfer claim, transfer status, source-hardware evaluation, limitations, and non-claims
- Advisory `physical_skill_evidence.claim_level`
- Advisory `physical_skill_evidence.transfer_claim`

## Artifact Categories

| Category | Example files | Purpose |
|----------|---------------|---------|
| Evidence | `artifacts/datasets/example-episode.jsonl`, `artifacts/telemetry/control-log.csv`, `artifacts/calibration/calibration-bundle.json`, `artifacts/embodiment/source-system.json` | Show the fictional source episode, control log, calibration context, and source system description. |
| Representation | `artifacts/datasets/example-episode.jsonl` | Demonstrate phase labels and condensed observations as a derived view of the fabricated capture. |
| Policy | `artifacts/policy/policy-metadata.json` | Show how policy-related metadata can be packaged without including executable policies, model weights, or runtime instructions. |
| Validation | `artifacts/transfer/transfer-claim.json`, `artifacts/transfer/transfer-status.json`, `artifacts/evals/source-hardware-eval.json` | State validation scope, known limits, non-claims, and fictional source-hardware evaluation context. |

## Transfer Claim Summary

| Field | Value |
|-------|-------|
| `claim_level` | `evidence_for_adaptation` |
| `validation_scope` | `source_hardware_only` |
| Required adaptation | Local calibration, fine-tuning/adaptation outside OKPF, and human supervision |
| Known limits | Not validated on different hardware, not validated on different material classes, not safe for unsupervised operation |
| Known non-claims | Does not guarantee transfer, does not define executable robot control, does not certify safety |

## Core Limitation

A physical skill evidence pack is evidence for adaptation and validation, not an installable robot skill.
