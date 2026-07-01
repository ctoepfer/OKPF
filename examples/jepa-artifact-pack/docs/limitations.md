<!-- SPDX-License-Identifier: Apache-2.0 -->
# Known Limitations

> **Note:** This document is part of a non-normative OKPF packaging example. Limitations listed are illustrative of the type of content that would appear in a production model artifact pack.

---

## Architecture Limitations

- **No pixel-level reconstruction.** JEPA predicts in representation space, not pixel space. Downstream tasks requiring fine-grained pixel reconstruction (e.g., generative image inpainting as an end product) require a separate decoder head not included in the base architecture.
- **Masking strategy sensitivity.** Performance is sensitive to the choice of target mask scale and context mask ratio during training. Default hyperparameters may not transfer well to domains with significantly different spatial statistics than the training distribution.
- **Modality scope.** This example covers image representations (I-JEPA) only. Extension to video (V-JEPA), audio, text, or multimodal inputs requires separate architecture variants and is outside the scope of this pack.
- **Linear probing vs. fine-tuning gap.** Frozen-backbone performance on downstream tasks may be significantly lower than a fully fine-tuned counterpart, particularly for tasks with large domain shift from the pretraining distribution.

---

## Packaging Limitations (OKPF-Specific)

- **No weights included.** This pack contains representation metadata, training provenance, evaluation summaries, and model card documentation only. Model weights are not part of this OKPF artifact pack. OKPF does not define a weight serialization format.
- **Placeholder values.** All numeric results (benchmark scores, parameter counts, compute estimates, EMA decay, hyperparameters) are illustrative placeholders, not results from a real training run.
- **No inference runtime.** OKPF provides packaging, provenance, and metadata. It does not include or define an inference engine, serving runtime, framework-specific loader, or hardware backend.
- **SHA-256 hashes omitted.** This example omits per-artifact `sha256` declarations. A production pack SHOULD declare sha256 values for each artifact to support offline integrity verification.

---

## Provenance Limitations

- Training dataset is referenced by name in `provenance/training_run.json` but is not included, validated, or verified by this pack.
- OKPF Core validation checks pack structure and integrity hashes only. It does not verify the factual accuracy of provenance records, benchmark claims, or license assertions.
- Compute and duration estimates in `provenance/training_run.json` are illustrative and do not reflect a real training run.

---

## Evaluation Scope

- Benchmark results in `evals/jepa_eval_report.json` are placeholder values. Independent reproduction on the target model is required before any comparative use.
- Evaluation conditions (dataset splits, preprocessing, evaluation protocol) are described in summary form only. Full evaluation reproducibility requires the original evaluation scripts and dataset access.
- Out-of-distribution performance and failure modes are not characterized in this example.
