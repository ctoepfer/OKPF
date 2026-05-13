# 0002: Keep Blockchain Optional

## Status

Accepted

## Context

Some future OKPF ecosystems may want timestamping, ownership proofs, royalties, or registry anchoring. The core format must remain vendor-neutral and infrastructure-neutral.

## Decision

Blockchain anchoring is not required for OKPF v0.1.0. Future extensions may reference chains, ledgers, or registries, but a basic pack must work offline without them.

## Consequences

OKPF can support blockchain-adjacent workflows without becoming a blockchain project.
