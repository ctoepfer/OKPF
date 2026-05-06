# Provenance in OKPF

Provenance answers the question: *where did this knowledge come from, and how did it get here?*

This document explains the OKPF provenance model, why it matters, and how to use it effectively.

---

## Why Provenance Matters

A piece of knowledge is only as trustworthy as its source. Without provenance:

- You can't evaluate whether a claim is expert opinion or folk wisdom
- You can't trace a piece of knowledge back to its original context
- You can't detect when knowledge has been distorted through retelling
- You can't identify who is responsible when knowledge turns out to be wrong

OKPF treats provenance as a first-class concept — not just an optional metadata field, but a core part of what makes a knowledge pack trustworthy.

---

## The Provenance Model

OKPF provenance is built from two concepts:

### Sources

A **source** is an original input from which content in the pack was derived. Sources can be:

| Type | Examples |
|------|---------|
| `original` | Content created directly for this pack, from scratch |
| `interview` | A recorded or transcribed expert interview |
| `publication` | A book, paper, article, or specification |
| `dataset` | An existing dataset or reference table |
| `observation` | Direct observation or measurement |
| `derived` | Content derived from another source |

Each source can carry:
- A URI (URL, DOI, or internal reference)
- An access date
- A SHA-256 hash of the source content at time of capture
- Its own license declaration

### Transformations

A **transformation** records a step in the process of turning source material into pack artifacts. Transformations can be:

| Type | Examples |
|------|---------|
| `manual` | A human writing or editing content |
| `automated` | A script or tool extracting or converting content |
| `review` | A subject-matter expert verifying accuracy |
| `translation` | Language translation |
| `summarization` | Condensing a longer source |
| `extraction` | Pulling specific facts or structures from a source |
| `curation` | Selecting and organizing content |

Each transformation records:
- Which sources were inputs
- Which pack artifacts were outputs
- Who performed the transformation (contributor ID)
- When it was performed
- What tool was used (for automated steps)
- Who reviewed the result (for review steps)

---

## Example Provenance Record

```json
{
  "created_by": "expert-jane",
  "created_at": "2026-03-01T00:00:00Z",
  "sources": [
    {
      "id": "src-interview-01",
      "type": "interview",
      "title": "Interview with Jane Smith, Master Brewer",
      "accessed": "2026-02-15",
      "description": "Recorded 60-minute interview on water chemistry."
    },
    {
      "id": "src-palmer-water",
      "type": "publication",
      "title": "Water: A Comprehensive Guide for Brewers",
      "uri": "https://www.brewerspublications.com/products/water",
      "license": "LicenseRef-commercial",
      "description": "Used as background reference; no content copied."
    }
  ],
  "transformations": [
    {
      "id": "tx-interview-transcription",
      "type": "manual",
      "input_sources": ["src-interview-01"],
      "output_artifacts": ["transcript"],
      "performed_by": "editor-bob",
      "performed_at": "2026-02-20T00:00:00Z",
      "description": "Manual transcription and lightly edited for clarity."
    },
    {
      "id": "tx-guide-authoring",
      "type": "manual",
      "input_sources": ["src-interview-01", "src-palmer-water"],
      "output_artifacts": ["guide"],
      "performed_by": "expert-jane",
      "performed_at": "2026-03-01T00:00:00Z",
      "reviewed_by": "reviewer-carlos",
      "description": "Guide written from interview notes and personal expertise."
    }
  ]
}
```

---

## Provenance and AI-Assisted Content

If any pack content was generated or assisted by AI tools (e.g., a draft was written by an AI and reviewed by an expert), this should be captured in the transformation record:

```json
{
  "id": "tx-ai-draft",
  "type": "automated",
  "tool": "claude-3.7-sonnet",
  "tool_version": "claude-3-7-sonnet-20250219",
  "output_artifacts": ["guide-draft"],
  "performed_at": "2026-03-01T00:00:00Z",
  "description": "Initial draft generated from interview notes."
},
{
  "id": "tx-expert-review",
  "type": "review",
  "input_sources": ["src-interview-01"],
  "output_artifacts": ["guide"],
  "performed_by": "expert-jane",
  "performed_at": "2026-03-05T00:00:00Z",
  "description": "Expert reviewed and corrected AI-generated draft."
}
```

OKPF does not prohibit AI-assisted content. It requires honest recording of how content was produced.

---

## Provenance and Trust

Provenance records are only as reliable as the people who write them. OKPF cannot technically enforce that provenance is accurate. What OKPF provides is:

1. A structured place to record provenance
2. Schema validation to ensure records are well-formed
3. Optional cryptographic signatures that can sign the provenance record
4. A norm that "no provenance declared" is a signal to consumers

Communities and registries can establish norms around provenance quality — for example, requiring peer-reviewed packs to have transformation records with named reviewers.

---

## Relation to W3C PROV

OKPF's provenance model is inspired by [W3C PROV-O](https://www.w3.org/TR/prov-o/) — specifically the concepts of `Entity`, `Activity`, and `Agent`. OKPF simplifies this model for practical use:

| W3C PROV | OKPF |
|----------|------|
| `Entity` | Source or content artifact |
| `Activity` | Transformation |
| `Agent` | Contributor |
| `wasDerivedFrom` | Transformation `input_sources` → `output_artifacts` |
| `wasGeneratedBy` | Transformation record |
| `wasAssociatedWith` | Transformation `performed_by` |

OKPF does not require RDF, SPARQL, or any semantic web infrastructure. The JSON representation is designed to be readable and writable by humans and simple tools.
