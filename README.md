<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/okpf-light.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/okpf.svg">
    <img src="docs/assets/okpf.svg" alt="OKPF logo" width="160">
  </picture>
</p>

# OKPF — Open Knowledge Pack Format

**An open, infrastructure-neutral standard for packaging, attributing, and distributing structured human expertise.**

> OKPF is a file format specification — not a platform, not a marketplace, and not a blockchain project.  
> It is designed to be simple, composable, and long-lived.

---

OKPF was initiated by [Charles Toepfer](https://github.com/ctoepfer) as an open effort to develop a portable, vendor-neutral standard for packaging structured human expertise for AI systems and future computational tools. It is designed from the outset as a community-driven project — open in governance, open in implementation, and intended to remain independent of any single organization, platform, or technology stack.

---

## Table of Contents

- [Current Status: OKPF Core v0.1.0](#current-status-okpf-core-v010)
- [Vision](#vision)
- [Why OKPF Exists](#why-okpf-exists)
- [Design Principles](#design-principles)
- [Non-Goals](#non-goals)
- [Core Concepts](#core-concepts)
- [Package Philosophy](#package-philosophy)
- [What Goes in a Knowledge Pack](#what-goes-in-a-knowledge-pack)
- [Use Cases](#use-cases)
  - [Technical and Scientific Domains](#technical-and-scientific-domains)
  - [Creative and Artistic Domains](#creative-and-artistic-domains)
  - [Software and Engineering Workflows](#software-and-engineering-workflows)
  - [Professional and Enterprise Domains](#professional-and-enterprise-domains)
  - [Educational Domains](#educational-domains)
- [Example Pack Structures](#example-pack-structures)
- [Roadmap](#roadmap)
- [Future Optional Capabilities](#future-optional-capabilities)
- [Optional Ecosystem Layers](#optional-ecosystem-layers)
- [Blockchain Philosophy](#blockchain-philosophy)
- [Relationship to Existing Standards](#relationship-to-existing-standards)
- [Infrastructure Neutrality](#infrastructure-neutrality)
- [Governance](#governance)
- [Compatibility Philosophy](#compatibility-philosophy)
- [Security Philosophy](#security-philosophy)
- [Licensing](#licensing)
- [AI and Autonomous System Compatibility](#ai-and-autonomous-system-compatibility)
- [Contributing](#contributing)
- [Repository Structure](#repository-structure)

---

## Current Status: OKPF Core v0.1.0

**Phase 1 is complete.** OKPF Core v0.1.0 establishes the minimum viable foundation for the format.

### What it is

A knowledge pack is a directory (or `.kpack` zip) containing a `manifest.json` that describes the pack's identity, content, license, and optional metadata. Tools that read packs start with the manifest.

### Minimal valid pack structure

```
my-pack/
  manifest.json       ← required: identity, content index, license
  README.md           ← recommended: human-readable overview
  LICENSE             ← recommended: license text
  license.json        ← required if manifest uses $ref
  content/            ← content artifacts
```

### Quickstart: validate an example pack

```bash
# Install jsonschema (for schema validation)
pip install jsonschema

# Validate the minimal example pack
python reference/python/okpf_validate.py examples/basic-pack

# Validate the homebrew recipe pack (multi-artifact, multiple roles)
python reference/python/okpf_validate.py examples/homebrew-recipe-pack

# Print SHA-256 hashes for artifacts (useful when authoring)
python reference/python/okpf_validate.py examples/basic-pack --hash-only
```

### Key Phase 1 deliverables

| Deliverable | Location |
|-------------|---------|
| Core specification | [SPEC.md](SPEC.md) |
| Manifest JSON Schema | [schemas/manifest.schema.json](schemas/manifest.schema.json) |
| Minimal example pack | [examples/basic-pack/](examples/basic-pack/) |
| Homebrew recipe pack (multi-artifact) | [examples/homebrew-recipe-pack/](examples/homebrew-recipe-pack/) |
| Standalone validator | [reference/python/okpf_validate.py](reference/python/okpf_validate.py) |
| Python SDK | [reference/python/okpf/](reference/python/okpf/) |
| JavaScript/TypeScript SDK | [reference/javascript/src/](reference/javascript/src/) |
| Phase 1 roadmap | [docs/phase-1-roadmap.md](docs/phase-1-roadmap.md) |

### What is NOT in Phase 1

Blockchain ownership, marketplace payments, royalty enforcement, content encryption, zero-knowledge proofs, trusted execution environments, and hosted registry protocols are intentional exclusions. They are future optional extensions to be built on top of a stable core. See [docs/phase-1-roadmap.md](docs/phase-1-roadmap.md) for the full inclusion/exclusion list.

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
| **Verifiability** | Packs can include evaluations — structured test cases that assert what the knowledge predicts and allow for quality checking. |
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
- Optional: contributors, provenance, evaluations, embeddings, signatures, anchors, capabilities, AI metadata, trust state

The manifest is the authoritative index. Tools that work with packs start by reading it.

### Artifacts

Every piece of content inside a pack is an **artifact** — a named, typed file with a declared semantic role. Artifacts can be Markdown documents, JSON data, images, workflow definitions, transcripts, evaluation sets, or any other MIME-typed content.

### Attribution and Provenance

**Contributors** are first-class records — not optional fields at the bottom of a document. Every contributor can be credited for specific artifacts and identified by ORCID, URL, or affiliation.

**Provenance** records the chain of custody from original source to finished artifact: what the sources were, what transformations were applied, who performed them, and who reviewed the results.

### Evaluations

**Evaluations** are structured test cases attached to pack content. They express what the knowledge in a pack predicts, and allow automated or manual quality checks. A pack with evaluations is more trustworthy than one without.

---

## Package Philosophy

OKPF thinks about packaging knowledge the way Git thinks about versioning code and Docker thinks about distributing environments — as a solved, composable layer that other systems can depend on without needing to reinvent.

The `.kpack` format is the unit of exchange. Like an npm package, a pip wheel, or an OCI container image, it:
- carries everything it needs to be used without external dependencies
- declares its own identity, version, and content explicitly
- is addressable by a stable identifier
- can be composed with other packs through dependency declarations
- supports integrity verification through content hashing

Unlike those analogies, OKPF packages are *knowledge*, not code. This introduces considerations that software packaging does not face: licensing for human use versus AI use, attribution to the original experts, provenance back to primary sources, and evaluation criteria for quality. The OKPF manifest is designed specifically for these concerns.

The goal is that a well-formed `.kpack` should be interpretable by any conformant tool — today or in ten years — without requiring access to the system that created it, the platform it was published on, or the organization that maintained it. Packs should outlive the tools that made them.

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

---

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

### Creative and Artistic Domains

OKPF is designed to support structured human expertise across creative domains, not only technical ones. Creative knowledge packs can package the kind of structured understanding that experienced artists, designers, and composers develop over years of practice.

**An important distinction:** OKPF does not — and cannot — claim ownership of artistic styles. Styles are not ownable. What OKPF enables is the responsible packaging of *descriptions*, *techniques*, *annotated examples*, and *usage policies* that artists, designers, and practitioners choose to share. The emphasis throughout is on attribution, consent, licensing, and provenance — not on control of style itself.

**Visual art and illustration**
- Illustration technique packs: annotated workflows, brush usage, compositional approaches
- Style reference datasets: curated examples with attribution, creator licensing terms, and declared usage scope
- Figure drawing and anatomy knowledge: structured reference with progression exercises
- Color theory and palette design packs with annotated examples

**Design systems**
- Typography packs: font selection rationale, hierarchy principles, spacing systems
- Visual design system knowledge: grid systems, component reasoning, accessibility principles
- Brand and identity design workflows: documented decision processes

**Animation and motion**
- Animation workflow packs: pose-to-pose vs. straight-ahead rationale, timing principles
- Rigging knowledge packs for specific character archetypes
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
- Licensing terms that differentiate between personal use, redistribution, and commercial use
- A format foundation that registries and platforms can build royalty and consent infrastructure upon

---

### Software and Engineering Workflows

OKPF is well-suited to packaging structured software knowledge — not code itself, but the reasoning, patterns, procedures, and decisions that experienced engineers accumulate.

**Architecture and design**
- Architectural pattern packs with trade-off analysis and decision frameworks
- Anti-pattern catalogs with root cause analysis and refactoring guidance
- System design decision trees: structured approaches to common architectural choices

**Development operations**
- Deployment procedure packs: runbooks, rollback procedures, validation checklists
- Incident response packs: structured escalation and diagnosis workflows
- API and SDK expertise packs: usage patterns, common errors, operational procedures

**Domain-specific engineering knowledge**
- Framework expertise packs: annotated patterns and known pitfalls for specific libraries
- Debugging strategy packs: documented diagnostic reasoning for specific systems
- Code review knowledge: structured criteria and evaluation rubrics for domain-specific quality

**Toolchain and process knowledge**
- Build system expertise: configuration patterns with rationale and failure modes
- Testing strategy packs: structured approaches to coverage, property testing, integration
- Security knowledge packs: threat models, mitigation patterns, evaluation criteria

Software knowledge packs differ from documentation in that they carry evaluations — test cases that can be run programmatically to verify whether the knowledge is being correctly applied. A debugging strategy pack can include scenarios; a code review pack can include rubrics that automated tools can execute.

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

### A fully attributed pack with capabilities

```json
{
  "okpf_version": "0.1.0",
  "id": "urn:okpf:brewing:water-chemistry:0.2.0",
  "name": "Water Chemistry for Brewing",
  "version": "0.2.0",
  "domain": "brewing",
  "created": "2026-05-01T00:00:00Z",
  "license": { "$ref": "license.json" },
  "contributors": { "$ref": "contributors.json" },
  "provenance": { "$ref": "provenance.json" },
  "capabilities": ["retrieval", "evaluation", "workflow-execution"],
  "ai": {
    "recommended_use": ["rag", "fine-tuning"],
    "safe_for_training": true,
    "contains_pii": false,
    "modalities": ["text", "structured-data"],
    "risk_level": "low",
    "evaluation_available": true
  },
  "content": [
    {
      "id": "guide",
      "path": "content/guide.md",
      "type": "text/markdown",
      "role": "guide",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ],
  "evaluations": { "$ref": "evaluations/test-cases.json" }
}
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
    └── text-embedding-3-small.jsonl   optional; tagged with model and provider
```

---

## Roadmap

| Milestone | Goal |
|-----------|------|
| **0 — Foundation** | Specification draft, schemas, examples, reference implementation stubs ✓ |
| **1 — Stable Core** | v0.1.0 spec, validator, complete examples, Python + JS SDKs ✓ |
| **2 — Ecosystem** | Embeddings and signatures tooling, packaging CLI, IPFS integration |
| **3 — Quality and Discovery** | Evaluation runner, registry protocol, peer review workflows |
| **4 — Maturity** | v1.0.0 stable spec, conformance test suite, third-party implementations |

See [ROADMAP.md](ROADMAP.md) for the full milestone breakdown.

---

## Future Optional Capabilities

The core format is intentionally minimal. The following capabilities are planned as optional extensions to the format itself. A pack that uses none of them is still fully conformant and fully functional.

### Cryptographic signatures
Sign a manifest, individual artifact, or full pack archive using GPG, SSH keys, or Ed25519. Signatures prove authorship and detect tampering. Supported in the schema; tooling planned for Milestone 2.

### Encrypted artifacts
Selective encryption of individual artifacts, allowing mixed open/restricted packs where some content is publicly readable and other content requires decryption. Useful for packs with tiered access.

### Zero-knowledge proofs
Prove that a pack satisfies certain properties — authored by a credentialed professional, produced through a verified review process — without revealing the underlying data. Not in the current spec; noted for future exploration.

### Trusted execution environments (TEEs)
Optional attestation records proving that specific transformations were performed in a verified, isolated environment. Out of scope for current milestones; relevant for high-sensitivity knowledge production pipelines.

### Compute-to-data references
Rather than distributing content directly, packs could reference content that is only accessible within an authorized compute environment. Useful for privacy-sensitive medical, legal, or proprietary commercial knowledge.

### Capability-based access tokens
Declaring what credential or capability tokens are required to access specific artifacts within a pack. Compatible with W3C Verifiable Credentials and similar identity systems.

### Content-addressed storage
IPFS CIDs as anchor values provide both availability and integrity verification. A natural complement to the existing SHA-256 hashes in the artifact schema.

---

## Optional Ecosystem Layers

There is an important distinction between **capabilities built into the OKPF format** (described above) and **ecosystem layers built on top of OKPF**. The second category is out of scope for the core specification — but OKPF is designed with these layers in mind.

These are things that application platforms, registries, and distribution systems can build using OKPF packs as a substrate:

### Attribution tracking and royalties

Because every pack carries structured contributor records, licensing terms, and provenance, a distribution platform could implement attribution tracking and royalty distribution without any changes to the OKPF format. The information required — who contributed what, under what license, with what AI training permissions — is already in every conformant pack.

OKPF does not define payment protocols. It defines the attribution and licensing metadata that payment and royalty systems require.

### Knowledge licensing and leasing

A platform could implement time-limited or scoped access to pack content — "leasing" a pack for a specific use case, duration, or organization — using the pack's declared license terms and a separate access layer. OKPF's per-artifact licensing and `scope` fields provide the structured foundation for these policies.

OKPF does not define leasing protocols. It defines the licensing granularity that leasing systems can act on.

### Ownership and rights registries

A registry built on OKPF could record pack ownership, track rights transfers, and maintain a verifiable history of who holds rights to a body of knowledge. The `anchors` field in the manifest can point to external ownership records — blockchain-based or otherwise.

OKPF does not define ownership protocols. It defines stable identifiers and provenance records that ownership systems can reference.

### Verification services

A third-party verification service could attest that a pack's contributors are credentialed in their domain, that the content has been peer-reviewed, or that the provenance records are accurate. These attestations can be referenced in the `trust.attestations` array in the manifest.

OKPF does not define verification services. It defines the `trust` metadata structure that attestation records are attached to.

### Pack registries and discovery

A registry could index packs by domain, capability, license terms, and trust state — providing search, versioning, and distribution services. OKPF defines the metadata fields that registries need to implement these features.

OKPF does not define registry protocols. It defines the format that all registries can consume.

**The principle:** OKPF is the packaging standard. Infrastructure, economic, and governance layers are built *on top of* it — they do not need to be built *into* it. This keeps the base format simple, long-lived, and implementable by anyone without dependencies on any specific platform or protocol.

---

## Blockchain Philosophy

Blockchain is one of several technologies that can add external verifiability to a knowledge pack. OKPF supports it as a first-class optional extension — not as a requirement, not as a privileged integration, and not as the primary mechanism for any core format feature.

### What blockchain can add to OKPF packs

- **Proof of existence at a point in time**: Recording a pack's hash on a public chain proves it existed in that form at that moment, even if original storage is later lost.
- **Tamper evidence**: If the pack is later modified, the hash will no longer match the on-chain record.
- **Decentralized verification**: Anyone with access to the public chain can verify the anchor, without trusting any central authority.

### What blockchain cannot provide for OKPF packs

- **Content accuracy**: A blockchain record proves a file existed, not that its contents are correct.
- **Authorship proof**: Chain of custody is separate from content quality. Provenance records and signatures serve authorship better.
- **Availability**: The pack must still be stored and accessible somewhere. Blockchain records the hash, not the content.

### Design decisions

OKPF blockchain support is defined by four principles:

1. **Chain-agnostic**: The `anchors[].network` field is a free-form string. OKPF makes no recommendation about which chain to use.
2. **No on-chain logic**: Anchoring is a simple hash commitment. No smart contracts, tokens, or programmable protocols are required.
3. **Optional and additive**: Removing all anchors from a pack leaves a fully valid pack.
4. **Not privileged over other mechanisms**: A GPG signature or a trusted registry anchor is equally valid for integrity purposes.

For implementers who want to add blockchain anchoring, see [docs/blockchain.md](docs/blockchain.md).

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

This neutrality is a feature, not a limitation. It means:

1. A pack authored today can be read by a tool built in ten years, without depending on services that may no longer exist.
2. Organizations with strict data sovereignty requirements can use OKPF entirely on-premises, offline, and without external dependencies.
3. Tooling built on OKPF is not locked to any provider's ecosystem.
4. The format can compose with any infrastructure layer without requiring it.

When infrastructure is useful — when blockchain anchoring adds verifiability, when embeddings enable faster retrieval, when IPFS enables decentralized distribution — OKPF supports those as optional extensions. When infrastructure is not available or not wanted, the pack still works.

---

## Governance

OKPF is an open standard. It is not owned by any company, tied to any product, or governed by a single maintainer.

The project was initiated by Charles Toepfer and is designed from the outset to be governed transparently and collaboratively — with decisions made in the open, documented in the repository, and traceable over time.

**Current stage:** Early development. The specification is in draft and the community is forming.

**Principles:**
- Specification changes are proposed via GitHub Issues and Discussions
- Breaking changes require open discussion and community consensus
- Minor additions require at least one reviewer beyond the author
- All versions of the specification are archived; older packs remain valid
- No single contributor, company, or organization will hold veto power

**Long-term intent:** As the community grows, governance will evolve toward a model similar to mature open standards — with documented decision processes, clear maintainer responsibilities, and formal mechanisms for community input.

See [GOVERNANCE.md](GOVERNANCE.md) for the full governance model.

---

## Compatibility Philosophy

OKPF is designed for long-term backward compatibility.

**Readers must not reject packs with unknown fields.** This is the foundation of forward compatibility — a pack written for OKPF v0.3.0 should be readable by a tool written for OKPF v0.1.0, ignoring fields it doesn't understand.

**Required fields are minimal and stable.** The set of required manifest fields is kept small deliberately. Adding to it is a breaking change requiring a major version bump and community consensus.

**Schema versioning is explicit.** Every pack declares the OKPF spec version it conforms to in `manifest.json`. Tools use this to choose the right parsing behavior.

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

## AI and Autonomous System Compatibility

OKPF is designed for machine consumption, not just human authorship. Several features of the format are specifically intended to make packs useful to AI systems, agent frameworks, robotics platforms, and automated tooling.

### Machine-readable schemas

All metadata is declared in JSON, validated by published JSON Schemas (Draft 2020-12). An AI system that reads `manifest.json` and resolves its `$ref` pointers has complete, structured access to:
- What content exists (`content[]`)
- What the pack is licensed for (`license.json`, including `scope.ai_training`)
- What capabilities the pack declares (`capabilities[]`)
- AI-specific routing hints (`ai.*`)
- Trust and verification state (`trust.*`)

No natural language parsing required to make routing decisions.

### Capability declarations

The `capabilities` array in the manifest provides a standardized vocabulary for AI system negotiation:

```json
"capabilities": ["retrieval", "evaluation", "workflow-execution"]
```

Defined values: `retrieval`, `fine-tuning`, `evaluation`, `workflow-execution`, `simulation`, `robotics`, `multimodal`, `reasoning`, `tutoring`, `diagnostics`, `code-generation`, `decision-support`.

An orchestrator can filter available packs by capability before loading any content — keeping negotiation lightweight.

### Evaluations as machine-testable quality checks

Every pack can include structured evaluations (question/answer pairs, multiple-choice, rubrics) that AI systems can run programmatically. Evaluations are:
- Stored in `evaluations/` and indexed in the manifest
- Structured per `evaluation.schema.json`
- Usable as domain benchmarks and as post-ingestion quality checks

### Provenance for trust-weighted retrieval

Provenance records in `provenance.json` give AI systems signals for weighting retrieved content:
- Source type (`original`, `interview`, `peer-reviewed-publication`)
- Transformation type (`manual`, `expert-review`, `automated`)
- Named reviewer (`reviewed_by` contributor ID)

Systems that surface citations can trace any output back through the provenance chain to the original source.

### Infrastructure independence

OKPF packs work offline, without cloud services, without a specific LLM, and without a specific vector database. The same pack can be used by a local open-source model and a hosted API-based model without modification. Embeddings, when included, are tagged with model and provider — so systems can select the right embedding set or compute their own.

### Reference implementations

- Python: `reference/python/` — `Pack`, `Manifest`, `validate()`, `EvaluationCase`
- JavaScript/TypeScript: `reference/javascript/` — `Pack`, type definitions for all manifest fields

### Further reading

| Document | Contents |
|----------|---------|
| [AI_DISCOVERY.md](AI_DISCOVERY.md) | Concise machine-friendly onboarding for AI agents and tooling |
| [docs/ai-integration.md](docs/ai-integration.md) | RAG, fine-tuning, evaluation, workflow execution, robotics — detailed patterns |
| [docs/agent-interoperability.md](docs/agent-interoperability.md) | Agent orchestration, capability negotiation, distributed agent ecosystems |
| [schemas/manifest.schema.json](schemas/manifest.schema.json) | Authoritative manifest schema including `ai`, `capabilities`, `trust` |

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
├── AI_DISCOVERY.md        Machine-friendly onboarding for AI agents and tooling
├── SPEC.md                Full format specification
├── ROADMAP.md             Development milestones
├── CONTRIBUTING.md        Contribution guide
├── GOVERNANCE.md          Governance model and decision process
├── CODE_OF_CONDUCT.md     Community standards
├── AUTHORS.md             Project founder and contributors
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
│   ├── basic-pack/             Minimal valid example pack
│   ├── homebrew-recipe-pack/   Multi-artifact example (recipe, data, prompt, evals)
│   ├── brewing/                Water chemistry example pack
│   ├── mechanic-diagnostics/   Placeholder
│   └── software-architecture/  Placeholder
├── docs/
│   ├── assets/
│   │   ├── okpf.svg           OKPF logo, vector
│   │   ├── okpf-light.svg     OKPF logo, vector for dark backgrounds
│   │   └── okpf.png           OKPF logo, raster
│   ├── concepts.md
│   ├── phase-1-roadmap.md      Phase 1 inclusions/exclusions
│   ├── ai-integration.md
│   ├── agent-interoperability.md
│   ├── licensing.md
│   ├── licensing-strategy.md
│   ├── provenance.md
│   ├── blockchain.md
│   ├── security.md
│   └── examples.md
├── reference/
│   ├── python/
│   │   ├── okpf_validate.py    Standalone validator CLI script
│   │   └── okpf/               okpf-py reference library
│   └── javascript/             okpf-js reference library
└── tools/
    └── README.md          CLI tooling plan
```

---

*OKPF is an early-stage open standard. The specification is in draft. Feedback, critique, and contributions are actively sought.*

*If you are building a system that could benefit from portable, attributed, licensed knowledge packs — and especially if the current format does not quite fit your use case — please open an issue. The spec is shaped by real use cases.*
