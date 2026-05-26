<!-- SPDX-License-Identifier: Apache-2.0 -->

# When Not to Use OKPF

OKPF is a structured knowledge packaging format. It adds value when packaging, attribution, provenance, versioning, and reuse matter. It does not add value when those properties are unnecessary overhead.

This document is intentionally direct. It is also honest about the limits of what OKPF can accomplish.

---

## Cases Where OKPF Is Probably Not Worth It

### A single private note file

If you have one Markdown file that you use privately and do not intend to share, validate, attribute, or reuse, OKPF adds no value. A plain `.md` file is sufficient.

### Throwaway prompts and ephemeral context

Prompts you type once, context windows you discard, and scratch notes that will be deleted tomorrow do not benefit from packaging, attribution, or licensing. OKPF is for knowledge you intend to preserve, version, and potentially share.

### Simple Markdown documentation with no reuse need

A project README, a quick API reference, or internal meeting notes that will never leave your team's wiki do not need OKPF structure. If no one will ever import, validate, or reuse the content as a package, the format adds friction without benefit.

### Knowledge that changes too rapidly to maintain

If the underlying knowledge changes daily and the pack would be stale before it is used, the overhead of maintaining accurate records, provenance, and versioning outweighs the benefit. Consider whether a live document or database is more appropriate.

### Highly sensitive or private data with no distribution plan

If data is confidential and will never be distributed outside your organization, there is no structural benefit to packaging it in an open format. OKPF does not add access control or encryption. A restricted internal system is more appropriate for sensitive data.

### Domains where existing standards are sufficient and well-adopted

If your domain already has a well-adopted standard format — SCORM for e-learning, BeerXML for brewing recipes, HL7/FHIR for clinical data — and your goal is single-domain exchange, use that standard. OKPF adds value when you need general-purpose packaging, portability, attribution, or cross-domain reuse on top of those formats, not as a replacement for them.

### Provenance and attribution genuinely do not matter

Some knowledge is effectively public domain, has no authorship question, and will never be redistributed in a form where source matters. For that knowledge, the `creators`, `provenance`, and `usage_policy` fields in OKPF are overhead without benefit.

### Cases where licensing metadata is expected to enforce itself

OKPF `license` and `usage_policy` fields express intent. They do not technically restrict access. If your licensing model requires technical enforcement — DRM, access tokens, encrypted content — OKPF does not provide those mechanisms. It provides metadata that enforcement layers can act on; it is not itself an enforcement layer.

### Certification-dependent contexts

If your use case requires certified technical procedures, medical protocols, legally binding compliance records, or safety-critical documentation where OKPF metadata would need to be treated as authoritative, be careful. OKPF validation confirms structure and declared integrity; it does not confirm factual correctness, professional certification, regulatory compliance, or fitness for a specific purpose.

---

## OKPF Is Not a Moat

This deserves its own section.

Once knowledge is distributed in any form — including as an OKPF pack — control weakens. A recipient can:

- Copy the pack and strip the license metadata.
- Ingest it into a RAG system and query it without attribution.
- Summarize it with a language model, producing a derivative that loses provenance.
- Distill it into a smaller model that contains the knowledge without citing the source.

OKPF can improve attribution and provenance at the point of packaging and at the point of ingestion by conformant tools. It cannot guarantee that attribution persists through all downstream transformations, summaries, or uses.

Licensing fields state the author's intent. In jurisdictions and contexts where that intent has legal weight, it matters. In others, or in practice, it may not be enforced.

The same is true of all open format standards. Being clear about this is not defeatist — it is honest. OKPF's value is in improving the starting conditions for knowledge sharing: structured, attributed, versioned, and with explicit license terms. What happens after distribution depends on the people and systems involved, not on the format.

---

## What OKPF Is Actually Useful For

To balance the above: OKPF is useful when you want to:

- Preserve authorship and source lineage across distribution.
- Package structured knowledge with evaluations for quality checking.
- Make ingestion decisions (What is the license? What domain is this? What records are present?) answerable without scanning the content.
- Move knowledge between tools without vendor lock-in.
- Maintain a versioned history of a body of expertise in a Git-compatible format.
- Demonstrate to a recipient that content is structured, validated, and traceable.

If those goals matter for your use case, OKPF is worth evaluating. If they do not, use a simpler approach.

---

## See Also

- [docs/adoption-strategy.md](adoption-strategy.md) — where OKPF may add value
- [docs/benchmark-plan.md](benchmark-plan.md) — measurable comparisons against simpler alternatives
- [docs/v0.1-conformance.md](v0.1-conformance.md) — what conformance means and does not mean
- [docs/security.md](security.md) — security model and limitations
