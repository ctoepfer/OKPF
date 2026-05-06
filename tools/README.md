# OKPF Tools

This directory will contain CLI tooling for working with OKPF knowledge packs.

**Status:** Planned — see [ROADMAP.md](../ROADMAP.md) for timeline.

---

## Planned CLI: `okpf`

The `okpf` command-line tool will be the primary interface for working with knowledge packs.

### Commands (Milestone 1)

```
okpf validate <path>     Validate a pack against the OKPF spec
okpf info <path>         Display a summary of a pack
okpf init                Interactively scaffold a new pack
```

### Commands (Milestone 2)

```
okpf pack <dir>          Package a directory into a .kpack archive
okpf unpack <file>       Extract a .kpack archive
okpf sign <path>         Sign a pack with a private key
okpf verify <path>       Verify signatures on a pack
okpf diff <a> <b>        Compare two pack versions
```

### Commands (Milestone 3)

```
okpf eval <path>         Run evaluations against a pack
okpf publish <path>      Publish a pack to a registry
okpf search <query>      Search a registry
```

---

## `okpf validate`

The validator will check:

1. `manifest.json` exists and is valid JSON
2. `manifest.json` conforms to the manifest JSON Schema
3. `license.json` exists and is valid
4. All `content[*].path` entries resolve to existing files
5. All declared `sha256` hashes match actual file contents
6. All `$ref` pointers resolve

Exit code 0 = valid. Exit code 1 = validation errors. Exit code 2 = fatal errors (file not found, etc.)

Example output:
```
$ okpf validate examples/brewing/
✓ manifest.json valid
✓ license.json valid
✓ contributors.json valid
✓ provenance.json valid
✓ content/guide.md (sha256 match)
✓ content/mineral-chart.json (sha256 match)
✓ evaluations/test-cases.json valid

Pack: Water Chemistry for Brewing v0.1.0
Domain: brewing
License: CC-BY-4.0
Artifacts: 4
Evaluations: 7

Status: VALID
```

---

## `okpf init`

An interactive scaffolding wizard that creates a new pack directory:

```
$ okpf init

OKPF Pack Initializer

Pack name: My Expertise Pack
Domain: my-domain
Version [0.1.0]: 
License [CC-BY-4.0]: 
Language [en]: 
Author name: Jane Smith
Author email (optional): jane@example.com

Creating my-expertise-pack/
  ✓ manifest.json
  ✓ license.json
  ✓ contributors.json
  ✓ provenance.json
  ✓ content/guide.md (template)
  ✓ evaluations/test-cases.json (template)

Pack initialized. Edit the files in my-expertise-pack/ to add your content.
Run 'okpf validate my-expertise-pack/' to check your pack.
```

---

## Contributing Tooling

If you want to contribute CLI tooling:

1. The reference Python library (`reference/python/`) is the preferred implementation for the CLI
2. The CLI entry point will be `okpf.cli:main`
3. Use `argparse` or `click` for argument parsing
4. Target Python 3.9+ for maximum compatibility
5. All CLI commands should have `--json` output mode for machine consumption

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
