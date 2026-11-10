<!-- SPDX-License-Identifier: Apache-2.0 -->
# Semantic invariants / anti-masking: draft v0.1

**Experimental artifact convention, not OKPF Core or an institutional-profile
requirement.** Identifier: `okpf.semantic_invariants.draft.v0.1`. Schema:
[`commitment.schema.json`](../../schemas/extensions/semantic-invariants/draft-v0.1/commitment.schema.json).
It is bundled through the reference package's existing schema mechanism.

This draft records what a metric means before evaluating a policy. It makes
changes reviewable; it does not make concepts immune to semantic drift. It does
not establish a trusted timestamp, prove pre-commitment, authenticate a signer,
validate an intervention, or execute a measurement or fallback.

## Artifact structure

A commitment artifact contains:

- `extension` and `status: draft` identifying this provisional convention.
- `taxonomy_bindings`: an array of unique `concept_id` bindings, each with an
  explicit `taxonomy_version`, `definition`, `definition_sha256`, and
  `source_reference`. A reference is attribution, not permission to fetch it.
- `operational_test`: one declarative test with `metric_id`, `concept_ids`,
  `population`, `numerator`, `denominator`, `unit`, `operator`, `threshold`,
  `evaluation_horizon_months`, `measurement_method`, `data_source`,
  `missing_data_policy`, `owner`, and `fallback_action`.

The test distinguishes inclusion rules from the numerator and denominator; failed,
withdrawn, missing and disputed observations need an explicit treatment. Unit,
time origin, calendar-month interpretation, zero-denominator behavior and data
collection must be explained in the authored fields. The linter checks their
presence, not their substantive adequacy.

`threshold` is a decimal **string**, avoiding binary floating-point serialization
ambiguity. `operator` is one of `gt`, `gte`, `lt`, `lte`, `eq`. A positive integer
horizon is required. Every referenced concept must be bound; duplicate concept
IDs are rejected. Unknown optional fields are preserved and included in baseline
comparison. Multiple metrics use separate artifacts in this draft.

## Integrity and baseline comparison

`definition_sha256` is SHA-256 over the parsed definition string encoded as UTF-8,
without Unicode normalization, case folding or whitespace normalization. JSON/YAML
container formatting is irrelevant; an actual string change alters the digest.
This is a consistency check, not proof of authenticity: an editor can change both
the definition and its digest.

`okpf-tool check-semantics` additionally compares the complete parsed artifact
with a separately supplied baseline. It reports changed JSON Pointers, including
changes to thresholds, denominators, missing-data rules, versions, and unknown
optional metadata. Dictionary key order does not matter; array order does.
Changed definitions remain detectable against that baseline even if their embedded
digests were recomputed. The emitted baseline receipt hashes sorted-key ASCII JSON
with compact separators; it is a local receipt, not a cross-implementation
canonicalization standard or signature format.

```bash
okpf-tool check-semantics \
  --document examples/floss-maintainer-succession/semantics/release-review.json \
  --baseline examples/floss-maintainer-succession/review/release-review-baseline.json
```

Exit 0 means schema/digest consistency and, if supplied, baseline equality. Exit 1
means structural errors or changes; exit 2 means input/processing failure. Without
`--baseline`, success means **self-consistency only**. Nothing is written or
executed. Paths are explicit local inputs; parsing uses bounded safe readers.

The baseline must be independently retained and approved by the reviewing process.
The example baseline in the same pack demonstrates mechanics, not independent
custody. Replacing both baseline and candidate defeats this comparison. Unchanged
text can also be applied dishonestly or acquire a different practical meaning.
Independent sampling, measurement audits, reviewed version history, and any
external signature/trust policy remain outside this draft. No cryptographic
verification is claimed by this implementation.

## Compatibility and adoption

Declare artifacts using normal manifest `artifacts` entries and hashes. A producer
may also describe them under `extensions["okpf.semantic_invariants.draft.v0.1"]`.
Core consumers ignore this optional metadata; existing packs remain valid without
it. The MCP catalog preserves it. `check-semantics` is an explicit consumer check;
Core validation and the five MCP tools do not automatically enforce this draft.

Changes require an explicit reviewer decision and a retained prior baseline. The
checker does not automatically accept a changed version number or rewrite the
baseline. This conservative comparison intentionally reports benign editorial
changes as well as potentially substantive ones. A future version needs independent
review of taxonomy governance, measurement protocols, and baseline authentication
before stronger anti-masking claims would be justified.
