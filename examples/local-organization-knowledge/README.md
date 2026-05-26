<!-- SPDX-License-Identifier: Apache-2.0 -->

# Local Organization Knowledge — OKPF Example Pack

This pack demonstrates OKPF as a format for preserving organizational knowledge: procedures, governance records, and decision history.

**All content is fictional placeholder data.** It does not represent any real organization, legal requirement, or certified governance guidance.

## Contents

| Path | Description |
|------|-------------|
| `artifacts/board-meeting-procedure.md` | Example board meeting procedure |
| `artifacts/vendor-contact-sop.md` | Example vendor contact SOP |
| `records/decisions.jsonl` | Example decision history records |
| `provenance/sources.json` | Provenance metadata |
| `evals/procedure-questions.json` | Sample evaluation questions |

## Validate

```bash
python3 reference/python/okpf_validate.py examples/local-organization-knowledge
```

## What This Example Shows

- Multi-artifact pack with Markdown governance documents
- JSONL decision-history records with facets for topic and knowledge role
- Provenance metadata linking source documents
- Evaluation questions for knowledge quality checking
- Appropriate usage policy for example content

## Disclaimer

This is a format demonstration only. Do not use as real organizational guidance.
