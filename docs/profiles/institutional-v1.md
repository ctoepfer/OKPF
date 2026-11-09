<!-- SPDX-License-Identifier: Apache-2.0 -->

# Institutional reliability profile v1

Status: experimental application profile. The original layout below remains
valid. An additive `review-v1` layout and offline comparison command are
documented in [institutional review](../institutional-review.md).

`okpf.profile.institutional.v1` is an optional application profile for
institutional post-mortems, governance failure modes, and design-review datasets.
It treats institutions as reliability systems: authority, resources, stressors,
safeguards, and observed outcomes can be compared without turning a historical
narrative into a universal prescription. Validation establishes structure, not
factual accuracy, institutional legitimacy, or causal proof.

For new institutional evidence authoring, start with the
[provisional examples](../institutional-evidence-packs.md). This earlier scaffold
remains supported and opt-in. Reconciliation requires experience with reviewed
examples and actual consumers. Neither the profile nor the example conventions
establishes causal or predictive validity.

## Packaging and manifest

The profile uses OKPF Core v0.1 (`okpf_version` `0.1` or `0.1.0`). A pack MUST
satisfy the Core manifest schema and the
[profile manifest schema](../../schemas/profiles/institutional/v1/profile_manifest.json).
It MUST set `profile` to `okpf.profile.institutional.v1` and SHOULD also list that
identifier in the standard `profiles` array for discovery.

The required `institutional_profile` block contains `domain_family`, an
`observation_window` with integer `start_year` and `end_year`, `coding_standard`
(`single_coder`, `dual_coder_reconciled`, `consensus_panel`, or `panel_consensus`), `sampling_frame`,
and `boundary_conditions` (string tags; an empty array is allowed). The start
year MUST NOT exceed the end year. The sampling frame SHOULD identify the cohort
denominator and selection method, including quiet failures and successful cases
where available. A purposive seed is not a representative cohort.

At least one case MUST exist under `cases/`. Cases are UTF-8 JSON or safe YAML
(`.json`, `.yaml`, `.yml`), one object per file; nested directories are supported.
They SHOULD be declared as `artifacts` with `role: "domain_artifact"`. They are
domain documents, not universal Core records; declaring them under `records`
would additionally require the Core record envelope. Unknown optional fields
remain allowed. License and usage policy retain their separate Core meanings.

## Original case contract

The [case schema](../../schemas/profiles/institutional/v1/case_record.json)
requires `id`, `canonical_name`, `domain`, `topology`, `stressor`, `intervention`,
`outcomes`, `perspectives`, `structural_divergences`, and `unobserved_variables`.
IDs MUST contain only ASCII letters and digits and MUST be unique within a pack;
filenames may contain hyphens. The validator checks every case, including files
not listed in the manifest. Non-JSON/YAML files under `cases/` are rejected;
keep documentation elsewhere.

`topology` describes resource type, actor distribution, funding, and credential
architecture. Actor distribution and credential architecture are nonempty,
open objects: domain-specific counts, tiers, custody models, and explicit unknowns
belong here. `stressor.telemetry_onset` is `rapid`, `delayed`, or `chronic`.
`intervention` contains `type`, `mechanism`, and `formal_safeguards_active` (string
tags, possibly empty). An empty safeguards list means none recorded, not proof
that none existed.

`outcomes` is a nonempty map keyed by `t_plus_N`, where N is a nonnegative integer.
Each slice MUST contain nonblank `status` and `reporting_source` strings.
Producers SHOULD state `outcome_time_origin` and `outcome_time_unit`, distinguish
observations within an interval from measurements at its endpoint, and explicitly
mark unobserved horizons instead of inventing follow-up results. The manifest
observation window covers collected evidence, not hypothetical outcome horizons.

`perspectives` MUST contain three nonblank strings:

- `formal_charter`: de jure rules, or an explicit statement that they are unknown.
- `shadow_practice`: observed de facto practice, with uncertainty attributed.
- `post_mortem_consensus`: a sourced synthesis, including disagreement or limits
  on consensus where relevant.

Separating charter from practice is structurally mandatory because formal
safeguards do not establish that those safeguards operated. Collapsing the two
would hide the very implementation gaps a reliability review needs to detect.
The schema enforces distinct fields; reviewers must assess their substance.

`structural_divergences` contains objects with `factor`, `analog_comparison`, and
`divergence_reason`; an empty array means no comparison was recorded. These fields
make differences in enforcement, distribution costs, authority, or feedback
latency explicit before analogies are transferred across institutions.

`unobserved_variables` MUST contain at least one nonblank string documenting
missing or unmeasured evidence. These flags counter the telemetry illusion:
what a dataset measures is not everything that happened. Explicit denominators,
divergences, source attribution, and negative evidence help expose historiographical
bias; they cannot eliminate it. Producers SHOULD retain primary-source citations
in optional `evidence_sources` and label analyst interpretation separately.

## Validation

From the repository with development dependencies installed:

```bash
python3 reference/python/okpf_validate.py examples/institutional --profile okpf.profile.institutional.v1
PYTHONPATH=reference/python python3 -m okpf validate examples/institutional --strict-profile
```

Python callers can use `okpf.institutional.validate_institutional_pack(path)`;
it returns the reference validator's `ValidationResult`. Both directories and
`.kpack` ZIP archives are supported. Explicit profile selection, or
`--strict-profile` on a declaring manifest, enables mandatory profile checks.
Without these options, Core validation remains independent of this profile.
Schemas are bundled with the Python package and resolved locally; validation
never fetches citations or schema URLs and never executes case content.

The [seed pack](../../examples/institutional/manifest.json) documents the 2018
event-stream incident using [npm's incident report](https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident)
and [BitPay's response](https://www.bitpay.com/blog/copay-npm-security-update).
It is a single-coder scaffold with explicit missing observations. The experimental [review command](../institutional-review.md) now compares
explicit declarations and reports mismatches; it does not infer causes or
predict outcomes. Signing remains optional and external to Core validation.
