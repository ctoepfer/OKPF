# okpf-py — Python Reference Implementation

A Python library for reading, validating, and creating OKPF knowledge packs.

**Status:** Stub / Work in Progress  
**Python:** 3.11+

---

## Installation (planned)

```bash
pip install okpf
```

---

## Planned API

### Reading a Pack

```python
from okpf import KnowledgePack

# Open a pack directory
pack = KnowledgePack.open("examples/brewing/")

print(pack.name)          # "Water Chemistry for Brewing"
print(pack.version)       # "0.1.0"
print(pack.domain)        # "brewing"
print(pack.license.spdx)  # "CC-BY-4.0"

# Iterate over content
for artifact in pack.content:
    print(f"{artifact.id}: {artifact.path} ({artifact.type})")

# Read a specific artifact
guide = pack.read("guide")
print(guide.text)  # Markdown content of guide.md
```

### Validating a Pack

```python
from okpf import validate

result = validate("examples/brewing/")

if result.valid:
    print("Pack is valid")
else:
    for error in result.errors:
        print(f"  {error.path}: {error.message}")
```

### Creating a Pack

```python
from okpf import PackBuilder

builder = PackBuilder(
    name="My Knowledge Pack",
    domain="my-domain",
    version="0.1.0"
)

builder.set_license("CC-BY-4.0", use="open", redistribution="open")
builder.add_contributor("Jane Smith", role="author")
builder.add_content("content/guide.md", id="guide", role="guide")

pack = builder.build()
pack.save("my-pack.kpack")
```

### Running Evaluations

```python
from okpf import KnowledgePack, EvaluationRunner

pack = KnowledgePack.open("examples/brewing/")
runner = EvaluationRunner(pack)

results = runner.run_all()
for result in results:
    print(f"{result.id}: {'PASS' if result.passed else 'FAIL'}")
```

---

## File Structure (planned)

```
reference/python/
├── README.md
├── pyproject.toml
├── okpf/
│   ├── __init__.py
│   ├── pack.py          # KnowledgePack class
│   ├── manifest.py      # Manifest parsing and validation
│   ├── license.py       # License handling
│   ├── provenance.py    # Provenance records
│   ├── contributors.py  # Contributor records
│   ├── evaluations.py   # Evaluation running
│   ├── builder.py       # PackBuilder
│   └── validate.py      # Validation logic
└── tests/
    ├── test_pack.py
    ├── test_validate.py
    └── test_builder.py
```

---

## Contributing

The Python reference implementation needs contributors. Good first issues:

1. Implement `KnowledgePack.open()` for directory packs
2. Add .kpack archive support to the SDK pack loader
3. Implement SHA-256 hash verification for content artifacts
4. Implement `PackBuilder.build()`
5. Write tests against the brewing example pack

See [CONTRIBUTING.md](../../CONTRIBUTING.md) to get started.
