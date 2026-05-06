# OKPF Concepts

This document explains the core concepts behind the Open Knowledge Pack Format.

---

## The Problem OKPF Solves

Human expertise is fragile and trapped.

A master brewer's knowledge of water chemistry lives in their head and in informal notes. A senior mechanic's diagnostic intuition exists only in years of lived experience. A principal engineer's architectural judgment is scattered across Slack threads, documents, and memory.

When these experts retire, leave, or become unavailable, their knowledge is largely lost. What survives is usually stripped of context: raw text, unattributed, unlicensed, with no record of who knows it to be correct or why.

OKPF is a format for packaging that expertise so it is:

- **Preserved** — structured, durable, and not dependent on any single platform
- **Attributed** — clearly crediting the humans who generated it
- **Licensed** — declaring exactly how it may be used and by whom
- **Verifiable** — including evaluations that test whether the knowledge is accurate
- **Portable** — usable offline, across organizations, and without vendor lock-in

---

## The Knowledge Pack

A **knowledge pack** (`.kpack`) is the atomic unit in OKPF. Think of it like a Git repository for a body of expertise, or a Docker image for a specific knowledge domain.

A pack is:

- **Self-contained** — everything needed to understand and use the knowledge is inside
- **Versioned** — packs follow semantic versioning; breaking changes are deliberate
- **Attributable** — contributors are tracked at the pack and artifact level
- **Licensable** — licensing is declared explicitly, not assumed
- **Extensible** — new content types can be added without breaking existing tooling

### What Goes in a Pack

| Content Type | Examples |
|-------------|---------|
| Documents | Guides, tutorials, reference materials |
| Transcripts | Expert interviews, Socratic dialogues |
| Workflows | Decision trees, diagnostic procedures |
| Evaluations | Test cases, rubrics, benchmarks |
| Data | Reference tables, datasets, measurements |
| Images | Diagrams, photographs |
| Embeddings | Optional pre-computed vector representations |

---

## Artifacts

Everything inside a pack is an **artifact** — a named, typed, hashable piece of content. Each artifact has:

- A unique `id` within the pack
- A `path` pointing to its file
- A MIME `type`
- A semantic `role` (guide, transcript, workflow, etc.)
- An optional SHA-256 hash for integrity verification

Artifacts are listed in the manifest, which is the authoritative index of a pack's contents.

---

## Contributors

**Contributors** are the humans (and organizations) who created or curated the content in a pack. OKPF treats attribution as a first-class concept — not an afterthought.

Every contributor record can include:
- Name and role
- ORCID identifier (for academic contributors)
- Which artifacts they contributed to
- Affiliation
- Contact details (optional)

Attribution is a prerequisite for trust. If you don't know who made a knowledge pack, you can't evaluate its credibility.

---

## Provenance

**Provenance** records the chain of custody from original source to packaged artifact. It answers:

- Where did this content come from?
- What transformations were applied?
- Who did those transformations?
- What tools were used?

Provenance is modeled as:
- **Sources** — original inputs (publications, interviews, observations, datasets)
- **Transformations** — the steps from source to artifact (extraction, summarization, curation, review)

OKPF provenance is inspired by the [W3C PROV-O](https://www.w3.org/TR/prov-o/) standard but simplified for practical use without requiring semantic web infrastructure.

---

## Licensing

Every pack MUST declare a license. OKPF uses [SPDX expressions](https://spdx.org/licenses/) for machine-readable license identification.

The license schema captures:
- An SPDX expression (e.g., `CC-BY-4.0`, `Apache-2.0`)
- Granular permissions for use, redistribution, derivative works, and AI training
- Attribution requirements
- Optional custom terms

This granularity matters because knowledge packs raise new licensing questions that standard open source licenses don't always address — particularly around AI training use.

---

## Evaluations

**Evaluations** are test cases that verify the quality of knowledge in a pack. They are a form of structured quality assurance.

An evaluation can be:
- A question with an expected answer
- A multiple-choice question
- A rubric for evaluating free-form responses
- A scenario with expected reasoning

Evaluations serve several purposes:
- They help pack authors verify their own content
- They help consumers assess whether a pack covers what they need
- They enable automated quality checks as part of a pack publishing workflow

---

## The Manifest

The **manifest** (`manifest.json`) is the root descriptor of every pack. It is the authoritative source of truth for:

- Pack identity (ID, name, version)
- Content index (what artifacts are in this pack)
- References to license, provenance, contributors
- Optional metadata (tags, language, embeddings, signatures, anchors)

Every valid OKPF pack has a manifest. Tools that work with packs start by reading the manifest.

---

## Optional Capabilities

OKPF defines several optional capabilities that packs can include when useful:

### Embeddings

Pre-computed vector embeddings of content, for use with retrieval systems. Embeddings are:
- Stored alongside content in the pack
- Tagged with the model and provider used to create them
- Not required for any pack functionality

### Signatures

Cryptographic signatures over pack content (manifest, individual artifacts, or the full pack). Signatures provide:
- Integrity verification (content hasn't been tampered with)
- Authorship verification (signature holder approved this content)

Supported types: GPG, SSH key, Ed25519, JWT.

### Anchors

Pointers to external registries or content-addressed stores. Examples:
- An IPFS CID for the packed archive
- A blockchain transaction anchoring the pack hash
- A DOI for a published version

Anchors are **informational only** — they do not affect pack functionality.

---

## Capabilities

**Capabilities** are declared in the manifest's `capabilities` array. They tell consuming systems what a pack can be used for, enabling lightweight negotiation before any content is loaded.

```json
{
  "capabilities": ["retrieval", "evaluation", "workflow-execution"]
}
```

### Defined capabilities

| Capability | Meaning |
|-----------|---------|
| `retrieval` | Content is suitable for embedding-based retrieval (RAG) |
| `fine-tuning` | Content may be used as fine-tuning or pre-training data |
| `evaluation` | Pack includes structured evaluation test cases |
| `workflow-execution` | Pack includes structured workflow artifacts (task.schema.json) |
| `simulation` | Content defines or supports simulation environments |
| `robotics` | Content is applicable to robotics sensing or procedure systems |
| `multimodal` | Pack contains non-text content modalities |
| `reasoning` | Content supports multi-step reasoning or decision tasks |
| `tutoring` | Content is structured for educational or tutoring delivery |
| `diagnostics` | Content supports diagnostic decision workflows |
| `code-generation` | Content describes APIs, coding patterns, or software workflows |
| `decision-support` | Content includes decision frameworks or structured trade-off analyses |

### Capability philosophy

Capabilities are **advisory declarations**, not enforceable contracts. A pack that declares `retrieval` is asserting that its content is well-suited for indexing and retrieval — but a consuming system is free to use it in other ways (subject to license constraints).

This is intentional. Capabilities support:
- **Routing** — an orchestrator can select packs appropriate for a task without loading all content
- **Filtering** — a registry can index packs by capability for discovery
- **Negotiation** — two systems can agree on a shared consumption mode before exchanging a pack

Capabilities do not replace license declarations. A capability declaration says nothing about what is *permitted* — only about what is *structurally possible*. Always check `license.json` before acting on a capability.

### Interoperability and composability

Packs can declare multiple capabilities. A pack with `["retrieval", "evaluation", "workflow-execution"]` can be ingested into a RAG system, benchmarked against a model, and executed as a structured procedure — by the same consuming system or different ones, without modification.

This composability is one of OKPF's core properties. A pack is not authored for a specific consumer — it is authored for its domain, and consumers adapt to the pack rather than the other way around.

### Future: capability negotiation in agent systems

As autonomous systems become more capable, capability declarations will serve as the vocabulary for agent-to-agent knowledge negotiation:

```
Agent A needs: knowledge with capabilities ["diagnostics", "workflow-execution"]
Agent B offers: pack urn:okpf:automotive:mechanic-diagnostics:1.0.0
              capabilities: ["diagnostics", "workflow-execution", "evaluation"]
→ Negotiation succeeds; Agent A loads the pack
```

No protocol standard for this negotiation is defined by OKPF today — but the capability vocabulary is designed to support it. See [docs/agent-interoperability.md](agent-interoperability.md) for a conceptual discussion.

---

## AI Metadata

The optional `ai` block in the manifest provides interoperability hints for AI systems:

```json
{
  "ai": {
    "recommended_use": ["rag", "fine-tuning"],
    "safe_for_training": true,
    "contains_pii": false,
    "modalities": ["text", "structured-data"],
    "risk_level": "low",
    "evaluation_available": true,
    "workflow_capable": false
  }
}
```

These fields are advisory. They help AI pipelines make routing decisions without reading content — analogous to package metadata that a build system reads before downloading the package.

- `ai_training` permission in `license.json` is the authoritative source for training permissions. `safe_for_training` is a supplementary hint, not a grant of permission.
- `contains_pii: true` signals that data handling policies should be applied before training or indexing.
- `risk_level` reflects content sensitivity, not licensing.

---

## Trust Metadata

The optional `trust` block summarizes the verification state of a pack:

```json
{
  "trust": {
    "signed": false,
    "verified_contributors": false,
    "provenance_complete": true,
    "verification_method": "editorial review by pack registry"
  }
}
```

Trust metadata is informational and infrastructure-neutral. It describes what has been done — not what is enforced. Consuming systems should use trust fields to weight knowledge, not as binary access controls.

See [docs/security.md](security.md) for the full security model.

---

## What OKPF Is Not

Understanding what OKPF is not helps clarify its scope:

| What people might expect | What OKPF actually is |
|--------------------------|----------------------|
| A platform or marketplace | A file format specification |
| An AI model or embedding system | A packaging format that can optionally include embeddings |
| A blockchain project | A format with optional, chain-agnostic blockchain anchoring |
| A training data format | A knowledge pack format (though packs may declare training permissions) |
| A replacement for documentation systems | A portable complement to them |
| A proprietary standard | An open standard with community governance |

---

## Design Analogies

If you're familiar with these technologies, the following analogies may help:

| OKPF concept | Analogy |
|-------------|---------|
| `.kpack` file | Docker image / `.epub` / npm package |
| `manifest.json` | `package.json` / OCI manifest / EPUB `content.opf` |
| Content artifacts | Files in a Git repository |
| Pack version | Git tag / SemVer release |
| Evaluations | Unit tests for knowledge |
| Provenance | Git blame / SBOM |
| Anchors | Git remote / IPFS CID |
