# 0001: Use ZIP-Based `.kpack` Archives

## Status

Accepted

## Context

OKPF packages need to be portable, inspectable, and easy to create with existing tooling.

## Decision

`.kpack` archives are ZIP files with safe relative paths. Directory packages use the same layout for authoring.

## Consequences

ZIP keeps the format simple and widely supported. Validators must reject unsafe archive paths such as absolute paths or `../` traversal.
