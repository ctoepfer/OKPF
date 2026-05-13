# AI Integration Guide

This document explains how AI systems — including RAG pipelines, fine-tuning workflows, agent frameworks, robotics systems, and evaluation benchmarks — can consume OKPF knowledge packs.

OKPF does not prescribe how AI systems work internally. It provides a standard packaging layer so that structured knowledge can be ingested consistently, regardless of the downstream AI architecture.

---

## Table of Contents

- [Core Principle: Knowledge Separate from Infrastructure](#core-principle)
- [How Schemas Help AI Systems](#how-schemas-help-ai-systems)
- [Pack Discovery and Loading](#pack-discovery-and-loading)
- [RAG Ingestion](#rag-ingestion)
- [Fine-Tuning Datasets](#fine-tuning-datasets)
- [Workflow Execution](#workflow-execution)
- [Evaluation and Benchmarking](#evaluation-and-benchmarking)
- [Provenance-Aware Retrieval](#provenance-aware-retrieval)
- [Multimodal Processing](#multimodal-processing)
- [Robotics and Simulation](#robotics-and-simulation)
- [Trust and Verification](#trust-and-verification)
- [Capability Negotiation](#capability-negotiation)
- [Future Agent Interoperability](#future-agent-interoperability)

---

## Core Principle

OKPF separates **knowledge** from **infrastructure**.

A knowledge pack contains content, structure, provenance, and licensing. It does not contain embeddings of a specific model, pointers to a specific vector database, or code that runs on a specific runtime. This separation means:

- The same pack can be used by a GPT-based RAG pipeline and an open-source local LLM without modification.
- The same pack can be used for fine-tuning today and inference-time retrieval tomorrow.
- Embeddings can be added to a pack for a specific model/provider and replaced when a better model becomes available.
- A pack created for one AI system can be read by another without translation.

The manifest is the interface. AI systems that start by reading the manifest can understand what a pack contains, what it permits, and how it should be used — before loading any content.

### Domain-specific artifacts inside OKPF

OKPF can embed or reference domain-specific artifacts without replacing their native standards. For example, a pack may include BeerXML for brewing recipes, SCORM or xAPI for learning content, JSON-LD or RDF for semantic data, CSV or Parquet for tabular datasets, and Markdown, PDF, or text files for human-readable source material.

In those cases, OKPF provides the surrounding package context: the manifest, normalized records, provenance, licensing, attribution, intended use, evaluations, workflows, and AI/tooling guidance. The domain artifact remains useful in its native ecosystem while the OKPF pack makes it portable across broader computational workflows.

---

## How Schemas Help AI Systems

The JSON Schemas in `schemas/` provide more than validation. For AI systems, they serve as a **contract**:

- **Manifest schema** declares what fields always exist, what types they are, and what values are valid. An AI tool that parses a manifest can rely on these guarantees without inspecting each pack individually.
- **`capabilities` array** lets a system filter packs by what they support before loading any content — analogous to checking a package manifest for supported platforms.
- **`ai` metadata block** provides advisory hints — safe for training, contains PII, modalities present — that let AI pipelines make routing decisions without reading content.
- **`trust` block** summarizes verification state so trust-aware systems can weight packs differently based on provenance completeness and signing status.
- **Evaluation schema** provides a standard shape for test cases that AI systems can execute programmatically.

### Example: schema-guided routing

```python
import json

manifest = json.load(open("pack/manifest.json"))

# Route based on declared capabilities
if "fine-tuning" in manifest.get("capabilities", []):
    send_to_training_pipeline(manifest)

# Skip packs with PII for public training
if manifest.get("ai", {}).get("contains_pii", False):
    skip_training(manifest)

# Check training permission before ingesting
license = json.load(open("pack/license.json"))
if license["scope"].get("ai_training") == "prohibited":
    raise PermissionError("Pack license prohibits AI training use")
```

---

## Pack Discovery and Loading

Any tool that processes OKPF packs MUST start with `manifest.json`.

### Loading sequence

1. Open `manifest.json` at the pack root (directory or `.kpack` archive)
2. Resolve `$ref` values: `{"$ref": "license.json"}` → load `license.json` from pack root
3. Validate manifest against `manifest.schema.json`
4. Verify SHA-256 hashes on content artifacts (when declared)
5. Proceed with content based on `content[*].role` and `content[*].type`

### Content roles for AI systems

| Role | MIME types | AI relevance |
|------|-----------|-------------|
| `guide` | `text/markdown` | Primary source for RAG and fine-tuning |
| `transcript` | `text/markdown` | Conversational training data source |
| `workflow` | `application/json` | Executable by workflow engines |
| `evaluation` | `application/json` | Benchmark test cases |
| `data` | `application/json`, `text/csv` | Structured retrieval targets |
| `image` | `image/*` | Multimodal training and retrieval |

### Python loading example

```python
from okpf import Pack

pack = Pack.load("examples/brewing/")

print(pack.manifest.name)         # "Water Chemistry for Brewing"
print(pack.manifest.domain)       # "brewing"
print(pack.capabilities)          # ["retrieval", "evaluation", "workflow-execution"]
print(pack.manifest.ai.risk_level) # "low"

for artifact in pack.manifest.content:
    if artifact.role == "guide":
        text = pack.read(artifact.id)
        ingest_for_rag(text)
```

---

## RAG Ingestion

Knowledge packs are well-suited for RAG (Retrieval-Augmented Generation) because they are self-describing and include integrity verification.

### Ingestion approach

1. **Load the manifest** — use `capabilities` to confirm `"retrieval"` is declared.
2. **Check license** — verify `scope.use` permits the intended retrieval use.
3. **Index content by role** — `guide` and `transcript` artifacts are primary retrieval targets; `data` artifacts are good for structured lookup.
4. **Preserve metadata at chunk level** — when chunking, carry forward:
   - Pack ID and version (`manifest.id`, `manifest.version`)
   - Artifact ID and SHA-256 hash
   - License SPDX expression and attribution text
   - Contributor IDs
5. **Use evaluations to validate retrieval** — after ingestion, run the pack's evaluation cases and verify the system retrieves correct answers.

### Chunk metadata example

When a RAG system chunks a pack artifact, the chunk's metadata store should include:

```json
{
  "chunk_id": "brewing-water-chemistry:guide:chunk-003",
  "pack_id": "urn:okpf:brewing:water-chemistry:0.1.0",
  "pack_version": "0.1.0",
  "artifact_id": "guide",
  "artifact_sha256": "e3b0c...",
  "license_spdx": "CC-BY-4.0",
  "attribution": "Water Chemistry for Brewing by OKPF Contributors, licensed under CC BY 4.0.",
  "domain": "brewing",
  "language": "en"
}
```

This ensures attribution information travels with retrieved chunks — important for citation and audit.

### Embedding model independence

OKPF packs MAY include pre-computed embeddings in the `embeddings/` directory, tagged with the model and provider. However, RAG systems SHOULD NOT require these embeddings to be present. The preferred approach is:

1. Check for pre-computed embeddings matching your preferred model.
2. If absent, compute embeddings from the raw content artifacts.
3. If using pre-computed embeddings, verify the model/provider matches your system.

This keeps packs usable across different embedding infrastructures.

---

## Fine-Tuning Datasets

OKPF packs can serve as provenance-aware training datasets when the license permits.

### Pre-flight checks

Before using any pack for training:

```python
license = pack.read_license()

assert license.scope.ai_training != "prohibited", \
    f"Pack {pack.manifest.id} prohibits AI training use"

assert not pack.manifest.ai.get("contains_pii", False), \
    "Pack contains PII — review before training use"
```

### Preparing training examples

Different artifact roles map to different training data shapes:

**`guide` artifacts → instruction-following pairs**
```json
{
  "instruction": "Explain the role of calcium in brewing water.",
  "response": "Calcium (Ca²⁺) promotes enzyme activity...",
  "source_pack": "urn:okpf:brewing:water-chemistry:0.1.0",
  "source_artifact": "guide",
  "license": "CC-BY-4.0"
}
```

**`evaluation` artifacts → benchmark examples**
```json
{
  "question": "Which mineral addition increases sulfate without adding calcium?",
  "correct_answer": "Epsom Salt (MgSO₄·7H₂O)",
  "source_pack": "urn:okpf:brewing:water-chemistry:0.1.0",
  "difficulty": "beginner"
}
```

**`transcript` artifacts → dialogue training data**
Transcripts of expert interviews can be used directly as conversational training examples, with appropriate attribution metadata attached.

### Provenance in training data

Every training example derived from a pack should carry:
- `source_pack`: the pack ID
- `source_artifact`: the artifact ID within the pack
- `license`: the SPDX expression
- `attribution`: the required attribution text if `attribution_required: true`

This creates an auditable lineage from training data back to the original knowledge source.

---

## Workflow Execution

Packs with `"workflow-execution"` in `capabilities` contain structured workflow artifacts that can be executed by compatible systems.

### Workflow artifact structure

Workflow artifacts conform to the `task.schema.json` schema:
- `inputs` — named parameters the workflow requires
- `steps` — ordered procedural steps with branching conditions
- `outputs` — expected results

### Execution model

OKPF does not define a specific workflow engine. Any system that can:
1. Parse a JSON workflow artifact conforming to `task.schema.json`
2. Present the workflow's `inputs` to a user or upstream system
3. Execute `steps` in order, following branching `next_step` conditions
4. Collect `outputs`

...is a conformant workflow executor.

### Example: loading a workflow

```python
pack = Pack.load("examples/brewing/")

workflow = pack.get_workflow("adjustment-workflow")
print(workflow.title)     # "Brewing Water Adjustment Workflow"
print(workflow.inputs)    # list of named inputs
print(len(workflow.steps))  # 13

# Execute with an agent
result = agent.execute_workflow(workflow, inputs={
    "starting_water_type": "tap-water-with-report",
    "beer_style": "West Coast IPA",
    "batch_size_gallons": 6
})
```

---

## Evaluation and Benchmarking

Evaluations in OKPF serve two distinct purposes:

1. **Quality assurance for the pack author** — verifying that the knowledge is accurate and complete.
2. **Benchmarking for AI systems** — testing whether a model has correctly ingested or can reason over the pack's content.

### Evaluation types

| Type | Description |
|------|-------------|
| `qa` | Question with expected answer text or keywords |
| `multiple-choice` | Question with labeled options, correct flag |
| `rubric` | Open-ended question with scoring criteria |
| `benchmark` | Automated test with expected output |
| `checklist` | List of assertions that should all be true |

### Running evaluations programmatically

```python
from okpf import Pack

pack = Pack.load("examples/brewing/")
evaluations = pack.evaluations

for eval in evaluations:
    print(f"[{eval.difficulty}] {eval.question}")
    # Pass to your model / RAG system for answer generation
    response = model.generate(eval.question, context=pack_context)
    score = evaluate_response(response, eval.expected_answer)
    print(f"  Score: {score}")
```

### Evaluation-as-benchmark

Packs that declare `"evaluation"` in `capabilities` can be used as lightweight domain benchmarks. A curated set of evaluated packs across domains constitutes a cross-domain knowledge benchmark — without requiring any single central authority to maintain it.

---

## Provenance-Aware Retrieval

Provenance records in OKPF enable retrieval systems to weight and filter results by source quality and transformation history.

### Provenance signals for retrieval

| Signal | How to use |
|--------|-----------|
| Source type (`original`, `interview`, `publication`) | Weight `original` and `interview` sources higher than `derived` |
| Transformation type (`review`, `manual`) | Prefer content with explicit review transformations |
| `reviewed_by` contributor | Higher confidence when a named domain expert reviewed a transformation |
| `sha256` on sources | Detect if the original source has changed since the pack was authored |
| Contributor ORCID | Cross-reference contributor credentials for domain expertise |

### Trust-weighted retrieval example

```python
def retrieval_weight(chunk_metadata, pack):
    weight = 1.0
    
    if pack.manifest.trust.get("provenance_complete"):
        weight *= 1.2
    
    if pack.manifest.trust.get("signed"):
        weight *= 1.1
    
    if pack.manifest.trust.get("verified_contributors"):
        weight *= 1.15
    
    return weight
```

---

## Multimodal Processing

Packs may contain multiple content modalities. The `ai.modalities` field declares which are present.

| Modality value | Content types |
|---------------|--------------|
| `text` | `text/markdown`, `text/plain` |
| `image` | `image/png`, `image/jpeg`, `image/svg+xml` |
| `structured-data` | `application/json`, `text/csv` |
| `code` | `text/x-python`, `application/javascript` |
| `audio` | `audio/mpeg`, `audio/wav` |
| `video` | `video/mp4` |
| `3d` | `model/gltf+json`, `model/gltf-binary` |

### Processing strategy

```python
pack = Pack.load("illustration-techniques/")

for artifact in pack.manifest.content:
    if artifact.type.startswith("image/"):
        image_data = pack.read_binary(artifact.id)
        process_image(image_data, metadata={
            "pack_id": pack.manifest.id,
            "artifact_id": artifact.id,
            "role": artifact.role
        })
    elif artifact.type == "text/markdown":
        text = pack.read(artifact.id)
        process_text(text)
```

---

## Robotics and Simulation

OKPF packs with `"robotics"` or `"simulation"` capabilities encode knowledge that is relevant to physical or virtual agents.

### Robotics use cases

- **Sensor interpretation** — packs describing what sensor readings mean in specific environments and conditions
- **Manipulation procedures** — structured workflows for physical tasks, with safety conditions as explicit fields
- **Failure mode catalogs** — documented fault patterns with diagnostic decision trees
- **Environment knowledge** — spatial and object relationship data in structured form

For robotics packs, the `task.schema.json` workflow format is particularly relevant — the `inputs`, `steps`, and `outputs` structure maps naturally to robotic task planning: perception inputs → deliberative steps → action outputs.

### Simulation use cases

- **Environment definitions** — parameters describing simulated world properties
- **Agent behavior policies** — decision-logic packs that define agent responses to states
- **Calibration datasets** — provenance-tracked reference data for simulation tuning

### Offline and edge operation

OKPF packs are designed to operate fully offline. A robot or edge device that has loaded a relevant pack does not require network access to use the knowledge it contains. This is a deliberate design choice — physical systems must be resilient to connectivity loss.

---

## Trust and Verification

OKPF provides a layered trust model. AI systems should use these signals to weight and filter knowledge accordingly.

### Trust signals in priority order

1. **Cryptographic signatures** (`signatures[]`) — mathematically verifiable; strongest signal
2. **Attestations** (`trust.attestations[]`) — external review records; strength depends on attester
3. **Provenance completeness** (`trust.provenance_complete`) — all artifacts have traceable origins
4. **Verified contributors** (`trust.verified_contributors`) — contributor identities externally verified
5. **Evaluations present** (`ai.evaluation_available`) — content has associated quality tests
6. **License declared** — any explicit license is better than none

### Trust does not mean accuracy

OKPF trust signals indicate process quality, not content accuracy. A fully signed pack from a credentialed expert can still contain errors. Evaluations are the primary mechanism for assessing content accuracy — trust signals assess the process by which content was produced.

### Consuming untrusted packs

For packs from unknown sources:
1. Run available evaluations to spot-check content quality.
2. Check provenance for missing or implausible transformation records.
3. Do not use for high-stakes applications without additional review.
4. Do not pass `trust.signed: false` packs to safety-critical systems.

---

## Capability Negotiation

Systems that consume multiple packs can use `capabilities` for efficient routing.

### Example: multi-pack orchestration

```python
def route_pack(pack, task):
    caps = set(pack.capabilities)
    
    if task == "answer_question" and "retrieval" in caps:
        return rag_pipeline(pack)
    elif task == "run_benchmark" and "evaluation" in caps:
        return evaluation_runner(pack)
    elif task == "execute_procedure" and "workflow-execution" in caps:
        return workflow_engine(pack)
    elif task == "train_model":
        if "fine-tuning" not in caps:
            raise CapabilityError("Pack does not declare fine-tuning capability")
        return training_pipeline(pack)
    else:
        raise CapabilityError(f"No handler for task={task} with caps={caps}")
```

Capability declarations are advisory. A pack may contain content usable for retrieval without explicitly declaring the `retrieval` capability — tools should treat undeclared capabilities as unknown, not as absent.

---

## Future Agent Interoperability

OKPF is designed to be useful beyond today's AI architectures. Several future integration patterns are anticipated:

### Tool call / function call integration

A future extension could describe pack content as callable tools — so an agent framework can inspect a pack's tasks and register them as callable functions without additional configuration.

### MCP (Model Context Protocol) adapters

Adapter libraries that expose OKPF packs as MCP resources would allow any MCP-compatible agent framework to browse and consume pack content using a standard protocol, without custom integration for each pack.

### Federated pack graphs

Multiple packs, connected by `dependencies`, form a directed knowledge graph. Future agent systems can traverse this graph to assemble composite context — pulling the most relevant sub-packs for a given query.

### Long-running agent memory

Packs can function as persistent, versioned memory stores for agents — a structured alternative to unstructured conversation history. Version-controlled packs allow agents to have stable, auditable knowledge bases.

### Cross-agent knowledge sharing

Two agents built on different architectures, models, or providers can share knowledge by exchanging OKPF packs. The format's infrastructure neutrality is precisely what makes this possible — neither agent needs to know anything about the other's internal architecture.

For a deeper treatment of agent interoperability, see [docs/agent-interoperability.md](agent-interoperability.md).
