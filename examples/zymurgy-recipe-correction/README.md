<!-- SPDX-License-Identifier: Apache-2.0 -->

# Zymurgy Recipe Correction Example

This fictional example demonstrates a human correction loop:

```text
AI output -> human correction -> outcome evidence -> training derivative
```

It packages an AI-generated beer recipe, a human-adjusted recipe, a structured diff, brewer feedback, outcome evidence, and compact training-ready derivatives.

## What This Demonstrates

- Human correction loop packaging
- Hybrid Mode: source artifacts plus OKPF records and derivatives
- Profile composition with `human-correction-loop` and `fermentation`
- Source recipe vs corrected recipe
- Training derivative vs source artifacts
- Contributor expertise metadata
- Outcome evidence
- Limits of portability

## Important Limitations

This is illustrative. It does not prove recipe quality. It does not replace brewer judgment.

Corrections from one brewer may not generalize to all systems, ingredients, water profiles, equipment, or palates. Expertise metadata helps review and weighting but does not prove correctness.

All recipes, measurements, outcomes, and contributor context are fictional examples for OKPF documentation. No private recipes or proprietary formulations are included.

## Key Files

| File | Purpose |
|------|---------|
| `artifacts/prompts/original-prompt.md` | Original AI prompt |
| `artifacts/recipes/ai-generated-west-coast-ipa.json` | Candidate AI recipe |
| `artifacts/recipes/human-adjusted-west-coast-ipa.json` | Human-adjusted recipe |
| `artifacts/recipes/recipe-diff.json` | Structured correction diff |
| `artifacts/outcomes/batch-results-001.json` | Fictional measured outcome |
| `artifacts/outcomes/sensory-notes-001.md` | Fictional sensory notes |
| `records/records.jsonl` | OKPF records summarizing correction events and limits |
| `training/correction-events.jsonl` | Compact correction-event derivative |
| `training/instruction.jsonl` | Compact instruction-style derivative |
| `training/derivation.json` | Derivation metadata |
| `evals/recipe-correction-eval.jsonl` | Fictional evaluation examples |
