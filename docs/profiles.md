# Profiles

Profiles extend OKPF Core for a domain without making the universal record schema too large.

The core profile is `okpf-core`. Domain packages may add profiles such as `okpf-fermentation`, `okpf-medicine`, `okpf-robotics`, or organization-specific profiles.

## Profile Responsibilities

A profile may define:

- preferred `record_type` values
- required or recommended metadata keys
- domain-specific schemas
- controlled vocabularies
- validation levels beyond core usefulness checks

Core importers should not reject a package only because they do not understand a profile. They may warn and continue with core validation.

## Fermentation Example

The `okpf-fermentation` profile may use record types such as:

- `recipe`
- `style_guideline`
- `ingredient_reference`
- `process_note`
- `troubleshooting`
- `sensory_description`
- `equipment_reference`
- `formula`
- `document_section`
