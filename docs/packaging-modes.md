<!-- SPDX-License-Identifier: Apache-2.0 -->
# OKPF Packaging Modes

OKPF is a packaging format, not a replacement for domain formats. This document describes three ways to use OKPF depending on what knowledge you are packaging and what formats already exist for it.

**Central principle:** OKPF can add value around a domain format without becoming that domain format.

OKPF is not always the internal data format. In some packs OKPF records and artifacts are the primary representation. In others OKPF is a thin envelope around a mature domain artifact. In many real-world packs it is both.

---

## Overview

| Mode | When to use | Domain format role | OKPF records role |
|------|-------------|-------------------|-------------------|
| [Native](#native-mode) | Knowledge is naturally textual, procedural, or record-shaped | None | Primary and authoritative |
| [Envelope](#envelope-mode) | A mature domain format already exists and must remain authoritative | Preserved in `sources/` as domain artifact | Optional or absent |
| [Hybrid](#hybrid-mode) | Domain artifact must stay intact, but normalized records also add value | Preserved in `sources/` as domain artifact | Derived alongside |

None of these modes require changes to OKPF Core schemas or new required manifest fields.

---

## Native Mode

In Native Mode, OKPF records and artifacts are the primary and authoritative representation of the knowledge. The pack does not depend on any external domain format. Knowledge is authored directly as OKPF records, Markdown artifacts, checklists, decision logs, examples, and evaluations.

**Best for:**

- Software project onboarding packs
- Organizational knowledge and decision-log packs
- SOP and checklist packs
- Training and documentation packs
- Local knowledge archives
- Field repair and diagnostic guides

Native Mode is appropriate when the knowledge is naturally represented as documents, records, checklists, notes, examples, and evaluations — and when no mature, widely-deployed domain format already dominates the space.

### Typical manifest structure

```json
{
  "okpf_version": "0.1.0",
  "package_id": "my-org-knowledge",
  "name": "My Organization Knowledge",
  "version": "1.0.0",
  "domain": "organizational-knowledge",
  "license": { "type": "CC-BY-4.0" },
  "artifacts": [
    { "path": "artifacts/procedures.md", "type": "text/markdown", "role": "guide" }
  ],
  "records": [
    { "path": "records/decisions.jsonl", "format": "jsonl" }
  ]
}
```

### When to choose Native Mode

- No existing structured format covers your knowledge domain well.
- The knowledge is procedural, textual, or record-shaped.
- Downstream consumers will use OKPF records without needing a separate domain format.
- You want to author and maintain knowledge in OKPF directly.

---

## Envelope Mode

In Envelope Mode, a mature domain format already exists and should remain the authoritative representation. OKPF wraps that artifact with package-level identity, provenance, licensing, usage policy, validation metadata, evaluation references, known limitations, profile declarations, and lineage. OKPF records are not required.

**OKPF does not redefine the wrapped format.** A BeerXML, Parquet, HDF5, ROS bag, FHIR bundle, ONNX model, or CAD file remains fully governed by its own format specification. OKPF adds the packaging layer around it.

**Best for:**

- BeerXML and MeadXML brewing recipes
- LeRobot, RLDS, and Robo-DM robotics datasets
- ROS bag files and robotics sensor logs
- HDF5 and Parquet scientific datasets
- FHIR health records and clinical bundles
- CAD, BIM, and GIS artifacts (IFC, DWG, GeoJSON, Shapefile)
- ONNX, PyTorch, and Safetensors model artifacts
- SCORM and xAPI training packages
- Any format where performance, loading compatibility, or ecosystem tooling depends on the native format

### What OKPF provides in Envelope Mode

| What OKPF adds | What it does not do |
|----------------|---------------------|
| Package identity and versioning | Parse or validate the domain artifact |
| Provenance (origin, authorship, transformations) | Re-encode the domain artifact |
| Attribution and contributor records | Understand domain-specific semantics |
| License terms | Replace domain tooling |
| Usage policy (RAG, fine-tuning, redistribution, commercial use) | Add format-specific required fields to Core |
| Validation metadata and evaluation references | Enforce correctness of domain content |
| Known limitations and expert notes | |
| Profile declarations | |
| Lineage back to primary sources | |

### Typical manifest structure

```json
{
  "okpf_version": "0.1.0",
  "package_id": "my-domain-pack",
  "name": "My Domain Pack",
  "version": "1.0.0",
  "domain": "your-domain",
  "license": { "type": "CC-BY-4.0" },
  "usage_policy": {
    "allow_rag": true,
    "allow_fine_tuning": false,
    "require_attribution": true,
    "notes": "The domain artifact is the authoritative representation. OKPF provides package context."
  },
  "sources": [
    {
      "path": "sources/domain-artifact.xml",
      "format": "your-domain-format",
      "role": "domain_artifact"
    }
  ],
  "dependencies": [
    {
      "name": "YourDomainFormat",
      "version": "1.0",
      "uri": "https://example.org/your-format-spec",
      "optional": true,
      "description": "Domain format used by the source artifact. Consumers that cannot read this format can still use OKPF package metadata."
    }
  ]
}
```

### When to choose Envelope Mode

- A mature domain format exists with its own tooling ecosystem.
- Performance, loading compatibility, or ecosystem compatibility requires the native format.
- The domain format must remain the authoritative source of truth.
- You do not want to maintain a second representation of the same content.
- You want to add provenance, license, and usage policy without altering the artifact.

---

## Hybrid Mode

In Hybrid Mode, a domain artifact remains authoritative and is preserved intact in `sources/`, while normalized OKPF records coexist in `records/`. Tools choose which representation to use based on their capabilities. Systems that understand the domain format use the source artifact. Systems that use OKPF records (RAG pipelines, evaluation harnesses, review tools) use the derived records.

Hybrid Mode will likely be the most common advanced use case. Most real-world knowledge exists in some structured form, but many downstream consumers cannot read that form directly. Hybrid Mode preserves fidelity to the source while expanding accessibility.

**Best for:**

- BeerXML recipe + brewing SOP and process records
- Robotics dataset (LeRobot/ROS) + transfer claim and evaluation records
- Maintenance PDF + structured diagnostic checklist records
- Software repository README + architecture decision records
- CAD or BIM files + inspection, verification, or evaluation records
- ONNX or Safetensors model artifact + provenance, evaluation, and usage records
- Any case where source fidelity and downstream accessibility both matter

### Typical manifest structure

```json
{
  "okpf_version": "0.1.0",
  "package_id": "my-hybrid-pack",
  "name": "My Hybrid Pack",
  "version": "1.0.0",
  "domain": "your-domain",
  "license": { "type": "CC-BY-4.0" },
  "usage_policy": {
    "allow_rag": true,
    "notes": "The source artifact is authoritative. OKPF records are a normalized derived view."
  },
  "sources": [
    {
      "path": "sources/domain-artifact.xml",
      "format": "your-domain-format",
      "role": "domain_artifact"
    }
  ],
  "records": [
    {
      "path": "records/records.jsonl",
      "format": "jsonl",
      "record_count": 5
    }
  ]
}
```

### Provenance in Hybrid Mode

When OKPF records are derived from a domain artifact, the derivation SHOULD be documented in provenance so consumers can trace the lineage:

```json
{
  "sources": [
    {
      "source_id": "src-domain-artifact",
      "path": "sources/domain-artifact.xml",
      "format": "your-domain-format",
      "role": "domain_artifact"
    }
  ],
  "transformations": [
    {
      "description": "Normalized records extracted from domain artifact",
      "derived_from": "src-domain-artifact"
    }
  ]
}
```

### Keeping representations in sync

OKPF does not enforce synchronization between the domain artifact and derived records. If you update the domain artifact, you are responsible for regenerating or updating the OKPF records. Document this in `expert_notes.limitations`:

```json
"expert_notes": {
  "limitations": [
    "OKPF records are a derived view of the source artifact. Regenerate records when the source changes."
  ]
}
```

### When to choose Hybrid Mode

- A domain artifact must remain intact for domain-specific consumers.
- Normalized OKPF records improve accessibility for RAG, evaluation, or review systems.
- Both representations — the domain artifact and OKPF records — add value for different consumers.
- You are willing to maintain both (or generate OKPF records automatically from the domain artifact).

---

## Choosing a Packaging Mode

**Use Native Mode when:**

- The source knowledge is mostly textual or procedural.
- OKPF records and artifacts are a sufficient and natural representation.
- No mature domain format already dominates the space.

**Use Envelope Mode when:**

- A mature domain format already exists with its own schema, validation, and tooling.
- Performance or loading compatibility depends on the native format.
- The domain format must remain authoritative.
- OKPF mainly adds provenance, policy, lineage, and evaluation context around an artifact that domain consumers already know how to read.

**Use Hybrid Mode when:**

- Source artifacts need to remain intact for domain consumers.
- Normalized OKPF records improve retrieval, review, or evaluation for other consumers.
- Both the domain format and OKPF records add value, for different audiences.

A pack can evolve from one mode to another without breaking consumers. Envelope Mode packs can gain records (becoming Hybrid) without requiring new manifest fields. Native packs can add domain artifacts in `sources/` if the need arises later.

---

## Example Classification

The following table classifies all example packs in the repository by packaging mode. Only directories with a `manifest.json` are listed.

| Example | Packaging Mode | Why |
|---------|---------------|-----|
| [`examples/hello-world/`](../examples/hello-world/) | Native | One Markdown artifact; no domain format source |
| [`examples/minimal/`](../examples/minimal/) | Native | OKPF records only; no domain format source |
| [`examples/basic-pack/`](../examples/basic-pack/) | Native | OKPF artifacts; no domain format source |
| [`examples/software-onboarding/`](../examples/software-onboarding/) | Native | Markdown guides and JSONL records authored directly as OKPF |
| [`examples/software-architecture/`](../examples/software-architecture/) | Native | OKPF artifacts describing software architecture; no domain format |
| [`examples/local-organization-knowledge/`](../examples/local-organization-knowledge/) | Native | OKPF records and artifacts for org procedures and decisions |
| [`examples/field-repair-checklist/`](../examples/field-repair-checklist/) | Native | Diagnostic records authored as OKPF; no domain format source |
| [`examples/mechanic-diagnostics/`](../examples/mechanic-diagnostics/) | Native | OKPF artifacts for automotive diagnostics; no domain format |
| [`examples/brewing/`](../examples/brewing/) | Native | Markdown brewing content authored as OKPF artifacts; no BeerXML |
| [`examples/homebrew-recipe-pack/`](../examples/homebrew-recipe-pack/) | Native | Brewing artifacts authored in OKPF; no domain format source |
| [`examples/fermentation-recipe-pack/`](../examples/fermentation-recipe-pack/) | Native | Fermentation records authored in OKPF; no domain format source |
| [`examples/fermentation-ingredient-reference/`](../examples/fermentation-ingredient-reference/) | Native | Fermentation ingredient records authored in OKPF |
| [`examples/fermentation-bjcp-style/`](../examples/fermentation-bjcp-style/) | Native | OKPF records are primary; Markdown source note is reference material, not a domain artifact |
| [`examples/fermentation-mixed-bundle/`](../examples/fermentation-mixed-bundle/) | Native | OKPF records are primary across beer, cider, mead, wine; Markdown source is reference material |
| [`examples/brewing-with-beerxml/`](../examples/brewing-with-beerxml/) | Hybrid | BeerXML preserved as `sources/` domain artifact; OKPF records normalized alongside |

No current example is Envelope Mode only (domain artifact without accompanying OKPF records). `examples/brewing-with-beerxml/` is the only Hybrid Mode example. All others are Native Mode.

---

## What OKPF Does Not Replace

OKPF's role is packaging. It does not define, validate, or replace domain knowledge formats. Regardless of mode:

- OKPF does not replace BeerXML, MeadXML, or BJCP standards.
- OKPF does not replace FHIR, HL7, or DICOM.
- OKPF does not replace SCORM, xAPI, or IMS Global standards.
- OKPF does not replace GeoJSON, Shapefile, IFC, or OGC standards.
- OKPF does not replace ONNX, PyTorch, Safetensors, or model serialization formats.
- OKPF does not replace ROS bags, HDF5, Parquet, or scientific dataset formats.
- OKPF does not replace LeRobot, RLDS, Robo-DM, or robotics dataset schemas.
- OKPF does not replace any format that has its own schema, validation, and tooling ecosystem.

OKPF wraps, cites, normalizes, augments, or packages those formats when rights allow. It does not subsume them.

---

## Related Documents

- [Package Structure](package-structure.md) — directory layout and `sources/` directory
- [Profile Authoring](profile-authoring.md) — domain conventions in profiles, not Core
- [Provenance](provenance.md) — how to document origin and transformation history
- [When Not to Use OKPF](when-not-to-use-okpf.md) — cases where simpler alternatives are better
- [`examples/brewing-with-beerxml/`](../examples/brewing-with-beerxml/) — concrete Hybrid Mode example
- [`examples/software-onboarding/`](../examples/software-onboarding/) — concrete Native Mode example
