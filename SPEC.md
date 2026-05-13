# OKPF v0.1.0 Specification

**Status:** Draft  
**Canonical human-readable specification:** this file

OKPF, the Open Knowledge Pack Format, is an open, model-neutral, vendor-neutral, and blockchain-neutral standard for packaging structured human expertise as portable knowledge archives.

OKPF is a packaging format. It is not a model format, vector database format, blockchain protocol, marketplace, runtime, or single-domain interchange format.

## Normative Language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in uppercase.

This specification is implementation-neutral. It does not require Python, JavaScript, a particular validator, a particular AI model, a vector database, a workflow runtime, a registry, or a blockchain.

## Simple Core, Optional Power

A minimal OKPF pack SHOULD be possible to write by hand. Advanced capabilities SHOULD be optional layers.

Dependency resolution, cryptographic signatures, registries, JSON-LD mappings, workflow runtimes, and evaluation runners MUST NOT be required for a basic valid pack. OKPF SHOULD support serious trust and interoperability features without making the Hello World example difficult to understand.

## What OKPF Is

An OKPF package is a directory or `.kpack` archive that contains knowledge artifacts plus machine-readable context:

- identity and version metadata
- artifacts and/or normalized records
- provenance and attribution
- license and usage policy
- optional dependencies
- optional integrity hashes
- optional workflows, evaluations, docs, sources, assets, chunks, and schemas

Consumers MUST start with `manifest.json`.

## `.kpack` Archive Structure

The preferred file extension is `.kpack`. The suggested MIME type is `application/x-kpack`. Formal MIME registration is future work.

A `.kpack` file MUST be a ZIP archive containing the same file layout as a directory package. ZIP entries MUST use safe relative paths. Producers MUST NOT write absolute paths, parent traversal, backslash traversal, Windows drive paths, or NUL bytes. Validators and importers MUST reject unsafe paths such as:

```text
/absolute/file.txt
../outside.txt
records/../../outside.txt
C:\Users\name\file.txt
sources\..\outside.txt
```

## Required Package Structure

Every OKPF v0.1.0 package MUST contain `manifest.json`.

Every package MUST declare at least one useful knowledge payload in one or more of:

- `artifacts`
- `records`
- `content`

`artifacts` is the preferred v0.1.0 field for package files. `records` is the preferred field for normalized universal records. `content` is accepted as a compatibility alias for earlier v0.1 examples and tools.

Common optional directories and files include:

```text
content/
records/
sources/
docs/
assets/
schemas/
provenance/
chunks/
evals/
workflows/
import_report.json
README.md
LICENSE
```

## Schema Versioning

The v0.1.0 manifest schema is located at:

```text
schemas/v0.1.0/manifest.schema.json
```

Manifests MAY include:

```json
"$schema": "https://okpf.org/schema/v0.1.0/manifest.schema.json"
```

The URL is an intended stable public schema identifier. Official schema URLs are expected to become stable once OKPF has a public documentation site. Local repository schemas are authoritative for this draft.

## Required Manifest Fields

`manifest.json` MUST be a UTF-8 JSON object with:

| Field | Type | Meaning |
|---|---|---|
| `okpf_version` | string | Spec version, such as `0.1.0` |
| `package_id` | string | Stable package identifier |
| `name` | string | Human-readable package name |
| `version` | string | Package version |
| `domain` | string | Primary knowledge domain |
| `license` | object | License summary or reference |
| `artifacts` or `records` | array | Declared payload files |

For compatibility, consumers MAY treat legacy `id` as `package_id` when `package_id` is absent. Consumers MAY treat legacy `content` as `artifacts`.

## Optional Manifest Fields

Common optional fields include:

| Field | Type | Meaning |
|---|---|---|
| `$schema` | string | Schema identifier |
| `title` | string | Display title when different from `name` |
| `description` | string | Short human-readable description |
| `profiles` | array | Profiles such as `okpf-core` or `okpf-fermentation` |
| `tags` | array | Discovery tags |
| `language` | string | Primary BCP 47 language |
| `created` / `updated` | string | Timestamps |
| `creators` | array | People or organizations responsible for the pack |
| `contributors` | array or object | Contributor records or reference |
| `sources` | array | Retained original or intermediate files |
| `provenance` | object | Source and transformation references |
| `usage_policy` | object | Machine-readable operational intent |
| `expert_notes` | object | Human-authored rationale and context |
| `dependencies` | array | Optional package or external dependencies |
| `integrity` | object | Optional hashes for verification |
| `evaluations` | object or array | Evaluation files or records |
| `workflows` | array | Workflow artifacts |
| `ai` | object | Advisory AI consumption hints |
| `extensions` | object | Namespaced extension data |

Unknown optional fields MUST NOT make a package invalid. Consumers SHOULD preserve unknown fields when rewriting manifests.

## Artifact Model

Artifacts are files carried by the package. They MAY be Markdown, TXT, PDF, JSON, JSONL, CSV, Parquet, images, videos, diagrams, source files, workflows, evaluations, BeerXML, SCORM, xAPI, JSON-LD, RDF, or other domain-specific formats.

Artifact paths MUST be safe relative paths. Artifact descriptors SHOULD include:

| Field | Type | Meaning |
|---|---|---|
| `path` | string | Safe relative path |
| `type` | string | Media type or practical type label |
| `title` | string | Human-readable title |
| `role` | string | Artifact role |
| `description` | string | Short description |
| `sha256` | string | Optional file hash |

Recommended artifact roles include `source`, `guide`, `reference`, `domain_artifact`, `record_file`, `workflow`, `evaluation`, `example`, `asset`, `schema`, and `documentation`. Consumers SHOULD NOT reject unknown roles.

## Record Model

Records are normalized knowledge units. They are useful for RAG, fine-tuning preparation, evaluation, indexing, and agent ingestion, but not every artifact MUST be converted to a record.

Minimal record fields:

| Field | Type |
|---|---|
| `id` | string |
| `record_type` | string |
| `title` | string |
| `text` | string |
| `domain` | string |
| `metadata` | object |

`record_type` is intentionally open-ended. Domain profiles MAY recommend values.

## License vs Usage Policy

`license` describes legal permission. It MAY be an inline object or a reference to a license file.

`usage_policy` is separate:

- `license` = legal permission.
- `usage_policy` = machine-readable operational intent and constraints.

Suggested `usage_policy` fields:

| Field | Type |
|---|---|
| `allow_rag` | boolean |
| `allow_fine_tuning` | boolean |
| `allow_evaluation` | boolean |
| `allow_commercial_use` | boolean |
| `allow_derivatives` | boolean |
| `allow_commercial_derivatives` | boolean |
| `require_attribution` | boolean |
| `notes` | string |

Consumers SHOULD treat `usage_policy` as advisory operational metadata unless the license makes the same restriction legally binding.

## Provenance and Attribution

OKPF separates source retention, attribution, and transformation history:

- `sources` lists retained or referenced source files.
- `creators` and `contributors` identify people or organizations.
- `provenance` points to source lists, transformation logs, review notes, extraction tools, or rebuild information.

Attribution SHOULD be specific enough for humans and tools to understand who created, transformed, curated, or reviewed the knowledge.

## Expert Notes

`expert_notes` MAY provide human-authored rationale and context. Suggested fields:

| Field | Type |
|---|---|
| `rationale` | string |
| `assumptions` | string or array |
| `limitations` | string or array |
| `decision_basis` | string |
| `review_notes` | string |

`expert_notes` is for human-authored rationale and review context. It MUST NOT be treated as private model reasoning traces, and OKPF v0.1.0 defines no private reasoning-trace field.

## Dependencies

`dependencies` is an optional array. Each dependency MAY include:

| Field | Type |
|---|---|
| `name` | string |
| `version` | string |
| `uri` | string |
| `optional` | boolean |
| `description` | string |

Dependency resolution is non-mandatory in v0.1.0. Validators MAY check structure, but MUST NOT be required to fetch remote dependencies.

## Cross-Pack References

Tools MAY use this early human-readable reference convention:

```text
okpf:pack-id@version:/path/to/artifact
```

Example:

```text
okpf:org.example.brewing-basics@0.1.0:/content/guide.md
```

This convention MAY evolve before v1.0.0. It does not imply registry lookup, dependency resolution, or network fetching.

## Integrity and Hashes

`integrity` is optional. The recommended v0.1.0 structure is:

```json
{
  "algorithm": "sha256",
  "manifest_sha256": "...",
  "content_sha256": "...",
  "artifacts": [
    {
      "path": "content/hello.md",
      "sha256": "..."
    }
  ]
}
```

Validators MAY verify hashes when present. Consumers SHOULD treat missing hashes as unknown integrity, not as failure.

### Future: Signatures and Cryptographic Seals

Future OKPF versions MAY support detached signatures, Ed25519, PGP, DID or public-key references, timestamping, blockchain anchoring, cryptographic seals, and Merkle roots. None of these are required for v0.1.0.

### Future: Merkle Hashing

Future versions MAY support Merkle-tree-based content hashing so that a root hash can verify full archive contents while still allowing individual artifact verification. Merkle hashing is not mandatory in v0.1.0.

## Evaluations

Packs MAY include evaluation artifacts or references. OKPF v0.1.0 defines a lightweight evaluation result schema but does not require an evaluation runner.

Evaluation result files SHOULD use `schemas/v0.1.0/evaluation-result.schema.json` when possible. Consumers MAY store evaluation results inside or outside a pack.

## Workflows

Packs MAY include workflow artifacts. OKPF v0.1.0 does not require a workflow runtime. Consumers SHOULD inspect workflow type, license, usage policy, and provenance before execution.

## Extensions

Extensions MAY be added through unknown manifest fields or an `extensions` object. Extension keys SHOULD use stable namespacing when possible. Consumers MUST ignore unknown optional fields they do not understand and SHOULD preserve them when rewriting manifests.

## Compatibility and Versioning

OKPF uses semantic versioning for the specification and for packages.

Consumers SHOULD:

- accept compatible `0.1` and `0.1.0` manifests
- ignore and preserve unknown optional fields
- reject unsafe paths
- avoid assuming a package is tied to any model, vector database, runtime, registry, or blockchain
- avoid requiring optional fields such as `ai`, `integrity`, `dependencies`, `expert_notes`, or `usage_policy`

Producers SHOULD:

- keep paths relative and portable
- include clear license and attribution
- preserve original sources when rights allow
- include normalized records when useful
- include provenance when packages are derived from source materials
- keep minimal packs easy to author by hand

## Validator Expectations

A basic OKPF v0.1.0 validator SHOULD:

- load `manifest.json`
- validate the manifest shape against the published schema when possible
- confirm required manifest fields
- confirm at least one declared payload exists
- confirm declared artifact, content, source, and record paths exist
- reject unsafe paths
- parse JSON and JSONL record files
- check required record fields
- validate optional `usage_policy`, `dependencies`, `integrity`, `expert_notes`, provenance, and import report shapes when present
- return a nonzero exit code on failure

Validators SHOULD NOT:

- require embeddings
- fetch remote dependencies
- require blockchain anchors
- require signatures
- require Merkle roots
- require every artifact to be normalized into records
- reject packages only because optional unknown fields are present

## Consumer Expectations

Consumers SHOULD start from `manifest.json`, inspect license and usage policy before ingestion, preserve unknown fields, and process only the fields and artifacts they understand.

If a consumer does not understand an optional field or profile, it SHOULD warn and continue with the core package when safe to do so.
