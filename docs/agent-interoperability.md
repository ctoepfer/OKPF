# Agent Interoperability

This document describes how OKPF knowledge packs can serve as the shared knowledge layer for autonomous systems — AI agents, robotics platforms, orchestration frameworks, and distributed agent ecosystems.

OKPF is infrastructure-neutral. This document is technology-neutral. No specific agent framework, LLM provider, or robotics platform is required or assumed.

---

## Framing: Portable Expertise Infrastructure

Knowledge packs are not merely training data formats. They are **portable expertise infrastructure** — structured knowledge bundles that autonomous systems can discover, negotiate over, and execute against, without depending on any centralized authority or specific runtime.

The closest analogies from software:
- A **package registry** (npm, PyPI) distributes code packages to many runtimes.
- An **OCI container** carries a complete, self-describing execution environment.
- A **Git repository** provides a versioned, attributable, inspectable knowledge store.

OKPF occupies an analogous role for *structured human expertise* — providing a standard unit of knowledge that multiple autonomous systems can consume, independent of their internal architecture.

---

## Autonomous System Interaction Model

### Discovery

An autonomous system discovers relevant packs through:
- A local filesystem or archive path
- A pack registry (not standardized by OKPF; registries are out of scope for the core format)
- A dependency declaration in another pack's `dependencies` field
- Direct provision by a human operator or orchestration layer

### Negotiation

Before loading any content, a system reads the manifest to determine fit:

```
read manifest.json
  → check capabilities[]       # does this pack support the needed task?
  → check ai.modalities[]      # can this system handle the content types?
  → check ai.risk_level        # is this within acceptable risk bounds?
  → read license.json          # is the intended use permitted?
  → check trust.*              # does this pack meet trust requirements?
```

If any check fails, the system can reject the pack without loading content. This keeps the negotiation lightweight.

### Execution

After negotiation, execution depends on the pack's declared capabilities:
- `retrieval` → chunk, embed, and index content artifacts
- `workflow-execution` → parse and execute task artifacts
- `evaluation` → run evaluation cases against a knowledge base or model
- `fine-tuning` → extract and format training examples
- `robotics` → load sensing and procedure knowledge into a robot's knowledge base

### Attribution propagation

When an autonomous system uses pack content to produce output, it should propagate attribution:
- Cite the pack ID and version in any output that draws on pack content
- Pass the license `attribution_text` forward when redistributing derived content
- Record the pack ID and artifact ID in any training data derived from the pack

---

## Orchestration Frameworks

Multi-agent systems often include an **orchestrator** — a system that delegates tasks to specialized agents. OKPF packs are well-suited to this model:

```
Orchestrator
├── receives task: "diagnose engine fault"
├── queries pack registry for packs with capabilities: ["diagnostics"]
├── selects pack: "mechanic-diagnostics:v1.2.0"
├── loads manifest, verifies trust requirements
├── delegates to DiagnosticsAgent:
│   ├── provides: pack content as context
│   ├── provides: workflow artifact for structured procedure
│   └── provides: evaluation cases for answer verification
└── receives: structured diagnosis with citations
```

The orchestrator does not need to know how the DiagnosticsAgent works internally — only that it accepts an OKPF pack and returns structured output. This is the interoperability benefit: knowledge exchange is mediated by the pack format, not by agent-specific APIs.

### Capability-based dispatch

```python
def dispatch(task_type, available_packs):
    capability_map = {
        "answer_question":    "retrieval",
        "execute_procedure":  "workflow-execution",
        "run_benchmark":      "evaluation",
        "train_component":    "fine-tuning",
        "diagnose_fault":     "diagnostics",
        "simulate_scenario":  "simulation",
    }
    
    required_cap = capability_map.get(task_type)
    if not required_cap:
        raise ValueError(f"Unknown task type: {task_type}")
    
    eligible = [p for p in available_packs if required_cap in p.capabilities]
    return select_best(eligible, task_type)
```

---

## Workflow Chaining

Complex autonomous tasks often require multiple sequential knowledge operations. OKPF's `dependencies` field supports this:

```json
{
  "id": "urn:okpf:brewing:advanced-recipes:1.0.0",
  "dependencies": [
    { "id": "urn:okpf:brewing:water-chemistry:0.1.0" },
    { "id": "urn:okpf:brewing:yeast-biology:0.2.0" }
  ]
}
```

An agent framework that loads the `advanced-recipes` pack can recursively resolve dependencies and compose a complete knowledge context before starting task execution.

### Workflow composition

Individual workflow artifacts (conforming to `task.schema.json`) can be chained:
- The `outputs` of one workflow become the `inputs` of the next.
- A workflow that produces `{ "target_water_profile": "Burton" }` as output feeds into a workflow whose input is `{ "id": "profile", "type": "text" }`.
- The branching `next_step` conditions in task artifacts enable dynamic routing based on intermediate results.

---

## Evaluation Loops

Autonomous systems that both consume and produce knowledge benefit from closed-loop evaluation:

```
Load pack
    ↓
Ingest content into agent knowledge base
    ↓
Run pack evaluations against the agent
    ↓
Score results against expected answers
    ↓
If below threshold: flag for human review, adjust retrieval, or reject pack
    ↓
Proceed to task execution
```

This loop is entirely local — it does not require any external service. The evaluations travel with the pack, making quality verification reproducible across environments and agents.

### Continuous quality monitoring

For long-running agents that maintain a knowledge base across many packs:

1. Track evaluation pass rates per pack over time.
2. Re-run evaluations when a pack is updated to a new version.
3. Alert when a pack upgrade degrades evaluation pass rates (regression detection).
4. Use evaluation scores as a confidence signal when retrieval ranks multiple sources.

---

## Trust-Aware Retrieval

An agent that retrieves knowledge from multiple packs must handle differing trust levels:

| Trust state | Signal | Recommended behavior |
|------------|--------|---------------------|
| Signed + verified contributors | `trust.signed: true`, `trust.verified_contributors: true` | Use with high confidence; cite |
| Provenance complete, unsigned | `trust.provenance_complete: true` | Use with standard confidence |
| No provenance, no signature | All trust fields absent/false | Use with caution; do not cite without review |
| Evaluations pass | Pack evaluations run and passing | Increases confidence regardless of trust fields |

Trust weighting should be transparent. When an agent produces output that draws on pack content, it should be possible to explain why specific packs were weighted as they were.

---

## Robotics

### Knowledge loading

A robot's onboard knowledge system can load OKPF packs at startup or over a local network. Once loaded, the pack is available offline — a critical requirement for physical systems that may operate in connectivity-limited environments.

Typical knowledge categories for robotics packs:
- **Perception knowledge** — what sensor readings mean, how to classify observations
- **Action knowledge** — how to perform physical procedures, with safety conditions
- **Environment knowledge** — maps, object properties, spatial relationships
- **Fault knowledge** — failure mode signatures and recovery procedures

### Procedure execution

A robot executing a manipulation task can use a workflow artifact as its task plan:
- `inputs` map to perceived environment state (object position, joint angles, force readings)
- `steps` map to primitive robot actions or sub-task invocations
- `next_step` branching conditions map to sensor checks between actions
- `outputs` map to success/failure reports and state updates

### Edge and embedded operation

OKPF packs are static archives — they do not require a running server or cloud connection. An embedded system with sufficient storage can carry its complete knowledge base as a set of `.kpack` files and operate fully air-gapped.

---

## Simulation Environments

Simulation systems benefit from OKPF packs in two ways:

1. **Environment definition** — packs that describe the physical, behavioral, or logical properties of a simulated environment. A simulation engine can load these to initialize a consistent environment state.

2. **Agent policy** — packs that define decision policies for simulated agents. An agent in a simulation draws on pack knowledge to make decisions, with evaluations serving as unit tests for the simulation's behavioral correctness.

---

## Future Integration Patterns

### MCP (Model Context Protocol) adapters

A thin adapter that wraps an OKPF pack as an MCP resource would allow any MCP-compatible agent to:
- List pack content as browsable resources
- Retrieve artifact content on demand
- Execute workflow artifacts as MCP tools
- Run evaluation cases as structured prompts

This adapter pattern requires no changes to the OKPF format — it is a translation layer. The adapter reads OKPF's standard manifest and exposes it through MCP's standard protocol.

### Local agent integration

Local agents (running entirely on a single machine without cloud services) benefit from OKPF packs because:
- Packs are self-contained — no API calls required
- The format is implementation-agnostic — works with any local model
- Pack content can be pre-processed (chunked, embedded) once and reused across many sessions
- Versioned packs allow reproducible knowledge states

### Distributed agent ecosystems

In a multi-agent system where different agents specialize in different domains, OKPF packs serve as the knowledge exchange protocol:

```
Agent A (brewing domain expert)
    publishes:   urn:okpf:brewing:water-chemistry:1.0.0
    
Agent B (recipe generation)
    consumes:    urn:okpf:brewing:water-chemistry:1.0.0
    depends_on:  urn:okpf:brewing:yeast-biology:0.3.0
    publishes:   urn:okpf:brewing:ipa-recipes:0.1.0

Agent C (quality assurance)
    evaluates:   any pack with capabilities["evaluation"]
    reports:     evaluation scores to registry
```

No agent needs to know the other's internal architecture. Knowledge flows through pack IDs and capability declarations.

### Compute-to-data patterns

For privacy-sensitive or proprietary knowledge, a future OKPF extension could define packs whose content is never transmitted in plaintext. Instead:
1. A consuming system sends a computation request (a query, a model, an evaluation function).
2. The knowledge-holding system executes the computation locally against the pack content.
3. Only the result is returned — the raw pack content never leaves its origin.

This pattern is common in federated machine learning and privacy-preserving analytics. OKPF's format separation between knowledge structure and content makes it a natural target for this approach.

---

## Design Principles for Agent Interoperability

These principles should guide any system that integrates with OKPF:

1. **Parse the manifest first.** Never assume pack contents — always derive them from the manifest.
2. **Respect capabilities declarations.** Do not force a pack into a role it does not declare.
3. **Check the license before acting.** `scope.ai_training`, `scope.use`, and `scope.redistribution` must be checked before any consumption mode.
4. **Propagate attribution.** Any output derived from pack content should carry the pack ID and attribution text.
5. **Use evaluations.** Running available evaluations is the primary quality check; do not skip it for production use.
6. **Treat trust as advisory.** Trust signals inform weighting; they are not binary access controls.
7. **Remain implementation-neutral.** Build adapters, not dependencies — translate between OKPF and your runtime rather than making OKPF depend on your runtime.
8. **Preserve unknown fields.** Forward compatibility requires that unrecognized manifest fields are kept, not discarded, when re-serializing.
