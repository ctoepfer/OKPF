<!-- SPDX-License-Identifier: Apache-2.0 -->

# Git-Native Workflow for OKPF Packs

Before registries, before marketplaces, before any hosted distribution infrastructure exists: distribute OKPF packs through Git.

This document describes how to author, version, validate, and distribute OKPF packs using Git as the primary collaboration and distribution layer.

---

## Why Start with Git

Git already provides:

- version history for all manifest and record changes
- diff-based review for knowledge updates
- branch-and-PR workflows for collaborative authoring
- tag-based versioning for releases
- access control through existing repo permissions
- offline access for anyone with a clone

OKPF packs in a Git repository are fully inspectable, reviewable, and auditable without any additional infrastructure. This is sufficient for early adoption, and it is how all example packs in this repository are maintained.

---

## Storing an Unpacked Directory Pack in Git

Commit the OKPF pack directory directly. Do not zip it before committing unless you are specifically creating a release artifact.

**Example structure in a repository:**

```text
my-repo/
  knowledge/
    software-onboarding/
      manifest.json
      artifacts/
        setup-guide.md
        architecture-overview.md
      records/
        onboarding-checklist.jsonl
      provenance/
        sources.json
      evals/
        setup-questions.json
```

Or, if the entire repository is a pack:

```text
my-knowledge-pack/
  manifest.json
  artifacts/
  records/
  provenance/
  evals/
```

Both layouts work. The key is that `manifest.json` is at the root of the pack directory.

---

## Reviewing Manifest Changes in Pull Requests

Because manifests are plain JSON, PR diffs show exactly what changed:

```diff
-  "version": "0.1.0",
+  "version": "0.2.0",

-  "description": "Initial onboarding pack.",
+  "description": "Expanded onboarding pack with troubleshooting section.",

+  {
+    "path": "artifacts/troubleshooting.md",
+    "type": "text/markdown",
+    "title": "Common Troubleshooting Notes",
+    "role": "guide"
+  }
```

This is a significant advantage over opaque binary formats or schema-less JSON blobs. Reviewers can see:

- which artifact was added, removed, or renamed
- whether the version was bumped appropriately
- whether the license or usage policy changed
- whether provenance references were updated

---

## Reviewing Record and Provenance Changes in Diffs

JSONL record files are one record per line, making diffs readable:

```diff
+{"id": "onboard-006", "record_type": "document_section", "title": "Code Review Standards", ...}
```

A new record is one added line. A corrected record shows exactly which fields changed. A deleted record shows one removed line.

This makes OKPF records an excellent format for collaborative knowledge authoring with review workflows.

---

## Using CI to Run Validation

Add validation to your CI pipeline so that any PR that breaks pack structure is caught before merging.

**Example GitHub Actions step:**

```yaml
- name: Validate OKPF pack
  run: |
    pip install jsonschema
    python3 reference/python/okpf_validate.py examples/software-onboarding
    python3 reference/python/okpf_validate.py examples/local-organization-knowledge
    python3 reference/python/okpf_validate.py examples/field-repair-checklist
```

Or using the package CLI:

```yaml
- name: Validate OKPF packs
  run: |
    pip install -e ".[dev]"
    PYTHONPATH=reference/python python3 -m okpf validate examples/software-onboarding
    PYTHONPATH=reference/python python3 -m okpf validate examples/local-organization-knowledge
```

The validator exits with code 0 on success and 1 on any validation error. Warnings do not cause a non-zero exit.

---

## Generating .kpack Artifacts for Releases

When you are ready to distribute a versioned pack, generate a `.kpack` file and attach it to a GitHub release.

```bash
# Pack a directory into a .kpack archive
PYTHONPATH=reference/python python3 -m okpf pack examples/software-onboarding dist/software-onboarding-0.1.0.kpack

# Validate the produced archive
PYTHONPATH=reference/python python3 -m okpf validate dist/software-onboarding-0.1.0.kpack
```

The `dist/` directory is an example convention — adapt it to your project. Do not commit generated `.kpack` files to the source tree unless you are using them as test fixtures.

Add `dist/` to `.gitignore`:

```
dist/
*.kpack
```

Then attach the `.kpack` file to a GitHub release or distribute it directly. Recipients can unpack it with:

```bash
PYTHONPATH=reference/python python3 -m okpf unpack software-onboarding-0.1.0.kpack software-onboarding/
```

---

## Using Tags for Versioned Packs

Tag releases in Git so that the version declared in `manifest.json` is traceable to a specific commit:

```bash
git tag v0.1.0-software-onboarding
git push origin v0.1.0-software-onboarding
```

Consumers can reference a specific version by checking out the tag. This gives packs a stable, auditable version anchor without requiring a registry.

---

## Keeping Source Artifacts and Normalized Records Together

Do not separate source files from the OKPF pack. The pack is the unit of distribution:

```text
software-onboarding/
  manifest.json
  artifacts/          # human-authored source artifacts
    setup-guide.md
  records/            # normalized structured records derived from artifacts
    onboarding-checklist.jsonl
  provenance/         # links records back to their source artifacts
    sources.json
```

When you update `setup-guide.md`, also update the relevant records in `records/` and the provenance entry in `provenance/sources.json`. The pack should always be internally consistent.

---

## What Not to Commit

- Generated `.kpack` ZIP files (unless they are explicitly test fixtures).
- Unpacked output directories from `okpf unpack`.
- `out/` directories from `okpf-prep` runs.
- `.venv/`, `__pycache__/`, `*.egg-info/`.
- Any file containing credentials, API keys, private URLs, or real personal data in example packs.

---

## Worked Example

Starting from scratch with a new organizational knowledge pack:

```bash
# 1. Create the pack directory
mkdir -p my-org-knowledge/{artifacts,records,provenance,evals}

# 2. Author the manifest
cat > my-org-knowledge/manifest.json << 'EOF'
{
  "okpf_version": "0.1.0",
  "package_id": "org.example.my-org-knowledge",
  "name": "My Organization Knowledge Pack",
  "version": "0.1.0",
  "domain": "organizational-knowledge",
  "license": {"type": "CC-BY-4.0"},
  "artifacts": [
    {"path": "artifacts/procedures.md", "type": "text/markdown", "role": "guide"}
  ]
}
EOF

# 3. Add content
echo "# Procedures\n\nExample content." > my-org-knowledge/artifacts/procedures.md

# 4. Validate
PYTHONPATH=reference/python python3 -m okpf validate my-org-knowledge

# 5. Inspect
PYTHONPATH=reference/python python3 -m okpf inspect my-org-knowledge

# 6. Commit
git add my-org-knowledge/
git commit -m "Add organizational knowledge pack v0.1.0"

# 7. Release
mkdir -p dist
PYTHONPATH=reference/python python3 -m okpf pack my-org-knowledge dist/my-org-knowledge-0.1.0.kpack
# Attach dist/my-org-knowledge-0.1.0.kpack to a GitHub release
```

---

## See Also

- [docs/adoption-strategy.md](adoption-strategy.md) — adoption thesis and target verticals
- [docs/benchmark-plan.md](benchmark-plan.md) — comparing OKPF against simpler alternatives
- [docs/v0.1-conformance.md](v0.1-conformance.md) — conformance levels for producers and consumers
- [docs/security.md](security.md) — path safety and integrity verification
