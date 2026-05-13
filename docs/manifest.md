# Manifest

`manifest.json` is the root descriptor for an OKPF package.

The v0.1.0 schema lives at `schemas/v0.1.0/manifest.schema.json`. Manifests may include:

```json
"$schema": "https://okpf.org/schema/v0.1.0/manifest.schema.json"
```

Official schema URLs are intended to be stable once OKPF has a public documentation site.

## Required Fields

- `okpf_version`: OKPF spec version, such as `"0.1.0"`.
- `package_id`: stable package identifier.
- `name`: human-readable package name.
- `version`: package version.
- `domain`: primary domain.
- `license`: legal permission summary or reference.
- `artifacts` or `records`: declared payload files.

For compatibility, some older v0.1 examples use `id` instead of `package_id` and `content` instead of `artifacts`.

## Recommended Fields

- `sources`: retained original or intermediate source files.
- `provenance`: provenance summary or pointer.
- `usage_policy`: machine-readable operational intent and constraints.
- `dependencies`: package or external dependencies. Validators do not fetch them in v0.1.0.
- `integrity`: optional SHA-256 hashes.
- `expert_notes`: human-authored rationale and review context, not private model reasoning traces.
- `description`, `language`, `tags`: discovery metadata.

## Example

```json
{
  "$schema": "https://okpf.org/schema/v0.1.0/manifest.schema.json",
  "okpf_version": "0.1.0",
  "package_id": "bjcp-2021-beer-styles",
  "name": "BJCP 2021 Beer Style Training Pack",
  "version": "1.0.0",
  "domain": "fermentation",
  "profiles": ["okpf-core", "okpf-fermentation"],
  "records": [
    {
      "path": "records/beer_styles.jsonl",
      "format": "jsonl",
      "record_count": 127
    }
  ],
  "sources": [
    {
      "path": "sources/bjcp_2021_source_notes.md",
      "format": "markdown"
    }
  ],
  "license": {
    "type": "source-specific",
    "details": "See provenance/sources.json"
  },
  "usage_policy": {
    "allow_rag": true,
    "allow_fine_tuning": false,
    "allow_evaluation": true,
    "allow_commercial_use": true,
    "allow_derivatives": true,
    "allow_commercial_derivatives": false,
    "require_attribution": true,
    "notes": "Check source-specific license terms before reuse."
  }
}
```

`license` and `usage_policy` are intentionally separate. `license` records legal permission; `usage_policy` gives machines operational guidance.

The manifest may include profile-specific extension fields. Core readers should preserve unknown fields when rewriting manifests.
