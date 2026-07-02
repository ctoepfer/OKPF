<!-- SPDX-License-Identifier: Apache-2.0 -->

# Local History: The Lost Electric Sign

This pack demonstrates historical evidence preservation. It does not claim
to prove the full history of the sign it documents.

It preserves a source clipping, a transcription, structured claims, open
questions, research leads, and placeholder negative-search records. It
shows how OKPF can preserve incomplete evidence trails without forcing
false certainty.

## The story

A June 29, 1927 article in *The Pomona Progress* (Pomona, California, page
5) reports that the San Dimas chamber of commerce decided to erect an
electric sign — donated by William McNeil of Charter Oak — at the corner of
San Dimas Avenue and Bonita Avenue. A committee of John Campbell and L. R.
Belknap was appointed to handle installation, with an estimated $10/month
electricity cost. The article discusses placing the sign diagonally so it
could be seen from both streets.

That is where the documented trail in this pack ends. No photo, removal
date, maintenance record, or confirmation of final placement is known to
this pack. What happened to the sign is an open question.

## What's in this pack

```text
manifest.json                        identity, license, usage policy
README.md                            this file

sources/newspaper-clipping/
  bonita-electric-sign-article.jpeg  the original clipping image
  bonita-electric-sign-article.txt   plain-text transcription

artifacts/
  article-transcription.md           presented transcription + citation
  research-summary.md                known vs. unknown, and what this pack does NOT claim
  location-analysis.md               the reported location and the open orientation question
  unanswered-questions.md            the open research questions

records/
  source-excerpts.jsonl              the source excerpt as a structured record
  claims.jsonl                       7 source-attested historical claims
  people-organizations.jsonl         people, organizations, and the publication
  timeline.jsonl                     known/approximate/unconfirmed events
  research-leads.jsonl               8 candidate next research steps
  negative-searches.jsonl            placeholders for "checked, no result" tracking

provenance/
  sources.json                       provenance entry for the clipping
  transcription-notes.json           transcription method and limitations
  search-log.json                    placeholder search log

evals/
  historical-research-questions.json questions testing whether a consumer respects the pack's uncertainty
```

The teaching pattern:

```text
original image source → transcription → structured claim records → research leads → open questions
```

## Why this matters

OKPF started as a way to archive expertise for AI, but the same packaging
also works as a durable human knowledge archive — the kind of thing that
outlives whoever originally cared about the answer. One way to put it:

> OKPF is for the knowledge that disappears even when the documents survive.

A historical preservation pack like this one preserves not only what is
known, but *how* it is known, what remains unknown, what has already been
checked, and where future research should continue. See
[docs/historical-evidence-packs.md](../../docs/historical-evidence-packs.md)
for the broader use case this example demonstrates.

## Try it

```bash
PYTHONPATH=reference/python python3 -m okpf validate examples/local-history-lost-electric-sign
PYTHONPATH=reference/python python3 -m okpf inspect examples/local-history-lost-electric-sign
PYTHONPATH=reference/python python3 -m okpf export-rag examples/local-history-lost-electric-sign out/local-history-rag.jsonl
```

## What this pack is not

This is a fictionalized-but-source-grounded example built for OKPF format
demonstration. It is not a peer-reviewed local history publication, and its
placeholder research/search-log entries do not represent an exhaustive
historical investigation — see
[`artifacts/research-summary.md`](artifacts/research-summary.md) for the
explicit list of what this pack does not claim.
