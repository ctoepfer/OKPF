# Records

Records are normalized knowledge units. They are intentionally broad so OKPF can represent style guidelines, troubleshooting notes, procedures, formulas, reference entries, lessons, annotations, and future record types.

## Required Fields

- `id`: stable record identifier unique within the package.
- `record_type`: type of knowledge represented.
- `title`: human-readable title.
- `text`: primary normalized text.
- `domain`: domain for the record.
- `metadata`: object for source, profile, and domain-specific metadata.

## Example

```json
{
  "id": "bjcp-2021-21a",
  "record_type": "style_guideline",
  "title": "21A American IPA",
  "text": "Style description text...",
  "domain": "fermentation",
  "metadata": {
    "source": "BJCP 2021",
    "style_id": "21A"
  }
}
```

## Formats

Record files MAY be JSONL, JSON arrays, single JSON record objects, or JSON objects with a `records` array. JSONL is recommended for large packages and partial processing.

The core schema does not restrict `record_type` to a fixed enum. Domain profiles can define preferred record types.
