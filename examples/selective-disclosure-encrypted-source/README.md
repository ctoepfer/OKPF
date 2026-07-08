<!-- SPDX-License-Identifier: Apache-2.0 -->

# Selective Disclosure With Encrypted Source

This non-normative OKPF example demonstrates a selective disclosure pack with:

- a public summary artifact
- derived public records
- a redacted source excerpt
- an encrypted source placeholder
- an inspectable derivation report
- an inspectable evaluation plan

The encrypted file in `sources/source.enc` is a harmless placeholder fixture. It is not actually secure and contains no real secrets. Real producers should encrypt private source material outside OKPF Core with a tool such as `age`, GPG, or organization-approved encryption tooling.

OKPF Core validation does not decrypt `sources/source.enc`. Core validators can still inspect `manifest.json`, provenance, usage policy, evaluation metadata, artifact disclosure states, safe paths, and SHA-256 hashes over packaged bytes.

Encrypted artifacts are controlled disclosure metadata, not DRM. OKPF does not prevent copying after decryption, revoke access, enforce licenses automatically, or prove source truth or ownership.
