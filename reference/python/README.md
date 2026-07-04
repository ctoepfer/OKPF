# okpf-py — Python Reference Implementation

The Python reference implementation for the Open Knowledge Pack Format:
the `okpf` CLI, the `Pack`/`Manifest` SDK, and the standalone
`okpf_validate.py` validator.

**Python:** 3.11+

---

## Installation

From a source checkout, without publishing anywhere:

```bash
pip install ./reference/python
```

This is not yet published to PyPI — see the root
[README](../../README.md) and [docs/phase-1-roadmap.md](../../docs/phase-1-roadmap.md)
for status. Once installed this way, `okpf` works as a normal console
command, and schemas/templates are bundled with the package so validation
and `okpf init` both work without a repo checkout present.

For local development instead of a real install, use `PYTHONPATH`:

```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/hello-world
```

---

## The CLI

See [tools/README.md](../../tools/README.md) for the full command
reference (`init`, `add`, `fix`, `explain`, `validate`, `inspect`, `pack`,
`unpack`, `compare-layout`, `export-rag`, `export-citations`, `benchmark`,
`demo`) and [docs/five-minutes.md](../../docs/five-minutes.md) for a
walkthrough.

## The SDK

```python
from okpf import Pack

# Directory pack or .kpack archive -- both work the same way.
pack = Pack.load("examples/software-onboarding/")
# pack = Pack.load("out/software-onboarding.kpack")

print(pack.manifest.package_id)     # "okpf-example-software-onboarding"
print(pack.manifest.display_name)   # manifest 'title' if set, else 'name'
print(pack.manifest.domain)         # "software-engineering"
print(pack.capabilities)            # declared 'capabilities', if any

# Content
for artifact in pack.content:
    print(artifact.id, artifact.path, artifact.role)
guide = pack.read(pack.content[0].id)
print(guide.text)

# Evaluations -- resolves file-reference entries
# ({"path": "evals/x.json"}) as well as inline evaluation objects.
for ev in pack.evaluations:
    print(ev.question)

# Validation
result = pack.validate()
print(result.valid)

pack.close()  # or: with Pack.load(...) as pack: ...
```

```python
from okpf_validate import validate_pack  # the standalone validator

result = validate_pack("examples/hello-world")
print(result.valid)
for issue in result.issues:
    print(issue)
```

`okpf.validate.validate()` (used internally by `Pack.validate()`) is a
lighter-weight SDK validator: manifest schema + required fields + safe
paths + SHA-256 integrity, for both directories and `.kpack` files. The
standalone `reference/python/okpf_validate.py` additionally does deeper
record/profile checks and powers the `okpf` CLI — see
[tools/README.md](../../tools/README.md#okpf-validate).

## File structure

```
reference/python/
├── README.md
├── pyproject.toml
├── okpf_validate.py      # standalone validator (also stays directly
│                          # executable: python3 reference/python/okpf_validate.py <pack>)
└── okpf/
    ├── __init__.py        # Pack, Manifest, validate exports
    ├── cli.py              # `okpf` console script
    ├── pack.py             # Pack, ArtifactContent
    ├── manifest.py         # Manifest, ContentArtifact, EvaluationCase
    ├── validate.py         # lightweight SDK validator
    ├── export.py           # okpf.rag_export.v0.1 contract
    ├── benchmark.py         # okpf benchmark
    ├── scaffold.py          # okpf init template rendering
    ├── demo.py              # okpf demo
    ├── schemas/             # bundled copy of the top-level schemas/ (packaging)
    └── templates/           # okpf init built-in templates
```

## Known gaps

- No `PackBuilder`/pack-authoring API yet — use `okpf init`/`okpf add` from
  the CLI, or write `manifest.json` directly.
- Not published to PyPI yet.

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) to get started. If you're
adding a manifest field the SDK doesn't parse yet, check
`tests/test_pack_sdk.py` first — `Pack.load()`/`Manifest` previously had
zero test coverage against real example packs, which is exactly how they
drifted out of sync with the schema before. Any change here should be
exercised against at least one real `examples/` pack, not just synthetic
fixtures.
