<!-- SPDX-License-Identifier: Apache-2.0 -->
# Packaging Model Artifacts in OKPF

**Status:** Non-normative guidance
**Applies to:** OKPF v0.1.0

This document explains how OKPF MAY be used to package machine learning model artifacts. It is entirely non-normative. Nothing here adds required fields to OKPF Core or modifies the OKPF v0.1.0 specification.

---

## What OKPF Does and Does Not Define

OKPF is a general-purpose knowledge packaging format. When used with model artifacts, OKPF provides:

- Package identity and version metadata
- Provenance and training attribution
- License and usage policy declarations
- Integrity hashes for included files
- Evaluation reports and benchmark summaries
- Model cards and limitation documentation
- Optional extension metadata for architecture-specific fields

OKPF does **not** define:

- Neural network architectures, layer definitions, or hyperparameter schemas
- Weight serialization formats (ONNX, SafeTensors, PyTorch `.pt`, Flax, TensorFlow SavedModel, etc.)
- Inference engines, serving runtimes, or hardware backends
- Training pipelines, orchestrators, or distributed training protocols
- Compute or hardware requirements
- Embedding models, vector databases, or retrieval infrastructure
- Registry protocols, model hubs, or download mechanisms

Packs that include model weights treat them as opaque artifacts. OKPF does not parse, validate, execute, or re-encode weight files. Consumers that need to load weights must use the appropriate framework independently.

---

## Packaging Modes for Model Artifacts

OKPF supports three packaging modes (see `docs/packaging-modes.md`). For model artifacts:

- **Envelope Mode** — The model checkpoint remains governed by its native format (SafeTensors, ONNX, etc.). OKPF provides the surrounding package: identity, provenance, license, usage policy, and evaluation context. This is the most common mode when distributing a pre-trained model alongside its documentation.
- **Hybrid Mode** — Both the native checkpoint and OKPF-normalized records coexist. Normalized records might include derived representation metadata, evaluation summaries, or structured documentation that consumers can use without loading the full checkpoint.
- **Native Mode** — The pack contains only OKPF-structured artifacts: model cards, provenance records, evaluation reports, representation metadata. No weight files are present. Useful for distributing model documentation and audit trails independently of the checkpoint, or for packs where weights are too large or proprietary to distribute.

---

## Suggested Artifact Roles

OKPF artifact `role` values are free-form strings. The following conventions are suggested for model artifact packs:

| Role | Suggested Path | Description |
|---|---|---|
| `model-card` | `docs/model_card.md` | Human-readable model card (Markdown or structured JSON) |
| `model-checkpoint` | `models/<name>.<ext>` | Native-format model weights (opaque to OKPF) |
| `representation-metadata` | `models/representation.json` | Architecture summary, embedding dimensions, representation type |
| `training-provenance` | `provenance/training_run.json` | Dataset, compute, hyperparameters, framework, run ID |
| `evaluation-report` | `evals/<name>_eval_report.json` | Structured benchmark results and methodology |
| `limitations` | `docs/limitations.md` | Structured or narrative description of known limitations |
| `license-notice` | `docs/model_license.md` | Supplemental license notice for the model artifact itself |

These role values are conventions, not OKPF Core requirements. Domain profiles or extensions MAY define controlled vocabularies for model artifact roles.

---

## Model Cards

A model card SHOULD be packaged as a Markdown artifact with role `model-card`. Content SHOULD follow established model card practice (Mitchell et al., 2019; Hugging Face model card conventions) and include:

- Intended use and out-of-scope uses
- Performance metrics and evaluation conditions
- Known limitations and biases
- Attribution, citations, and license summary

Model cards are human-authored documentation. They are not LLM chain-of-thought or private reasoning traces.

---

## Training Provenance

Training provenance records SHOULD be placed in `provenance/` and listed in `artifacts` with role `training-provenance`. A training provenance record MAY include:

- Dataset name and version (a pointer or identifier, not the dataset itself)
- Compute summary (hardware class, duration, framework versions)
- Hyperparameters or a reference to an external config file
- Output checkpoint identifier or hash
- Evaluator identity and audit date

OKPF does not validate the factual accuracy of provenance records. Consumers are responsible for verifying claims against primary sources.

The top-level `provenance` field in `manifest.json` MAY reference the primary training provenance file via `{"$ref": "provenance/training_run.json"}`.

---

## Evaluation Reports

Evaluation artifacts SHOULD be placed in `evals/` and listed in `artifacts` with role `evaluation-report`. An evaluation report MAY include:

- Benchmark name and version
- Metric definitions and numeric results
- Evaluation methodology and conditions
- Evaluator identity and evaluation date
- Reproduction caveats and scope of claims

---

## Extension Metadata

Architecture-specific or framework-specific metadata that does not belong in OKPF Core fields MAY be placed in the `extensions` object of `manifest.json`. Extension keys SHOULD use a namespaced prefix (e.g., `"jepa"`, `"huggingface"`, `"onnx"`) to avoid collisions with future Core fields. Unknown extension keys MUST NOT invalidate a core-valid pack.

```json
"extensions": {
  "jepa": {
    "architecture_family": "jepa",
    "variant": "I-JEPA",
    "target_encoder": "ViT-H/16",
    "predictor": "narrow-transformer"
  }
}
```

---

## Integrity and Hashes

Artifact SHA-256 hashes declared in `manifest.json` or the `integrity` block allow consumers to verify file integrity before loading. For model checkpoints, verifying hashes is especially important before loading weights into an inference framework.

When weight files are not included in the pack (e.g., documentation-only or Native Mode packs), `sha256` fields on those artifact entries SHOULD be omitted rather than given placeholder values.

---

## Security Notes

- OKPF Core validation is offline-capable. Do not fetch remote schemas, weight registries, or model hubs during core validation.
- Model weight files are opaque to OKPF. OKPF does not execute, inspect, or verify the semantic content of weight files beyond declared SHA-256 hash integrity.
- Artifact paths are subject to the same safe-path requirements as all OKPF artifacts. Reject absolute paths, parent traversal, and Windows drive paths before reading archive entries.
- Do not auto-execute scripts referenced in provenance or evaluation artifacts. Packs are data, not executable trust boundaries.

---

## Example: JEPA Artifact Pack

`examples/jepa-artifact-pack/` demonstrates how a JEPA-family model's non-weight artifacts may be packaged in OKPF using Native Mode. It includes:

- `manifest.json` — package identity, artifact list, provenance reference, license, usage policy, and JEPA extension metadata
- `docs/model_card.md` — model card with intended use, limitations, and attribution
- `docs/limitations.md` — structured limitations summary
- `models/representation.json` — representation metadata: architecture summary, embedding dimensions, training objective
- `provenance/training_run.json` — placeholder training provenance record
- `evals/jepa_eval_report.json` — placeholder evaluation report with benchmark summaries

No model weights are included. All numeric values are illustrative placeholders, clearly marked as such. Validate the example pack:

```bash
python3 reference/python/okpf_validate.py examples/jepa-artifact-pack
```

---

*See also: `docs/ai-integration.md`, `docs/provenance.md`, `docs/packaging-modes.md`, `docs/security.md`*
