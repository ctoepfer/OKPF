# OKPF Specification

**Version:** 0.1.0  
**Status:** Draft  
**Date:** 2026-05-06

---

## 1. Introduction

The Open Knowledge Pack Format (OKPF) defines a portable, self-describing archive format for packaging structured human expertise. A knowledge pack (`.kpack`) is a directory or archive that bundles content, metadata, licensing, provenance, and attribution into a single transferable unit.

OKPF is designed to be:

- **Model-neutral** — no dependency on any AI, ML, or embedding model
- **Vendor-neutral** — no dependency on any cloud provider or SaaS platform
- **Blockchain-neutral** — blockchain anchoring is optional and chain-agnostic
- **Offline-capable** — packs are fully usable without network access
- **Extensible** — new content types and metadata can be added without breaking readers
- **Backward-compatible** — older packs remain readable as the schema evolves

OKPF Core describes a portable, inspectable, validated package of knowledge artifacts and metadata. It does not define payment systems, ownership enforcement, marketplaces, blockchain mechanics, encryption, or execution environments. Those are optional extensions to be built on top of a stable core.

| People often expect | What OKPF actually is |
|---------------------|----------------------|
| A platform or marketplace | A file format specification |
| An AI model or embedding service | A packaging format that *can* optionally include embeddings |
| A blockchain project | A format with optional, chain-agnostic external anchors |
| A training data format | A knowledge pack format (packs may declare training permissions) |
| A replacement for documentation systems | A portable, structured complement to them |
| A proprietary standard | An open standard with community governance |

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Knowledge Pack** | A self-contained bundle of structured expertise conforming to this spec |
| **Pack** | Shorthand for Knowledge Pack |
| **.kpack** | File extension for a packaged knowledge pack (ZIP-based archive) |
| **Manifest** | The root descriptor file (`manifest.json`) of a pack |
| **Artifact** | Any content item within a pack (document, image, workflow, etc.) |
| **Domain** | The field of expertise the pack covers (e.g., `brewing`, `medicine`) |
| **Contributor** | Any person or organization that created or transformed pack content |
| **Provenance** | A record of where content came from and how it was transformed |
| **Anchor** | An optional reference to an external registry, ledger, or content-addressed store |

---

## 3. Pack Structure

### 3.1 Directory Layout

A knowledge pack is a directory (or ZIP archive with `.kpack` extension) with the following structure:

```
<pack-name>/
├── manifest.json          REQUIRED  Root descriptor
├── README.md              RECOMMENDED  Human-readable overview
├── LICENSE                RECOMMENDED  License file (text)
├── license.json           REQUIRED (if $ref)  Machine-readable license
├── provenance.json        RECOMMENDED  Chain of custody
├── contributors.json      RECOMMENDED  Attribution records
├── content/               RECOMMENDED  Content artifacts
│   └── ...
├── prompts/               OPTIONAL  Prompt templates
│   └── ...
├── evals/                 OPTIONAL  Evaluation test cases
│   └── ...
├── workflows/             OPTIONAL  Structured workflow definitions
│   └── ...
├── embeddings/            OPTIONAL  Pre-computed embeddings
│   └── ...
├── signatures/            OPTIONAL  Cryptographic signatures
│   └── ...
└── extensions/            OPTIONAL  Vendor/domain extensions
    └── ...
```

### 3.2 Archive Format

When distributed as a file, a pack MUST be a ZIP archive with the `.kpack` extension. The archive MUST NOT use password protection. The archive SHOULD use DEFLATE compression level 6 or higher for text files and store (no compression) for already-compressed binary files.

### 3.3 File Encoding

All JSON files MUST be encoded in UTF-8. Text content files SHOULD be encoded in UTF-8. Binary files are unrestricted.

---

## 4. manifest.json

The manifest is the root descriptor of a knowledge pack. It MUST be present at the root of the pack.

### 4.1 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `okpf_version` | string | OKPF spec version this pack conforms to (SemVer) |
| `id` | string | Globally unique pack identifier (URN format recommended) |
| `name` | string | Human-readable pack name |
| `version` | string | Pack version (SemVer) |
| `domain` | string | Primary knowledge domain |
| `created` | string | ISO 8601 creation timestamp |
| `license` | object or `$ref` | Licensing declaration or reference to `license.json` |
| `content` | array | List of content artifact descriptors |

### 4.2 Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Short human-readable description |
| `tags` | array of strings | Discovery and categorization tags |
| `language` | string | BCP 47 language code (e.g., `"en"`) |
| `contributors` | object or `$ref` | Attribution reference |
| `provenance` | object or `$ref` | Provenance reference |
| `updated` | string | ISO 8601 last-modified timestamp |

### 4.3 Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `pack_type` | string | Broad classification: `reference_pack`, `training_pack`, `workflow_pack`, `evaluation_pack`, `mixed_pack` |
| `intended_uses` | array | Advisory declared uses: `read`, `rag`, `fine_tuning`, `evaluation`, `workflow_execution`, `simulation`, `robotics`, `other` |
| `not_intended_for` | array of strings | Advisory excluded uses (not binding — use `license.json` for restrictions) |
| `homepage` | string (URI) | Pack homepage URL |
| `repository` | string (URI) | Source repository URL |
| `anchors` | array | External registry or blockchain anchors |
| `evaluations` | object or `$ref` | Reference to evaluations |
| `embeddings` | array | Embedding index descriptors |
| `signatures` | array | Cryptographic signature references |
| `dependencies` | array | References to other packs this one depends on |
| `capabilities` | array | AI capability tags (see [docs/concepts.md](docs/concepts.md)) |
| `ai` | object | AI interoperability hints (advisory) |
| `trust` | object | Verification state summary (advisory) |
| `extensions` | object | Namespace-keyed extension data |

### 4.4 Content Artifact Descriptor

Each item in the `content` array MUST include:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Artifact identifier (unique within pack) |
| `path` | string | Relative path within the pack |
| `type` | string | MIME type |

Each item SHOULD include:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable title |
| `description` | string | Brief description |
| `sha256` | string | SHA-256 hash of the file contents |
| `role` | string | Semantic role (see §8 — `guide`, `rag_source`, `evaluation`, `prompt_template`, etc.) |
| `language` | string | BCP 47 language code if different from pack default |

### 4.5 ID Format

Pack IDs SHOULD follow the URN format:

```
urn:okpf:<domain>:<name>:<version>
```

Example: `urn:okpf:brewing:water-chemistry:0.1.0`

For packs without a registered domain prefix, use a UUID URN:

```
urn:uuid:550e8400-e29b-41d4-a716-446655440000
```

---

## 5. license.json

Every pack MUST declare licensing terms.

### 5.1 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `spdx_expression` | string | [SPDX](https://spdx.org/licenses/) license expression |
| `scope` | object | What the license applies to |

### 5.2 Scope Fields

| Field | Type | Description |
|-------|------|-------------|
| `use` | string | License for using the knowledge (`open`, `restricted`, `commercial`, `personal`) |
| `redistribution` | string | License for redistribution |
| `derivative_works` | string | License for derivative works |
| `ai_training` | string | License for use as AI training data (`permitted`, `restricted`, `prohibited`, `unspecified`) |

### 5.3 Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `full_text_url` | string | URL to full license text |
| `full_text` | string | Inline full license text |
| `custom_terms` | string | Additional terms beyond the SPDX license |
| `attribution_required` | boolean | Whether attribution is required when using/redistributing |
| `attribution_text` | string | Required attribution text |

---

## 6. provenance.json

Provenance records the origin and transformation history of pack content.

### 6.1 Structure

```json
{
  "sources": [ ... ],
  "transformations": [ ... ],
  "created_by": "...",
  "created_at": "...",
  "notes": "..."
}
```

### 6.2 Source Record

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Source identifier |
| `type` | string | Source type: `original`, `derived`, `interview`, `publication`, `dataset` |
| `title` | string | Source title |
| `uri` | string | URI or URL of source (if applicable) |
| `accessed` | string | ISO 8601 date accessed |
| `sha256` | string | Hash of source content (if captured) |
| `license` | string | SPDX expression for source license |

### 6.3 Transformation Record

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Transformation identifier |
| `type` | string | `manual`, `automated`, `review`, `translation`, `summarization` |
| `input_sources` | array | Source IDs used as input |
| `output_artifacts` | array | Content artifact IDs produced |
| `performed_by` | string | Contributor ID |
| `performed_at` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `tool` | string | Tool used (if automated) |

---

## 7. contributors.json

Contributors are the humans and organizations responsible for pack content.

### 7.1 Contributor Record

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Contributor identifier (unique within pack) |
| `name` | string | Full name or organization name |
| `role` | string | `author`, `editor`, `reviewer`, `translator`, `curator`, `sponsor` |
| `contributions` | array | List of artifact IDs this contributor is credited for |

Optional:

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | Contact email |
| `orcid` | string | [ORCID](https://orcid.org) identifier |
| `url` | string | Personal or organization URL |
| `affiliation` | string | Institutional affiliation |

---

## 8. Content Types and Artifact Roles

OKPF supports any MIME type as content. The following roles are defined for use in the `content[].role` field:

| Role | Common MIME Types | Description |
|------|------------------|-------------|
| `guide` | `text/markdown`, `text/html` | Tutorial, how-to, or reference document for human readers |
| `transcript` | `text/markdown`, `text/plain` | Expert interview, Socratic dialogue, or recorded conversation |
| `workflow` | `application/json` | Structured process or decision tree |
| `evaluation` | `application/json`, `application/jsonl` | Test cases, rubrics, or benchmarks |
| `reference` | `application/pdf`, `text/markdown` | Reference material, tables, glossaries |
| `image` | `image/*` | Photographs, diagrams, illustrations |
| `data` | `application/json`, `text/csv` | Datasets, measurements, structured reference data |
| `rag_source` | `text/markdown`, `text/plain` | Content optimized for embedding-based retrieval (RAG) |
| `training_source` | `text/markdown`, `application/jsonl` | Content intended as AI/ML training or fine-tuning data |
| `prompt_template` | `text/markdown`, `text/plain` | Reusable prompt or instruction template |
| `documentation` | `text/markdown` | Pack-level documentation (README, changelogs, release notes) |
| `other` | any | Any artifact not covered by the above roles |

---

## 9. Evaluations

Evaluations provide test cases that can verify the quality of knowledge in a pack.

### 9.1 Evaluation Record

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Evaluation identifier |
| `type` | string | `qa`, `rubric`, `benchmark`, `checklist` |
| `question` | string | The question or prompt |
| `expected_answer` | string or object | Expected correct answer |
| `difficulty` | string | `beginner`, `intermediate`, `expert` |
| `source_artifacts` | array | Content artifact IDs that should answer this |

---

## 10. Embeddings (Optional)

Packs MAY include pre-computed embeddings for their content. Embeddings are optional and supplementary — the pack remains fully usable without them.

### 10.1 Embedding Descriptor

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Embedding set identifier |
| `model` | string | Human-readable model name |
| `model_version` | string | Model version |
| `provider` | string | Provider (e.g., `openai`, `cohere`, `local`) |
| `dimensions` | integer | Vector dimensions |
| `path` | string | Path to embedding file within pack |
| `format` | string | `npy`, `jsonl`, `safetensors` |
| `content_ids` | array | Artifact IDs these embeddings cover |
| `created` | string | ISO 8601 creation timestamp |

Embeddings from different providers SHOULD be stored as separate embedding descriptors so consumers can choose which to use.

---

## 11. Signatures (Optional)

Packs MAY include cryptographic signatures over their content.

### 11.1 Signature Record

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Signature identifier |
| `type` | string | `gpg`, `ssh`, `ed25519`, `jwt` |
| `signer` | string | Contributor ID |
| `signed_at` | string | ISO 8601 timestamp |
| `covers` | string | `manifest`, `full-pack`, `artifact:<id>` |
| `path` | string | Path to signature file |
| `public_key_hint` | string | Key fingerprint or URL |

---

## 12. Anchors (Optional)

Packs MAY include anchors to external registries, content-addressed stores, or blockchain networks.

### 12.1 Anchor Record

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | `ipfs`, `blockchain`, `registry`, `doi`, `arxiv` |
| `value` | string | The anchor value (CID, transaction hash, DOI, etc.) |
| `network` | string | For blockchain anchors: network name (e.g., `ethereum-mainnet`) |
| `created` | string | ISO 8601 timestamp |
| `note` | string | Human-readable context |

Anchors MUST NOT be required for pack functionality. They are informational pointers for additional verifiability.

---

## 13. Versioning and Compatibility

OKPF follows [Semantic Versioning](https://semver.org):

- **MAJOR**: Incompatible changes that require a new reader
- **MINOR**: New optional fields or content types; backward-compatible
- **PATCH**: Clarifications, corrections; no structural changes

Readers MUST NOT reject packs with unknown optional fields. Readers SHOULD warn when encountering a pack with a higher MAJOR version than they support.

Pack versions are independent of OKPF spec versions. Both are tracked in `manifest.json`.

---

## 14. Conformance

A pack is **conformant** with this specification if:

1. It contains a valid `manifest.json` at its root.
2. `manifest.json` includes all required fields with valid values.
3. It contains a valid `license.json`.
4. All `content` paths in the manifest resolve to files within the pack.
5. All SHA-256 hashes declared in the manifest match actual file contents.

A **conformant reader** MUST:

1. Parse and validate `manifest.json` against the published JSON Schema.
2. Resolve all content paths before presenting to the user.
3. Display licensing information when presenting pack content.
4. Preserve unknown fields when re-serializing (round-trip safe).

---

## 15. MIME Type and File Extension

| Item | Value |
|------|-------|
| File extension | `.kpack` |
| MIME type | `application/vnd.okpf.pack+zip` |
| Manifest MIME type | `application/vnd.okpf.manifest+json` |

---

## Appendix A: Example Manifest

```json
{
  "okpf_version": "0.1.0",
  "id": "urn:okpf:brewing:water-chemistry:0.1.0",
  "name": "Water Chemistry for Brewing",
  "version": "0.1.0",
  "description": "A practical guide to water chemistry for home and craft brewers.",
  "domain": "brewing",
  "tags": ["brewing", "water", "chemistry", "homebrewing"],
  "language": "en",
  "created": "2026-05-01T00:00:00Z",
  "license": { "$ref": "license.json" },
  "contributors": { "$ref": "contributors.json" },
  "provenance": { "$ref": "provenance.json" },
  "content": [
    {
      "id": "guide",
      "path": "content/guide.md",
      "type": "text/markdown",
      "title": "Water Chemistry Guide",
      "role": "guide",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    {
      "id": "mineral-chart",
      "path": "content/mineral-chart.json",
      "type": "application/json",
      "title": "Mineral Ion Reference Chart",
      "role": "data",
      "sha256": "..."
    }
  ],
  "evaluations": { "$ref": "evaluations/test-cases.json" }
}
```

---

## Appendix B: JSON Schema References

All schemas are in the `schemas/` directory:

- [`manifest.schema.json`](schemas/manifest.schema.json)
- [`license.schema.json`](schemas/license.schema.json)
- [`provenance.schema.json`](schemas/provenance.schema.json)
- [`contributor.schema.json`](schemas/contributor.schema.json)
- [`evaluation.schema.json`](schemas/evaluation.schema.json)
- [`task.schema.json`](schemas/task.schema.json)

---

## Appendix C: Changelog

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0 | 2026-05-06 | Added pack_type, intended_uses, not_intended_for, homepage, repository fields; expanded artifact roles with rag_source, training_source, prompt_template, documentation; added prompts/ and evals/ to recommended directory layout |
| 0.1.0-draft | 2026-05-05 | Initial draft |
