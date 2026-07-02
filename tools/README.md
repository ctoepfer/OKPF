# OKPF Tools

The `okpf` reference CLI (`reference/python/okpf/cli.py`) is the primary
interface for working with OKPF knowledge packs. It is not yet published as
a standalone `pip`/`pipx` package — run it from a source checkout with:

```bash
PYTHONPATH=reference/python python3 -m okpf <command> ...
```

See [docs/five-minutes.md](../docs/five-minutes.md) for a full walkthrough.

---

## Implemented commands

```
okpf templates                       List built-in okpf init templates
okpf init <dest> --template <name>   Scaffold a new pack from a template
okpf add <pack_dir> <file>           Add a file to a pack's manifest
okpf fix <pack_dir>                  Apply additive fixes for common issues
okpf explain <pack_path>             Validate and explain each issue in plain language
okpf validate <path>                 Validate a pack against the OKPF spec
okpf inspect <path> / okpf info <path>  Display a summary of a pack
okpf pack <dir> <output.kpack>       Package a directory into a .kpack archive
okpf unpack <file.kpack> <dir>       Extract a .kpack archive
okpf compare-layout <dir> <out_dir>  Export alternative layouts for benchmark comparison
okpf demo <source_file>              Run an end-to-end demo: pack, validate, inspect, evaluate
```

### `okpf validate`

Checks manifest presence and schema conformance, safe artifact/record
paths, record file validity, provenance references, optional import
reports, and (when `--profile <name>` is given) profile-specific rules.
Warns — without failing — when a pack still uses the legacy `id`/`content`
fields instead of `package_id`/`artifacts`.

Exit code 0 = valid. Exit code 1 = validation errors.

```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/hello-world
PYTHONPATH=reference/python python3 -m okpf validate examples/fermentation-mixed-bundle --profile fermentation
```

### `okpf init`

Non-interactive scaffolding from a built-in template
(`minimal`, `software-onboarding`, `rag-source`, `local-org-knowledge`,
`field-repair-checklist`). Templates live as plain files under
`reference/python/okpf/templates/<id>/` — inspect or copy them directly.

```bash
PYTHONPATH=reference/python python3 -m okpf init my-pack --template software-onboarding \
  --package-id org.example.my-pack --name "My Pack"
```

`okpf init` validates the pack it just generated before returning, and
refuses to write into a non-empty destination unless `--force` is given.

### `okpf add`

Copies a file into `<pack_dir>/artifacts/`, computes its SHA-256 hash, and
appends an entry to `manifest.json` — without disturbing any other field.

```bash
PYTHONPATH=reference/python python3 -m okpf add my-pack docs/setup.md --role guide
```

### `okpf fix`

Applies a small, additive set of fixes: adds `package_id`/`artifacts` next
to legacy `id`/`content` fields (never removing the legacy field), and
backfills missing `sha256` hashes for artifact entries that point at real
files. Use `--dry-run` to preview.

### `okpf explain`

Runs the same checks as `okpf validate`, but pairs each issue with a
plain-English explanation and a concrete next step (often `okpf fix` or
`okpf add`).

---

## Not yet implemented

Signing (`okpf sign`/`okpf verify`), registry commands (`okpf publish`,
`okpf search`), a `.jsonl`/RAG export command, and benchmark tooling are
future work — see [ROADMAP.md](../ROADMAP.md) and
[docs/phase-1-roadmap.md](../docs/phase-1-roadmap.md).

## Contributing tooling

1. The reference Python library (`reference/python/`) is the preferred
   implementation for the CLI.
2. The CLI entry point is `okpf.cli:main`, using `argparse`.
3. `okpf` requires Python `>=3.11` (see root [CLAUDE.md](../CLAUDE.md)).
4. New CLI commands should validate their own output where practical (see
   `okpf init`) rather than silently returning a broken pack.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
