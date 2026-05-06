# Example Pack: Software Architecture Patterns (Placeholder)

**Domain:** Software Engineering  
**Status:** Placeholder — contributions welcome

---

## About This Pack (Planned)

This knowledge pack will encode expert-level software architecture knowledge — not just definitions, but the reasoning, trade-offs, and context-sensitivity that distinguishes experienced architects from those who have merely read the patterns catalog.

## Planned Content

- **Architectural patterns with trade-off analysis** — When to use each pattern, when NOT to use it, and why
- **Decision frameworks** — How to choose between competing approaches given specific constraints
- **Case studies** — Real-world architectural decisions with reasoning (anonymized)
- **Anti-patterns** — Common architectural mistakes and how to recognize them early
- **Evaluation test cases** — Architecture scenario questions with expected reasoning

## Example Topics

- Monolith vs. microservices (and the spectrum between)
- Event-driven architecture trade-offs
- Data consistency patterns (eventual vs. strong consistency)
- API design principles (REST, GraphQL, gRPC — when to use each)
- Distributed systems failure modes
- Observability architecture
- Security architecture patterns (zero trust, defense in depth)
- Scaling strategies (horizontal, vertical, database sharding)

## How to Contribute

If you have software architecture expertise and want to contribute, see [CONTRIBUTING.md](../../CONTRIBUTING.md).

Strong contributions include:
1. A pattern analysis with real trade-off reasoning (not textbook summaries)
2. A decision tree for choosing between architectural options
3. A case study from your own experience (anonymized as needed)
4. Evaluation questions that test architectural judgment, not just recall

## Pack Structure (When Complete)

```
software-architecture/
├── manifest.json
├── license.json
├── contributors.json
├── provenance.json
├── content/
│   ├── patterns/
│   │   ├── microservices.md
│   │   ├── event-driven.md
│   │   └── cqrs-event-sourcing.md
│   ├── decision-frameworks/
│   │   └── monolith-vs-microservices.json
│   └── anti-patterns/
│       └── distributed-monolith.md
└── evaluations/
    └── scenario-tests.json
```
