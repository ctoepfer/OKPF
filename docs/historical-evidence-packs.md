<!-- SPDX-License-Identifier: Apache-2.0 -->

# Historical Evidence Packs

OKPF started as a way to archive expertise for AI, but the same packaging
is equally suited to durable human knowledge archives — the kind of
archive that outlives whoever originally cared about the answer:

> OKPF is for the knowledge that disappears even when the documents survive.

A historical evidence pack preserves not only what is known, but *how* it
is known, what remains unknown, what has already been checked, and where
future research should continue.

This is a documented use case, not a new Core requirement. Nothing here
changes `SPEC.md` or the manifest schema — a historical evidence pack is
just an OKPF pack, authored with a particular discipline about uncertainty.

## Why this is different from "just write down what you know"

Most knowledge packaging formats implicitly assume the knowledge is
settled: here are the facts, here is the documentation. Historical
research is usually not settled. A single surviving source can attest to
some claims strongly, some weakly, and say nothing at all about most of
the questions a reader will actually have.

Historical packs preserve claims, sources, hypotheses, timelines,
locations, uncertainties, negative searches, and research leads. They are
most useful precisely when the trail is incomplete — which is the normal
condition for local and family history, not the exception.

They should distinguish between:

- **known** — established beyond the scope of this pack's own sources
- **source-attested** — directly supported by a specific cited source
- **probable** — a reasonable inference, not directly stated
- **disputed** — sources disagree
- **unknown** — no source in the pack addresses it
- **not-yet-checked** — a lead exists but hasn't been researched
- **checked-no-result** — a search was performed and found nothing

Collapsing these into a single "here's what happened" narrative is exactly
what turns a source-attested fact into an overclaim.

## Avoid turning absence of evidence into evidence of absence

If a pack contains no photograph of something, the correct claim is "no
photograph is currently known to this pack" — not "no photograph exists."
The same discipline applies to removal dates, maintenance records, or any
other fact a pack's sources simply don't cover. Historical evidence packs
should preserve open questions and dead ends as first-class content, not
as an implicit gap a reader is left to notice on their own.

## Why this matters for both humans and AI systems

A human researcher benefits from a pack that clearly separates "the
article says X" from "we assume X happened." An AI/RAG system benefits
even more, because it has no independent judgment about historical
plausibility — it will confidently state whatever the retrieved context
implies, including implications the source never actually made. A pack
that preserves uncertainty explicitly reduces accidental invention and
false certainty in both audiences.

## Example: the Bonita Avenue electric sign

A 1927 newspaper article says an electric sign was to be erected at
Bonita Avenue and San Dimas Avenue. The article provides source-attested
facts, but does not tell us whether the sign was actually installed,
photographed, maintained, or removed. An OKPF historical evidence pack can
preserve the clipping, transcription, extracted claims, open questions,
and future research leads without pretending the mystery is solved.

See [`examples/local-history-lost-electric-sign/`](../examples/local-history-lost-electric-sign/)
for the full worked example: a source image and transcription, structured
claim records with per-claim confidence, people/organization references, a
timeline that marks its own uncertainty, research leads, placeholder
negative-search records, and an eval set that specifically tests whether a
consumer respects the pack's documented uncertainty instead of inventing
a tidy ending.

## Future profile possibility

This document does not define a formal `historical-evidence` profile.
OKPF profiles are meant to emerge from convergent practice across several
real examples (see [docs/profile-authoring.md](profile-authoring.md)), and
right now there is exactly one example of this pattern in this repo.

If several historical/archival examples converge on the same shape, a
future `historical-evidence` profile could recommend a controlled set of
record types, such as:

```text
historical_claim
source_excerpt
evidence_item
timeline_event
location_reference
person_reference
organization_reference
hypothesis
counterargument
negative_search
research_lead
oral_history_note
uncertainty_note
```

Until then, these are conventions demonstrated by example, not
Core-enforced or profile-enforced vocabulary — consistent with OKPF's
general rule that domain conventions belong in profiles and examples, not
in Core.

## See also

- [`examples/local-history-lost-electric-sign/`](../examples/local-history-lost-electric-sign/) — the worked example
- [docs/provenance.md](provenance.md) — provenance and source modeling
- [docs/records.md](records.md) — the record shape used throughout
- [docs/rag-export.md](rag-export.md) — how historical claim records export for RAG/citation use
- [docs/profile-authoring.md](profile-authoring.md) — how a future profile would be proposed
