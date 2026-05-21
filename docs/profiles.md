# Profiles

Profiles extend OKPF Core for a domain without making the core record schema too large.

OKPF Core defines the package boundary, manifest, artifacts, records, provenance, licensing, and validation basics. Profiles define optional domain-specific conventions such as recommended record types, facets, vocabularies, validation rules, and examples.

The core profile name is `okpf-core`. Domain packages may add profiles such as `okpf-fermentation`, `okpf-medicine`, `okpf-robotics`, or organization-specific profiles.

```json
{
  "profiles": ["okpf-core", "okpf-fermentation"]
}
```

Unknown profiles should not make a package invalid at the OKPF Core level. Core importers may warn and continue with core validation.

## Facets

Records may include an optional `facets` object. Facets are machine-readable classification hints used for filtering, retrieval, validation, display, and routing.

OKPF Core does not define a fixed global facet vocabulary. Profiles may recommend or require facet keys and allowed values.

```json
{
  "id": "example-record-001",
  "record_type": "process_note",
  "title": "Temperature control note",
  "text": "Keep fermentation temperature stable during active fermentation.",
  "domain": "fermentation",
  "facets": {
    "subject": "fermentation",
    "process": "temperature_control",
    "material": ["yeast"],
    "intent": "process_guidance"
  },
  "metadata": {}
}
```

## Profile Responsibilities

A profile may define:

- preferred `record_type` values
- recommended or required facet keys
- domain-specific schemas
- controlled vocabularies
- validation levels beyond core usefulness checks

## Fermentation Example

The draft fermentation profile lives at [../profiles/fermentation/v0.1.0/](../profiles/fermentation/v0.1.0/). It is one example profile, not core behavior.

It recommends record types such as:

- `recipe`
- `style_guideline`
- `ingredient_reference`
- `process_note`
- `sensory_description`
- `formula`
- `comparison`
- `glossary_entry`
- `document_section`
- `troubleshooting`
- `equipment_reference`

It recommends facets such as `beverage_type`, `product_family`, `process_type`, `base_ingredient`, `style_family`, `fermentation_type`, `ingredient_role`, `sensory_family`, `equipment_type`, and `knowledge_role`.

The fermentation profile is not a replacement for BeerXML, BJCP, MeadXML, or other domain formats. OKPF may wrap, cite, normalize, augment, or package those formats.
