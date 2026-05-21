# Records

Records are normalized knowledge units. They are intentionally broad so OKPF can represent style guidelines, troubleshooting notes, procedures, formulas, reference entries, lessons, annotations, and future record types.

## Required Fields

- `id`: stable record identifier unique within the package.
- `record_type`: type of knowledge represented.
- `title`: human-readable title.
- `text`: primary normalized text.
- `domain`: domain for the record.
- `metadata`: object for source, profile, and domain-specific metadata.

## Optional Facets

Records may include `facets`, an object of machine-readable classification hints used for filtering, retrieval, validation, display, and routing.

OKPF Core does not define a global facet vocabulary. Profiles may recommend or require facet keys and allowed values.

## Example

```json
{
  "id": "bjcp-2021-21a",
  "record_type": "style_guideline",
  "title": "21A American IPA",
  "text": "Style description text...",
  "domain": "fermentation",
  "facets": {
    "beverage_type": "beer",
    "style_family": "ipa",
    "knowledge_role": "style_guideline"
  },
  "metadata": {
    "source": "BJCP 2021",
    "style_id": "21A"
  }
}
```

## Formats

Record files MAY be JSONL, JSON arrays, single JSON record objects, or JSON objects with a `records` array. JSONL is recommended for large packages and partial processing.

The core schema does not restrict `record_type` to a fixed enum. Domain profiles can define preferred record types.
