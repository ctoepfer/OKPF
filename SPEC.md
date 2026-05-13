# OKPF Specification

**Version:** 0.1  
**Status:** Draft

OKPF, the Open Knowledge Pack Format, is an open, model-neutral, vendor-neutral, blockchain-neutral standard for packaging structured human expertise for AI systems, robotics, RAG, fine-tuning, simulation, and future computational tools.

The current v0.1 design is intentionally practical:

- required package structure: `manifest.json` and `records/`
- optional retained sources, docs, assets, schemas, provenance, chunks, import reports, README, and LICENSE files
- `.kpack` as a ZIP-based container with safe relative paths only
- minimal universal records that support many domains and record types
- optional domain profiles for stricter domain-specific conventions
- no requirement for embeddings, vector databases, models, blockchain, or app-specific architecture

## Core Documents

- [Core v0.1](docs/spec-v0.1.md)
- [Package structure](docs/package-structure.md)
- [Manifest](docs/manifest.md)
- [Records](docs/records.md)
- [Provenance](docs/provenance.md)
- [Import reports](docs/import-report.md)
- [Profiles](docs/profiles.md)

## Minimal Package

```text
manifest.json
records/
```

## Optional Package Directories and Files

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

OKPF packages durable knowledge artifacts in this lifecycle. Target systems decide how to chunk, embed, index, fine-tune, simulate, or execute against those artifacts.
