<!-- SPDX-License-Identifier: Apache-2.0 -->

# Compatibility review of RAG and boundary-transition proposals

Status: documentation-only designs, as explicitly selected by the user on
2026-11-10. These are not adopted schemas or implemented commands.
These proposals do not modify the frozen study, its rubric, or its results.
OKPF remains a general-purpose knowledge packaging format. Institutional analysis
is one optional profile, not the identity or purpose of OKPF Core.

## Optional retrieval cache

An existing experimental extension already addresses this space:
[`okpf.semantic_retrieval.v0`](../../../extensions/semantic-retrieval.md).
Prefer extending that design deliberately over silently introducing a competing
`okpf.ext.rag.v1` contract. No namespace migration is decided here.

- Core manifests use `okpf_version: "0.1.0"`, `package_id` (or retained `id`),
  object-valued `license`, required package metadata, and at least one declared
  payload. `pack_id` and `1.0.0` do not satisfy current Core. `profiles` is the Core
  declaration; the institutional tooling also recognizes a profile-specific
  singular field. Preserve existing aliases and unknown optional metadata.
- Canonical means authoritative for the pack version, not factually true or
  necessarily human-authored. Signatures, content addressing, embeddings and
  particular source directories remain optional. Signatures need an external
  trust policy and do not certify factual accuracy.
- Use existing SHA-256 conventions for a compatible first design. BLAKE3 would
  require an explicit optional extension algorithm contract; do not put it in
  Core's SHA-256-only integrity field or imply a Core requirement.
- Bind each cache to a sorted source-file inventory with exact byte hashes,
  projection version/parameters, chunk identities and cache-file hashes. A bare
  directory digest needs a precisely specified serialization. Verify chunk
  projection reproducibility separately from vector provenance and compatibility.
- Model name and dimension alone are insufficient compatibility metadata. Pin
  model/tokenizer revisions, preprocessing, normalization, numeric representation,
  distance metric and row-to-chunk mapping. A matching file hash does not prove
  that a vector was correctly computed from its claimed text. Numerical rebuilds
  may need declared tolerances rather than promises of bitwise determinism.
- Reject unsafe paths before reading files; bound parsing/resource usage and
  reject duplicate/missing mappings. Do not execute serialized index code or
  retrieve models automatically. Invalid caches can be bypassed; rebuilding uses
  an explicitly configured local backend and an explicit user action.
- A memory-mapped index still incurs verification, metadata and I/O costs; no
  zero-millisecond latency is supported. Hash binding detects mismatched bytes,
  not malicious but consistently hashed content or prompt injection. Treat all
  retrieved content as untrusted data.
- Preserve license, operational usage policy, attribution, provenance, uncertainty
  and correction links in projections. Do not promote analyst interpretations to
  consensus or invent source facts while rendering chunks.

The pasted event-stream projection contains historical assertions not established
by this compatibility review. It is not a replacement for sourced case records.
`rag build` and `rag verify` remain proposed commands, not existing capabilities.
The current semantic-retrieval document's illustrative manifest also needs a
separate correction: its string license and absent declared payload do not form
a complete Core-valid manifest. No normative source was edited in this pass.

## Optional institutional boundary transitions

`boundary_transitions` is a reasonable proposed name for explicit transfers of
function, custody, state and accountability. It belongs in an optional profile
field or a separately versioned extension, not in required Core fields.

A future design should distinguish source and target roles, transferred function,
payload, acceptance gate, accountability during the interval, feedback path and
latency, semantic/units mappings, and retained or lost context. Each claim needs
source references, observation dates, epistemic status and unknown values.
Separate stated rules from reported practice and independent observation.

Absence of a recorded acceptance gate does not prove there was no gate. Do not
infer legal liability, actual access rights, an NDA, or security credentials from
an analyst category. Failure-mode categories should remain extensible, with
profile diagnostics expressed as missing/unknown/mismatch findings rather than
proof of historical causality or successful intervention.

The shelter example is illustrative, not an observed incident or justification
for disclosing sensitive client data. Any field-level privacy constraints need to
be retained through projections. Claims that failures almost always occur at
boundaries, or that a stated percentage of engineers misunderstand a term, are
unsupported here and should not enter normative prose. The proposed historical
attribution to specific systems-engineering manuals also needs source verification
before publication as fact.

Scope decision: document compatible designs separately and keep the frozen
evaluation unchanged. Implementation is outside this pass. No schema, pack,
retriever, MCP endpoint, CLI contract or evaluation measurement was changed.
