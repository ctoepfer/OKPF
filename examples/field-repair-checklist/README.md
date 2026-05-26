<!-- SPDX-License-Identifier: Apache-2.0 -->

# Field Repair Checklist — OKPF Example Pack

This pack demonstrates OKPF as a format for field repair and maintenance knowledge: safety prechecks, diagnostic procedures, fault symptom records, escalation rules, and post-repair verification.

**FOR FORMAT DEMONSTRATION ONLY.** All content is fictional placeholder data. This is not certified repair or safety guidance. Do not use to guide real maintenance work on any equipment.

The example deliberately avoids high-stakes safety domains such as aviation, medical devices, fire/life safety, and critical infrastructure.

## Contents

| Path | Description |
|------|-------------|
| `artifacts/safety-precheck.md` | Safety precheck procedure |
| `artifacts/diagnostic-checklist.md` | Diagnostic checklist |
| `artifacts/post-repair-verification.md` | Post-repair verification procedure |
| `records/fault-symptoms.jsonl` | Fault symptom and resolution records |
| `provenance/sources.json` | Provenance metadata |
| `evals/diagnostic-questions.json` | Evaluation questions for procedure knowledge |

## Validate

```bash
python3 reference/python/okpf_validate.py examples/field-repair-checklist
```

## What This Example Shows

- Multi-artifact pack with Markdown maintenance procedures
- JSONL fault-symptom records with severity and fault-category facets
- `expert_notes` field documenting limitations and scope
- Evaluation questions for knowledge verification
- Clear disclaimer in usage_policy and LICENSE

## Disclaimer

Format demonstration only. Not certified repair guidance. Do not use for real maintenance work.
