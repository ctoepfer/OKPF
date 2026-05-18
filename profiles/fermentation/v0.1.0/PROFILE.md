# OKPF Fermentation Profile v0.1.0

**Status:** Draft optional profile

The OKPF fermentation profile defines optional conventions for packaging fermentation-related knowledge in OKPF packs. It is intended for beer, wine, mead, cider, perry, sake, fermented foods and drinks, ingredients, process guidance, equipment references, style summaries, and troubleshooting notes.

This profile is not part of OKPF Core. A pack can be valid OKPF Core without using this profile, and an OKPF Core validator should not reject a pack only because it does not understand this profile.

## Relationship To Domain Formats

The fermentation profile is not a replacement for BeerXML, BJCP, MeadXML, wine recipe formats, lab records, regulatory records, or other domain formats. OKPF may wrap, cite, normalize, augment, or package those formats alongside provenance, licensing, examples, import reports, and normalized records.

## Declaring The Profile

Manifests may declare the profile with:

```json
{
  "profiles": ["okpf-core", "okpf-fermentation"]
}
```

Profile-aware tools may also use a versioned profile identifier such as `okpf-fermentation@0.1.0` or a local path to this directory. Unknown profile identifiers should not make a pack invalid at the OKPF Core level.

## Recommended Record Types

The profile recommends, but does not require, these `record_type` values:

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

Profile validators should warn, not fail, on unknown record types unless a stricter project-specific policy is enabled.

## Recommended Facets

The profile recommends, but does not require, these facet keys:

- `beverage_type`
- `product_family`
- `process_type`
- `base_ingredient`
- `style_family`
- `fermentation_type`
- `ingredient_role`
- `sensory_family`
- `equipment_type`
- `knowledge_role`

Recommended `beverage_type` values:

- `beer`
- `wine`
- `mead`
- `cider`
- `perry`
- `sake`
- `seltzer`
- `soda`
- `kombucha`
- `vinegar`
- `distilling`
- `ingredient`
- `process`
- `equipment`
- `general`

Profile validators should preserve unknown facet keys. Unknown facet values may produce warnings if a local vocabulary is configured.

## Validation Guidance

Core validation checks package shape, manifest requirements, safe paths, record shape, provenance basics, licensing basics, and checksums when present. Core validation does not require fermentation facets and does not reject unknown record types.

Profile validation may check recommended record types, recommended facets, controlled vocabulary values, and examples. For v0.1.0, profile validation should prefer warnings over hard failures.

