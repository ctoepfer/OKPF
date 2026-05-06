# OKPF Licensing Strategy

This document explains the licensing choices made for the OKPF project itself, the rationale behind them, and guidance for contributors and knowledge pack authors.

---

## Summary

| Component | License | SPDX Identifier |
|-----------|---------|----------------|
| Specification (SPEC.md) | Apache 2.0 | `Apache-2.0` |
| JSON Schemas | Apache 2.0 | `Apache-2.0` |
| Reference implementations (Python, JavaScript) | Apache 2.0 | `Apache-2.0` |
| CLI tooling | Apache 2.0 | `Apache-2.0` |
| Documentation (docs/) | Apache 2.0 | `Apache-2.0` |
| Example packs (examples/) | Creative Commons BY 4.0 | `CC-BY-4.0` |

---

## Why Apache 2.0 for the Specification and Code

### The core requirement: broad adoption

For an open format standard to succeed, it needs to be implementable by anyone — individuals, startups, large companies, academic institutions, and government bodies. The license must create no friction for any of these adopters. That requirement eliminates most options immediately:

- **GPL family (GPLv2, GPLv3, AGPL)**: Copyleft requirements would make OKPF effectively unusable in proprietary software. A standard that cannot be implemented in closed-source tools will not achieve broad adoption. GPL is appropriate for applications and tools that want copyleft guarantees; it is not appropriate for a portable format standard.
- **LGPL**: Reduced copyleft, but still creates compliance complexity for commercial implementers and is poorly understood for non-library contexts like schemas.
- **MPL 2.0**: File-level copyleft — modifications to OKPF files must remain MPL 2.0. This is workable but introduces friction for corporate legal review. It also means a company that extends the schema for internal use must release those extensions as MPL 2.0, which discourages adoption.

### Apache 2.0 versus MIT

Both are permissive and commercially compatible. The difference that matters for a format standard:

**The patent grant.**

Apache 2.0 includes an explicit patent license from every contributor to every user of the project. If a contributor holds a patent that reads on the implementation of OKPF, the Apache 2.0 grant means they cannot enforce that patent against users of the standard.

MIT provides no patent grant. A contributor could hold a patent covering part of the MIT-licensed specification and still sue implementers.

For a format that may be implemented widely across industries, the Apache 2.0 patent grant is not a theoretical concern — it is a meaningful protection for the ecosystem.

**Summary comparison:**

| Property | MIT | Apache 2.0 | MPL 2.0 | GPLv3 |
|----------|-----|-----------|---------|-------|
| Permissive | Yes | Yes | Partial | No |
| Patent grant | No | Yes | Yes | Yes |
| Commercial use | Yes | Yes | Yes | Yes (with copyleft) |
| Proprietary use | Yes | Yes | Yes (modified files must be MPL) | No |
| Corporate-friendly | Yes | Yes | Mostly | No |
| Standard practice for specs | Sometimes | Yes (common) | Rare | No |

Precedents for Apache 2.0 on open format standards and infrastructure: Apache Kafka, gRPC, OpenTelemetry, Kubernetes, the Linux Foundation generally.

**Conclusion:** Apache 2.0 is the right choice for the OKPF specification, schemas, reference implementations, and tooling.

---

## Why Creative Commons for Example Packs

The content in `examples/` is human-readable knowledge — guides, data tables, workflows — not software. Software licenses are designed for code; they are awkward applied to prose and structured knowledge. Creative Commons licenses are designed for creative and educational works and are widely understood in that context.

**CC BY 4.0** (Creative Commons Attribution 4.0 International) is recommended for open example packs because:

- It explicitly covers text, data, and multimedia
- It requires attribution (contributor credits travel with the content)
- It permits commercial use, redistribution, and derivative works
- It is the most widely adopted open content license
- It is recognized by the Open Knowledge Foundation as satisfying the Open Definition
- The `ai_training: permitted` field in OKPF's own `license.json` schema makes it explicit that these examples can be used for training purposes

---

## SPDX Identifiers

All OKPF files should use SPDX identifiers in license headers and `license.json` declarations. SPDX (Software Package Data Exchange) provides a standard machine-readable vocabulary for licenses.

Key identifiers:

| License | SPDX Identifier |
|---------|----------------|
| Apache License 2.0 | `Apache-2.0` |
| MIT License | `MIT` |
| Creative Commons BY 4.0 | `CC-BY-4.0` |
| Creative Commons BY-SA 4.0 | `CC-BY-SA-4.0` |
| Creative Commons BY-NC 4.0 | `CC-BY-NC-4.0` |
| Creative Commons Zero (Public Domain) | `CC0-1.0` |
| GNU General Public License v3 | `GPL-3.0-only` |
| Mozilla Public License 2.0 | `MPL-2.0` |
| Custom / proprietary | `LicenseRef-custom` |

Full SPDX license list: https://spdx.org/licenses/

---

## Copyright Header Examples

### Source files (Python, JavaScript, Go, etc.)

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
```

Abbreviated form (acceptable for brevity):

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
```

### Markdown / documentation files

```markdown
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 OKPF Contributors -->
```

### JSON schema files

```json
{
  "$comment": "SPDX-License-Identifier: Apache-2.0. Copyright 2026 OKPF Contributors.",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  ...
}
```

### Example knowledge packs

Example packs in the `examples/` directory use CC BY 4.0 and declare this in their `license.json`:

```json
{
  "spdx_expression": "CC-BY-4.0",
  "scope": {
    "use": "open",
    "redistribution": "open",
    "derivative_works": "open",
    "ai_training": "permitted"
  },
  "attribution_required": true,
  "attribution_text": "[Pack Name] by OKPF Contributors, licensed under CC BY 4.0."
}
```

---

## Guidance for Knowledge Pack Authors

When creating knowledge packs, you choose your own license. The `license.json` in your pack is entirely your decision. OKPF imposes no restrictions on pack content licenses.

### Recommended licenses by use case

| Use Case | Recommended License | Notes |
|----------|--------------------|-|
| Fully open knowledge, training permitted | `CC-BY-4.0` | Standard open content |
| Open knowledge, derivatives must remain open | `CC-BY-SA-4.0` | Copyleft for knowledge |
| Open for personal use, no commercial | `CC-BY-NC-4.0` | Non-commercial restriction |
| Public domain, no restrictions | `CC0-1.0` | Maximum freedom |
| Reference data, fact-based | `CC0-1.0` | Facts are not copyrightable, but CC0 signals intent |
| Open, no training permitted | `CC-BY-4.0` + `ai_training: prohibited` | OKPF's `ai_training` field adds what CC BY does not cover |
| Proprietary / commercial | `LicenseRef-custom` | Use `custom_terms` field for full text |

### The `ai_training` field

Standard open licenses (including Creative Commons) do not address AI/ML training use. OKPF's `license.json` schema includes an `ai_training` field specifically for this:

| Value | Meaning |
|-------|---------|
| `permitted` | Content may be used as AI/ML training data without restriction |
| `restricted` | Training use allowed only under specific conditions — use `custom_terms` to detail them |
| `prohibited` | Content must not be used for AI/ML training |
| `unspecified` | The pack author has not declared a position |

This field is informational. OKPF does not technically enforce it. Its purpose is to make creator intent explicit so that consumers and registries can act on it.

---

## Contributor License Agreement

OKPF does not currently require a formal CLA (Contributor License Agreement). By submitting a contribution, contributors agree that:

1. Their contribution is their original work or that they have the right to submit it.
2. Their contribution will be licensed under Apache 2.0 (for code, schemas, and documentation) or CC BY 4.0 (for example pack content) as applicable.
3. They grant OKPF maintainers and all users of the project the rights described by those licenses.

If a contribution includes content from a third party, that content must be clearly identified and carry a compatible license.

---

## Future Governance of Licensing Decisions

As OKPF matures, licensing decisions may be revisited by the community. Any change to the project's primary license would require:

1. A public proposal with justification
2. A defined comment period (minimum 30 days)
3. Consensus among active maintainers
4. A clear migration path for existing implementations

The intent is that Apache 2.0 remains the long-term license for the OKPF project. Changes to this decision should be rare and weighty.
