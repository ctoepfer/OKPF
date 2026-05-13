# Import Report

`import_report.json` records what happened when a builder or importer processed sources into an OKPF package. It is optional, but useful for partial success and clear failure messages.

## Minimal Shape

```json
{
  "import_id": "lumina-import-001",
  "status": "partial_success",
  "started_at": "2026-05-12T12:00:00Z",
  "completed_at": "2026-05-12T12:01:00Z",
  "summary": {
    "sources_total": 2,
    "sources_succeeded": 1,
    "sources_failed": 1,
    "records_created": 3
  },
  "items": [
    {
      "path": "sources/example.md",
      "stage": "normalization",
      "status": "success",
      "message": "Created normalized records."
    },
    {
      "path": "sources/bad.pdf",
      "stage": "extraction",
      "status": "error",
      "message": "PDF text extraction failed."
    }
  ]
}
```

`status` may be `success`, `partial_success`, or `failed`. Item stages should use clear practical names such as `discovery`, `container`, `extraction`, `normalization`, `validation`, `chunking`, or `indexing`.
