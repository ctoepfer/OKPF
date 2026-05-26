<!-- SPDX-License-Identifier: Apache-2.0 -->

# Software Onboarding — OKPF Example Pack

This pack demonstrates OKPF as a format for software project onboarding knowledge: setup guides, architecture overviews, troubleshooting notes, and structured checklists.

**All content is fictional placeholder data.** "Acme Backend Service" does not exist. Do not use as real project documentation.

## Contents

| Path | Description |
|------|-------------|
| `artifacts/setup-guide.md` | Local development setup walkthrough |
| `artifacts/architecture-overview.md` | Service component overview |
| `artifacts/troubleshooting.md` | Common issue resolutions |
| `records/onboarding-checklist.jsonl` | Structured checklist records |
| `provenance/sources.json` | Provenance metadata |
| `evals/setup-questions.json` | Evaluation questions for onboarding knowledge |

## Validate

```bash
python3 reference/python/okpf_validate.py examples/software-onboarding
```

## What This Example Shows

- Multi-artifact pack with Markdown engineering documents
- JSONL checklist records with facets for topic, knowledge role, and phase
- Evaluation questions suitable for new-hire knowledge verification
- Software engineering domain usage (non-brewing)

## Disclaimer

Fictional format demonstration only. Not documentation for any real system.
