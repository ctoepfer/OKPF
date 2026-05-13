# 0004: Use JSON Schema for Manifest Validation

## Status

Accepted

## Context

OKPF should be implementable across languages and tools. Manifest validation should not depend on a reference implementation.

## Decision

OKPF uses JSON Schema for manifest validation. Versioned schemas live under `schemas/v0.1.0/`.

## Consequences

Implementers can validate manifests with standard tooling. The schema captures structure, while the prose specification remains the normative human-readable source.
