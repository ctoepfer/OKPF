# Blockchain Integration in OKPF

OKPF supports optional blockchain anchoring. This document explains what that means, what it is good for, and — equally importantly — what it is not good for.

---

## First: What OKPF Is Not

OKPF is **not** a blockchain project.

Blockchain is one of several optional mechanisms that can add verifiability to a knowledge pack. It is not required, not privileged, and not a core part of the format. A knowledge pack without any blockchain anchors is fully conformant and fully functional.

If you are evaluating OKPF and are skeptical of blockchain — that skepticism is compatible with using OKPF. The format is designed so that blockchain infrastructure is entirely optional.

---

## What Anchors Are

In OKPF, an **anchor** is a pointer from a knowledge pack to an external record. Anchors can point to:

- An IPFS CID (content-addressed storage)
- A blockchain transaction hash (any chain)
- A DOI (Digital Object Identifier, for academic packs)
- An arXiv preprint identifier
- A URL in a trusted registry

Anchors live in the `anchors` array in `manifest.json`:

```json
"anchors": [
  {
    "type": "ipfs",
    "value": "bafybeif...",
    "created": "2026-05-01T00:00:00Z",
    "note": "IPFS CID for the v0.1.0 .kpack archive"
  },
  {
    "type": "blockchain",
    "value": "0x1a2b3c...",
    "network": "ethereum-mainnet",
    "created": "2026-05-01T00:00:00Z",
    "note": "Transaction anchoring SHA-256 hash of manifest.json"
  }
]
```

---

## What Blockchain Anchors Provide

A blockchain anchor provides **external timestamping and immutability**. Specifically:

- **Proof of existence at a point in time** — If you record the hash of a pack on a blockchain at time T, you can later prove the pack existed in that exact form at T, even if the original storage is gone or compromised.
- **Tamper evidence** — If anyone modifies the pack after anchoring, the hash will no longer match the on-chain record.
- **Decentralized verification** — The anchor can be verified by anyone with access to the public chain, without trusting any central authority.

---

## What Blockchain Anchors Do Not Provide

Blockchain anchors do **not**:

- **Prove the content is accurate** — A blockchain confirms a file existed, not that its contents are correct.
- **Replace cryptographic signatures** — Signatures prove authorship; blockchain proves timing. They are complementary, not substitutes.
- **Guarantee availability** — The pack itself must still be stored somewhere accessible. IPFS or a registry handles this; the blockchain record only proves what was stored at a given time.
- **Require smart contracts** — OKPF anchoring is simply recording a hash on-chain. No smart contracts, tokens, or economic mechanisms are required or defined.

---

## Design Principles

OKPF's blockchain support is governed by these principles:

1. **Chain-agnostic** — OKPF makes no recommendation about which blockchain to use. The `network` field is a free-form string. Bitcoin, Ethereum, IPFS, Arweave, a private chain — all are equally valid.

2. **No on-chain logic** — OKPF does not define any smart contracts. Anchoring is a simple hash commitment, not a programmable protocol.

3. **Optional and additive** — Removing all anchors from a pack leaves a fully valid pack. Anchors cannot be required by the spec.

4. **Interoperable with IPFS** — Content-addressed storage (IPFS, Filecoin, or similar) is the most natural complement to OKPF blockchain anchoring, because it provides both availability and integrity.

---

## A Practical Anchoring Workflow

For those who want to use blockchain anchoring:

1. Create and finalize your knowledge pack
2. Compute the SHA-256 hash of the pack archive (`.kpack` file)
3. Store the pack in IPFS (get a CID)
4. Submit a transaction to your chosen blockchain recording the CID and/or hash
5. Add the IPFS CID and blockchain transaction hash to `manifest.json` as anchors
6. Re-pack the archive (note: the manifest now changes, so hashes change — anchor the original archive, then optionally anchor the final one too)

Tools to assist with this workflow are planned for the OKPF CLI (see [ROADMAP.md](../ROADMAP.md)).

---

## Community Considerations

OKPF does not endorse any specific blockchain network, token, or economic model. Community members who build tooling for specific chains are encouraged to build adapter libraries rather than requesting core OKPF changes.

If you are building a blockchain adapter for OKPF, see the `extensions` field in the manifest schema for namespace-keyed extension data.

---

## Summary

| Question | Answer |
|----------|--------|
| Is blockchain required? | No |
| Is blockchain recommended? | Optional, depends on use case |
| Which blockchain does OKPF support? | Any, or none |
| What does anchoring prove? | That a pack existed in a given form at a given time |
| Does anchoring prove accuracy? | No |
| Can I use OKPF without ever touching blockchain? | Yes, fully and completely |
