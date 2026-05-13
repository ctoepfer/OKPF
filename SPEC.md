# OKPF v0.1.0 Specification

**Status:** Draft  
**Canonical human-readable specification:** this file

OKPF, the Open Knowledge Pack Format, is an open, model-neutral, vendor-neutral, and blockchain-neutral standard for packaging structured human expertise as portable knowledge archives.

OKPF is a packaging format, not a model format, vector database format, blockchain protocol, marketplace, or single-domain interchange format. It is designed to carry knowledge and its context for AI systems, robotics, RAG, fine-tuning preparation, simulation, education, workflow execution, evaluation, and future computational tools.

## What OKPF Is

An OKPF package is a directory or `.kpack` archive that contains knowledge artifacts plus machine-readable context:

- identity and version metadata
- artifacts and/or normalized records
- provenance and attribution
- license and usage policy
- optional dependencies
- optional integrity hashes
- optional workflows, evaluations, docs, sources, assets, chunks, and schemas

The format is intentionally easy to inspect. A conforming consumer starts with `manifest.json`.

## What a `.kpack` Is

A `.kpack` file is a ZIP-based OKPF package. It contains the same files as a directory package.

ZIP entries MUST use safe relative paths. Producers MUST NOT write absolute paths, parent traversal, backslash traversal, Windows drive paths, or NUL bytes. Validators and importers MUST reject unsafe paths such as:

```text
/absolute/file.txt
../outside.txt
records/../../outside.txt
C:\Users\name\file.txt
sources\..\outside.txt
```

## Required Package Structure

Every OKPF v0.1.0 package MUST contain:

```text
manifest.json
```

Every package MUST also declare at least one useful knowledge payload in one or more of:

```text
artifacts
records
content
```

`artifacts` is the preferred v0.1.0 field for package files. `records` is the preferred field for normalized universal records. `content` is accepted as a compatibility alias for earlier examples and tooling.

Common package directories:

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

Only `manifest.json` and a declared payload are required. Other files and directories are optional.

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

For compatibility, readers MAY treat legacy `id` as `package_id` when `package_id` is absent.

## Optional Manifest Fields

Common optional fields include:

| Field | Type | Meaning |
|---|---|---|
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
| `dependencies` | array | Optional package or external dependencies |
| `integrity` | object | Optional hashes for verification |
| `evaluations` | object or array | Evaluation files or records |
| `workflows` | array | Workflow artifacts |
| `ai` | object | Advisory AI consumption hints |
| `extensions` | object | Namespaced extension data |

Unknown optional fields MUST NOT make a package invalid. Consumers SHOULD preserve unknown fields when rewriting manifests.

## Artifact Model

Artifacts are files carried by the package. They may be Markdown, TXT, PDF, JSON, JSONL, CSV, Parquet, images, videos, diagrams, source files, workflows, evaluations, BeerXML, SCORM, xAPI, JSON-LD, RDF, or other domain-specific formats.

`artifacts` entries SHOULD include:

| Field | Type | Meaning |
|---|---|---|
| `path` | string | Safe relative path |
| `type` | string | Media type or practical type label |
| `title` | string | Human-readable title |
| `role` | string | Role such as `source`, `guide`, `workflow`, `evaluation`, `domain_artifact`, or `reference` |
| `description` | string | Short description |
| `sha256` | string | Optional file hash |

Earlier manifests may use `content` with the same structure. Validators SHOULD check both.

## Record Model

Records are normalized knowledge units. They are useful for RAG, fine-tuning preparation, evaluation, indexing, and agent ingestion, but not every artifact must be converted to a record.

Minimal record fields:

| Field | Type |
|---|---|
| `id` | string |
| `record_type` | string |
| `title` | string |
| `text` | string |
| `domain` | string |
| `metadata` | object |

`record_type` is intentionally open-ended. Domain profiles may recommend values.

## Provenance and Attribution Model

OKPF separates source retention, attribution, and transformation history:

- `sources` lists retained or referenced source files.
- `creators` and `contributors` identify people or organizations.
- `provenance` points to source lists, transformation logs, review notes, extraction tools, or rebuild information.

Attribution SHOULD be specific enough for humans and tools to understand who created, transformed, curated, or reviewed the knowledge.

## Licensing Model

`license` describes legal permission. It may be an inline object or a reference to a license file.

Examples:

```json
{
  "license": {
    "type": "CC-BY-4.0",
    "details": "Attribution required."
  }
}
```

```json
{
  "license": {
    "$ref": "license.json"
  }
}
```

OKPF does not replace legal review. It makes license information discoverable and machine-readable.

## Usage Policy Model

`usage_policy` is separate from `license`.

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

## Dependency Model

`dependencies` is an optional array. Each dependency may include:

| Field | Type |
|---|---|
| `name` | string |
| `version` | string |
| `uri` | string |
| `optional` | boolean |
| `description` | string |

Dependency resolution is non-mandatory in v0.1.0. Validators MAY check structure, but MUST NOT be required to fetch remote dependencies.

## Integrity and Hash Model

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

Future OKPF versions may define detached signatures, Ed25519 signatures, DID or public-key references, timestamping, cryptographic seals, registry attestations, or blockchain anchoring. None of these are required for v0.1.0.

## Compatibility and Versioning

OKPF uses semantic versioning for the specification and for packages.

Consumers SHOULD:

- accept compatible `0.1` and `0.1.0` manifests
- ignore and preserve unknown optional fields
- reject unsafe paths
- avoid assuming a package is tied to any model, vector database, runtime, or blockchain
- avoid requiring optional fields such as `ai`, `integrity`, `dependencies`, or `usage_policy`

Producers SHOULD:

- keep paths relative and portable
- include clear license and attribution
- preserve original sources when rights allow
- include normalized records when useful
- include provenance when packages are derived from source materials

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
- validate optional `usage_policy`, `dependencies`, `integrity`, provenance, and import report shapes when present
- return a nonzero exit code on failure

Validators SHOULD NOT:

- require embeddings
- fetch remote dependencies
- require blockchain anchors
- require signatures
- require every artifact to be normalized into records
- reject packages only because optional unknown fields are present

## Consumer Expectations

Consumers SHOULD start from `manifest.json`, inspect license and usage policy before ingestion, preserve unknown fields, and process only the fields and artifacts they understand.

If a consumer does not understand an optional field or profile, it SHOULD warn and continue with the core package when safe to do so.
