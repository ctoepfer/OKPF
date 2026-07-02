<!-- SPDX-License-Identifier: Apache-2.0 -->

# OKPF in 5 minutes

This walks through creating, enriching, validating, and packing an OKPF
pack from a source checkout of this repository. Every command below is
copy-pasteable and runs offline.

> These commands use `PYTHONPATH=reference/python python3 -m okpf ...`
> because the `okpf` reference CLI isn't published as a standalone
> `pip`/`pipx` package yet — that's tracked as later distribution work.
> `okpf-prep` (a separate tool) is already installable; see the root
> [README](../README.md#setup) for its setup.

## 0. Setup

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## 1. See what templates are available

```bash
PYTHONPATH=reference/python python3 -m okpf templates
```

```
field-repair-checklist Field Repair Checklist Pack
        A step-by-step diagnostic or repair checklist for field/technician use.
local-org-knowledge     Local Organization Knowledge Pack
        Internal policy or process knowledge for a team or organization.
minimal                 Minimal Pack
        The smallest valid OKPF pack — one manifest, one artifact.
rag-source              RAG Source Pack
        A single source document plus pre-chunked records, ready for RAG ingestion.
software-onboarding     Software Onboarding Pack
        Setup guide, architecture notes, troubleshooting, and an onboarding checklist for a codebase.
```

## 2. Create a pack

```bash
PYTHONPATH=reference/python python3 -m okpf init my-onboarding-pack \
  --template software-onboarding \
  --package-id org.example.my-onboarding-pack \
  --name "My Project Onboarding"
```

`okpf init` refuses to write into a non-empty directory unless you pass
`--force`, and it validates the pack it just created before handing it back
to you — you should see `OKPF package is valid: ...` immediately.

## 3. Add a real file

Templates ship with placeholder Markdown and JSONL. Replace a placeholder,
or add a brand-new artifact without hand-editing `manifest.json`:

```bash
echo "# Deploying to staging" > deploy-notes.md
PYTHONPATH=reference/python python3 -m okpf add my-onboarding-pack deploy-notes.md \
  --role guide --type text/markdown --title "Deploy Notes"
```

This copies the file into `my-onboarding-pack/artifacts/`, computes its
SHA-256 hash, and appends an entry to the pack's `artifacts` array —
every other field in `manifest.json` is left untouched.

## 4. Validate

```bash
PYTHONPATH=reference/python python3 -m okpf validate my-onboarding-pack
```

If validation ever fails or warns about something you don't recognize, run:

```bash
PYTHONPATH=reference/python python3 -m okpf explain my-onboarding-pack
```

`explain` runs the same checks as `validate`, but pairs each issue with a
plain-English explanation and a concrete next step. For fixable structural
issues (like a pack still using the legacy `id`/`content` fields, or an
artifact missing its `sha256`), run:

```bash
PYTHONPATH=reference/python python3 -m okpf fix my-onboarding-pack --dry-run
PYTHONPATH=reference/python python3 -m okpf fix my-onboarding-pack
```

`fix` is additive only — it never deletes a legacy field, it only adds the
modern equivalent alongside it.

## 5. Pack and unpack

```bash
PYTHONPATH=reference/python python3 -m okpf pack my-onboarding-pack out/my-onboarding-pack.kpack
PYTHONPATH=reference/python python3 -m okpf unpack out/my-onboarding-pack.kpack out/my-onboarding-pack-unpacked
PYTHONPATH=reference/python python3 -m okpf validate out/my-onboarding-pack-unpacked
```

`.kpack` is a plain ZIP archive — `pack` rejects unsafe paths before
writing, and `unpack` rejects unsafe archive entries before extracting
anything.

## 6. Export for RAG

```bash
PYTHONPATH=reference/python python3 -m okpf export-rag my-onboarding-pack out/rag.jsonl
```

Each line is one `okpf.rag_export.v0.1` row, carrying license, usage
policy, provenance, and a deterministic `chunk_id` — no guessing required
by whatever loads it. Because `my-onboarding-pack` declares `records`
(from the `software-onboarding` template), the export comes from
`records/decisions.jsonl`, not from `deploy-notes.md` added in step 3 —
`export-rag` treats records as the authored RAG-ready form; see
[docs/rag-export.md](rag-export.md) for the full chunking rule and field
contract, and [docs/rag-integrations.md](rag-integrations.md) for
framework loader snippets.

## What you just proved

- A pack can be created, enriched, and validated without hand-editing JSON.
- The pack round-trips through a `.kpack` archive without losing anything.
- Structural mistakes come with an explanation and, where possible, a fix.
- The pack exports to a documented, predictable RAG-ingestion format.

For the fully filled-out reference version of the software-onboarding
template, see [examples/software-onboarding/](../examples/software-onboarding/).
