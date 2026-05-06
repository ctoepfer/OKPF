# OKPF Examples

This document provides an overview of the example knowledge packs included in this repository and guidance for creating your own.

---

## Included Examples

### Brewing — Water Chemistry

**Path:** [`examples/brewing/`](../examples/brewing/)  
**Status:** Complete starter pack  
**Domain:** Brewing / Food Science

A practical, complete knowledge pack demonstrating all core OKPF features:

- Full brewing water chemistry guide (Markdown)
- Mineral ion reference chart (JSON data)
- Classic water profiles reference (JSON data)
- Water adjustment workflow (structured task)
- 7 evaluation test cases

Use this as a template when creating your first pack.

---

### Mechanic Diagnostics

**Path:** [`examples/mechanic-diagnostics/`](../examples/mechanic-diagnostics/)  
**Status:** Placeholder — contributions welcome  
**Domain:** Automotive Repair

Planned content: diagnostic procedures, symptom-to-cause decision trees, OBD-II reference, mechanic reasoning transcripts.

---

### Software Architecture Patterns

**Path:** [`examples/software-architecture/`](../examples/software-architecture/)  
**Status:** Placeholder — contributions welcome  
**Domain:** Software Engineering

Planned content: architectural patterns with trade-off analysis, decision frameworks, anti-patterns, case studies.

---

## Building Your Own Pack

### Step 1: Start with the structure

Copy the brewing example directory as a starting point:

```bash
cp -r examples/brewing examples/my-domain
cd examples/my-domain
```

### Step 2: Edit the manifest

Update `manifest.json`:
- Change `id` to a unique URN: `urn:okpf:<domain>:<name>:<version>`
- Change `name`, `description`, `domain`, `tags`
- Update the `content` array to match your actual files

### Step 3: Declare a license

Edit `license.json`. For open knowledge, CC BY 4.0 is recommended:

```json
{
  "spdx_expression": "CC-BY-4.0",
  "scope": {
    "use": "open",
    "redistribution": "open",
    "derivative_works": "open",
    "ai_training": "permitted"
  },
  "attribution_required": true,
  "attribution_text": "Your Pack Name by Your Name, licensed under CC BY 4.0."
}
```

### Step 4: Add your contributors

Edit `contributors.json` with your own name and role:

```json
{
  "contributors": [
    {
      "id": "author-01",
      "name": "Jane Smith",
      "role": "author",
      "contributions": ["guide"],
      "orcid": "https://orcid.org/0000-0000-0000-0000"
    }
  ]
}
```

### Step 5: Record provenance

Edit `provenance.json` to describe where your knowledge came from:

- If it's entirely original: add a single `original` source
- If it's based on interviews: add `interview` sources
- If it includes content from publications: add `publication` sources with URIs

### Step 6: Add your content

Put your actual knowledge content in `content/`:
- Guides as `text/markdown` (`.md` files)
- Structured data as `application/json` (`.json` files)
- Images as `image/png` or `image/jpeg`

### Step 7: Write evaluations (optional but encouraged)

Add test cases to `evaluations/test-cases.json`. Even 3–5 well-crafted questions greatly increase the value of a pack.

### Step 8: Validate

```bash
# Validate your manifest (requires jsonschema)
python -m jsonschema -i manifest.json ../../schemas/manifest.schema.json

# Check all referenced files exist
python -c "
import json, os
manifest = json.load(open('manifest.json'))
for artifact in manifest['content']:
    path = artifact['path']
    assert os.path.exists(path), f'Missing: {path}'
    print(f'OK: {path}')
"
```

---

## Content Guidelines

When authoring knowledge pack content, aim for:

**Depth over breadth** — A pack that goes deep on one topic is more valuable than a shallow overview of many topics. The brewing example covers a single topic (water chemistry) comprehensively.

**Expert reasoning, not just facts** — The most valuable packs capture *why* experts make decisions, not just *what* the decisions are. Include:
- When a rule applies vs. when it doesn't
- Common mistakes and why they happen
- Trade-offs between approaches

**Evaluations that test judgment** — Write test cases that require understanding, not just recall. "What is the target mash pH?" is less valuable than "Why is high bicarbonate water problematic for Pilsners?"

**Honest provenance** — Record where your knowledge came from. If it's based on experience, say so. If you used AI tools to help draft it, record that and note who reviewed it.

---

## Domain Ideas

OKPF is suited for any domain where expertise is valuable and hard to transfer:

| Domain | Example Topics |
|--------|---------------|
| Trades | Electrical diagnostics, plumbing, HVAC |
| Medicine | Clinical decision protocols, drug interactions |
| Agriculture | Soil health, crop management, pest identification |
| Engineering | Mechanical diagnosis, materials selection |
| Science | Laboratory procedures, analytical methods |
| Finance | Risk assessment frameworks |
| Legal | Contract analysis patterns |
| Education | Teaching strategies, curriculum design |
| Gastronomy | Fermentation, cooking chemistry, flavor pairing |
| Music | Theory, arrangement, production |

Any domain where an expert's judgment is valuable — and where that judgment is hard to document — is a candidate for OKPF.
