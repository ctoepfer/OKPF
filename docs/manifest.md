# Manifest

`manifest.json` is the root descriptor for an OKPF package.

## Required Fields

- `okpf_version`: OKPF spec version, such as `"0.1"`.
- `package_id`: stable package identifier.
- `name`: human-readable package name.
- `version`: package version.
- `domain`: primary domain.
- `profiles`: list of profiles used by the package.
- `records`: list of record files.

## Recommended Fields

- `sources`: retained original or intermediate source files.
- `license`: package or source-specific license summary.
- `provenance`: provenance summary or pointer.
- `description`, `language`, `tags`: discovery metadata.

## Example

```json
{
  "okpf_version": "0.1",
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
  }
}
```

The manifest may include profile-specific extension fields. Core readers should preserve unknown fields when rewriting manifests.
