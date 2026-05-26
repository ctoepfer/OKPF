<!-- SPDX-License-Identifier: Apache-2.0 -->

# Profile Authoring Guide

This guide explains how to create an OKPF profile without expanding or modifying OKPF Core.

---

## What Profiles Are For

A profile is a named set of conventions — recommended record types, facets, vocabularies, and validation rules — for a specific domain. Profiles let domain communities standardize the structure and classification of knowledge packs in their area without changing the base format.

Examples:
- `okpf-fermentation` — conventions for beer, wine, mead, cider, and other fermented beverage knowledge
- `okpf-field-repair` — conventions for maintenance and repair knowledge packs
- `okpf-software-onboarding` — conventions for software project onboarding packs
- `physical-skill-evidence` — conventions for physical skill evidence packs in Envelope or Hybrid Mode

A pack declares its profiles in `manifest.json`:

```json
{
  "okpf_version": "0.1.0",
  "package_id": "org.example.fermentation.bjcp-styles",
  "profiles": ["okpf-fermentation"]
}
```

An unknown profile does not invalidate a core-conformant pack. Profile validation is advisory by default.

---

## What Profiles Must Not Do

A profile MUST NOT:

- Redefine or override OKPF Core required fields (`okpf_version`, `name`, `version`, `domain`, `license`).
- Introduce new required manifest fields at the core level.
- Require infrastructure that is not offline-capable (remote registries, AI endpoints, hosted validation services).
- Mandate blockchain anchors, signatures, embeddings, or encrypted content.
- Auto-execute content or define runtime behavior for consuming tools.
- Make unknown profiles an error at the core validation level.
- Collapse `license` and `usage_policy`, or treat one as a substitute for the other.
- Treat `expert_notes` as private model reasoning traces.

A profile SHOULD NOT:

- Impose mandatory record fields beyond those in the core record schema.
- Require domain-specific file formats as mandatory artifacts.
- Define record types so narrowly that general knowledge is forced into inappropriate categories.

---

## Suggested Profile Directory Layout

```text
profiles/<profile-name>/v0.1.0/
  PROFILE.md              Human-readable profile description and rationale
  manifest.schema.json    Optional: additional manifest constraints for this profile
  record.schema.json      Optional: recommended record schema for this profile
  examples/
    <example-record>.json Example records conforming to the profile
```

The version subdirectory (`v0.1.0/`) allows profiles to evolve independently.

---

## How to Define Recommended Record Types

Define record types as string values that may appear in the `record_type` field of records. Recommended, not mandatory.

Document each type in `PROFILE.md`:

```markdown
## Record Types

| Type | Description |
|------|-------------|
| `recipe` | A complete formulation for a fermented beverage |
| `style_guideline` | A style category with sensory parameters |
| `ingredient_reference` | Properties and usage guidance for an ingredient |
| `process_note` | Notes on a fermentation process or technique |
| `glossary_entry` | Definition of a domain term |
```

In `record.schema.json`, list the types as an `enum` in the `record_type` property. Mark the constraint as a profile-level recommendation, not a core requirement.

---

## How to Define Recommended Facets

Facets are machine-readable classification keys in `records[].facets`. OKPF Core does not restrict facet keys; profiles MAY recommend specific keys.

Document recommended facets in `PROFILE.md`:

```markdown
## Recommended Facets

| Key | Type | Description |
|-----|------|-------------|
| `beverage_type` | string or array | Category of beverage (e.g., `beer`, `wine`, `mead`) |
| `knowledge_role` | string | How the record is intended to be used (e.g., `reference`, `recipe`) |
| `style_family` | string | Broad style grouping |
```

Validators SHOULD emit warnings — not errors — when recommended facets are absent.

---

## How to Define Profile-Specific Schemas

Place JSON Schema (Draft 2020-12) files in the profile directory.

`manifest.schema.json` can add constraints on top of the core manifest schema. For example, it might recommend that packs targeting this profile include specific values in `domain`.

`record.schema.json` defines the recommended structure for records in this profile. Use `"additionalProperties": true` to allow records with additional fields to remain valid.

Validation tools apply profile schemas in addition to — not instead of — core schemas.

---

## How to Define Examples

Place example records and manifests in `examples/`:

```text
profiles/fermentation/v0.1.0/examples/
  recipe-record.json
  style-guideline-record.json
```

Each example should be a realistic, minimal record that conforms to both the core record schema and the profile record schema.

---

## How to Handle Profile Validation as Warning-First

Profile validators SHOULD:

- Emit unknown `record_type` values as **warnings**, not errors, by default.
- Emit missing recommended facets as **warnings**.
- Escalate warnings to errors only when strict profile mode is explicitly requested by the user.
- Return a non-zero exit code for errors but not for warnings in default mode.

This preserves interoperability: a pack that was authored before a profile existed, or that deliberately uses custom types, remains processable.

---

## How to Avoid Mandatory Infrastructure

Profiles MUST NOT:

- Require that consumers fetch schemas from a remote URL to validate records.
- Require that pack authors submit to a registry before a pack is valid.
- Mandate that consumers run a specific AI model or embedding provider.
- Define a compliance checkpoint that requires network access.

Profiles MAY:

- Recommend (not require) that pack authors provide embeddings as optional artifacts.
- Document registry conventions without making registry submission mandatory.
- Link to online resources for informational purposes.

All schemas referenced by a profile MUST be resolvable locally from the profile directory.

---

## How to Avoid Turning Profiles into Hidden Runtimes

Profiles define knowledge structure conventions. They do not define:

- How a consumer retrieves or queries records.
- How a consumer invokes AI models.
- How evaluation results are computed or reported.
- Scheduling, orchestration, or workflow execution semantics.
- Access control or authentication requirements.

If your profile finds itself defining how tools behave at runtime, that behavior belongs in the consuming application layer, not in the profile.

---

## How to Avoid Redefining Core Manifest Semantics

Do not reinterpret existing core fields in a profile-specific way. For example:

- Do not treat `license` as equivalent to `usage_policy`.
- Do not treat `domain` as a controlled vocabulary enforced at the profile level with error severity.
- Do not treat `expert_notes` as a structured AI reasoning trace.
- Do not add required fields to the core manifest via a profile schema.

If you need additional manifest metadata for your domain, use unknown optional fields (they are tolerated by all conformant consumers) or propose a new optional core field through the OKPF contribution process.

---

## Minimal Profile Skeleton

The following skeleton is a starting point for a new profile.

### `profiles/my-domain/v0.1.0/PROFILE.md`

```markdown
# OKPF My-Domain Profile — v0.1.0

## Purpose

This profile defines recommended conventions for OKPF knowledge packs in the my-domain domain.

## Profile Identifier

`okpf-my-domain`

## Record Types

| Type | Description |
|------|-------------|
| `concept` | A defined concept or term |
| `procedure` | A step-by-step process |
| `reference` | A reference table or data sheet |

## Recommended Facets

| Key | Description |
|-----|-------------|
| `topic` | High-level topic classification |
| `knowledge_role` | Intended use (e.g., `reference`, `procedure`, `example`) |

## Profile Validation

Profile validators emit warnings (not errors) for:
- Unknown `record_type` values
- Missing recommended facets

Strict mode (`--strict-profile`) escalates warnings to errors.
```

### `profiles/my-domain/v0.1.0/record.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$comment": "SPDX-License-Identifier: Apache-2.0 | Copyright 2026 OKPF Contributors",
  "$id": "okpf:profile:my-domain:v0.1.0:record",
  "title": "OKPF My-Domain Profile Record",
  "description": "Recommended record structure for my-domain profile packs.",
  "type": "object",
  "properties": {
    "record_type": {
      "type": "string",
      "enum": ["concept", "procedure", "reference"],
      "description": "Recommended record types for this profile."
    },
    "facets": {
      "type": "object",
      "properties": {
        "topic": { "type": "string" },
        "knowledge_role": { "type": "string" }
      }
    }
  },
  "additionalProperties": true
}
```

### `profiles/my-domain/v0.1.0/examples/concept-record.json`

```json
{
  "id": "concept-001",
  "record_type": "concept",
  "title": "Example Concept",
  "text": "A brief definition of an example concept in the my-domain domain.",
  "domain": "my-domain",
  "facets": {
    "topic": "fundamentals",
    "knowledge_role": "reference"
  },
  "metadata": {
    "source": "Internal documentation",
    "reviewed": true
  }
}
```

---

## See Also

- [docs/v0.1-conformance.md](v0.1-conformance.md) — conformance levels and producer/consumer requirements
- [profiles/fermentation/v0.1.0/](../profiles/fermentation/v0.1.0/) — the reference fermentation profile
- [SPEC.md](../SPEC.md) — authoritative OKPF specification
- [schemas/v0.1.0/manifest.schema.json](../schemas/v0.1.0/manifest.schema.json) — core manifest schema
- [schemas/record.schema.json](../schemas/record.schema.json) — core record schema
