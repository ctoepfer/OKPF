# OKPF Core v0.1

OKPF, the Open Knowledge Pack Format, is an open, model-neutral, vendor-neutral, and blockchain-neutral format for packaging structured human expertise.

Version 0.1 is intentionally small. It defines a package boundary, a manifest, universal records, and optional structures for source retention, provenance, import reporting, domain profiles, and rebuild/audit workflows.

## Goals

- Package useful knowledge without depending on any application, model, embedding provider, vector database, or chain.
- Preserve original source files when possible, not only normalized records.
- Treat ZIP and future `.kpack` files as containers.
- Validate practical usefulness: package identity, record discoverability, parseable records, safe paths, and clear import/report metadata.
- Support partial success and clear failure stages during ingestion.
- Leave room for ownership, leasing, signatures, royalties, provenance extensions, and other future ecosystem layers without requiring them in core.

## Required Structure

```text
manifest.json
records/
```

`manifest.json` is the authoritative package index. `records/` contains normalized records suitable for downstream systems to inspect, chunk, index, fine-tune on, simulate with, or transform further.

## Optional Structure

```text
sources/
docs/
assets/
schemas/
provenance/
chunks/
import_report.json
README.md
LICENSE
```

Original inputs belong in `sources/` whenever redistribution rights permit. Derived chunks belong in `chunks/` and are not required. Schemas and profile-specific extensions belong in `schemas/`.

## Profiles and Facets

OKPF Core defines package structure, manifest basics, records, artifacts, provenance, licensing, and validation basics. Profiles define optional domain-specific conventions such as recommended record types, facets, vocabularies, schemas, and examples.

A manifest may declare zero or more profiles:

```json
{
  "profiles": ["okpf-core", "okpf-fermentation"]
}
```

Unknown profiles should not make a package invalid under core validation.

Records may include optional `facets`, an object of machine-readable classification hints. OKPF Core does not define a global facet vocabulary. Domain-specific concepts, including fermentation and recipe concepts, belong in profiles rather than in core fields.

## `.kpack` Container

A `.kpack` file is a ZIP archive containing the same directory layout. ZIP entry paths MUST be safe relative paths. Importers MUST reject absolute paths and traversal paths such as `../secret`, `/tmp/file`, or `records/../../file`.

Importers SHOULD also reject platform-specific unsafe paths, including Windows drive paths and backslash-separated traversal.

## Lifecycle

```text
original source
-> extraction
-> normalization
-> validation
-> optional chunking
-> indexing/import by target system
-> rebuild/audit/reuse
```

OKPF packages the durable artifacts in this lifecycle. It does not prescribe a specific extraction engine, embedding model, vector database, RAG stack, fine-tuning system, robotics runtime, blockchain, or application architecture.

## Embeddings and Chunks

OKPF does not require embeddings. Chunks are optional derived artifacts. A target system may create its own chunks and embeddings from records and sources.

Import reports may distinguish `record_count`, `chunk_count`, and `indexed_count`. `record_count` means normalized source records. `chunk_count` means derived chunks. `indexed_count` is importer-specific and should define its counting unit, such as `chunk`.

## Reference Importers

Lumina may act as an early reference importer for practical feedback, but OKPF does not depend on Lumina. Other importers should be able to read the same package using only the spec.
