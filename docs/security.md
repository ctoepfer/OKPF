# Security in OKPF

This document covers the security model for OKPF — what guarantees the format provides, what it doesn't, and how to use OKPF securely.

---

## Security Properties

OKPF provides mechanisms for:

- **Integrity** — Detecting whether pack content has been modified since authoring
- **Authenticity** — Verifying who signed a pack or artifact
- **Non-repudiation** — Providing evidence that a contributor approved specific content

OKPF does not currently define:

- **Encryption** — Packs are not encrypted at rest in the base format
- **Access control** — The format does not enforce who can read a pack
- **Revocation** — No mechanism for revoking a published pack (though registries can handle this)

---

## Content Integrity: SHA-256 Hashes

Every content artifact in a pack MAY declare a `sha256` hash in the manifest:

```json
{
  "id": "guide",
  "path": "content/guide.md",
  "type": "text/markdown",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

Conformant readers SHOULD verify these hashes when reading pack content. A mismatch indicates either accidental corruption or deliberate tampering.

**Recommendation:** Always include SHA-256 hashes for all content artifacts in published packs.

---

## Signatures

Packs MAY include cryptographic signatures over their content. Signatures are stored in the `signatures/` directory and referenced in `manifest.json`.

### Supported Signature Types

| Type | Description |
|------|-------------|
| `gpg` | GPG/PGP detached signature |
| `ssh` | SSH key signature (using `ssh-keygen -Y sign`) |
| `ed25519` | Raw Ed25519 signature |
| `jwt` | JSON Web Token (for integration with identity systems) |

### What Can Be Signed

| Scope | Description |
|-------|-------------|
| `manifest` | The `manifest.json` file |
| `full-pack` | The entire `.kpack` archive |
| `artifact:<id>` | A specific content artifact |

### Signature Example

```json
"signatures": [
  {
    "id": "sig-author",
    "type": "gpg",
    "signer": "author-01",
    "signed_at": "2026-05-01T12:00:00Z",
    "covers": "manifest",
    "path": "signatures/author.sig",
    "public_key_hint": "0xABCD1234..."
  }
]
```

### Verification Workflow

1. Read `manifest.json` to find signature records
2. Locate the signature file at the declared `path`
3. Obtain the signer's public key (from `public_key_hint`, ORCID, or a key server)
4. Verify the signature over the declared scope

Tools for signature creation and verification are planned for the OKPF CLI.

---

## Trust Model

OKPF signatures prove that a key holder signed a pack at a given time. They do **not** prove:

- That the key holder is who they claim to be (that requires key infrastructure — PGP web of trust, certificate authority, or similar)
- That the content is accurate
- That the contributors' claims about provenance are true

**OKPF provides the infrastructure for trust; communities establish the norms.**

A registry can require that packs in a specific domain be signed by verified contributors. An organization can establish an internal CA for signing internal packs. These are policy decisions above the format level.

---

## Handling Untrusted Packs

When consuming a pack from an untrusted source:

1. **Verify content hashes** before reading artifacts
2. **Check signatures** if present, and verify the signing key against a trusted source
3. **Inspect provenance** for suspicious claims or missing records
4. **Review evaluations** to get a sense of claimed accuracy
5. **Be skeptical of packs with no license** — even if technically valid, they should prompt caution

---

## Content Safety

Knowledge packs may contain information that is dangerous in the wrong hands (e.g., medical dosing, chemical procedures, electrical systems). OKPF does not define content safety controls. However:

- The `tags` field in the manifest can include safety-relevant tags
- The `license.json` `custom_terms` field can include safety notices
- Extensions can carry domain-specific safety metadata

Communities that distribute sensitive knowledge packs should establish their own safety review and access control processes at the registry/distribution layer.

---

## Archive Security

The `.kpack` format is a ZIP archive. Tooling that unpacks `.kpack` files should:

- **Reject path traversal** — Do not allow paths like `../../etc/passwd`
- **Enforce size limits** — Very large archives should be rejected or handled with streaming reads
- **Verify ZIP integrity** — Check CRC checksums on extraction
- **Not execute content** — Packs are data, not code; no automatic execution of content

---

## Reporting Security Issues

If you discover a security issue in the OKPF specification or reference implementations, please report it privately to the maintainers via GitHub Security Advisories before public disclosure.
