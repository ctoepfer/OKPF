<!-- SPDX-License-Identifier: Apache-2.0 -->

# How To Package Encrypted Artifacts

Use encrypted artifacts when a pack should expose useful metadata, records, evaluations, and redacted derivatives while protecting raw source material. Common cases include private notes, licensed source documents, internal records, customer material, or high-value originals.

Encryption is optional extension metadata. OKPF Core validation MUST NOT require decryption.

## Disclosure States

Artifact-level `disclosure` values describe what a consumer can inspect:

- `public`: the artifact is directly readable.
- `redacted`: a reduced or modified artifact is included.
- `encrypted`: protected bytes are included, but separate key material or authorization is needed to read plaintext.

Related source-visibility values describe source handling:

- `withheld`: source artifacts are not included in the pack payload.
- `escrowed`: source artifacts are held by a custodian outside the pack.
- `auditor_available`: source artifacts are available only to approved auditors under a separate process.

These terms are not access-control mechanisms. They are metadata that helps consumers understand what exists and what is inspectable.

## Create Public And Redacted Derivatives

Start by deciding what can be shared without private source access:

1. Write public summaries, guides, records, or evaluation descriptions that do not expose protected details.
2. Create redacted excerpts when consumers need to see source shape or review context.
3. Document the transformation and redaction process in a derivation report.
4. Preserve source references, artifact IDs, hashes, license, usage policy, and attribution in derived records.

Do not include private identifiers, rare phrases, or sensitive source details in public or redacted layers unless the rights and review process allow it.

## Encrypt Outside OKPF Core

OKPF does not define an encryption runtime. Encrypt private source material with a tool such as `age`, GPG, or organization-approved encryption tooling.

Illustrative `age` command:

```bash
age -r age1examplepublicrecipientkey... \
  -o sources/source.enc \
  private/source.txt
```

This command is only an example. Use your organization's key-management, rotation, retention, and review process for real private source material.

## Declare The Encrypted Artifact

Declare encrypted artifacts in `manifest.json` with `disclosure: "encrypted"` and optional `okpf.encrypted_artifacts.v0` metadata:

```json
{
  "id": "source-encrypted",
  "path": "sources/source.enc",
  "type": "application/octet-stream",
  "role": "source_material",
  "sha256": "a9514a740fadd409d4ddc727e3d2cf541b4e66324c637b6211f2863d8a4f97fe",
  "disclosure": "encrypted",
  "encryption": {
    "extension": "okpf.encrypted_artifacts.v0",
    "algorithm": "XChaCha20-Poly1305",
    "key_wrapping": ["age"],
    "ciphertext_sha256": "a9514a740fadd409d4ddc727e3d2cf541b4e66324c637b6211f2863d8a4f97fe",
    "required_for_core_validation": false
  },
  "derived_records": [
    "records/derived-notes.jsonl"
  ]
}
```

`ciphertext_sha256` identifies the packaged encrypted bytes and should match artifact-level `sha256` when both are present. `plaintext_sha256` is optional and may be withheld.

## Validate Without Decryption

Core validators can inspect the pack without plaintext access:

```bash
python3 reference/python/okpf_validate.py examples/selective-disclosure-encrypted-source
```

They can check manifest shape, safe paths, public records, provenance, evaluation declarations, and declared hashes over packaged bytes. They must not require decryption for OKPF Core validation.

## Authorized Review

An authorized reviewer may decrypt outside Core validation for audit, rebuild, or private evaluation workflows. That review is an additional process layered above OKPF Core.

For example:

```bash
age -d -i ~/.config/age/keys.txt \
  -o /tmp/source.txt \
  sources/source.enc
```

After decryption, reviewers may compare plaintext to private commitments, rebuild derived records, or inspect redaction quality. Those steps are not required for a pack to be Core-valid.

## Limitations

Encrypted artifacts are controlled disclosure metadata, not DRM. OKPF does not:

- prevent copying or redistribution after decryption
- revoke access to already disclosed plaintext
- enforce access control
- enforce license terms automatically
- prove factual correctness
- prove source ownership
- require key servers, registries, cloud services, blockchains, TEEs, ZK proofs, or hosted infrastructure

See also:

- [Encrypted Artifacts Extension](../extensions/encrypted-artifacts.md)
- [Private Source Derivation](../private-source-derivation.md)
- [Security in OKPF](../security.md)
- [Selective Disclosure With Encrypted Source](../../examples/selective-disclosure-encrypted-source/)
