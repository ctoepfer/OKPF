<!-- SPDX-License-Identifier: Apache-2.0 -->

# Adoption Outreach Kit

This is tactical material for Phase 5 of the adoption plan (see
[docs/adoption-strategy.md](adoption-strategy.md)): things a human can
actually copy, paste, and post. It exists because getting a real external
user is the one part of this project's roadmap that can't be done by
writing more code — someone has to actually put the pitch in front of
people who might try it.

Nothing in this document claims adoption that hasn't happened. Fill in
the `[ ]` evidence log in `docs/adoption-strategy.md` only when something
real occurs.

---

## The elevator pitch

Use this as the connective tissue across any venue — adapt tone, keep the
substance:

> OKPF is a small, Git-friendly file format for packaging knowledge —
> human expertise, RAG source material, organizational know-how — with
> provenance, licensing, and validation built in. It's meant to be easier
> than inventing your own manifest, safer than a blind ZIP, richer than a
> bare JSONL file, and more predictable for AI/RAG ingestion than an ad
> hoc loader. `pip install`-able soon; usable from a source checkout
> today.

Do not claim: a platform, a marketplace, an AI model, a training
pipeline, or a finished standard. It's a file format and reference
implementation, pre-1.0, actively looking for real-world friction to
learn from.

---

## The 60-second proof (embed directly in posts)

```bash
git clone https://github.com/ctoepfer/OKPF && cd OKPF
python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

PYTHONPATH=reference/python python3 -m okpf init my-pack --template software-onboarding
PYTHONPATH=reference/python python3 -m okpf validate my-pack
PYTHONPATH=reference/python python3 -m okpf export-rag my-pack rag.jsonl
```

If asked "why not just a folder of Markdown files," the honest answer —
straight from [docs/benchmark-results.md](benchmark-results.md), run
against the flagship example — is:

```
attribution completeness:                  100%  (OKPF)   vs   0%  (Markdown folder)   vs   0%  (JSONL-only)
source lineage completeness:               100%  (OKPF)   vs   0%  (Markdown folder)   vs   0%  (JSONL-only)
ingestion decisions requiring guessing:       0  (OKPF)   vs   5  (Markdown folder)   vs   4  (JSONL-only)
```

Don't round these up or embellish them — they're pack-specific and
reproducible by anyone with `okpf benchmark`, which is exactly the point.

---

## Copy-paste posts

### Hacker News ("Show HN")

**Title:** `Show HN: OKPF – a Git-friendly file format for packaging knowledge with provenance built in`

**Body:**

> I've been building OKPF, an open file format for packaging structured
> knowledge — human expertise, RAG source material, local/organizational
> knowledge — so that license, provenance, and validation travel with the
> content instead of getting lost between a docs folder and whatever
> ingests it later.
>
> The concrete pitch: a `manifest.json` plus `artifacts/`/`records/`,
> validated locally (no network calls), packed as a plain ZIP
> (`.kpack`), and exportable to a documented JSONL contract for RAG
> pipelines (`okpf export-rag`) instead of an ad hoc loader guessing at
> field names.
>
> It's pre-1.0 and I'm specifically looking for people to try it against
> a real docs-folder-or-JSONL workflow and tell me where it falls short —
> the repo has an issue template for exactly that
> (`.github/ISSUE_TEMPLATE/adopter-feedback.md`).
>
> Repo: https://github.com/ctoepfer/OKPF
> 5-minute walkthrough: docs/five-minutes.md
> Honest scope limits: docs/when-not-to-use-okpf.md

### Reddit (r/LocalLLaMA, r/Rag, r/MachineLearning — adjust framing per sub's norms)

**Title:** `OKPF: an open packaging format for RAG source material with provenance/license baked in (looking for real feedback)`

**Body:**

> Most RAG pipelines ingest a folder of Markdown or a bare JSONL file and
> just... hope the license/source/attribution questions don't matter.
> OKPF is my attempt at a boring, Git-friendly alternative: a manifest +
> records format that validates offline, packs to a plain ZIP, and
> exports to a stable JSONL contract (`okpf export-rag`) that carries
> license, usage policy, provenance, and a deterministic chunk ID on
> every row — so a RAG loader isn't guessing.
>
> It's not trying to be a vector DB, an embedding format, or a platform —
> just the packaging layer underneath whatever you already use.
>
> If you've built a RAG pipeline and hit the "where did this chunk
> actually come from" problem, I'd genuinely like to hear whether this
> would have helped, or what it's missing. Issue template for feedback:
> `.github/ISSUE_TEMPLATE/adopter-feedback.md`.
>
> Repo: https://github.com/ctoepfer/OKPF

### Short form (Discord/Slack/X — under ~400 characters)

> Building OKPF: a Git-friendly file format for packaging knowledge
> (docs, RAG sources, org know-how) with provenance + license + validation
> built in. `okpf init/validate/export-rag` — offline, no platform. Looking
> for people to break it on a real workflow: https://github.com/ctoepfer/OKPF

---

## Where to point people, in order

1. Root [README.md](../README.md) — first-screen pitch and pack anatomy.
2. [docs/five-minutes.md](five-minutes.md) — the actual hands-on proof.
3. [docs/when-not-to-use-okpf.md](when-not-to-use-okpf.md) — send this
   proactively to anyone skeptical. Being upfront about when OKPF is
   overkill is more persuasive than not mentioning it.
4. [examples/software-onboarding/](../examples/software-onboarding/) — the
   flagship demo, per the adoption plan.
5. [docs/benchmark-results.md](benchmark-results.md) — real numbers, not
   claims, for anyone asking "why should I believe this helps."
6. [docs/historical-evidence-packs.md](historical-evidence-packs.md) —
   the most distinctive, least-generic example
   (`examples/local-history-lost-electric-sign/`) if someone's reaction to
   the RAG pitch is "isn't this just another RAG format."

---

## When feedback actually arrives

1. **Thank them and ask one clarifying question if the report is vague.**
   Specificity is what makes feedback usable — "the provenance format was
   too complex" is less useful than "I didn't understand why sources.json
   needed both source_id and path."
2. **Check it against `docs/adoption-strategy.md`'s success criteria** —
   does this report speak to attribution, lineage, ingestion ambiguity, or
   authoring overhead? File it against the matching benchmark question in
   `docs/benchmark-plan.md` if it's a measurable claim.
3. **If it reveals real friction, open a normal issue/task for the fix** —
   don't let feedback threads become the only record of a problem.
4. **Record it.** Add a line to the (currently empty, honestly so)
   evidence log in `docs/adoption-strategy.md`. Do not backfill entries
   that didn't happen — an honest empty log is worth more than a padded
   one.
5. **If they'll let you, ask if their example can become a real
   `examples/` pack** — a genuine external use case is worth more than
   another fictional one.

---

## See also

- [docs/adoption-strategy.md](adoption-strategy.md) — the thesis and success metrics this kit serves
- [docs/benchmark-plan.md](benchmark-plan.md) / [docs/benchmark-results.md](benchmark-results.md) — what to cite when asked for evidence
- [.github/ISSUE_TEMPLATE/adopter-feedback.md](../.github/ISSUE_TEMPLATE/adopter-feedback.md) — where real feedback should land
