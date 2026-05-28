<!-- SPDX-License-Identifier: Apache-2.0 -->

# Project Status

Last reviewed: 2026-05-27
Branch context reviewed: `okpf-v0.1.0-rc-readiness`

This status reflects repository evidence from code, tests, docs, and recent commit history. It focuses on what is present today.

## Completed Work By Major Area

### 1) Core Specification And Schemas
Status: substantially implemented for Core v0.1.0 release-candidate readiness.

Evidence:
- Canonical spec exists: `SPEC.md`.
- Core and supporting schemas exist under `schemas/`, including `schemas/v0.1.0/manifest.schema.json` and `schemas/record.schema.json`.
- Conformance document exists: `docs/v0.1-conformance.md`.

### 2) Reference Validation And CLI Tooling
Status: implemented and tested for core workflows.

Evidence:
- Standalone validator: `reference/python/okpf_validate.py`.
- Reference CLI implements `validate`, `inspect`/`info`, `pack`, `unpack`, and `compare-layout`: `reference/python/okpf/cli.py`.
- CLI and validator test coverage exists (`tests/test_okpf_validate.py`, `tests/test_cli.py`, `tests/test_pack_archive.py`, `tests/test_validation.py`).

### 3) Prep Pipeline (`okpf-prep`)
Status: implemented as a Python package with CLI and tests.

Evidence:
- Package metadata and entry point in `pyproject.toml` (`okpf-prep = "okpf_prep.cli:main"`).
- Commands in `okpf_prep/cli.py`: `prepare`, `validate-profile`, `extract-text`.
- Supporting modules present (`extractors`, `profiles`, `runner`, `package_builder`, `beerxml`, `reports`, `ai/`).
- Tests exist (`tests/test_extractors.py`, `tests/test_profiles.py`, `tests/test_runner_mock.py`, `tests/test_package_builder.py`, `tests/test_beerxml.py`).

### 4) Profiles And Examples
Status: multiple profiles and examples are present; profile system is active.

Evidence:
- Profiles in `profiles/`, including fermentation, physical-skill-evidence, and human-correction-loop.
- Extensive example packs in `examples/` across domains.
- Recent commits show ongoing profile/example expansion (for example `b5902d1`, `10a7f33`, `90bdcd7`).

### 5) Documentation And Governance
Status: broad documentation baseline established.

Evidence:
- Core docs under `docs/` including packaging modes, conformance, security, AI integration, profile authoring, and benchmark/adoption planning.
- Governance and contribution files present (`GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`).

## Active Work-In-Progress Areas

Status indicates current activity and partial implementation, not roadmap promises.

- JavaScript reference implementation remains a stub/WIP (`reference/javascript/README.md`, minimal files in `reference/javascript/src/`).
- Some roadmap/checklist docs contain stale "planned" statements that no longer fully match implemented CLI behavior (for example `tools/README.md` and parts of `ROADMAP.md` still mark commands as future while reference CLI already has `pack`/`unpack`).
- Ongoing refinement of profile coverage and non-brewing examples continues (supported by recent commits and added docs).

## Open Questions, Risks, And Pending Decisions

- Documentation drift risk:
  - Multiple docs authored at different times have inconsistent status language (implemented vs planned).
  - Recommendation: establish one canonical status source and update roadmap/tooling docs to reference it.

- Scope and stability risk for v0.1.x:
  - Need to keep additive-only behavior in Core and avoid introducing new required fields without explicit consensus.
  - Recommendation: keep strict compatibility review for any schema changes affecting required fields.

- AI tooling expectation risk:
  - Presence of optional AI/trust fields may be over-interpreted by consumers as required behavior.
  - Recommendation: continue explicit "optional advisory metadata" language in docs and validators.

- Issue-tracker visibility gap in this local review:
  - Repository issue templates exist in `.github/ISSUE_TEMPLATE`, but open GitHub issues were not inspected from this offline/local view.

## Recommended Next Development Steps

1. Reconcile status docs with implementation reality.
- Update `ROADMAP.md` and `tools/README.md` to clearly distinguish implemented commands from future work.

2. Define a lightweight release-readiness checklist for Core v0.1.0.
- Include schema freeze criteria, compatibility checks, and required validation test runs.

3. Expand JavaScript reference implementation from stub to minimally conformant behavior.
- Prioritize manifest load/inspect and local validation parity with Python reference behavior.

4. Keep profile expansion separate from Core changes.
- Continue adding domain examples/profiles without tightening Core schema semantics.

5. Add a simple docs consistency pass to PR workflow (manual or scripted).
- Goal: avoid conflicting statements between README/ROADMAP/tools docs.

## Recent Commit Signals (Context)

Recent branch history indicates active work on RC readiness, profiles, and documentation tightening:
- `b5902d1` feat: add human correction loop profile
- `90bdcd7` docs: surface examples and physical skill evidence profile
- `10a7f33` feat: add physical skill evidence profile
- `eec5080` docs: tighten public messaging and training derivative framing
- `5d02e06` feat: add v0.1 conformance docs and pack tooling
- `5240180` stabilize v0.1.0 release-candidate readiness
