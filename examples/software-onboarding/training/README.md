# Training-Ready Derivatives — Software Onboarding Example

This directory contains illustrative training-ready derivatives derived from the `examples/software-onboarding` OKPF pack. All content is fictional placeholder data created for OKPF format demonstration only.

## Files

| File | Role | Description |
|------|------|-------------|
| `instruction.jsonl` | `instruction_dataset` | Five instruction/response pairs derived from onboarding checklist records |
| `derivation.json` | `derivation_report` | How the instruction pairs were produced from source records |
| `dataset-card.json` | `dataset_card` | Summary metadata for this derivative dataset |

## Important

- These files are illustrative only. They have not been evaluated for model improvement.
- Training use is subject to the pack license (`CC-BY-4.0`) and `usage_policy`. Check `usage_policy.allow_fine_tuning` before using for model training.
- Source records (`records/onboarding-checklist.jsonl`) are the authoritative representation. Derivatives are a derived view.
- Five examples are far too few for meaningful fine-tuning.

## Source

Derived from: `records/onboarding-checklist.jsonl` (5 records)  
Reference artifact: `artifacts/setup-guide.md`  
Derivation metadata: `training/derivation.json`
