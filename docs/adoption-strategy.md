<!-- SPDX-License-Identifier: Apache-2.0 -->

# OKPF Adoption Strategy — v0.1

This document is blunt and practical. OKPF v0.1 must prove usefulness through a small number of realistic workflows before making broad standardization claims.

The core spec can remain general. The early adoption push must be narrow, testable, and measurable.

Early adoption should:

- Start with narrow examples.
- Prove value against loose folders and ad hoc metadata.
- Focus on Git-friendly packs.
- Prioritize examples and validators over governance complexity.
- Benchmark where practical.
- Seek feedback from real users before adding optional layers.

---

## Purpose

OKPF is at the point where philosophical completeness is no longer the constraint. The constraint is adoption evidence.

The format must demonstrate value against alternatives that are already working: plain Markdown folders, YAML front-matter conventions, JSONL datasets, internal RAG ingestion schemas, and established archival formats. If OKPF cannot beat those alternatives in a few clear scenarios, the project should pivot rather than accumulate more specification.

This document describes the initial adoption thesis, target verticals, success criteria, and risks.

---

## Initial Target Verticals

Three verticals are recommended for initial validation. They were selected because they are realistic, do not require external partners to start, and represent distinct knowledge packaging problems.

---

### 1. Software Project Onboarding and Decision Logs

**Why OKPF may add value:**
- Onboarding knowledge is often scattered across wikis, READMEs, and informal notes with no provenance or version history.
- Decision rationale disappears when team members leave.
- RAG pipelines over plain wikis produce answers with no source traceability.
- OKPF records can link decisions back to a dated source, a named author, and a declared version.

**Existing alternatives:**
- Plain Markdown in a repo (Git history provides some version context).
- Confluence/Notion with internal search.
- ADR (Architecture Decision Records) in `docs/adr/` directories.
- GitHub Discussions and issue threads.

**What measurable improvement looks like:**
- A RAG query over an OKPF-packaged onboarding pack returns source-backed answers more reliably than the same query over the unpackaged folder.
- Attribution survives ingestion: the answering system knows which document and which author each fact came from.
- An update to a decision record produces a visible diff in the pack that a non-technical reviewer can audit in a pull request.

**Risks and limitations:**
- Teams that already have good ADR discipline may not gain much from OKPF.
- OKPF does not replace a wiki; it structures a snapshot of knowledge for distribution and reuse.
- Maintaining OKPF records alongside living documentation adds authoring overhead.

---

### 2. Local Organizational Knowledge Preservation

**Why OKPF may add value:**
- Small organizations (nonprofits, clubs, local government bodies) often have critical procedural knowledge that lives in one person's head or a single document nobody reviews.
- When that person leaves, the knowledge is lost.
- OKPF provides a portable, attributable, versioned container for board procedures, vendor contact SOPs, and decision history.
- The pack can be committed to a shared repo, attached to a release, or distributed via email — no infrastructure required.

**Existing alternatives:**
- Shared drives with unversioned files.
- Word/Google Docs with no licensing or attribution.
- Email threads.

**What measurable improvement looks like:**
- A pack validates cleanly against the OKPF schema, ensuring minimum structural quality.
- Records include a named author and a dated source entry.
- A new volunteer can answer routine procedural questions by loading the pack, without requiring a knowledge transfer session.

**Risks and limitations:**
- Very small organizations may find even minimal OKPF overhead unnecessary.
- Packs become stale unless someone is responsible for maintaining them.
- OKPF cannot guarantee the knowledge is accurate — only that it is structured, attributed, and versioned.

---

### 3. Field Repair and Maintenance Checklists

**Why OKPF may add value:**
- Maintenance knowledge is high-stakes, must be versioned, and requires clear authorship (who approved this procedure, and when).
- Fault symptom records benefit from structured facets (fault category, severity, escalation level).
- Evaluation questions can be used to verify technician knowledge before they work on equipment.
- OKPF packs can be distributed offline to field technicians without requiring a live network connection.

**Existing alternatives:**
- Paper checklists or PDF manuals.
- Proprietary CMMS (Computerized Maintenance Management System) databases.
- Internal wikis with no version control.

**What measurable improvement looks like:**
- A technician or AI assistant can load the OKPF pack offline and answer diagnostic questions with full source traceability.
- An update to a fault symptom record is reviewable as a diff before deployment.
- The pack validates cleanly, confirming all declared files are present and all records have required fields.

**Risks and limitations:**
- OKPF is not a certified safety document format. Using it in life-safety contexts without additional certification is inappropriate.
- The format does not enforce compliance — it structures and attributes knowledge.
- Proprietary CMMS systems are deeply entrenched in industrial maintenance contexts.

---

### Additional Domain: Fermentation and Manufacturing Compliance

The fermentation profile (`profiles/fermentation/v0.1.0/`) is a mature example domain with real ingestion experience. Brewing, wine, mead, and cider knowledge packs have demonstrated that the format works for structured domain data with controlled vocabularies, facets, and multi-source provenance. This domain continues to serve as a reference implementation for profiles.

It is not a Core vertical. It demonstrates how a domain-specific profile can work without modifying OKPF Core.

---

## Adoption Thesis

OKPF is most likely to be adopted if it helps teams with specific, measurable problems:

| Problem | How OKPF helps |
|---------|----------------|
| Attribution disappears after ingestion | Every record includes `id`, domain, and metadata; every artifact has a declared path; provenance links artifacts to sources |
| Source-to-record lineage is lost | The `provenance/sources.json` pattern explicitly links records to their origins |
| RAG ingestion is ambiguous | A validated OKPF pack provides a structured boundary that a loader can inspect before ingesting |
| Examples and evaluations are separated from knowledge | Evals live alongside the records in the same pack |
| Knowledge is locked to a vendor tool | A `.kpack` is a standard ZIP; any tool can read it |
| Version history is unclear | Pack version is declared in `manifest.json`; packs live in Git |

OKPF is unlikely to be adopted through philosophical persuasion. Adoption requires that users run the validator on their own knowledge, see fewer ambiguities, and prefer the packaged form over their current approach for at least one concrete workflow.

---

## Proof Before Expansion

OKPF should prove value through small, measurable examples before adding optional layers.

Success criteria:

- A user can validate and inspect a pack without asking the author.
- A RAG ingestion workflow can preserve source/provenance metadata.
- A training-ready derivative can be traced back to source artifacts.
- A profile can add useful domain conventions without changing OKPF Core.
- A pack can be reviewed as plain files in Git.
- A physical skill evidence pack can state transfer claims and non-claims clearly enough to prevent overstatement.

## Candidate Benchmarks

These are proposed benchmarks, not claimed results:

- Loose Markdown folder vs OKPF pack for RAG source traceability.
- Source records vs training-ready derivative traceability.
- Physical Skill Evidence pack clarity: can a reviewer identify what is claimed, not claimed, and validated?
- Fermentation profile: can profile validation catch missing required domain context better than Core validation alone?

---

## Non-Adoption Risks

These are real risks. They should be acknowledged, not minimized.

**Vendor indifference.** Large RAG vendors (LangChain, LlamaIndex, OpenAI, etc.) may build their own internal schemas and ignore OKPF. If they do, adoption will be slow regardless of format quality.

**Plain Markdown preference.** Many engineers will prefer a flat Markdown folder over any schema. If OKPF's value proposition does not clearly outperform plain folders in at least one measurable way, this preference will persist.

**Internal schema lock-in.** Enterprise teams often already have internal schemas for structured knowledge. OKPF must provide a clear migration path or interoperability argument.

**Attribution weakening downstream.** Once a pack is ingested into a vector database, summarized by a model, or distilled into a derivative, attribution information is frequently lost. OKPF improves attribution at the source; it cannot guarantee persistence after ingestion.

**Licensing metadata without enforcement.** `usage_policy` and `license` fields declare intent. They do not technically enforce restrictions. A consumer that ignores them faces no technical barrier, only legal and ethical ones.

**Profile fragmentation.** If many profiles emerge with incompatible conventions, the ecosystem fragments. Core OKPF validators remain useful, but profile-level interoperability deteriorates.

**Authoring overhead.** Every additional required field or schema check is a friction cost. If OKPF feels bureaucratic, adoption will stall.

**Commoditization acceleration.** Packaging and distributing expert knowledge more cleanly may make it easier to extract, summarize, and commoditize. OKPF improves the packaging; it does not prevent the economic dynamics of knowledge distribution.

---

## Success Metrics (6–9 months)

These are goals, not guaranteed outcomes. They represent the minimum evidence that would distinguish OKPF from another ignored open standard.

1. **At least 3 independent external projects** are experimenting with OKPF packs — not necessarily in production, but in a real workflow.

2. **At least 1 non-author project** is using OKPF for real documentation or RAG ingestion, with published results or public feedback.

3. **Benchmark evidence** exists showing OKPF improves at least one measurable property over simpler alternatives (see `docs/benchmark-plan.md`).

4. **At least one external tool or script** reads OKPF packs — a loader, a viewer, a CI validator, or a converter.

5. **Clear user feedback** on whether OKPF beats plain folders for at least one use case, collected through issues, discussions, or direct contact.

6. **The "When Not to Use OKPF" document** has been read and cited in at least one external context — indicating that the project's scope limitations are understood and respected.

## Success Means

- A developer can validate and inspect a pack without asking the author.
- A RAG pipeline can preserve source and provenance metadata during ingestion.
- A training derivative can be traced back to source records or artifacts.
- A domain profile can add useful conventions without changing OKPF Core.
- A pack remains useful as plain files in Git.
- A physical skill evidence pack can state transfer claims and non-claims clearly enough to prevent overstatement.

---

## What Happens If These Goals Are Not Met

If after 6–9 months, none of these criteria are approaching, the project should pivot:

- Narrow to a single domain profile and abandon the general-purpose Core claim.
- Adopt an existing archival format (RO-Crate, BagIt) as the container and contribute OKPF-style metadata as an overlay schema.
- Retire the project and document lessons learned.

This document is not pessimistic about OKPF's potential. It is realistic about the conditions under which a new open standard can achieve adoption.

---

## See Also

- [docs/benchmark-plan.md](benchmark-plan.md) — measurable comparison against simpler alternatives
- [docs/when-not-to-use-okpf.md](when-not-to-use-okpf.md) — clear scope boundaries
- [docs/git-native-workflow.md](git-native-workflow.md) — preferred early distribution approach
- [docs/v0.1-conformance.md](v0.1-conformance.md) — conformance levels
