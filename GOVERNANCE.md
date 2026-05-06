# OKPF Governance

This document describes how the Open Knowledge Pack Format project is governed, how decisions are made, and how contributors can participate in shaping the spec.

---

## Principles

OKPF governance is guided by:

- **Openness** — Decisions are made in public. Rationale is documented. Anyone can participate.
- **Meritocracy** — Influence is earned through sustained, quality contribution — not by affiliation or seniority.
- **Neutrality** — No single organization, vendor, or technology stack controls the direction of the spec. OKPF belongs to its community.
- **Stability** — Breaking changes are rare, deliberate, and clearly communicated. Consumers can rely on OKPF.
- **Pragmatism** — Governance serves the project, not the other way around. Lightweight process where possible; more rigor where stakes are high.

---

## Project History and Founding

OKPF was initiated by **Charles Toepfer** as an open effort to develop a portable, vendor-neutral standard for packaging structured human expertise for AI systems and future computational tools. From the outset, the project was designed to be community-driven, openly governed, and independent of any single organization or technology platform.

As the project matures and the contributor base grows, governance authority will migrate progressively from the founding maintainer toward the broader community.

---

## Roles

### Contributors

Anyone who opens an issue, submits a pull request, improves documentation, writes an example, or participates constructively in discussion is a **contributor**. No formal registration is required.

### Maintainers

**Maintainers** are contributors who have demonstrated sustained, high-quality participation and have been given write access to the repository. Maintainers:

- Review and merge pull requests
- Triage issues
- Participate in spec change decisions
- Represent the project in external discussions

The current maintainer list is in [AUTHORS.md](AUTHORS.md).

### Founding Maintainer

The **founding maintainer** (currently Charles Toepfer) has final decision authority during the project's early stage. This role exists to ensure consistency and momentum while the governance process matures. As the project grows, final authority will shift to collective maintainer consensus.

---

## Decision-Making

Most decisions — bug fixes, documentation improvements, new examples, tooling — are made through the normal pull request process: someone proposes a change, reviewers discuss it, and a maintainer merges it when consensus is reached.

For significant decisions, OKPF uses a tiered change classification (see below). Higher-tier changes require more deliberation and broader consensus.

### Consensus Model

Decisions are made by **lazy consensus**: a change moves forward if no maintainer objects within a reasonable review window (typically 7 days for Tier 1–2 changes, 14 days for Tier 3–4). Objections must be substantive — they should explain what would break or what principle is violated, not just express preference.

If consensus cannot be reached, the founding maintainer breaks the tie (until a more formal voting process is adopted when the maintainer group is large enough).

---

## Spec Change Tiers

Changes to the OKPF specification are classified into four tiers:

| Tier | Type | Examples | Process |
|------|------|---------|---------|
| **1** | Clarification | Fixing ambiguous spec language, adding examples, correcting errors in documentation | PR + one maintainer approval |
| **2** | Additive | New optional fields, new capability enum values, new artifact roles | PR + two maintainer approvals + 7-day review window |
| **3** | Required field addition | Making a previously optional field required, adding new required fields | GitHub Discussion + RFC comment period (14 days minimum) + majority maintainer approval |
| **4** | Breaking change | Removing fields, renaming required fields, changing enum semantics, changing $id of a schema | GitHub Discussion + RFC comment period (30 days minimum) + version bump + migration guide required |

Breaking changes (Tier 4) increment the minor or major version of the OKPF spec and are made only when the benefit is clear and migration is tractable.

### RFC Process (Tier 3–4)

1. Open a GitHub Discussion tagged `[RFC]` describing the motivation, proposed change, and alternatives considered.
2. Allow the minimum comment period for community feedback.
3. Summarize the feedback and propose a resolution in the Discussion thread.
4. If consensus is reached, open a pull request implementing the change, referencing the Discussion.
5. Merge requires explicit approval from a majority of active maintainers.

---

## Becoming a Maintainer

There is no formal application. Maintainers are invited based on demonstrated contribution. Criteria include:

- Sustained participation over at least 2–3 months
- High-quality pull requests or reviews
- Constructive, collegial engagement in issues and discussions
- Understanding of OKPF's design principles and neutrality goals

Any existing maintainer can nominate a contributor. The nomination is discussed privately among maintainers; the candidate is invited if there are no objections.

Maintainers who are inactive for 6+ months may be moved to **emeritus** status. Emeritus maintainers retain credit in AUTHORS.md but do not have write access or decision authority.

---

## Security Issues

Security vulnerabilities should be reported privately before public disclosure. See [SECURITY.md](SECURITY.md) (or open a private GitHub security advisory) with details. Maintainers will acknowledge within 72 hours and aim to resolve within 14 days.

Do not open public issues for security vulnerabilities.

---

## Code of Conduct

All participants in the OKPF project are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Maintainers are responsible for enforcement.

---

## Amendments to This Document

Governance changes are Tier 3 decisions: they require a GitHub Discussion, a minimum 14-day comment period, and majority maintainer approval. Substantive changes to this document should be explained in the PR description with reference to the Discussion thread.

---

## Long-Term Stewardship

OKPF is designed to outlast any individual contributor or organization. If the project ever needs to transition stewardship (e.g., to a foundation or neutral standards body), the community will be consulted and the process will be transparent and deliberate.

The goal is a format that is useful, durable, and community-owned — not controlled by the organization or individuals who started it.
