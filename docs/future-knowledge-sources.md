<!-- SPDX-License-Identifier: Apache-2.0 -->

# Future Knowledge Sources

This document is guidance, not specification. It does not add, change, or
imply any new required field in OKPF Core, and nothing here is normative
for v0.1 conformance. It exists to name where OKPF is headed conceptually,
so that near-term profile and convention work (and the roadmap items in
[docs/phase-1-roadmap.md](phase-1-roadmap.md)) doesn't have to be invented
from scratch each time a new kind of knowledge shows up at the door.

---

## 1. Why OKPF Starts with Human Expertise

OKPF's first examples are human expertise: brewing process knowledge,
onboarding checklists, field repair procedures, local history. That choice
was not a scope limit — it was a starting point chosen because human
expertise makes the core problem visible without any extra machinery.

The core problem is this: **most knowledge documents preserve
instructions, not the judgment that makes the instructions usable.**

> "Bake until done" survives in a thousand recipe boxes. "Done means the
> edges pull slightly away from the pan and the top springs back when
> pressed" does not — because it lived in the baker's head, not on the
> card.

Call this the **small knowledge problem**: knowledge that disappears even
when the documents that reference it survive. It is not about losing
files. It's about losing the interpretation, the judgment calls, the
"you'll know it when you see it" that made the file usable in the first
place. A recipe card, a maintenance manual, a decision log — these persist
as artifacts long after the context needed to correctly interpret them has
evaporated.

There's a second, related failure mode, best illustrated by an object
rather than a document: the Roman dodecahedron. Hundreds of small,
hollow, twelve-sided bronze objects survive from the Roman Empire. The
artifacts are intact. What's missing is any surviving account of what they
were *for* — and two thousand years of hypotheses (candlesticks, dice,
survey tools, knitting aids, religious objects) have failed to close that
gap because no one preserved the use-context alongside the object. Call
this the **Roman dodecahedron problem**: having the artifact or the data,
but losing the interpretation that would make it legible.

OKPF Core exists to prevent the small-knowledge problem for human
expertise: a manifest, records, provenance, license, and usage policy that
travel together so the judgment survives with the instruction. Everything
in this document is about the same failure mode showing up in new places
— AI-generated content, lab instruments, hybrid human/AI workflows,
non-human behavior — and asking what it would take to not repeat the
dodecahedron's mistake there too.

---

## 2. Why Provenance Must Expand Beyond Human Authorship

OKPF's current provenance model (see [docs/provenance.md](provenance.md))
was designed with a human author in mind: a person wrote or transcribed
something, and a source entry records where it came from. That model
still works. It stops being sufficient the moment a knowledge claim passes
through more than one *kind* of actor before it reaches a reader.

A single modern knowledge-production loop might involve a person framing
a question, an AI system drafting a candidate answer, a piece of lab
hardware producing a measurement that confirms or refutes it, and a person
again reviewing the result. None of those four steps is illegitimate. What
would be illegitimate is packaging the final claim as if a human wrote it
end to end, or as if it sprang fully formed from a model with no human
review, or as if a sensor reading were self-interpreting.

The fix is not a new required field. It's widening what a provenance
entry is *allowed* to name as a contributor, using a `role` that
distinguishes the kind of actor involved:

```json
{
  "source_id": "hvac-diagnostic-2026-04-hybrid",
  "path": "sources/compressor-fault-investigation.md",
  "format": "markdown",
  "title": "Compressor short-cycling — hybrid diagnostic trace",
  "contributors": [
    {
      "role": "human",
      "name": "J. Alvarez",
      "contribution": "Framed the fault symptoms and reviewed the final diagnosis."
    },
    {
      "role": "ai_system",
      "name": "diagnostic-assistant-v3",
      "contribution": "Proposed three candidate root causes ranked by likelihood."
    },
    {
      "role": "instrument",
      "name": "clamp-meter-fluke-376",
      "contribution": "Logged compressor amperage draw during the short-cycling event."
    }
  ],
  "license": {
    "type": "CC-BY-4.0"
  },
  "notes": "Root cause confirmed by matching AI-proposed hypothesis #2 against clamp-meter readings."
}
```

`role` here is an open string, the same way `record_type` and facet keys
are open elsewhere in OKPF Core — not a fixed enum, so a profile or a
single pack can introduce `simulation`, `historical_document`,
`peer_reviewer`, or whatever actor kind actually contributed, without
touching Core. What changes is the *expectation*: a hybrid provenance
entry should say which kind of actor did which part, not just that
"something" produced the artifact. That's the whole fix. It's additive to
the existing source-entry shape in docs/provenance.md, not a replacement
for it.

---

## 3. Knowledge Formation Traces

A **knowledge formation trace** is a record of how a specific claim,
example, rule, technique, or hypothesis came to exist in its current
form: created, transformed, reviewed, tested, accepted, rejected, or
revised, across however many steps and however many kinds of actors that
took.

This is a superset of what `provenance/transformations` already does in
today's packs (see the `brewing` example's `provenance.json`) — the
extension is that a formation trace is expected to survive **loops**, not
just linear pipelines. Two examples:

**Human → AI → hardware → human, repeated.** A technician suspects a
failing sensor. An AI system proposes a replacement part. The part is
installed; a follow-up sensor log either confirms or contradicts the
fix. If it contradicts, the loop repeats with the new evidence folded in.
The final record's formation trace isn't "AI generated this" — it's the
whole sequence of proposal, test, and revision, including the discarded
first hypothesis. Throwing away the discarded hypothesis is exactly how
the small-knowledge problem starts over: the next person hits the same
dead end because nobody kept the trace of it being a dead end.

**Human ⇄ AI drafting loop.** A brewer describes a fermentation problem in
plain language. An AI system drafts a structured troubleshooting record.
The brewer corrects two facets and rewrites one sentence because the
draft overstated confidence. The corrected version is what ships — but
the trace of *what the AI got wrong* and *what the human fixed* is itself
useful knowledge for anyone tuning that AI system later, and for any human
deciding how much to trust unreviewed output from it next time.

A formation trace does not need a new manifest field to exist today —
`provenance/transformations` entries with `input_sources`,
`performed_by`, and a `description` per step already express most of
this, and the [human-correction-loop profile](../profiles/human-correction-loop/v0.1.0/)
already demonstrates a two-step version of it. What's new here is naming
the general pattern so future profiles don't reinvent it per domain: a
trace is a sequence, it may loop, and no step in it should be silently
dropped just because a later step superseded it.

---

## 4. AI-Generated and Synthetic Knowledge

Synthetic knowledge — content an AI system generated, whether a design
candidate, a simulated outcome, a drafted explanation, or a proposed
fix — is not a problem for OKPF to solve away. It's a category OKPF needs
to be honest about carrying.

The danger isn't AI-generated content existing. The danger is
**unprovenanced synthetic content indistinguishable from reviewed human
knowledge** — a model's unverified guess, sitting in the same record shape
as a technician's twenty years of field experience, with nothing to tell
a future reader (human or model) which is which. That's how confident
nonsense launders itself into "established knowledge": not through malice,
but through missing metadata.

The mitigation is a small set of optional, recommended fields — not new
Core requirements, but a convention worth adopting deliberately wherever
synthetic content is present:

- **`origin_type`** — where the record's content actually came from:
  `human_authored`, `ai_generated`, `ai_assisted`, `instrument_generated`,
  `derived`, or a domain-specific value. Open string, same pattern as
  `record_type`.
- **`review_status`** — has a human looked at this: `unreviewed`,
  `human_reviewed`, `human_corrected`, `auto_accepted`.
- **`validation_status`** — has the claim been checked against anything
  external: `unvalidated`, `validated_against_source`,
  `validated_empirically`, `contradicted`.
- **`generation_context`** — free-form or structured note on what
  produced it: model/system name, prompt or task framing, and date.

None of these are required today, and none change what makes a pack Core
valid. What they buy, when used, is the ability for a consumer — human or
automated — to filter or weight records by how much scrutiny they've
actually received, instead of assuming a record schema equals a truth
guarantee. See also [docs/training-ready-derivatives.md](training-ready-derivatives.md),
which already carries a version of this discipline for training-data
derivatives specifically (declared transformations, filtering, and known
limitations); this section generalizes the same instinct to any synthetic
record, not just ones destined for a training set.

---

## 5. Empirical Discovery Packs

Empirical discovery is knowledge produced by observation and measurement
before it has hardened into settled fact: lab notebooks, brewing trial
logs, sensor time series, materials-testing runs. The failure mode unique
to this category is **flattening a single data point into a general
claim** — reporting "this alloy fails at 340°C" from one test run, when
what actually happened is one sample failed at 340°C under one specific
load profile, once.

A concrete pair of examples:

**Brewing trial.** A brewer runs a fermentation at three different
temperatures to compare ester production. The honest record is three
`evidence_item`-shaped entries — each with the specific batch,
temperature, and measured result — plus, separately, a
`derived_summary` record that says "cooler fermentation produced
noticeably fewer esters across these three trials," explicitly linked
back to the three source records it was derived from. What must not
happen is the summary replacing the trials in the pack, because a future
reader re-running the comparison needs the raw trials, not just the
conclusion someone drew from them once.

**Materials testing.** A single tensile-strength test on one sample
lot is evidence, not a spec. Packaging it as
`{"record_type": "evidence_item", "facets": {"sample_size": 1, "conditions": "..."}}`
alongside the actual measurement preserves exactly what was measured and
under what conditions. Packaging it as
`{"record_type": "instruction", "text": "This alloy fails at 340°C"}`
erases the conditions and invites someone to rely on a claim the data
never supported.

The pattern in both cases is the same: keep raw observations as their own
records, keep derived conclusions as their own records, and link the
derived record back to what it was derived from
(`metadata.derived_from` or an equivalent explicit pointer — the same
shape [docs/training-ready-derivatives.md](training-ready-derivatives.md)
already uses for derivation reports). A future `empirical-discovery`
profile (see §8) could eventually recommend `evidence_item` and
`derived_summary` as controlled record types for this purpose. Nothing
about doing this well requires that profile to exist first — it's a
packaging discipline, available today with `record_type` and `facets`
alone.

---

## 6. Non-Human Biological Observation Packs

This is the most speculative category here, and it's included narrowly
and cautiously on purpose: **structured observation of non-human
behavior — animal behavior, plant signaling, microbial adaptation — is a
legitimate knowledge domain, and OKPF should not need a redesign to carry
it.** What OKPF must not do is imply that packaging an observation is the
same thing as claiming to understand the intelligence, if any, behind it.

An ethogram (a catalog of observed behaviors) is a well-established
research tool precisely because it stays disciplined about this
boundary: it records "individual performed action X under condition Y,"
not "individual intended Z" or "individual understands W." OKPF's role
here is packaging, not zoology or botany — the same
`record_type`/`facets`/`metadata` shape used everywhere else, applied with
the same discipline an ethogram already enforces:

```json
{
  "id": "obs-corvid-tool-use-014",
  "record_type": "observation",
  "title": "Tool selection behavior, field session 14",
  "text": "Individual selected a hooked twig over three straight twigs available in the same location before extracting food from a crevice.",
  "domain": "animal-behavior",
  "facets": {
    "species": "Corvus moneduloides",
    "behavior_category": "tool_use",
    "interpretation_status": "observation_only"
  },
  "metadata": {
    "observer": "field-note-014",
    "location_context": "controlled field enclosure",
    "caveats": "Single observation; not compared against a control condition."
  }
}
```

No OKPF field should assert cognition, intent, or comprehension on the
observed organism's part — `record_type: "observation"` plus factual
`text`, not `record_type: "insight"` with an inferred motive. Where a
researcher wants to record an interpretation or hypothesis about *why*
the behavior occurred, that belongs in a separate, clearly-marked
`hypothesis` record (§8's epistemic status list) linked to the
observation it's interpreting — never merged into the observation itself.
This category stays structured and small until real examples exist to
generalize from; see §8 on why a formal profile isn't proposed yet.

---

## 7. What Belongs in Core Now

Nothing in this document changes OKPF Core v0.1. Core stays exactly what
[SPEC.md](../SPEC.md) and [schemas/v0.1.0/manifest.schema.json](../schemas/v0.1.0/manifest.schema.json)
already say it is: a manifest, at least one of `artifacts`/`records`/
`content`, license and usage policy metadata, and optional provenance —
domain-neutral, with `additionalProperties: true` throughout so none of
the conventions above ever invalidate a pack that doesn't use them.

Concretely, what's usable **today**, with zero schema changes:

- This document itself, as conceptual orientation.
- Hybrid provenance entries using an open `role` string per contributor
  (§2) — already legal under the existing provenance source-entry shape.
- Formation-trace-style `provenance/transformations` sequences (§3) —
  already legal, just not yet named as a pattern.
- `origin_type`/`review_status`/`validation_status` as record-level
  `metadata` or `facets` keys (§4) — already legal as unknown-but-tolerated
  fields.
- Empirical evidence/summary record pairs with explicit `derived_from`
  linkage (§5) — already legal, same mechanism
  `training-ready-derivatives.md` uses today.
- Disciplined `observation` records for non-human behavior (§6) — already
  legal, no new record type required.
- New example packs and working-knowledge-gap documentation demonstrating
  any of the above.

None of this requires a validator change. It requires authors to *choose*
these conventions, and future docs/examples to demonstrate them clearly
enough that they become common practice before they become a profile.

---

## 8. What Belongs in Future Extensions

Roughly in the order they're likely to matter, and none of them committed:

**Soon (optional, additive, no profile required):**
- Documented `origin_type` and `epistemic_status` conventions with a
  recommended (not required) vocabulary — the natural next step after
  this document, once a few real packs use the fields inconsistently
  enough to show what needs standardizing.
- `okpf lint`-style warnings (distinct from `okpf validate`'s pass/fail
  correctness checks) that flag a pack for *missing* provenance,
  missing `known_limitation` records, or synthetic-looking content with
  no `origin_type` declared — advisory, not blocking.

**Later (formal, opt-in profiles — see [docs/profile-authoring.md](profile-authoring.md)):**
- An `empirical-discovery` profile recommending `evidence_item` and
  `derived_summary` as controlled record types (§5).
- A `synthetic-knowledge` profile formalizing `origin_type`,
  `review_status`, and `validation_status` as recommended facets (§4).
- A `historical-evidence` profile (already sketched in
  [docs/historical-evidence-packs.md](historical-evidence-packs.md),
  which this document deliberately parallels — evidence, hypothesis, and
  uncertainty preservation are the same underlying problem showing up in
  two domains).
- Cryptographic attestations for formation-trace steps, once signing
  exists in OKPF at all (`signatures[]` is already sketched as a future
  Core-adjacent capability elsewhere; none of this document depends on it
  arriving first).

**Explicitly not proposed, here or later, as Core:**
- A universal ontology of "what knowledge is" — OKPF packages knowledge,
  it does not adjudicate epistemology.
- Mandatory registries for any of the categories above.
- DRM or enforcement mechanics tied to provenance or authorship role.
- A biological/behavioral schema standard — §6 is packaging guidance, not
  a proposal to formalize ethology.

An **epistemic status** convention deserves naming explicitly, since it
cuts across every category above: a recommended, non-mandatory
classification for what kind of claim a record actually is —
`observation`, `instruction`, `heuristic`, `claim`, `hypothesis`,
`example`, `counterexample`, `evaluation`, `correction`,
`derived_summary`, `synthetic_output`, `validated_result`,
`known_limitation`. Like `record_type` and `role`, this is an open,
recommended vocabulary, not a closed enum enforced by Core — its value is
in giving authors and future profiles a shared starting point instead of
each domain inventing its own status words from nothing.

---

## 9. Risks and Mitigations

Being honest about what expanding into these categories can go wrong is
part of the same discipline this document is arguing for.

**Hallucinated knowledge treated as fact.** An AI-generated claim, once
packaged in the same record shape as reviewed human expertise, is
visually indistinguishable from it. *Mitigation:* `origin_type` and
`review_status` (§4) exist specifically to prevent this — but only if
authors actually set them. A pack with synthetic content and no
`origin_type` is not lying, but it is silent in exactly the place silence
is most costly. Future `okpf lint` warnings (§8) are aimed at this gap.

**Knowledge laundering.** A claim passes through enough transformation
steps that its actual origin (a single unverified AI guess, an
uncontrolled experiment, a single anecdote) gets lost, and it emerges
looking like consensus. *Mitigation:* formation traces (§3) exist to make
laundering visible rather than to prevent it outright — a trace that
skips steps is itself a signal worth distrusting, but only if the
convention of keeping traces intact is actually followed.

**False authority from clean packaging.** A well-formed OKPF pack, with a
tidy manifest and confident record schema, can look more authoritative
than its actual evidence supports — the packaging itself becomes a
credibility signal independent of content quality. *Mitigation:* this is
exactly why `known_limitation` and `unvalidated` exist as first-class
epistemic statuses (§8) rather than being omitted for looking bad. A
pack that clearly marks its own weak spots is more trustworthy than one
that has none to show, not less.

**Ownership and rights confusion in hybrid provenance.** Once
`ai_system` and `instrument` are legitimate contributor roles (§2),
questions about who owns or can license the resulting knowledge get
harder, not easier. *Mitigation:* OKPF does not resolve authorship-rights
law and should not try to. `license` and `usage_policy` remain the
pack's operative permission statements regardless of how many
contributor roles are listed; hybrid provenance records *who did what*,
it does not adjudicate *who owns what*. Packs with genuinely unresolved
rights questions should say so in `expert_notes` or an equivalent
human-authored caveat, not paper over the ambiguity with a clean-looking
contributors list.

None of these risks are fully solved by adding fields. Fields only work
if the discipline behind them — declare uncertainty, keep the trace,
don't flatten evidence into claims — is actually practiced. That
discipline is the actual subject of this document; the fields are just
where it becomes visible in a pack.

---

OKPF preserves knowledge with its working context: sources, structure,
provenance, rights, evidence, limitations, and evaluation hooks, so
future humans and machines can inspect, reuse, challenge, and extend it.

OKPF is for the knowledge that disappears even when the documents
survive — and for the new kinds of knowledge whose origins, evidence, and
limits must not disappear as they move between humans and machines.
