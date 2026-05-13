# Package Structure

An OKPF v0.1 package is either a directory or a `.kpack` ZIP archive.

## Required

```text
manifest.json
records/
```

`manifest.json` declares package identity, domain, profiles, record files, and available licensing/provenance summaries. `records/` contains normalized JSON or JSONL records.

## Optional

```text
sources/
docs/
assets/
schemas/
provenance/
chunks/
import_report.json
README.md
LICENSE
```

- `sources/`: original source files such as Markdown, TXT, PDF, ZIP files, legacy structured packs, or future package formats.
- `docs/`: human-oriented notes and package documentation.
- `assets/`: images, diagrams, media, or binary support files.
- `schemas/`: package-local JSON Schemas or profile schemas.
- `provenance/`: source lists, transformation logs, attribution, license notes, and rebuild metadata.
- `chunks/`: optional derived chunks for systems that want to ship precomputed segmentation.
- `import_report.json`: optional report from an importer or builder, including partial success.
- `README.md`: human-readable package overview.
- `LICENSE`: package-level license text when applicable.

## Safe Paths

All package paths are relative POSIX-style paths. Producers MUST NOT write absolute paths or traversal paths. Consumers MUST reject unsafe paths.

Unsafe examples:

```text
/absolute/file.txt
../outside.txt
records/../../outside.txt
C:\Users\name\file.txt
sources\..\outside.txt
```
