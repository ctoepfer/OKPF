# Basic OKPF Example Pack — Overview

This is a minimal example of an Open Knowledge Pack Format (OKPF) knowledge pack. Its purpose is to demonstrate the simplest valid pack structure.

## What this pack contains

This pack contains one artifact: this overview document. It serves as a reference for pack authors who want to understand the minimum required structure.

## Pack structure

An OKPF pack is a directory (or `.kpack` zip archive) with:

- `manifest.json` — the root descriptor (required)
- `license.json` — machine-readable license declaration (required if referenced from manifest)
- `README.md` — human-readable summary (recommended)
- `LICENSE` — license text (recommended)
- `content/` — content artifacts

## How an AI system might use this pack

A system consuming this pack would:

1. Read `manifest.json` to understand what the pack contains and how it is licensed
2. Check the `license` field to determine permitted uses (e.g., RAG, fine-tuning, display)
3. Read each artifact listed in `content[]`, using `role` to understand its purpose
4. Optionally verify artifact integrity using `sha256` hashes

For a pack with `role: "rag_source"` artifacts, the content would be chunked and embedded into a vector store. For `role: "evaluation"` artifacts, the content would be used to benchmark a model's knowledge.

## Extending this pack

To extend this pack for a real domain:

1. Add more artifacts to `content/` and list them in `manifest.json`
2. Add `contributors.json` to credit content creators
3. Add `provenance.json` to document where the content came from
4. Compute and set `sha256` hashes for all artifacts
5. Update `license.json` with accurate permissions

See [SPEC.md](../../SPEC.md) for the full specification and [docs/concepts.md](../../docs/concepts.md) for design background.
