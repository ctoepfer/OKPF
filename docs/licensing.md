# Licensing in OKPF

Every knowledge pack must declare explicit licensing terms. This document explains the licensing model, how to choose a license, and what each field means.

---

## Why Licensing Matters

Knowledge packs contain human-generated content — guides, transcripts, workflows, evaluations. This content is intellectual property. Without a license, consumers of a pack have no legal clarity on how they may use it.

OKPF makes licensing a required field, not an optional one. There is no "no license declared" state — the closest equivalent is declaring a restrictive or custom license.

---

## The SPDX Expression

Every `license.json` must include an `spdx_expression` — a machine-readable identifier from the [SPDX License List](https://spdx.org/licenses/).

Examples:

| Expression | Meaning |
|-----------|---------|
| `CC-BY-4.0` | Creative Commons Attribution 4.0 — free to use with attribution |
| `CC-BY-SA-4.0` | CC Attribution ShareAlike — derivatives must use same license |
| `CC-BY-NC-4.0` | CC Attribution NonCommercial — no commercial use |
| `CC0-1.0` | Public domain dedication — no rights reserved |
| `Apache-2.0` | Apache 2.0 — permissive, with patent grant |
| `MIT` | MIT — very permissive, attribution required |
| `LicenseRef-custom` | Custom license — see `custom_terms` or `full_text` |

For most knowledge packs, a Creative Commons license is the most appropriate choice.

---

## Choosing a License

### For Open Knowledge Packs

**CC BY 4.0** is recommended for most open knowledge packs. It allows:
- Free use, sharing, and adaptation
- Commercial use
- Requires attribution to the original contributors

**CC0 1.0** (Public Domain) is appropriate when you want no restrictions whatsoever — including no attribution requirement. Good for reference data and factual tables.

**CC BY-SA 4.0** requires that any derivative packs use the same license. Useful if you want the knowledge to remain open in all derivatives.

### For Restricted Knowledge Packs

Use `LicenseRef-custom` with the full text of your terms in `custom_terms` or `full_text`. This preserves machine-readability while allowing any terms you need.

### The AI Training Field

OKPF adds a field that standard licenses don't address: `ai_training`. Valid values:

| Value | Meaning |
|-------|---------|
| `permitted` | Pack content may be used as AI/ML training data |
| `restricted` | Training use allowed only under specified conditions |
| `prohibited` | Pack content must not be used for AI/ML training |
| `unspecified` | License is silent on this question |

This distinction matters because some creators who are happy to share knowledge openly want to retain control over its use in training AI systems. CC BY 4.0 does not address this; OKPF's `ai_training` field provides clarity.

---

## Attribution

If `attribution_required` is `true`, the `attribution_text` field provides the exact text that must be included when using or redistributing the pack.

Example:
```json
{
  "attribution_required": true,
  "attribution_text": "Water Chemistry for Brewing by OKPF Contributors, licensed under CC BY 4.0."
}
```

Tools that display pack content should surface this attribution where content is shown.

---

## Per-Artifact Licensing

By default, the top-level `spdx_expression` applies to all artifacts in a pack. If individual artifacts have different licenses (e.g., a pack includes a CC-licensed image alongside Apache-licensed code), use the `per_artifact` array:

```json
{
  "spdx_expression": "CC-BY-4.0",
  "scope": { "use": "open", "redistribution": "open", "derivative_works": "open" },
  "per_artifact": [
    {
      "artifact_id": "diagram-01",
      "spdx_expression": "CC-BY-SA-4.0",
      "attribution_text": "Diagram by Jane Smith, CC BY-SA 4.0"
    }
  ]
}
```

---

## What OKPF Does Not Do

OKPF records and surfaces licensing information — it does not enforce it. Enforcement is a legal matter, not a technical one. The purpose of the `license.json` is to:

1. Make licensing intent unambiguous to both humans and machines
2. Enable automated tooling to flag license incompatibilities
3. Provide a foundation for trust between pack creators and consumers

---

## Relation to Open Knowledge Principles

OKPF is inspired by the [Open Definition](https://opendefinition.org/) from the Open Knowledge Foundation. An "open" knowledge pack in OKPF terms is one where `scope.use` and `scope.redistribution` are both `open`, which corresponds to the Open Definition's requirements for free use and redistribution.
