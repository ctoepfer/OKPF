<!-- SPDX-License-Identifier: Apache-2.0 -->

# OKPF Human Correction Loop Profile - v0.1.0

## Purpose

The `human-correction-loop` profile defines recommended conventions for OKPF packs where a system produces a candidate output and a human corrects, approves, rejects, ranks, labels, or adjusts it.

This profile is useful when the durable knowledge is not only the final answer, but the correction event itself: what the system proposed, what the human changed, why, who reviewed it, and what outcome evidence later supported or limited the correction.

Examples include:

- AI-generated zymurgy recipe corrected by a brewer
- Receipt category corrected by a user
- Transaction category corrected by a bookkeeper
- Support ticket routing corrected by an agent
- Email triage action corrected by a user
- Code review classification corrected by a developer
- Legal or risk flag corrected by a reviewer

The profile does not define a model training pipeline, fine-tuning format, reward model format, specific domain schema, or universal quality score.

## Profile Identifier

`human-correction-loop`

Packs MAY also use a versioned identifier such as `human-correction-loop@0.1.0`.

## Packaging Mode

Human correction loop packs are usually Hybrid Mode:

- Source artifacts preserve the prompt, candidate output, corrected output, diff, and outcome evidence.
- OKPF records summarize correction events, feedback, limitations, and review state.
- Optional training-ready derivatives provide compact examples derived from the source artifacts.

The source artifacts remain authoritative. Training derivatives are derived views.

## Recommended Record Types

These values are profile-level recommendations, not OKPF Core requirements.

| Type | Description |
|------|-------------|
| `correction_event` | A human correction, approval, rejection, ranking, label change, or adjustment event |
| `candidate_output` | Original system-generated candidate |
| `corrected_output` | Human-adjusted or approved output |
| `human_feedback` | Human explanation, annotation, or rationale |
| `review_note` | Review state, reviewer comments, or caveats |
| `outcome_observation` | Measured, observed, or reported outcome after use |
| `training_derivative` | Compact derived example for downstream training or evaluation use |
| `evaluation_example` | Example for evaluating future candidate outputs |
| `known_limitation` | Known limitation of the correction, reviewer context, or outcome evidence |

## Recommended Correction Event Fields

A correction event SHOULD include or map to:

- `id`
- `record_type`
- `task`
- `candidate_ref`
- `corrected_ref`
- `correction_type`
- `feedback_summary`
- `contributor_context`
- `confidence`
- `review_status`
- `outcome_ref`
- `source_refs`
- `metadata`

These are profile conventions. They are not required by OKPF Core.

## Recommended Correction Types

- `edit`
- `approve`
- `reject`
- `rank`
- `label_change`
- `parameter_adjustment`
- `substitution`
- `process_adjustment`

## Recommended Review Status Values

- `unreviewed`
- `reviewed`
- `outcome_pending`
- `outcome_recorded`
- `validated_personal_use_only`
- `validated_by_domain_expert`

## Contributor Expertise Context

User expertise varies and should be captured as metadata so consumers can filter, weight, or review examples.

Recommended fields:

- `expertise_level`
- `domain_experience_years`
- `batch_count_estimate`
- `professional_context`
- `certifications_or_roles`
- `sensory_training_level`
- `confidence`
- `reviewer_id`
- `review_notes`

Recommended `expertise_level` values:

- `novice`
- `intermediate`
- `advanced`
- `professional`
- `unknown`

Expertise metadata is context for review and weighting. It does not prove correctness.

## Training Derivatives

Correction loops are a practical source of training-ready derivatives, but derivatives are optional. When present, they SHOULD preserve references to:

- Candidate output
- Corrected output
- Correction rationale
- Contributor context
- Outcome evidence, when available
- Known limitations

OKPF packages these files and their provenance. It does not run training, evaluate model quality, or grant training permission.

## Related Example

See [`examples/zymurgy-recipe-correction/`](../../../examples/zymurgy-recipe-correction/) for a fictional Hybrid Mode example combining fermentation and human correction loop conventions.
