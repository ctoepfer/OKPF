<!-- SPDX-License-Identifier: Apache-2.0 -->
# OKPF Semantic Retrieval Extension

Extension Key: `okpf.semantic_retrieval.v0`  
Status: Draft / Experimental

**Applies to:** OKPF Core v0.1.x

---

## 1. Overview

The OKPF Semantic Retrieval Extension defines optional manifest metadata and artifact conventions for `.kpack` archives that include retrieval-ready chunks, embedding vectors, semantic index assets, retrieval prompts, citation behavior, and reproducibility metadata.

This document defines an optional extension, not a Core redesign and not a domain profile.

The extension helps capable consumers:

- accelerate local Retrieval-Augmented Generation (RAG) ingestion,
- verify embedding compatibility before reusing packaged vectors,
- rebuild chunks and embeddings deterministically from canonical source material,
- and preserve source-grounded attribution through the retrieval pipeline.

When declared, the extension metadata MUST be nested within the top-level `extensions` object of `manifest.json` using the key `okpf.semantic_retrieval.v0`.

This extension does not couple OKPF Core to any embedding model, vector database, inference runtime, hosted service, or network dependency. It is an optional, additive metadata layer. A consumer that has never heard of `okpf.semantic_retrieval.v0` can still validate, unpack, and use the pack's core records and artifacts.

The extension recognizes a layered hierarchy of retrieval-related material:

- Source records and source artifacts are the canonical knowledge layer for the pack version.
- Chunks are retrieval units.
- Portable vectors are database-agnostic embedding interchange artifacts.
- Prebuilt indexes are optional acceleration artifacts.

## 2. Non-Goals

This extension does **not**:

- make embeddings required for OKPF Core validity
- define a vector database format
- require any specific embedding model
- require any vector database engine
- require network access or live API dependencies for Core validation, inspection, or extension metadata processing
- define inference behavior
- define workflow execution semantics
- certify factual correctness, safety, legal compliance, attribution truth, or expertise quality
- replace source records or source artifacts as the canonical knowledge layer

## 3. Directory Layout Convention

The following layout is recommended, not mandatory. Producers MAY omit any subset of these directories.

```text
my-pack.kpack/
├── manifest.json
├── records/
│   └── chunks.jsonl
├── sources/
│   └── source-documents/
├── vectors/
│   ├── raw/
│   │   ├── vectors.parquet
│   │   └── metadata.jsonl
│   └── prebuilt/
│       ├── qdrant/
│       ├── faiss/
│       └── sqlite-vss/
├── prompts/
│   ├── retrieval-system.md
│   └── citation-policy.md
└── evals/
    └── retrieval-eval.jsonl
```

Layer semantics:

- **Source records and source artifacts** (`records/`, `sources/`) are the canonical knowledge layer for the pack version, per OKPF Core.
- **Chunks** (e.g. `records/chunks.jsonl`) are retrieval units derived from source material.
- **Portable vectors** (`vectors/raw/`) are database-agnostic embedding interchange artifacts. They carry embedding data in a format any consumer can read without a specific vector database engine.
- **Prebuilt indexes** (`vectors/prebuilt/<engine>/`) are optional acceleration artifacts tied to a specific vector database engine. They accelerate ingestion for consumers that use that engine but are never the canonical representation of the pack's knowledge.

## 4. Manifest Extension Example

```json
{
  "okpf_version": "0.1.0",
  "package_id": "org.example.semantic-history",
  "name": "Example Semantic History Pack",
  "version": "1.0.0",
  "domain": "general_knowledge",
  "license": "CC-BY-4.0",
  "extensions": {
    "okpf.semantic_retrieval.v0": {
      "embedding_profile": {
        "model_name": "BAAI/bge-large-en-v1.5",
        "model_family": "bge",
        "dimensions": 1024,
        "distance_metric": "cosine",
        "normalized": true,
        "precision": "float32",
        "model_ref": {
          "type": "huggingface",
          "repo": "BAAI/bge-large-en-v1.5"
        }
      },
      "chunking": {
        "strategy": "recursive_token",
        "chunk_size_tokens": 512,
        "chunk_overlap_tokens": 64,
        "tokenizer": "cl100k_base"
      },
      "vector_artifacts": [
        {
          "path": "vectors/raw/vectors.parquet",
          "format": "parquet",
          "role": "portable_vectors"
        },
        {
          "path": "vectors/raw/metadata.jsonl",
          "format": "jsonl",
          "role": "vector_metadata"
        },
        {
          "path": "vectors/prebuilt/qdrant/",
          "format": "qdrant_snapshot",
          "role": "prebuilt_index",
          "engine": "qdrant"
        }
      ],
      "retrieval_prompts": [
        {
          "path": "prompts/retrieval-system.md",
          "role": "retrieval_prompt"
        }
      ],
      "retrieval_evals": [
        {
          "path": "evals/retrieval-eval.jsonl",
          "role": "retrieval_eval"
        }
      ],
      "citation_policies": [
        {
          "path": "prompts/citation-policy.md",
          "role": "citation_policy"
        }
      ]
    }
  }
}
```

## 5. Field Semantics

### `embedding_profile`

Required only when the extension declares precomputed vector artifacts (any `vector_artifacts` entry with role `portable_vectors` or `prebuilt_index`). Otherwise optional.

| Field | Description |
|---|---|
| `model_name` | Identifier of the embedding model used to produce the packaged vectors. |
| `model_family` | Model family or architecture line (e.g. `bge`, `e5`, `gte`). |
| `dimensions` | Vector dimensionality. |
| `distance_metric` | One of `cosine`, `inner_product`, `l2`. |
| `normalized` | Whether packaged vectors are L2-normalized. |
| `precision` | Numeric precision of stored vectors (e.g. `float32`, `float16`). |
| `model_ref` | Pointer to the embedding model source, e.g. `{"type": "huggingface", "repo": "..."}`. Advisory only; consumers are not required to fetch it. |

### `chunking`

Recommended when chunks, vectors, or rebuildable retrieval artifacts are declared. Otherwise optional.

| Field | Description |
|---|---|
| `strategy` | Chunking strategy identifier (e.g. `recursive_token`, `fixed_char`, `semantic`). |
| `chunk_size_tokens` | Target chunk size in tokens. |
| `chunk_overlap_tokens` | Token overlap between adjacent chunks. |
| `tokenizer` | Tokenizer used to measure chunk size (e.g. `cl100k_base`). |

### `vector_artifacts`, `retrieval_prompts`, `retrieval_evals`, `citation_policies`

Each is an array of artifact references (`path`, `format`, `role`, and role-specific fields such as `engine`). All four arrays are required only when the corresponding artifact type is packaged; none is individually mandatory.

`vector_artifacts` entries MAY declare any interchange format for portable vectors. This draft recommends Apache Parquet for the initial portable vector representation, given its columnar layout, wide tooling support, and suitability for large embedding matrices. Producers MAY use other formats; consumers SHOULD NOT assume Parquet is the only supported format.

## 6. Artifact Roles

`vector_artifacts`, `retrieval_prompts`, `retrieval_evals`, and `citation_policies` entries use a `role` field. Recognized roles:

| Role | Description |
|---|---|
| `portable_vectors` | Database-agnostic embedding interchange file. |
| `vector_metadata` | Metadata mapping vectors to chunks or records. |
| `source_chunks` | Pointer to the chunk records the vectors were derived from. |
| `prebuilt_index` | Engine-specific index snapshot or build artifact. |
| `retrieval_prompt` | Optional advisory metadata describing suggested retrieval, grounding, and citation behavior. |
| `retrieval_eval` | Retrieval evaluation dataset or report. |
| `citation_policy` | Declared citation/attribution behavior for retrieval outputs. |

When `portable_vectors` and `vector_metadata` are both declared, consumers SHOULD treat vector row order and metadata row order as aligned unless an explicit vector identifier or row index is provided.

## 7. Compliance and Consumer Behavior

- Consumers MUST NOT require this extension for OKPF Core validity.
- A core-valid OKPF pack remains valid when this extension is absent, ignored, unsupported, or partially unsupported.
- Consumers that do not understand this extension SHOULD preserve the extension block when rewriting `manifest.json`.
- Semantic retrieval consumers MUST verify declared embedding compatibility before using packaged vector artifacts.
- If a consumer uses an embedding model, dimension count, normalization behavior, precision, or distance metric that differs from the declared `embedding_profile`, it MUST NOT treat the packaged vectors as compatible.
- Consumers MAY rebuild embeddings from source chunks, source records, or declared source artifacts.
- Consumers MAY bypass packaged vectors.
- Consumers SHOULD treat portable vector artifacts as the preferred embedding interchange format.
- Consumers MAY use prebuilt indexes for performance or convenience.
- Consumers MUST NOT treat prebuilt indexes as the canonical knowledge source.
- Retrieval prompts are advisory execution metadata only.
- Retrieval prompts MUST NOT be interpreted as mandatory workflow execution semantics.
- Citation policies are advisory metadata describing intended attribution behavior; they MUST NOT be interpreted as a substitute for the pack's `license` or `usage_policy` fields.

## 8. Security and Validation

- Consumers MUST NOT execute pack contents.
- Consumers MUST apply normal OKPF safe-path rules to all extension-declared paths.
- Consumers SHOULD verify hashes when declared by the core manifest.
- The extension does not verify factual correctness, safety, legal compliance, attribution truth, or expertise quality.
- Validation of this extension checks declared structure and compatibility metadata only.

## 9. Future Work

- JSON Schema for `okpf.semantic_retrieval.v0`
- Example semantic retrieval pack
- Retrieval evaluation dataset examples
- Citation policy examples
- Rebuild tooling for regenerating chunks and vectors from source
- Optional support for additional portable vector formats

---

*See also: `docs/manifest.md`, `docs/package-structure.md`, `docs/security.md`, `docs/model-artifacts.md`*
