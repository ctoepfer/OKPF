<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/okpf-light.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/okpf.svg">
    <img src="docs/assets/okpf.svg" alt="OKPF logo" width="160">
  </picture>
</p>

# OKPF — Open Knowledge Pack Format

**A simple, neutral packaging format for structured knowledge artifacts with provenance, licensing, and evaluation metadata.**

> OKPF is a file format specification — not a platform, not a marketplace, and not a blockchain project.  
> It is designed to be simple, composable, and long-lived.

---

OKPF is a simple, vendor-neutral package format for bundling knowledge artifacts, normalized records, provenance, licensing, usage policy, and evaluation metadata.

It is useful when teams need portable, inspectable knowledge packages for documentation, RAG ingestion, evaluation, archival transfer, domain profiles, or derived training datasets.

OKPF was initiated by [Charles Toepfer](https://github.com/ctoepfer) as an open effort to develop a practical, infrastructure-neutral format for packaging structured knowledge. It is designed as a community-driven project — open in governance, open in implementation, and independent of any single organization, platform, or technology stack.

## What OKPF Does / Does Not Do

| OKPF does | OKPF does not |
|-----------|---------------|
| Package knowledge artifacts and records | Prove the knowledge is true |
| Preserve declared provenance and attribution | Guarantee authorship or ownership |
| Declare license and usage policy metadata | Enforce licenses automatically |
| Carry evaluations and examples | Guarantee model or system performance |
| Wrap existing domain formats | Replace mature domain formats |
| Carry training-ready derivatives | Run training pipelines |
| Support profiles | Define a universal ontology |

## Example-Driven Development

OKPF is being developed through small, inspectable example packs rather than broad claims. Current examples show Native Mode knowledge packs, Hybrid Mode domain artifacts, training-ready derivatives, and a cautious Physical Skill Evidence profile for embodied/process data.

- [Examples overview](docs/examples.md)
- [Packaging modes](docs/packaging-modes.md)
- [Training-ready derivatives](docs/training-ready-derivatives.md)
- [Zymurgy recipe correction example](examples/zymurgy-recipe-correction/)
- [Physical Skill Evidence profile](profiles/physical-skill-evidence/v0.1.0/PROFILE.md)

---

## Table of Contents

- [Current Status: OKPF Core v0.1.0](#current-status-okpf-core-v010)
- [What OKPF Does / Does Not Do](#what-okpf-does--does-not-do)
- [Example-Driven Development](#example-driven-development)
- [Vision](#vision)
- [Why OKPF Exists](#why-okpf-exists)
- [Design Principles](#design-principles)
- [Simple Core, Optional Power](#simple-core-optional-power)
- [Non-Goals](#non-goals)
- [Core Concepts](#core-concepts)
- [Package Philosophy](#package-philosophy)
- [How OKPF Differs From Domain Formats Like BeerXML](#how-okpf-differs-from-domain-formats-like-beerxml)
- [Loose Files vs OKPF](#loose-files-vs-okpf)
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

OKPF Core v0.1.0 is in release-candidate readiness: the current focus is specification/schema consistency, conformance fixtures, reference validation, and conservative documentation cleanup.

### What it is

A knowledge pack is a directory or `.kpack` ZIP containing a `manifest.json` plus at least one declared payload in `artifacts`, `records`, or legacy `content`. It may also retain original sources, provenance, import reports, derived chunks, schemas, docs, assets, and license files.

### Minimal valid pack structure

```
my-pack/
  manifest.json
  content/ or records/ or other declared artifacts
```

### Quickstart: validate an example pack

```bash
# Validate the Hello World example pack
python3 reference/python/okpf_validate.py examples/hello-world
python3 reference/python/okpf_validate.py examples/fermentation-mixed-bundle --profile fermentation
python3 reference/python/okpf_validate.py examples/fermentation-mixed-bundle --strict-profile

# Or use the package CLI from a source checkout
PYTHONPATH=reference/python python3 -m okpf validate examples/hello-world
PYTHONPATH=reference/python python3 -m okpf validate examples/fermentation-mixed-bundle --profile fermentation
PYTHONPATH=reference/python python3 -m okpf inspect examples/hello-world
PYTHONPATH=reference/python python3 -m okpf pack examples/hello-world out/hello-world.kpack
PYTHONPATH=reference/python python3 -m okpf unpack out/hello-world.kpack out/hello-world-unpacked
```

### Key Phase 1 deliverables

| Deliverable | Location |
|-------------|---------|
| Core specification | [SPEC.md](SPEC.md) |
| Manifest JSON Schema | [schemas/v0.1.0/manifest.schema.json](schemas/v0.1.0/manifest.schema.json) |
| Evaluation result JSON Schema | [schemas/v0.1.0/evaluation-result.schema.json](schemas/v0.1.0/evaluation-result.schema.json) |
| Record JSON Schema | [schemas/record.schema.json](schemas/record.schema.json) |
| Import report JSON Schema | [schemas/import_report.schema.json](schemas/import_report.schema.json) |
| Provenance source entry schema | [schemas/provenance-source-entry.schema.json](schemas/provenance-source-entry.schema.json) |
| Hello World example pack | [examples/hello-world/](examples/hello-world/) |
| Minimal example pack | [examples/minimal/](examples/minimal/) |
| Fermentation profile example | [examples/fermentation-bjcp-style/](examples/fermentation-bjcp-style/) |
| Fermentation profile definition | [profiles/fermentation/v0.1.0/](profiles/fermentation/v0.1.0/) |
| Zymurgy recipe correction example | [examples/zymurgy-recipe-correction/](examples/zymurgy-recipe-correction/) |
| Physical skill evidence profile | [profiles/physical-skill-evidence/v0.1.0/](profiles/physical-skill-evidence/v0.1.0/) |
| Physical skill evidence example | [examples/physical-skill-sewing-evidence/](examples/physical-skill-sewing-evidence/) |
| Standalone validator | [reference/python/okpf_validate.py](reference/python/okpf_validate.py) |
| Python SDK | [reference/python/okpf/](reference/python/okpf/) |
| JavaScript/TypeScript SDK | [reference/javascript/src/](reference/javascript/src/) |
| Phase 1 roadmap | [docs/phase-1-roadmap.md](docs/phase-1-roadmap.md) |

### What is NOT in Phase 1

Blockchain ownership, marketplace payments, royalty enforcement, content encryption, zero-knowledge proofs, trusted execution environments, and hosted registry protocols are intentional exclusions. They are future optional extensions to be built on top of a stable core. See [docs/phase-1-roadmap.md](docs/phase-1-roadmap.md) for the full inclusion/exclusion list.

---

### Phase 2 — Conformance, Examples, and Pack Tooling

Phase 2 moves OKPF from "interesting draft format" toward "usable v0.1 draft standard" with four focused deliverables.

#### Conformance levels

The [v0.1 conformance document](docs/v0.1-conformance.md) defines four conformance levels:

| Level | Name | Summary |
|-------|------|---------|
| 0 | Manifest Reader | Locate and parse manifest.json; tolerate unknown fields; reject unsafe paths |
| 1 | Core Validator | Validate against local schema; check artifact presence; warn on missing metadata |
| 2 | Integrity-Aware Consumer | Verify SHA-256 hashes; preserve provenance on ingestion |
| 3 | Profile-Aware Consumer | Apply local profile schemas; warn on unknown profiles; strict mode optional |

The reference validator implements Level 2, with optional Level 3 for the fermentation profile.

#### Profile authoring

The [profile authoring guide](docs/profile-authoring.md) explains how to define domain-specific conventions without modifying OKPF Core. Profiles MUST NOT introduce new required manifest fields, mandate infrastructure, or redefine core semantics.

#### Practical non-brewing example packs

| Example | Domain | Description |
|---------|--------|-------------|
| [examples/local-organization-knowledge/](examples/local-organization-knowledge/) | Organizational | Board procedures, decision history, vendor SOPs |
| [examples/software-onboarding/](examples/software-onboarding/) | Software engineering | Setup guides, architecture overview, troubleshooting |
| [examples/field-repair-checklist/](examples/field-repair-checklist/) | Maintenance | Safety precheck, diagnostic checklist, fault symptoms |

All content is fictional placeholder data for format demonstration.

#### Pack and unpack CLI commands

The reference CLI now supports `pack` and `unpack`:

```bash
# Pack a directory into a .kpack archive
PYTHONPATH=reference/python python3 -m okpf pack examples/hello-world out/hello-world.kpack

# Unpack a .kpack archive
PYTHONPATH=reference/python python3 -m okpf unpack out/hello-world.kpack out/hello-world-unpacked

# Inspect a pack (directory or .kpack)
PYTHONPATH=reference/python python3 -m okpf inspect examples/hello-world
```

The `pack` command excludes generated directories (`__pycache__`, `.venv`, `.pytest_cache`, `*.egg-info`), rejects unsafe paths, and requires `manifest.json`. The `unpack` command rejects unsafe ZIP entries before extracting anything.

#### What Phase 2 deliberately excludes

Blockchain anchoring, signatures, registries, marketplaces, payment systems, model training pipelines, embeddings, vector database integrations, workflow execution, encryption, remote schema fetching, hosted services, AI-provider integrations, and new required manifest fields remain outside OKPF Core.

---

### Phase 3 — Adoption Proof and Benchmark Plan

OKPF Core remains intentionally small. Phase 3 is focused on proving practical value in a few realistic workflows before expanding claims about broader standardization.

#### Adoption strategy

The [adoption strategy](docs/adoption-strategy.md) names three initial target verticals — software onboarding, organizational knowledge preservation, and field repair checklists — and defines measurable 6–9 month success criteria. It also lists non-adoption risks honestly.

#### Benchmark plan

The [benchmark plan](docs/benchmark-plan.md) defines measurable questions comparing OKPF against plain Markdown folders, YAML front matter, JSONL-only files, RAG loader conventions, and archival formats. It identifies which benchmarks can be run today and which require future tooling.

#### When not to use OKPF

The [when-not-to-use document](docs/when-not-to-use-okpf.md) is direct: a single private note file, throwaway prompts, simple docs with no reuse need, and contexts where licensing metadata is expected to enforce itself are not good fits for OKPF. It also explains why OKPF is not a moat.

#### Git-native workflow

The [Git-native workflow guide](docs/git-native-workflow.md) describes how to author, version, validate, and distribute OKPF packs through Git before any registry or marketplace exists. This is the recommended early adoption path.

#### compare-layout benchmark helper

```bash
# Generate alternative layout exports for benchmark comparison
PYTHONPATH=reference/python python3 -m okpf compare-layout examples/software-onboarding out/comparison/
```

Outputs `markdown-folder/`, `jsonl-only/records.jsonl`, and `manifest-summary.json` — enabling side-by-side comparison of OKPF against simpler alternatives.

---

### Phase 4 — Packaging Modes

#### OKPF Packaging Modes

OKPF supports multiple packaging modes. Some packs are native OKPF record/document packs. Others use OKPF as an envelope around existing domain formats. Many practical packs are hybrid: they preserve source artifacts while adding normalized records, provenance, licensing, usage policy, and evaluation metadata.

| Mode | Use when | Example |
|------|----------|---------|
| **Native** | Knowledge is textual/procedural; no prior domain format | `examples/software-onboarding`, `examples/field-repair-checklist` |
| **Envelope** | A mature domain format must stay authoritative; OKPF adds package context | BeerXML, FHIR, ONNX, ROS bag, CAD file wrapped in OKPF |
| **Hybrid** | Domain artifact preserved; normalized records also needed | `examples/brewing-with-beerxml` |

See [docs/packaging-modes.md](docs/packaging-modes.md) for full guidance, including decision criteria, manifest examples, and a classification of all example packs in this repository.

#### A note on portability

OKPF packages artifacts, records, metadata, provenance, licensing, and usage policy. It does not guarantee that the packaged knowledge is complete, correct, safe, or fully transferable across contexts. A pack can express what a domain expert intended to share; it cannot substitute for the expert's judgment in new situations. Consumers should treat OKPF packs as structured references, not as authoritative ground truth.

#### Training-Ready Derivatives

OKPF source packs are not automatically training datasets. A pack may optionally include training-ready derivatives such as instruction JSONL, preference data, completion JSONL, retrieval-evaluation pairs, dataset cards, or Parquet datasets. These derivatives should declare what source records and artifacts they came from, what transformations were applied, what filtering or deduplication occurred, what review happened, and what limitations remain. OKPF packages these files and their provenance; it does not run training pipelines or guarantee model quality.

Training use is always subject to the pack's `license` and `usage_policy`. The presence of a `training/` directory does not create training permission. See [docs/training-ready-derivatives.md](docs/training-ready-derivatives.md) for guidance and conventions.

---

## Vision

The long-term aspiration is that useful knowledge should be easier to move across tools without losing its sources, permissions, review context, or evaluation evidence.

Experienced practitioners often leave behind documents, notes, checklists, datasets, and examples with no consistent package boundary, provenance trail, license, or evaluation context. OKPF defines a small packaging layer for those materials so they can be inspected, versioned, validated, and reused by humans and software systems.

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

Many AI, RAG, documentation, evaluation, and domain-specific tooling stacks use their own internal metadata conventions. These conventions often do not travel well across systems.

OKPF addresses all five problems with a single, open, composable packaging layer.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Portability** | A `.kpack` is a self-contained archive. No network access, no external service, and no runtime required to read it. |
| **Attribution first** | Contributors, sources, and transformations are explicit fields, so declared attribution can travel with the pack. |
| **License clarity** | Every pack declares explicit licensing terms, including permissions for use, redistribution, derivative works, and AI training. |
| **Provenance** | Packs can declare the chain of origin — who created an artifact, from what source, through what transformations, reviewed by whom. |
| **Evaluation support** | Packs can include evaluations — structured test cases or examples that support quality checking. |
| **Extensibility** | New content types and metadata fields can be added without breaking existing tools. Unknown fields are preserved, not rejected. |
| **Semantic versioning** | Both the OKPF spec and individual packs follow [SemVer](https://semver.org). Breaking changes are deliberate and documented. |
| **Openness** | The format is fully specified, freely implementable, and governed by the community — not by any single vendor. |
| **Composability** | Packs can reference other packs as dependencies. Systems built on OKPF are free to combine, extend, and layer. |
| **Infrastructure neutrality** | Blockchain, AI models, embedding providers, cloud storage, and vector databases are all optional. The base format works without any of them. |

---

## Simple Core, Optional Power

A minimal OKPF pack should be possible to write by hand. The core format stays small: a `manifest.json`, a package identifier, version, license, and one or more declared artifacts or record files.

Advanced features are optional layers. Dependency resolution, cryptographic signatures, registries, JSON-LD mappings, workflow runtimes, and evaluation runners are not required for a basic valid pack.

OKPF should support serious trust and interoperability features without making the Hello World example difficult to understand.

### Profiles and Facets

OKPF Core defines the package boundary, manifest, artifacts, records, provenance, licensing, and validation basics. Optional profiles define domain-specific conventions such as recommended record types, facets, vocabularies, validation rules, and examples.

A pack may declare zero or more profiles:

```json
{
  "okpf_version": "0.1.0",
  "package_id": "org.example.fermentation.bjcp-cider-2025",
  "name": "BJCP 2025 Cider Style Guidelines",
  "version": "0.1.0",
  "domain": "fermentation",
  "profiles": ["okpf-core", "okpf-fermentation"]
}
```

Unknown profiles do not make a pack invalid at the core level. Profile-aware validators can add warnings or stricter checks.

Records may include optional `facets`, which are machine-readable classification hints for filtering, retrieval, validation, display, and routing. OKPF Core does not define a global facet vocabulary; profiles may recommend keys and values.

The fermentation profile in [profiles/fermentation/v0.1.0/](profiles/fermentation/v0.1.0/) is an example profile informed by real ingestion work. It keeps beer, wine, mead, cider, ingredient, recipe, and fermentation-specific concepts out of OKPF Core.

The physical-skill-evidence profile in [profiles/physical-skill-evidence/v0.1.0/](profiles/physical-skill-evidence/v0.1.0/) shows how OKPF can wrap physical-process or robotics datasets as evidence for adaptation and validation. It does not define a robotics data format or guarantee skill transfer.

The [zymurgy recipe correction example](examples/zymurgy-recipe-correction/) demonstrates an AI-output to human-correction to outcome-evidence loop for portable training derivatives.

### OKPF and Lumina

Lumina is an early consumer/testbed for OKPF-style knowledge packs. Lessons from Lumina may inform OKPF examples and profiles, but OKPF remains independent of Lumina and does not require Lumina-specific fields.

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

Think of it as a directory or ZIP package for a body of knowledge — with explicit licensing, provenance, evaluations, and optional cryptographic integrity.

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

OKPF treats packaging as a small, composable layer that other systems can depend on without reinventing manifest, provenance, license, and evaluation metadata.

The `.kpack` format is the unit of exchange. Like an npm package, a pip wheel, or an OCI container image, it:
- carries everything it needs to be used without external dependencies
- declares its own identity, version, and content explicitly
- is addressable by a stable identifier
- can be composed with other packs through dependency declarations
- supports integrity verification through content hashing

Unlike those analogies, OKPF packages are *knowledge*, not code. This introduces considerations that software packaging does not face: licensing for human use versus AI use, attribution to the original experts, provenance back to primary sources, and evaluation criteria for quality. The OKPF manifest is designed specifically for these concerns.

The goal is that a well-formed `.kpack` should be interpretable by conformant tools without requiring access to the system that created it, the platform it was published on, or the organization that maintained it.

---

## How OKPF Differs From Domain Formats Like BeerXML

OKPF is not a replacement for BeerXML or other domain-specific standards. BeerXML describes brewing recipes and related brewing process data. OKPF describes portable knowledge packages.

BeerXML describes brewing recipes. OKPF describes portable knowledge packages. A brewing OKPF pack might contain BeerXML, but OKPF itself is not BeerXML.

An OKPF pack may include, reference, wrap, translate, or augment domain-specific formats such as BeerXML. For example, a brewing knowledge pack could include a BeerXML recipe file as a source or domain artifact, then add Markdown explanations, normalized records, workflow steps, evaluation questions, provenance, licensing, attribution, citation metadata, and AI/tooling instructions around it.

The goal is not to replace existing domain standards. The goal is to provide package context around them so that humans, AI systems, education platforms, RAG systems, training-data preparation workflows, and evaluation harnesses can inspect sources, permissions, records, and evidence.

OKPF supports three packaging modes depending on what domain assets already exist. See [docs/packaging-modes.md](docs/packaging-modes.md) for a full description:

- **Native Mode** — knowledge authored directly as OKPF records; no prior domain format involved
- **Envelope Mode** — an existing domain artifact (BeerXML, FHIR, SCORM, etc.) lives in `sources/`; OKPF adds provenance, license, and usage policy around it
- **Hybrid Mode** — domain artifact preserved plus OKPF records derived alongside it for consumers that cannot read the domain format

| OKPF is not | OKPF is |
|---|---|
| A replacement for BeerXML, SCORM, JSON-LD, RDF, ZIP, or model-specific training formats | A packaging convention that can include, reference, or coexist with those formats |
| A single-domain recipe format | A model-neutral knowledge package format |
| Only training data | A broader knowledge package with metadata, provenance, licensing, workflows, examples, and evaluations |
| Tied to one AI vendor, blockchain, database, or runtime | Vendor-neutral, model-neutral, and infrastructure-neutral |

---

## Loose Files vs OKPF

Loose RAG files provide content. OKPF provides content plus context: provenance, licensing, attribution, intended use, structure, workflows, evaluations, and machine-readable consumption guidance.

OKPF is complementary to RAG pipelines and simple file folders. It gives agents and tools a predictable package boundary when content needs to move across systems or be reused over time.

| Loose files / simple JSON | OKPF pack |
|---|---|
| Content only | Content plus manifest/context |
| Unclear provenance | Explicit provenance and attribution |
| Unclear usage rights | Machine-readable license and usage policy |
| No standard structure | Predictable package layout |
| Harder for AI agents to interpret consistently | Designed for AI/tool consumption |

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

OKPF is not limited to AI model training. Knowledge packs are useful when a workflow needs portable files plus inspectable context.

**Consumption modes supported:**
- Inference-time retrieval (RAG pipelines)
- Derived training and evaluation datasets
- Domain datasets wrapped in Envelope or Hybrid Mode
- Educational content and curriculum systems
- Expert systems and decision support
- Workflow automation

---

### Technical and Scientific Domains

**AI and machine learning**
- Labeled knowledge datasets with provenance and licensing for fine-tuning
- Domain-specific evaluation benchmarks distributed as packs
- RAG context packs with structured Q&A and evaluation test cases

**Robotics**
- Envelope or Hybrid packs around robotics datasets such as LeRobot, RLDS, Robo-DM, ROS bags, calibration bundles, and evaluation reports
- Physical skill evidence packs that document source data, embodiment descriptions, transfer claims, limitations, and validation evidence
- Failure mode catalogs and diagnostic references with provenance and review notes

Physical skill packs are evidence for adaptation and validation, not installable robot skills. OKPF does not define robot-control semantics, simulator behavior, model execution, or skill transfer guarantees.

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

### A pack with attribution and capabilities

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

### A robotics evidence pack in Hybrid Mode

```
warehouse-navigation-knowledge/
├── manifest.json
├── license.json
├── contributors.json
├── provenance.json
├── sources/
│   ├── sensor-run.rosbag
│   └── calibration.yaml
├── records/
│   └── evaluation-claims.jsonl
├── evaluations/
│   └── scenario-tests.json
└── docs/
    └── known-limitations.md
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

Because packs can carry structured contributor records, licensing terms, and provenance, a distribution platform could implement attribution tracking and royalty distribution without changing OKPF Core. The relevant metadata — who contributed what, under what license, with what declared AI training permissions — can travel with the pack.

OKPF does not define payment protocols. It defines the attribution and licensing metadata that payment and royalty systems require.

### Knowledge licensing and leasing

A platform could implement time-limited or scoped access to pack content — "leasing" a pack for a specific use case, duration, or organization — using the pack's declared license terms and a separate access layer. OKPF's per-artifact licensing and `scope` fields provide the structured foundation for these policies.

OKPF does not define leasing protocols. It defines the licensing granularity that leasing systems can act on.

### Ownership and rights registries

A registry built on OKPF could record declared pack ownership, track rights transfers, and maintain a history of claims about a body of knowledge. The `anchors` field in the manifest can point to external records — blockchain-based or otherwise.

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

OKPF is designed for machine consumption, not just human authorship. Several features of the format are intended to make packs useful to AI systems, agent frameworks, evaluation tooling, and domain-specific consumers.

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
| [docs/ai-integration.md](docs/ai-integration.md) | RAG, training-ready derivatives, evaluation, workflow execution, robotics evidence framing |
| [docs/agent-interoperability.md](docs/agent-interoperability.md) | Agent orchestration and capability negotiation |
| [schemas/v0.1.0/manifest.schema.json](schemas/v0.1.0/manifest.schema.json) | Authoritative v0.1.0 manifest schema |

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
│   ├── manifest.schema.json      Compatibility pointer
│   ├── v0.1.0/
│   │   ├── manifest.schema.json
│   │   └── evaluation-result.schema.json
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

---

## okpf-prep: Training Preparation Library

This repository includes `okpf-prep`, a Python library for converting source documents (Markdown, plain text, PDF) into OKPF-compatible packs with optional derived records.

`okpf-prep` is the canonical Python preparation tool for OKPF. It lives here so that any system — including Lumina — can consume it as an ordinary Python dependency.

### What okpf-prep does

1. Loads a training prep profile from YAML
2. Extracts text from source files (`.txt`, `.md`, `.pdf`)
3. Chunks extracted text into manageable sections
4. Builds prompts from the selected training profile
5. Sends prompts to a local AI backend (mock or Ollama)
6. Produces an OKPF-style output directory
7. Validates generated records against the profile
8. Provides a CLI and a Python API

It does **not** include a web UI, queue management, Qdrant ingestion, or application-layer workflow. Those belong to the consuming system (e.g. Lumina).

### Output structure

```
out/my-pack/
  manifest.json             # Package metadata
  records.json              # All OKPF records
  sources/
    original_source.md      # Copy of the source file
    extracted_text.md       # Extracted plain text
  reports/
    conversion_report.json  # Per-source conversion stats and validation result
```

### CLI usage

```bash
# Validate a training prep profile
okpf-prep validate-profile profiles/brewing_recipe.yaml

# Prepare a training pack using the deterministic mock backend (no AI required)
okpf-prep prepare \
  --source examples/brewing_notes.md \
  --profile profiles/brewing_recipe.yaml \
  --out out/brewing_notes \
  --backend mock

# Prepare using a local Ollama model
okpf-prep prepare \
  --source examples/brewing_notes.md \
  --profile profiles/brewing_recipe.yaml \
  --out out/brewing_notes_llm \
  --backend ollama \
  --model qwen2.5:7b

# Extract text only
okpf-prep extract-text examples/brewing_notes.md --out /tmp/extracted.md
```

### Python API usage

```python
from okpf_prep import prepare_training_pack

result = prepare_training_pack(
    source_path="examples/brewing_notes.md",
    profile_path="profiles/brewing_recipe.yaml",
    output_dir="out/brewing_notes",
    backend="mock",
)

print(f"Records : {result.record_count}")
print(f"Status  : {result.validation_status}")
print(f"Output  : {result.output_dir}")
```

Class-based API:

```python
from okpf_prep.profiles import load_profile
from okpf_prep.ai.mock import MockAIBackend
from okpf_prep.runner import PrepRunner

profile = load_profile("profiles/brewing_recipe.yaml")
runner = PrepRunner(profile, MockAIBackend())
result = runner.run("examples/brewing_notes.md", "out/brewing_notes")
```

### Dev install (from this repo)

```bash
cd /home/toepf/Projects/OKPF
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### How Lumina (or any other consumer) imports okpf-prep

**Local editable install during development:**

```bash
cd /mnt/lumina_share/lumina
runtime/venv/bin/pip install -e /home/toepf/Projects/OKPF
```

**Pinned Git dependency for production or reproducible builds:**

```
okpf-prep @ git+https://github.com/ctoepfer/OKPF.git@v0.1.0
```

Add to `requirements.txt`, or in `pyproject.toml`:

```toml
dependencies = [
    "okpf-prep @ git+https://github.com/ctoepfer/OKPF.git@v0.1.0",
]
```

Lumina should **not** contain a copy of `okpf_prep/`. Import it as an external dependency only.

### Training prep profiles

Profiles live in `profiles/` as YAML files. Two are included:

| Profile | Domain | Purpose |
|---|---|---|
| `profiles/brewing_recipe.yaml` | brewing | Recipes, ingredients, process notes, style guidelines |
| `profiles/general_knowledge.yaml` | general | Facts, definitions, procedures, references |

Note: `profiles/fermentation/` (in the same directory) contains OKPF domain profiles — JSON Schema definitions for record types — which are a different concept from prep profiles.

### AI backends

| Backend | Description |
|---|---|
| `mock` | Deterministic, no model required. Safe for tests and CI. |
| `ollama` | Calls a local Ollama instance. Default URL: `http://localhost:11434`. |

Tests use the mock backend only. Ollama is never required to run tests.
