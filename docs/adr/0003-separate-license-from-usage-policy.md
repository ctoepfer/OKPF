# 0003: Separate License From Usage Policy

## Status

Accepted

## Context

Legal permissions and operational intent are related but not the same. AI systems and tools need machine-readable guidance, while legal terms still need clear license metadata.

## Decision

`license` records legal permission. `usage_policy` records machine-readable operational intent and constraints.

## Consequences

Consumers can inspect both fields. `usage_policy` does not replace legal review or override the license.
