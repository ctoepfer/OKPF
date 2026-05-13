# Provenance

OKPF v0.1 treats provenance as optional but strongly recommended. Provenance helps rebuild packages, audit sources, preserve attribution, and understand license boundaries.

## Source Entry

A minimal source entry describes one retained or referenced input:

```json
{
  "source_id": "bjcp-2021-notes",
  "path": "sources/bjcp_2021_source_notes.md",
  "format": "markdown",
  "title": "BJCP 2021 source notes",
  "license": {
    "type": "source-specific",
    "details": "Use according to source terms."
  },
  "attribution": "BJCP 2021",
  "notes": "Human-authored summary notes retained as source context."
}
```

## Recommended Provenance Files

`provenance/sources.json` should list source entries. Additional files may record transformations, reviewers, hashes, extraction tools, rebuild commands, and audit decisions.

Future extensions may add signatures, ownership claims, leasing terms, royalty metadata, registry anchors, or chain references. None are required by OKPF Core.
