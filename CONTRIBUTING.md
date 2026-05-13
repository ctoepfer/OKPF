# Contributing to OKPF

Thank you for your interest in contributing to the Open Knowledge Pack Format. OKPF is a specification-first, community-driven standard and benefits from contributions of all kinds.

---

## Ways to Contribute

- **Example packs** — Create knowledge packs in new domains to demonstrate the format
- **Schema improvements** — Propose additions or clarifications to the JSON schemas
- **Specification feedback** — File issues against the spec draft
- **Reference implementations** — Improve or extend the Python/JavaScript libraries
- **Tooling** — Build CLI tools, validators, or converters
- **Documentation** — Clarify concepts, fix typos, add examples
- **Bug reports** — Report problems with schemas, examples, or documentation

---

## Development Setup

No build system is required for schema and documentation work. For reference implementations:

```bash
# Python
cd reference/python
pip install -e ".[dev]"

# JavaScript
cd reference/javascript
npm install
```

---

## Submitting Changes

1. Fork the repository.
2. Create a branch: `git checkout -b feature/my-improvement`
3. Make your changes.
4. Ensure JSON files are valid: `python -m json.tool < schemas/manifest.schema.json`
5. Commit with a clear message.
6. Open a pull request against `main`.

---

## Spec Change Process

Changes to `SPEC.md` and the JSON schemas follow a deliberate process:

Normative spec changes should be discussed before implementation. Breaking changes require extra care because OKPF packages should remain readable over time. New features should preserve the **Simple Core, Optional Power** principle: a minimal pack should remain easy to write by hand, and advanced capabilities should be optional layers.

| Change Type | Process |
|-------------|---------|
| Typo / clarification | PR with label `spec:clarification` |
| New optional field | PR with label `spec:addition` — requires 1 approval |
| New required field | GitHub Discussion first — requires community consensus |
| Breaking change | GitHub Discussion → RFC → vote — requires 2/3 maintainer approval |

Breaking changes are only considered between major versions.

Future versions may use a lightweight enhancement process called KPEPs: Knowledge Pack Enhancement Proposals. The project does not require formal KPEPs yet; for now, open an issue or discussion before large normative changes.

---

## Example Pack Guidelines

When contributing example packs:

- Place them under `examples/<domain>/`
- Include a complete `manifest.json` and `license.json`
- Include at least one content artifact
- Include a `README.md` in the example directory explaining the domain
- Use realistic content — placeholder text is acceptable for initial PRs but should be replaced before merge
- Declare a license that allows redistribution for example purposes (CC BY 4.0 recommended)

---

## Copyright Headers

New source files should include an SPDX license header. Use the shortest form that is unambiguous.

**Python / shell scripts:**
```python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
```

**JavaScript / TypeScript:**
```typescript
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 OKPF Contributors
```

**JSON files** (schemas, tooling config):
```json
{
  "$comment": "SPDX-License-Identifier: Apache-2.0. Copyright 2026 OKPF Contributors.",
  ...
}
```

**Markdown documentation:**
```markdown
<!-- SPDX-License-Identifier: Apache-2.0 -->
```

Example knowledge packs use CC BY 4.0, declared in their `license.json` — no file-level header required inside the pack directory.

---

## Code of Conduct

OKPF follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) Code of Conduct. Be welcoming, respectful, and constructive.

---

## License

By contributing to OKPF, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE). For knowledge pack examples you contribute, you retain the right to choose the license declared in `license.json`, subject to it being compatible with redistribution in this repository (CC BY 4.0 or more permissive recommended).

For a full discussion of the project's licensing choices, see [docs/licensing-strategy.md](docs/licensing-strategy.md).

---

## Questions?

Open a [GitHub Discussion](https://github.com/ctoepfer/OKPF/discussions) for questions that aren't bugs or feature requests.
