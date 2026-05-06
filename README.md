# OKPF — Open Knowledge Pack Format

**An open, infrastructure-neutral standard for packaging, attributing, and distributing structured human expertise.**

> OKPF is a file format specification — not a platform, not a marketplace, and not a blockchain project.  
> It is designed to be simple, composable, and long-lived.

---

## Table of Contents

- [Vision](#vision)
- [Why OKPF Exists](#why-okpf-exists)
- [Design Principles](#design-principles)
- [Non-Goals](#non-goals)
- [Core Concepts](#core-concepts)
- [What Goes in a Knowledge Pack](#what-goes-in-a-knowledge-pack)
- [Use Cases](#use-cases)
  - [Technical and Scientific Domains](#technical-and-scientific-domains)
  - [Creative Domains](#creative-domains)
  - [Professional and Enterprise Domains](#professional-and-enterprise-domains)
  - [Educational Domains](#educational-domains)
- [Example Pack Structures](#example-pack-structures)
- [Roadmap](#roadmap)
- [Future Optional Capabilities](#future-optional-capabilities)
- [Relationship to Existing Standards](#relationship-to-existing-standards)
- [Infrastructure Neutrality](#infrastructure-neutrality)
- [Governance](#governance)
- [Compatibility Philosophy](#compatibility-philosophy)
- [Security Philosophy](#security-philosophy)
- [Licensing](#licensing)
- [Contributing](#contributing)

---

## Vision

Human expertise is one of the most valuable and least portable assets in the world.

A master brewer, an experienced diagnostician, a senior architect, a cinematographer, a composer — each carries a body of structured knowledge built over years of practice. That knowledge shapes decisions, prevents mistakes, and encodes patterns that are not easily written down. When it is written down, it is scattered across documents, informal notes, and conversations with no consistent structure, no attribution, no license, and no reliable way to verify its accuracy.

OKPF defines a standard for packaging that expertise — in a form that is structured, portable, attributable, licensed, versioned, and verifiable — so that it can be reliably shared, preserved, consumed by software systems, and extended by future contributors.

The format is deliberately infrastructure-neutral. It works offline, without cloud services, without AI models, and without blockchain. It is also designed to compose well with those systems when they are useful.

---

## Why OKPF Exists

### The portability problem

Expertise is currently trapped in formats that are either too informal (documents, chat logs, personal wikis) or too tightly coupled to a specific platform. Neither survives well across organizations, tools, or time.

### The attribution problem

When knowledge is extracted from a human expert — through interviews, documentation, or observation — the attribution chain is typically lost immediately. Who said this? What was the source? Who reviewed it? These questions rarely have clear answers once content is scraped, re-published, or incorporated into a system.

### The licensing problem

Most shared knowledge has no explicit license. Without a license, consumers face legal uncertainty. Creators cannot express their intent — whether they want their work to be freely used, attributed, kept open in derivatives, or excluded from AI training.

### The verification problem

There is currently no standard way to attach test cases or evaluation criteria to a body of structured knowledge. A document makes claims; there is no agreed mechanism for expressing what those claims predict, or for checking whether they hold.

### The fragmentation problem

Every AI training pipeline, every RAG system, every robotics behavior framework, and every educational platform has invented its own internal format for structured knowledge. These formats are not interoperable, not self-describing, and not portable across systems.

OKPF addresses all five problems with a single, open, composable packaging layer.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Portability** | A `.kpack` is a self-contained archive. No network access, no external service, and no runtime required to read it. |
| **Attribution first** | Contributors, sources, and transformations are first-class fields — not optional metadata. |
| **License clarity** | Every pack declares explicit licensing terms, including permissions for use, redistribution, derivative works, and AI training. |
| **Provenance** | Every artifact carries an auditable chain of origin — who created it, from what source, through what transformations, reviewed by whom. |
| **Verifiability** | Packs can include evaluations — structured test cases that assert what the knowledge predicts and allows for quality checking. |
| **Extensibility** | New content types and metadata fields can be added without breaking existing tools. Unknown fields are preserved, not rejected. |
| **Semantic versioning** | Both the OKPF spec and individual packs follow [SemVer](https://semver.org). Breaking changes are deliberate and documented. |
| **Openness** | The format is fully specified, freely implementable, and governed by the community — not by any single vendor. |
| **Composability** | Packs can reference other packs as dependencies. Systems built on OKPF are free to combine, extend, and layer. |
| **Infrastructure neutrality** | Blockchain, AI models, embedding providers, cloud storage, and vector databases are all optional. The base format works without any of them. |

---

## Non-Goals

Understanding what OKPF is not helps clarify its scope:

- **Not a platform or marketplace.** OKPF defines a file format, not a hosting or distribution service. Any party can build those on top.
- **Not an AI system.** OKPF does not define how models read, embed, or reason over packs. That is for application layers to decide.
- **Not a blockchain project.** Blockchain anchoring is a single optional feature among many. It is not required, not recommended by default, and not privileged over other anchor types.
- **Not a training data pipeline.** OKPF can package content intended for AI training, but it does not define pipelines, transformations, or model interfaces.
- **Not a marketplace.** OKPF does not define payment, discovery, or distribution protocols. Registries are out of scope for the core format.
- **Not a replacement for documentation systems.** OKPF is a portable packaging layer — it is meant to complement existing knowledge systems, not replace them.
- **Not tied to any execution engine.** OKPF packs describe knowledge; they do not define how that knowledge is executed, retrieved, or reasoned over.

---

## Core Concepts

### The Knowledge Pack (`.kpack`)

A **knowledge pack** is the atomic unit of OKPF. It is a self-contained, versioned, attributed archive of structured expertise in a specific domain.

Think of it as a Git repository for a body of knowledge — with explicit licensing, provenance, evaluations, and optional cryptographic integrity.

When distributed as a file, a pack uses the `.kpack` extension and is a standard ZIP archive. Packs can also exist as plain directories for authoring and development.

### The Manifest

Every pack contains a `manifest.json` that declares:
- Identity: a globally unique ID, a name, a domain, and a version
- Content: an index of every artifact in the pack
- License: a reference to the licensing terms
- Optional: contributors, provenance, evaluations, embeddings, signatures, anchors

The manifest is the authoritative index. Tools that work with packs start by reading it.

### Artifacts

Every piece of content inside a pack is an **artifact** — a named, typed file with a declared semantic role. Artifacts can be Markdown documents, JSON data, images, workflow definitions, transcripts, evaluation sets, or any other MIME-typed content.

### Attribution and Provenance

**Contributors** are first-class records — not optional fields at the bottom of a document. Every contributor can be credited for specific artifacts and identified by ORCID, URL, or affiliation.

**Provenance** records the chain of custody from original source to finished artifact: what the sources were, what transformations were applied, who performed them, and who reviewed the results.

### Evaluations

**Evaluations** are structured test cases attached to pack content. They express what the knowledge in a pack predicts, and allow automated or manual quality checks. A pack with evaluations is more trustworthy than one without.

---

## What Goes in a Knowledge Pack

| Content Type | Examples |
|-------------|---------|
| Documents | Guides, tutorials, reference materials, specifications |
| Transcripts | Expert interviews, structured dialogues, recorded reasoning |
| Workflows | Decision trees, diagnostic procedures, step-by-step processes |
| Evaluations | Test cases, rubrics, benchmarks, scenario exercises |
| Structured data | Reference tables, datasets, measurements, lookup tables |
| Images and diagrams | Illustrations, technical drawings, annotated photographs |
| Style and composition references | Annotated examples, technique demonstrations |
| Embeddings (optional) | Pre-computed vector representations for retrieval systems |
| Signatures (optional) | Cryptographic proofs of authorship and integrity |
| Blockchain anchors (optional) | External timestamping and immutability records |

---

## Use Cases

OKPF is not limited to AI model training. Knowledge packs are designed to be useful across a wide range of systems and workflows.

**Consumption modes supported:**
- Inference-time retrieval (RAG pipelines)
- Fine-tuning and pre-training datasets
- Robotics behavior and sensing knowledge
- Simulation environment definitions
- Educational content and curriculum systems
- Expert systems and decision support
- Tool orchestration and agent behavior
- Procedural generation systems
- Workflow automation

### Technical and Scientific Domains

**AI and machine learning**
- Labeled knowledge datasets with provenance and licensing for fine-tuning
- Domain-specific evaluation benchmarks distributed as packs
- RAG context packs with structured Q&A and evaluation test cases

**Robotics**
- Sensor interpretation guides: what sensor readings mean in specific contexts
- Manipulation procedure packs: step-by-step physical task workflows with safety notes
- Environment knowledge: structured spatial and object relationship data
- Failure mode catalogs: documented fault patterns and recovery procedures

**Software architecture and engineering**
- Architectural pattern packs with trade-off analysis and decision frameworks
- API and SDK expertise packs: usage patterns, common errors, operational procedures
- Debugging strategy packs: documented diagnostic reasoning for specific systems
- Toolchain and workflow knowledge: build systems, deployment procedures, runbooks
- Domain-specific framework expertise: annotated patterns and anti-patterns

**Scientific and medical**
- Laboratory procedure packs with safety requirements and verification steps
- Clinical decision-support knowledge with evaluation cases and sourcing
- Environmental measurement interpretation guides

**Manufacturing and engineering**
- CAD and manufacturing workflow packs with annotated process steps
- Quality control procedure packs with inspection criteria and failure examples
- Maintenance and repair knowledge with diagnostic decision trees

**Simulation**
- Physics-grounded environment descriptions with behavioral parameters
- Agent behavior policy packs for simulation training
- Domain calibration datasets with provenance

---

### Creative Domains

OKPF is designed to support structured human expertise across creative domains, not only technical ones. Creative knowledge packs can package the kind of structured understanding that experienced artists, designers, and composers develop over years of practice.

This does not mean claiming ownership of a style itself — artistic styles are not ownable. What OKPF enables is:
- Packaging a *description* of a style with proper attribution and licensing
- Distributing *technique* knowledge with clear creator consent
- Attaching explicit usage policies to creative reference material
- Making provenance visible in creative AI training workflows

**Visual art and illustration**
- Illustration technique packs: annotated workflows, brush usage, compositional approaches
- Style reference datasets: curated examples with attribution, licensing, and usage scope
- Figure drawing and anatomy knowledge: structured reference with progression exercises
- Color theory and palette design packs with annotated examples

**Design systems**
- Typography packs: font selection rationale, hierarchy principles, spacing systems
- Visual design system knowledge: grid systems, component reasoning, accessibility principles
- Brand and identity design workflows: documented decision processes

**Animation and motion**
- Animation workflow packs: pose-to-pose vs. straight-ahead rationale, timing principles
- Rigging and skinning knowledge packs for specific character archetypes
- Motion language references: annotated timing curves and easing approaches

**Cinematic and visual storytelling**
- Cinematic language datasets: shot vocabulary, lighting setups, color grading rationale
- Narrative structure packs: scene construction, pacing, dramatic tension approaches
- Director and DP workflow packs: production decision frameworks with example scenes

**Music**
- Music composition structure packs: harmonic progressions, rhythmic frameworks, orchestration notes
- Genre-specific production knowledge: annotated signal chains, sound design approaches
- Voice and dialogue style packs: annotated performance characteristics with consent records

**Procedural and generative systems**
- Worldbuilding knowledge packs: geopolitical, cultural, and environmental systems with internal logic
- Procedural generation rule sets: structured grammars for architecture, landscape, narrative
- Game design knowledge: mechanics documentation, balance rationale, player experience frameworks

**For creative packs specifically, OKPF provides:**
- Attribution-aware distribution so creator credits travel with the content
- Explicit `ai_training` permission fields so creators can control how their work is used in training
- Provenance records that track curation and transformation history
- Licensing terms that can differentiate between personal use, redistribution, and commercial use
- A foundation for royalty and consent infrastructure that registries can build on top of

---

### Professional and Enterprise Domains

**Expert systems and decision support**
- Compliance and regulatory knowledge: structured rules with sourcing and update history
- Risk assessment frameworks: decision trees with historical case references
- Audit procedure packs: checklists with reasoning and threshold documentation

**Trades and technical services**
- HVAC, electrical, and plumbing diagnostic packs
- Automotive diagnostic and repair knowledge
- Precision agriculture and land management expertise

**Healthcare and life sciences**
- Clinical pathway documentation with evidence sourcing
- Drug interaction reference packs
- Rehabilitation and therapy protocol knowledge

---

### Educational Domains

- Curriculum knowledge packs: structured learning progressions with prerequisite mapping
- Subject matter explanation packs at multiple difficulty levels
- Pedagogical strategy packs: teaching technique knowledge with effectiveness evidence
- Assessment and evaluation packs: rubrics and grading criteria with rationale

---

## Example Pack Structures

### A minimal pack

```
water-chemistry-brewing/
├── manifest.json       identity, version, content index, license reference
├── license.json        CC-BY-4.0 with ai_training: permitted
└── content/
    └── guide.md        the knowledge itself
```

```json
{
  "okpf_version": "0.1.0",
  "id": "urn:okpf:brewing:water-chemistry:0.1.0",
  "name": "Water Chemistry for Brewing",
  "version": "0.1.0",
  "domain": "brewing",
  "created": "2026-05-01T00:00:00Z",
  "license": { "$ref": "license.json" },
  "content": [
    {
      "id": "guide",
      "path": "content/guide.md",
      "type": "text/markdown",
      "role": "guide"
    }
  ]
}
```

---

### A complete attributed pack

```
illustration-technique-fundamentals/
├── manifest.json
├── license.json           CC-BY-NC-4.0; ai_training: restricted
├── contributors.json      primary author + technical reviewer
├── provenance.json        sources: workshop recordings, annotated sketchbooks
├── content/
│   ├── line-quality.md
│   ├── value-structure.md
│   ├── figure-construction.md
│   ├── annotated-examples/
│   │   ├── example-01.png
│   │   └── example-01-annotations.json
│   └── exercises.json     structured practice tasks
└── evaluations/
    └── comprehension-checks.json
```

---

### A software architecture pack

```
distributed-systems-patterns/
├── manifest.json
├── license.json           Apache-2.0
├── contributors.json
├── provenance.json
├── content/
│   ├── patterns/
│   │   ├── saga-pattern.md
│   │   ├── outbox-pattern.md
│   │   └── circuit-breaker.md
│   ├── decision-frameworks/
│   │   └── consistency-vs-availability.json
│   └── anti-patterns/
│       └── distributed-monolith.md
└── evaluations/
    └── architecture-scenarios.json
```

---

### A robotics sensing pack with optional embeddings

```
warehouse-navigation-knowledge/
├── manifest.json
├── license.json
├── contributors.json
├── provenance.json
├── content/
│   ├── obstacle-classification.md
│   ├── sensor-fusion-guide.md
│   └── failure-modes.json
├── evaluations/
│   └── scenario-tests.json
└── embeddings/
    └── openai-ada-002.jsonl    optional; tagged with model and provider
```

---

### A creative pack with usage policies

```
cinematic-lighting-language/
├── manifest.json
├── license.json           CC-BY-SA-4.0; ai_training: restricted; commercial_use: permitted
├── contributors.json      cinematographer (author) + editor
├── provenance.json        source: interview transcripts + annotated frame captures
├── content/
│   ├── lighting-setups.md
│   ├── three-point-fundamentals.md
│   ├── reference-frames/
│   │   ├── frame-01.jpg
│   │   └── frame-01-notes.json
│   └── style-vocabulary.json
├── signatures/
│   └── author.sig         author's cryptographic signature over manifest
└── evaluations/
    └── identification-exercises.json
```

---

## Roadmap

A summary of planned milestones:

| Milestone | Goal |
|-----------|------|
| **0 — Foundation** | Specification draft, schemas, examples, reference implementation stubs ✓ |
| **1 — Stable Core** | Finalized v0.1.0 spec, validator CLI, complete examples |
| **2 — Ecosystem** | Embeddings and signatures support, packaging tooling, IPFS integration |
| **3 — Quality and Discovery** | Evaluation runner, registry protocol, peer review workflows |
| **4 — Maturity** | v1.0.0 stable spec, conformance test suite, third-party implementations |

See [ROADMAP.md](ROADMAP.md) for the full milestone breakdown.

---

## Future Optional Capabilities

The core format is intentionally minimal. The following capabilities are planned as optional extensions, designed so that packs remain usable without them.

### Cryptographic signatures
Sign a manifest, an individual artifact, or a full pack archive using GPG, SSH keys, or Ed25519. Signatures prove authorship and detect tampering. Supported in the schema; tooling planned for Milestone 2.

### Blockchain anchors
Record a pack's hash or IPFS CID on a blockchain for external timestamping and immutability. Chain-agnostic — any public or private chain, or none at all. Currently supported as an optional `anchors` field in the manifest.

### Content-addressed storage
IPFS CIDs as anchor values provide both availability (if pinned) and integrity. A natural complement to the existing hash fields in the artifact schema.

### Zero-knowledge proofs
A future optional extension for packs in sensitive domains: prove that a pack satisfies certain properties (e.g., "authored by a credentialed professional in domain X") without revealing the underlying data. Not in the current spec; noted for exploration.

### Trusted execution environments (TEEs)
For high-sensitivity packs, future work may define optional attestation records from TEEs — proof that a specific transformation was performed in a verified, isolated environment. Out of scope for current milestones.

### Compute-to-data patterns
Rather than distributing pack content directly, a future extension could allow packs to reference content that can only be processed within an authorized compute environment. Useful for privacy-sensitive medical or proprietary commercial packs.

### Capability-based access
A future extension for access-controlled packs: declaring what capability tokens are required to access specific artifacts. Compatible with Verifiable Credentials and similar identity systems.

### Per-artifact encryption
Selective encryption of individual artifacts, allowing mixed open/restricted packs where some content is publicly readable and other content requires decryption.

All of these are designed as opt-in additions to the base format. A pack that uses none of them is still fully conformant and fully functional.

---

## Relationship to Existing Standards

OKPF is not a replacement for existing standards. It is a packaging layer that can reference, include, and build on content governed by them.

| Standard or Concept | Relationship to OKPF |
|---------------------|---------------------|
| **SPDX** | License expression syntax used in `license.json` |
| **Dublin Core / schema.org** | Metadata vocabulary inspiration for manifest fields |
| **W3C PROV-O** | Provenance model inspiration — OKPF simplifies PROV for practical JSON use |
| **Verifiable Credentials (W3C)** | Optional signing model; VC-compatible identity for contributors |
| **IPFS / Content-addressed storage** | Optional anchor target; CIDs as pack identifiers |
| **OCI / Docker image spec** | Packaging and layering analogy |
| **EPUB** | Self-contained bundle with manifest analogy |
| **SBOM (CycloneDX / SPDX)** | Provenance record analogy — OKPF provenance is an SBOM for knowledge |
| **OpenAPI / AsyncAPI** | Inspiration for domain-specific knowledge schemas |
| **Open Knowledge Definition** | Alignment on what "open" means for knowledge artifacts |
| **Creative Commons** | Primary recommended license family for knowledge packs |
| **ORCID** | Optional contributor identification for academic and professional packs |
| **DOI** | Optional anchor type for published packs |

---

## Infrastructure Neutrality

OKPF is explicitly designed to be independent of infrastructure choices. The format works without:

- Any AI model or embedding provider
- Any vector database or retrieval system
- Any blockchain network or smart contract
- Any cloud storage or CDN
- Any registry or marketplace
- Any execution runtime

This neutrality is a feature, not a limitation. It means that:

1. A pack authored today can be read by a tool built in ten years, without depending on services that may no longer exist.
2. Organizations with strict data sovereignty requirements can use OKPF entirely on-premises, offline, and without external dependencies.
3. Tooling built on OKPF is not locked to any provider's ecosystem.
4. The format can compose with any infrastructure layer without requiring it.

When infrastructure is useful — when blockchain anchoring adds verifiability, when embeddings enable faster retrieval, when IPFS enables decentralized distribution — OKPF supports those as optional extensions. When infrastructure is not available or not wanted, the pack still works.

---

## Governance

OKPF is an open standard. It is not owned by any company, tied to any product, or governed by a single maintainer.

**Current stage:** The project is in early development under its founding contributor. The governance model will evolve as the community grows.

**Intended governance model:**
- Specification changes are proposed via GitHub Issues and Discussions
- Breaking changes require open discussion and consensus before implementation
- Minor additions (new optional fields, new content types) require at least one reviewer
- The specification is versioned; older versions remain valid and documented
- No single contributor, company, or organization will hold veto power over the spec

The goal is a governance model similar to successful open standards — where decisions are made in the open, documented, and traceable, and where the standard serves its users rather than its stewards.

---

## Compatibility Philosophy

OKPF is designed for long-term backward compatibility.

**Readers must not reject packs with unknown fields.** This is the foundation of forward compatibility — a pack written for OKPF v0.3.0 should be readable by a tool written for OKPF v0.1.0, ignoring fields it doesn't understand.

**Required fields are minimal and stable.** The set of required fields in the manifest is kept small deliberately. Adding to it is a breaking change; it requires a major version bump and community consensus.

**Schema versioning is explicit.** Every pack declares the OKPF spec version it conforms to in `manifest.json`. Tools can use this to choose the right parsing behavior.

**Deprecation is gradual.** Fields are deprecated before removal. A deprecation notice appears in at least one minor version before a field is removed in a major version.

---

## Security Philosophy

OKPF's security model is layered and opt-in. The base format provides:

- **Content integrity** via SHA-256 hashes on artifacts — detect accidental corruption or tampering
- **Authorship** via contributor records — declare who is responsible for what
- **Provenance transparency** — make the chain of custody explicit rather than implicit

Optional layers add:

- **Cryptographic authenticity** via signatures — prove a key holder approved specific content
- **External timestamping** via blockchain or registry anchors — prove a pack existed at a given time
- **Future: encrypted content, ZK attestations, TEE records** — for high-sensitivity or access-controlled packs

OKPF does not currently define encryption at rest, access control, or revocation. These are handled at the distribution and registry layers.

For detailed security guidance, see [docs/security.md](docs/security.md).

---

## Licensing

### The OKPF project itself

The OKPF specification, schemas, reference implementations, tools, and documentation in this repository are licensed under the **[Apache License 2.0](LICENSE)** (`SPDX-License-Identifier: Apache-2.0`).

Apache 2.0 was chosen because:
- It is permissive and commercially compatible — anyone can implement OKPF tooling without restriction
- It includes a patent grant — implementers are protected against patent claims from contributors
- It is widely recognized and understood
- It supports broad adoption across academic, commercial, and government contexts
- It is compatible with most other open licenses used in the ecosystem

Example documentation and knowledge packs in the `examples/` directory are licensed under **[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)** (`SPDX-License-Identifier: CC-BY-4.0`), as declared in each example's `license.json`.

For a full discussion of license choices, see [docs/licensing-strategy.md](docs/licensing-strategy.md).

### Knowledge packs built with OKPF

Packs created using the OKPF format carry their own licenses, declared in their `license.json`. The OKPF format itself imposes no restrictions on the content of knowledge packs.

Pack authors choose their own licenses — CC BY 4.0 is recommended for open packs, but any SPDX-expressible license is valid. The `ai_training` field in `license.json` provides explicit control over whether pack content may be used as AI/ML training data — a dimension that standard open licenses do not address.

---

## Contributing

Contributions are welcome across all areas:

- **Specification** — propose additions, clarifications, or corrections to [SPEC.md](SPEC.md)
- **Schemas** — improve or extend the JSON Schemas in `schemas/`
- **Examples** — create knowledge packs in new domains under `examples/`
- **Reference implementations** — implement the Python or JavaScript library in `reference/`
- **Tooling** — build CLI tools, validators, converters, or registry adapters
- **Documentation** — improve or translate documentation in `docs/`

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide, including the spec change process, example pack guidelines, and the code of conduct.

The most impactful contributions are usually real-world example packs in new domains — they demonstrate the format's range and surface any gaps in the spec.

---

## Repository Structure

```
OKPF/
├── README.md              This file
├── SPEC.md                Full format specification
├── ROADMAP.md             Development milestones
├── CONTRIBUTING.md        Contribution guide
├── LICENSE                Apache 2.0
├── NOTICE                 Attribution and copyright notices
├── schemas/               JSON Schema definitions
│   ├── manifest.schema.json
│   ├── license.schema.json
│   ├── provenance.schema.json
│   ├── contributor.schema.json
│   ├── evaluation.schema.json
│   └── task.schema.json
├── examples/
│   ├── brewing/           Complete example pack (water chemistry)
│   ├── mechanic-diagnostics/   Placeholder
│   └── software-architecture/  Placeholder
├── docs/
│   ├── concepts.md
│   ├── licensing.md
│   ├── licensing-strategy.md
│   ├── provenance.md
│   ├── blockchain.md
│   ├── security.md
│   └── examples.md
├── reference/
│   ├── python/            okpf-py reference library (stub)
│   └── javascript/        okpf-js reference library (stub)
└── tools/
    └── README.md          CLI tooling plan
```

---

*OKPF is an early-stage open standard. The specification is in draft. Feedback, critique, and contributions are actively sought.*

*If you are building a system that could benefit from portable, attributed, licensed knowledge packs — and especially if the current format does not quite fit your use case — please open an issue. The spec is shaped by real use cases.*
