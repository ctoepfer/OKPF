<!-- SPDX-License-Identifier: Apache-2.0 -->

# Encrypted Artifacts Extension

Extension identifier: `okpf.encrypted_artifacts.v0`

Status: Draft optional extension

This extension defines optional metadata conventions for OKPF packs that include encrypted artifact payloads. It is an optional layer over OKPF Core. A pack MUST NOT require support for this extension to validate OKPF Core structure.

## Purpose

Selective disclosure packs may include a clean three-layer model:

- Public layer: manifest metadata, package identity, license, usage policy, public artifacts, public records, evaluation descriptions, source claims, and integrity metadata.
- Redacted layer: excerpts, summaries, transformed examples, normalized records, and source references without full source disclosure.
- Encrypted layer: raw source documents, private notes, licensed source material, customer or internal records, and high-value originals.

This extension describes how encrypted artifact entries can declare encryption metadata while keeping the manifest, provenance, integrity metadata, usage policy, and evaluation structure inspectable.

## Core Compatibility

Encryption remains optional. OKPF Core validation MUST NOT require decryption.

Core validators can still:

- read `manifest.json`
- validate manifest shape against local schemas
- check safe artifact paths
- verify declared hashes over packaged bytes
- inspect public records, provenance, usage policy, and evaluation metadata
- identify artifacts with `"disclosure": "encrypted"`
- preserve unknown extension fields

Consumers that do not implement `okpf.encrypted_artifacts.v0` SHOULD warn and continue with the public structure when safe to do so.

## Artifact Metadata

An encrypted artifact SHOULD set:

```json
{
  "id": "artifact.source_recipes.raw",
  "path": "artifacts/encrypted/source_recipes.okpf.enc",
  "role": "source_material",
  "disclosure": "encrypted",
  "encryption": {
    "extension": "okpf.encrypted_artifacts.v0",
    "algorithm": "XChaCha20-Poly1305",
    "key_wrapping": ["age"],
    "ciphertext_sha256": "...",
    "plaintext_sha256": "...",
    "required_for_core_validation": false
  },
  "derived_records": [
    "records/beer_style_patterns.jsonl"
  ]
}
```

`ciphertext_sha256` identifies the packaged encrypted bytes. `plaintext_sha256` is optional and may be withheld when revealing a plaintext commitment would expose sensitive information. If present, it is advisory metadata for authorized consumers after decryption.

`required_for_core_validation` MUST be `false` when present. Extension-aware tools MAY require decryption for workflows above Core validation, such as rebuilding records, auditing source claims, or running private evaluations.

## Redacted Counterparts

Packs MAY include redacted artifacts that point back to encrypted sources:

```json
{
  "id": "artifact.source_recipes.redacted",
  "path": "artifacts/redacted/source_recipes.redacted.md",
  "role": "redacted_source_excerpt",
  "disclosure": "redacted",
  "redaction": {
    "method": "human_reviewed",
    "redacts": [
      "exact ingredient quantities",
      "supplier-specific notes",
      "private recipe identifiers"
    ],
    "source_artifact": "artifact.source_recipes.raw"
  }
}
```

Redaction metadata is descriptive. It does not prove that redaction was complete or safe.

## Non-Goals

Encrypted artifacts are a controlled disclosure mechanism, not DRM. OKPF does not:

- guarantee secrecy after decryption
- prevent unauthorized copying
- enforce licensing automatically
- prove factual correctness
- require any key server, registry, cloud service, AI provider, blockchain, or external runtime

Key exchange, authorization, escrow, audit workflows, and decryption tooling are outside OKPF Core.
