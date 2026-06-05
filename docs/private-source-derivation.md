<!-- SPDX-License-Identifier: Apache-2.0 -->

# Private Source Derivation (Optional Pattern)

OKPF packs sometimes need to share useful derived knowledge while withholding original private source artifacts. This document defines an optional pattern for doing that in a transparent, auditable way without changing OKPF Core validation.

This pattern is domain-neutral. Recipe notes, repair diagnostics, support transcripts, training manuals, legal memos, lab notebooks, process documents, robotics demonstrations, and codebase-derived records can all use the same approach.

## 1. Purpose

Many producers can share transformed knowledge but cannot share original source materials. Common reasons include privacy, confidentiality, contractual limits, trade secrets, legal restrictions, safety concerns, or practical data size constraints.

This pattern helps producers:

- distribute derivative artifacts and records
- declare what source visibility model was used
- document how derivatives were produced
- communicate known reconstruction and leakage risks
- preserve license and usage policy clarity

This pattern does not change OKPF Core requirements.

## 2. Scope

This document covers optional conventions for packs where one or more derivative artifacts or records are created from source artifacts that are fully or partially withheld.

This document is guidance, not core validation. Implementations MAY adopt all, part, or none of it. Pack validity under OKPF Core MUST NOT depend on this pattern.

## 3. Non-goals

This pattern is not a security proof and not a legal determination mechanism. Specifically, it:

- does not prevent copying
- does not guarantee source reconstruction is impossible
- does not prove legal ownership or rights
- does not guarantee factual correctness
- does not enforce license terms
- does not require cryptography, blockchain, zero-knowledge proofs, signatures, registries, hosted services, or trusted third parties

## 4. Terminology

- source artifact: Original input material used to create derivative outputs.
- withheld source: Source artifact not distributed in the pack payload.
- derivative artifact: Distributed artifact produced by transforming one or more source artifacts.
- derived record: Structured record (for example JSON/JSONL) generated from one or more source artifacts.
- source commitment: Optional digest, Merkle root, signature reference, or equivalent identifier associated with a source set.
- derivation report: Structured metadata that explains how derivatives were produced and reviewed.
- attestation: Optional statement by a person or process about derivation steps or source handling.
- reconstruction risk: Risk that distributed derivatives allow approximate or exact recovery of withheld source details.
- leakage risk: Risk that private, identifying, or sensitive source details are exposed through derivatives.

## 5. Source Visibility Vocabulary (Optional)

Producers MAY use the following optional vocabulary in provenance fields such as `source_visibility`:

- included: source artifacts are included in pack files
- referenced: source artifacts are not included but are externally referenceable
- withheld: source artifacts are intentionally not distributed
- redacted: source artifacts are included in redacted form
- escrowed: source artifacts are held by a designated custodian
- auditor_available: source artifacts are available to approved auditors only
- synthetic: derivatives were generated from synthetic source material
- mixed: source set contains multiple visibility states
- unknown: visibility state is not known or not declared

Unknown values SHOULD remain valid as extension data.

## 6. Derivative Artifact Types (Optional)

Producers MAY use the following optional `derivative_type` values:

- summary
- normalized_record
- training_example
- evaluation_item
- statistical_aggregate
- embedding
- workflow_abstraction
- simulation_case
- qa_pair
- classification_example
- multimodal_annotation

These are conventions only. They are not core enums.

## 7. Derivation Report

When derivatives are distributed from withheld or partially withheld sources, producers SHOULD include a derivation report (for example `provenance/derivation_report.json` or `training/derivation.json`).

A derivation report SHOULD include, when applicable:

- source visibility declaration
- transformation method
- redaction method
- generalization method
- minimum source group size (for aggregation/k-anonymity style controls)
- fields removed
- numeric bucketing strategy
- privacy and leakage considerations
- human review status
- tools and process used to generate derivatives
- known limitations

If no such controls were applied, the report SHOULD say so explicitly.

## 8. Source Commitments

Packs MAY include optional source commitments in provenance metadata. Examples:

- hash lists over source artifacts
- Merkle roots over a source set
- detached signatures over commitment manifests
- timestamped references to a commitment document

Commitments can help identify a stable private source set for audit, escrow workflows, or later disclosure.

Commitments do not prove:

- truthfulness of claims
- ownership or legal rights
- legality of collection or processing
- quality, completeness, or correctness of derivatives

## 9. Reconstruction And Leakage Risk Guidance

When source secrecy matters, producers SHOULD:

- avoid one-to-one source-to-record mappings
- avoid exact names, identifiers, rare phrases, and unique combinations
- prefer aggregation, bucketing, paraphrasing, and minimum group sizes where appropriate
- include reconstruction and leakage risk notes or ratings

A low risk rating means reduced risk, not zero risk.

Consumers SHOULD treat all derivative packs as potentially reversible under sufficient external context.

## 10. Usage Policy Examples

Packs can declare usage intent clearly, for example:

```json
{
  "usage_policy": {
    "allow_fine_tuning": true,
    "allow_rag": true,
    "allow_redistribution": false,
    "prohibit_source_reconstruction": true,
    "source_artifacts_withheld": true,
    "notes": [
      "Derivative artifacts are provided without original source artifacts.",
      "Training and retrieval uses remain subject to license terms."
    ]
  }
}
```

Policy declarations communicate intent; they do not enforce behavior.

## 11. Example Manifest Fragment (Domain-Neutral)

```json
{
  "okpf_version": "0.1.0",
  "package_id": "org.example.private-derived.ops-knowledge.v1",
  "name": "Operations Knowledge Derivatives",
  "version": "1.0.0",
  "domain": "operations",
  "license": {
    "type": "CC-BY-NC-4.0"
  },
  "artifacts": [
    {
      "path": "records/derived-records.jsonl",
      "type": "application/x-ndjson",
      "role": "record_file",
      "description": "Derived records produced from withheld internal sources.",
      "derivative_type": "normalized_record"
    },
    {
      "path": "provenance/derivation_report.json",
      "type": "application/json",
      "role": "derivation_report"
    }
  ],
  "provenance": {
    "source_visibility": "withheld",
    "derivation_report": "provenance/derivation_report.json",
    "source_commitments": [
      {
        "type": "sha256_set",
        "digest": "b03f3d364f6f8b1f7fb5185a2ecf3f9f9b2db5f0988e5db24a11112222333344",
        "scope": "withheld_source_set_v1"
      }
    ]
  },
  "usage_policy": {
    "allow_fine_tuning": true,
    "allow_rag": true,
    "allow_redistribution": false,
    "prohibit_source_reconstruction": true,
    "source_artifacts_withheld": true
  }
}
```

This fragment is illustrative and intentionally permissive. Unknown fields remain compatible with OKPF Core conventions.

## 12. Example provenance/derivation_report.json

```json
{
  "derivative_set_id": "org.example.private-derived.ops-knowledge.v1",
  "source_visibility": "withheld",
  "transformation_method": "summarization_plus_normalization",
  "redaction_method": "pii_and_identifier_removal",
  "generalization_method": "bucketed_metrics_and_paraphrase",
  "minimum_source_group_size": 12,
  "fields_removed": [
    "person_name",
    "email",
    "ticket_id",
    "exact_timestamp"
  ],
  "numeric_bucketing": {
    "response_time_minutes": ["0-15", "16-60", "61-240", ">240"]
  },
  "privacy_and_leakage_considerations": [
    "Rare phrase filtering applied.",
    "Unique identifier patterns removed.",
    "Residual re-identification risk remains."
  ],
  "reconstruction_risk": {
    "rating": "low_to_moderate",
    "notes": "Small cohorts and external auxiliary data can increase risk."
  },
  "human_review": {
    "status": "completed",
    "reviewers": 2
  },
  "generation_process": {
    "tool": "internal-derivation-pipeline",
    "version": "2026.06"
  },
  "limitations": [
    "Not a legal safe-harbor statement.",
    "Does not prove source ownership or factual correctness."
  ]
}
```

## 13. Future Extension Path

If adoption justifies stronger interoperability, this pattern could evolve into one or more optional layers:

- an optional extension directory convention
- an optional JSON Schema for derivation report fields
- a profile-level convention for domain-specific controls
- a cryptographic attestation layer
- an optional zero-knowledge proof integration

None of the above are required for OKPF Core.

## Related Documents

- [Training-Ready Derivatives](training-ready-derivatives.md)
- [Provenance](provenance.md)
- [Licensing](licensing.md)
- [AI Integration](ai-integration.md)
- [When Not To Use OKPF](when-not-to-use-okpf.md)