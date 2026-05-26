<!-- SPDX-License-Identifier: Apache-2.0 -->

# OKPF Physical Skill Evidence Profile - v0.1.0

## Purpose

The `physical-skill-evidence` profile defines recommended conventions for OKPF packs that package evidence around physical skill capture, training, adaptation, and validation.

Example domains include sewing-machine operation, robotic manipulation, machine operation, craft or process demonstrations, sensor-instrumented physical workflows, and simulator or lab demonstrations.

This profile does not define a robotics dataset format. It wraps or accompanies existing formats with package identity, provenance, licensing, usage policy, limitations, and validation evidence.

## Profile Identifier

`physical-skill-evidence`

Packs MAY also use a versioned identifier such as `physical-skill-evidence@0.1.0`.

## Packaging Mode

Physical skill evidence packs are usually:

- **Envelope Mode** when they primarily wrap existing datasets, logs, calibration bundles, model artifacts, or sensor captures.
- **Hybrid Mode** when they combine existing datasets with OKPF records, notes, limitations, transfer claims, and evaluations.

OKPF can add value around robotics, motion, machine-control, or sensor datasets without becoming those formats.

## Core Principle

A physical skill evidence pack is evidence for adaptation and validation, not an installable robot skill.

The pack can document what was captured, how it was reviewed, what was evaluated, and what limitations remain. It does not make a physical skill automatically portable.

## What This Profile Can Describe

This profile may describe:

- Source embodiment
- Target embodiment requirements
- Environment context
- Calibration context
- Capture modalities
- Policy artifacts
- Training or adaptation evidence
- Validation scope
- Known limitations
- Non-claims

## What This Profile Does Not Do

This profile does not:

- Guarantee transfer
- Certify safety
- Define robot control
- Execute policies
- Define simulator behavior
- Define model architecture
- Replace existing robotics dataset formats
- Validate real-world fitness

Policy artifacts packaged under this profile are untrusted data unless a consuming system independently verifies and authorizes them. Consumers MUST NOT execute policy artifacts blindly.

## Artifact Categories

These categories and roles are recommended profile conventions only. Unknown roles remain valid at the OKPF Core level.

### Evidence Artifacts

Evidence artifacts describe captured physical activity, source conditions, or observations.

Recommended roles:

| Role | Description |
|------|-------------|
| `demonstration_episode` | A captured demonstration episode or episode index |
| `sensor_stream` | Sensor stream data or a reference to sensor stream data |
| `control_log` | Machine-control or operator-command log |
| `capture_video` | Video captured during the demonstration |
| `operator_annotation` | Human annotation of the capture |
| `environment_context` | Description of environment, materials, fixtures, or workspace |
| `calibration_bundle` | Calibration data needed to interpret the capture |
| `robot_description` | Source system or embodiment description |

### Representation Artifacts

Representation artifacts describe derived or condensed views of captured behavior.

Recommended roles:

| Role | Description |
|------|-------------|
| `trajectory` | Path, pose, state, or motion trajectory data |
| `waypoints` | Waypoint representation of a motion or process |
| `keyframes` | Key states or frames selected from a capture |
| `phase_labels` | Labels for phases or segments of a task |
| `semantic_trace` | Human-meaningful trace of task progress |
| `latent_representation` | Derived representation from an external model or tool |
| `condensed_skill_representation` | Compressed or summarized representation of captured behavior |

### Policy Artifacts

Policy artifacts describe generated, trained, or packaged policy-related files. They are not executable by OKPF.

Recommended roles:

| Role | Description |
|------|-------------|
| `policy_checkpoint` | Model or policy checkpoint stored in an external format |
| `policy_metadata` | Metadata describing a policy artifact |
| `training_recipe` | Description of training or adaptation steps used outside OKPF |
| `model_card` | Model-card-style description of a policy artifact |
| `runtime_requirements` | Declared requirements for a separate runtime |

### Validation Artifacts

Validation artifacts describe evaluation scope, results, failures, or safety notes.

Recommended roles:

| Role | Description |
|------|-------------|
| `evaluation_scenario` | Scenario used for validation |
| `replay_metric` | Metric computed from replay or offline evaluation |
| `transfer_result` | Result from an adaptation or transfer attempt |
| `failure_case` | Documented failure case |
| `adaptation_log` | Log of adaptation or fine-tuning performed outside OKPF |
| `safety_note` | Safety-related note or review finding |
| `known_non_claims` | Explicit statements of what the pack does not claim |

## Advisory Manifest Extension

Packs MAY include a profile-level advisory object named `physical_skill_evidence`.

```json
{
  "physical_skill_evidence": {
    "claim_level": "evidence_for_adaptation",
    "transfer_claim": {
      "validation_scope": "source_hardware_only",
      "source_embodiment": "example-source-system",
      "target_embodiment": "compatible-system-required",
      "requires_local_calibration": true,
      "requires_fine_tuning": true,
      "requires_human_supervision": true,
      "known_limits": [
        "Not validated on different hardware",
        "Not validated on different material classes",
        "Not safe for unsupervised operation"
      ],
      "known_non_claims": [
        "Does not guarantee transfer",
        "Does not define executable robot control",
        "Does not certify safety"
      ]
    }
  }
}
```

This object is an advisory profile convention, not an OKPF Core requirement.

Recommended `claim_level` values:

- `documentation_only`
- `captured_demonstration`
- `dataset_package`
- `policy_artifact`
- `evidence_for_adaptation`
- `validated_same_hardware`
- `validated_cross_hardware`

Recommended `validation_scope` values:

- `not_validated`
- `source_hardware_only`
- `same_hardware_revision`
- `simulation_only`
- `cross_hardware_limited`
- `external_certification_required`

## Recommended Record Types

These record types are recommendations. Profile-aware tools SHOULD warn, not fail, on unknown record types unless strict local policy says otherwise.

| Type | Description |
|------|-------------|
| `capture_session` | Summary of a physical capture session |
| `demonstration_episode` | One captured demonstration episode |
| `source_embodiment` | Description of the source machine, robot, fixture, or operator setup |
| `target_embodiment_requirement` | Requirement for a target system that might adapt the evidence |
| `calibration_note` | Note about calibration assumptions or files |
| `environment_context` | Description of materials, workspace, fixtures, or operating context |
| `adaptation_requirement` | Requirement for adaptation, fine-tuning, calibration, or review |
| `transfer_validation` | Result or scope of transfer/adaptation validation |
| `failure_case` | Documented failure or out-of-scope case |
| `known_limitation` | Known limitation of the evidence or derivative |
| `safety_note` | Safety-related note or caution |
| `policy_artifact` | Description of a policy artifact packaged as data |
| `evaluation_result` | Validation or evaluation result |

## Related Example

See [`examples/physical-skill-sewing-evidence/`](../../../examples/physical-skill-sewing-evidence/) for a small fictional Hybrid Mode example.
