<!-- SPDX-License-Identifier: Apache-2.0 -->
# Training-Ready Derivatives

OKPF source packs are not automatically training datasets. A pack may optionally include training-ready derivatives — files intended for direct or near-direct consumption by AI training, fine-tuning, evaluation, or retrieval-preparation systems.

Training-ready derivatives bridge the gap between OKPF source packs, which prioritize provenance, attribution, licensing, human review, and long-term portability, and lower-friction datasets used by AI practitioners.

---

## What Training-Ready Derivatives Are

Training-ready derivatives are optional files derived from a pack's source records and artifacts. They are packaged alongside the source knowledge so consumers can use either representation depending on their needs.

Physical-skill or robotics-adjacent packs may also include optional training derivatives, but those derivatives remain derived artifacts. They should declare provenance, source artifacts, transformations, filtering, review status, limitations, and any non-claims about transfer or safety.

**Examples:**

- Instruction-tuning JSONL (instruction / response pairs)
- Completion JSONL (prompt / completion pairs)
- Preference pairs (chosen / rejected response pairs)
- Classification examples (text / label pairs)
- Retrieval and evaluation pairs (query / relevant passage pairs)
- Synthetic QA pairs (question / answer from source records)
- Cleaned text corpora
- Parquet datasets
- Dataset folders for downstream training tools

These are artifact conventions. None of them are required by OKPF Core.

---

## What Training-Ready Derivatives Are Not

- **Not the source of truth.** Source records and artifacts remain authoritative. Derivatives are a derived view.
- **Not proof of quality.** The presence of training files does not imply the examples improve any model, are factually correct, or are suitable for production use.
- **Not proof of permission.** The presence of training files does not override `license` or `usage_policy`. Training use is only permitted if the pack's license and usage policy allow it.
- **Not model weights.** Derivatives are data files, not trained artifacts.
- **Not embeddings,** unless separately declared with model and dimension metadata.
- **Not training pipelines.** OKPF packages files; it does not run training, tokenization, or evaluation.
- **Not tokenized model-specific datasets,** unless explicitly declared as such in derivation metadata.
- **Not a guarantee** that training on these files is legally or technically appropriate for any specific use case. Consumers must verify independently.

---

## Why They Exist

AI practitioners often need low-friction, schema-consistent datasets for fine-tuning, evaluation, or retrieval experiments. But OKPF source packs prioritize provenance, attribution, human review, and long-term portability — not immediate ingestion convenience.

Training-ready derivatives serve both goals: they give AI consumers a ready-to-use format while preserving the source pack's provenance chain and making the transformation from source to derivative explicit and auditable.

---

## Recommended Directory Layout

The recommended convention for training-ready derivatives is:

```
pack/
  manifest.json
  records/
    records.jsonl              ← source records (primary)
  artifacts/
    guide.md                   ← source artifacts (primary)
  training/                    ← optional; may not exist
    README.md                  ← explains what is in training/
    derivation.json            ← how derivatives were created
    dataset-card.json          ← summary metadata for dataset consumers
    instruction.jsonl          ← instruction-tuning pairs
    completion.jsonl           ← completion pairs
    preference.jsonl           ← preference pairs
    classification.jsonl       ← classification examples
    retrieval-eval.jsonl       ← retrieval / evaluation pairs
```

**Rules:**

- `training/` is optional. Consumers MUST NOT assume it exists.
- Producers SHOULD include `derivation.json` when any training derivatives are present.
- Derivatives SHOULD reference the source records or artifacts they were derived from.
- Derivatives SHOULD declare transformations, filtering, deduplication, review status, and known limitations.
- Training derivatives MUST NOT be committed as if they are source knowledge.
- Large generated datasets SHOULD NOT be committed to Git; generate them from source packs at build time.

---

## Recommended Artifact Roles

When training derivative files are declared in the manifest `artifacts` array, the following roles are recommended:

| Role | Description |
|------|-------------|
| `training_dataset` | Generic training dataset (use a more specific role when available) |
| `instruction_dataset` | Instruction / response pairs for instruction tuning |
| `completion_dataset` | Prompt / completion pairs for completion models |
| `preference_dataset` | Chosen / rejected pairs for preference learning |
| `classification_dataset` | Text / label classification examples |
| `retrieval_eval_dataset` | Query / passage pairs for retrieval evaluation |
| `synthetic_qa_dataset` | Synthetic question / answer pairs |
| `dataset_card` | Metadata summary card for the training dataset |
| `derivation_report` | How the derivative was created from source |
| `filtering_report` | What filtering was applied |
| `deduplication_report` | What deduplication was applied |
| `quality_review` | Human review notes on derivative quality |

**Important:**

- These are recommended roles only. Unknown roles remain valid in Core.
- Roles do not imply quality, accuracy, or permission to train.
- A consumer that sees `role: "instruction_dataset"` knows the file format intent; it does not know whether the examples are good or training is permitted.

---

## Derivation Metadata

When training derivatives are present, include `training/derivation.json` to make the transformation chain auditable:

```json
{
  "derivative_id": "example.software-onboarding.instruction.v0.1.0",
  "derivative_type": "instruction_dataset",
  "derived_from": [
    {
      "type": "record_file",
      "path": "records/records.jsonl"
    },
    {
      "type": "artifact",
      "path": "artifacts/setup-guide.md"
    }
  ],
  "transforms": [
    {
      "type": "chunking",
      "description": "Split setup guide into task-level sections."
    },
    {
      "type": "instruction_pair_generation",
      "description": "Created instruction/response examples from source records."
    },
    {
      "type": "human_review",
      "description": "Reviewed generated examples for source faithfulness."
    }
  ],
  "filtering": {
    "removed_duplicates": true,
    "removed_low_confidence_examples": true,
    "removed_private_data": true
  },
  "quality_notes": [
    "Examples are illustrative and not benchmarked for model improvement."
  ],
  "limitations": [
    "Not tokenized for a specific model.",
    "Not validated for production fine-tuning."
  ]
}
```

See `schemas/training-derivation.schema.json` for the permissive JSON Schema.

---

## Optional `ai_training` Manifest Field

Packs that include training derivatives MAY declare them in the manifest using an `ai_training` extension object. This is an optional extension convention, not a required field.

```json
{
  "okpf_version": "0.1.0",
  "package_id": "my-pack",
  "name": "My Pack",
  "version": "1.0.0",
  "domain": "software-engineering",
  "license": { "type": "CC-BY-4.0" },
  "usage_policy": {
    "allow_fine_tuning": true,
    "require_attribution": true
  },
  "ai_training": {
    "contains_training_ready_derivatives": true,
    "recommended_formats": ["jsonl"],
    "derivatives": [
      {
        "path": "training/instruction.jsonl",
        "type": "instruction_dataset",
        "derived_from": ["records/records.jsonl"],
        "derivation_report": "training/derivation.json"
      }
    ],
    "notices": [
      "Training use remains subject to license and usage_policy.",
      "These derivatives are illustrative. Verify suitability before production use."
    ]
  }
}
```

**Important:**

- `ai_training` is not a required field. Its absence does not invalidate a pack.
- `license` and `usage_policy` control whether training is permitted. The presence of `training/` files or an `ai_training` field does not override legal terms.
- Consumers MUST check `usage_policy.allow_fine_tuning` before using any derivative for model training.
- Unknown fields in `ai_training` MUST be preserved by conformant readers (forward compatibility).

---

## Relationship to License and Usage Policy

Training derivatives do not create training permission. The chain of permission is:

```
license (legal terms)
  └── usage_policy.allow_fine_tuning (machine-readable operational intent)
        └── training derivatives (files, if present)
```

A pack that has `training/instruction.jsonl` but `usage_policy.allow_fine_tuning: false` does not permit fine-tuning. The file is present as a format example or for evaluation only.

Always check both `license` and `usage_policy` before using any pack content for model training, redistribution, or evaluation.

---

## Related Documents

- [Packaging Modes](packaging-modes.md) — Native, Envelope, and Hybrid modes
- [Package Structure](package-structure.md) — directory layout conventions
- [Provenance](provenance.md) — origin and transformation documentation
- [When Not to Use OKPF](when-not-to-use-okpf.md) — scope limitations
- [`examples/software-onboarding/`](../examples/software-onboarding/) — example with illustrative training derivatives
- [`schemas/training-derivation.schema.json`](../schemas/training-derivation.schema.json) — derivation metadata schema
