<!-- SPDX-License-Identifier: Apache-2.0 -->
# FLOSS maintainer succession: reference-pack candidate

**Coding status: `pending_dual_review`. Five AI-authored sourced drafts, awaiting independent dual coding.** This is
not a dual-coded reference corpus or a representative denominator. The user
explicitly selected draft preparation for dual review. Do not promote this pack
by changing a metadata label alone.

| Case | Actual episode scope | Evidence limit |
|---|---|---|
| Event-stream | Reported adversarial maintainer handoff | Registry account; private handoff and losses unmeasured |
| OpenSSL | Heartbleed disclosure and later capacity-funding account | Security disclosure plus organizational retrospective, not a succession post-mortem |
| Log4j | Iterative security remediation | Historical December 2021 account; no population remediation census |
| Core-js | Maintainer sustainability account | First-person appeal, not verified collapse or succession |
| Urllib3 | Planned v2 version migration | Limited contrast; neither smooth leadership succession nor universal migration success established |

Sources are primary reports or versioned project documentation, cited in each
case with locators, access dates and availability. Only original summaries are
packaged; third-party source bodies remain under their own terms. Bibliography
links may change; this pack is citation-only and does not freeze their contents.

All five records exercise `perspectives`, `unobserved_variables`, `evasion_vectors`
and `pre_mortem_falsification`. The last two remain **optional** in institutional
v1; populating them here does not change the profile or Core contract.

Every pre-mortem block is an explicitly **proposed retrospective exercise**, not
an observed historical commitment, recommendation, or calibrated threshold.
Event-stream's evasion record separates the reported deception from its analyst
category. Other evasion entries are explicitly **hypothetical, not observed**;
they are prospective review questions and do not allege misconduct by those
projects. Their source-reference arrays are empty intentionally. Consumers must
retain `epistemic_status` rather than count all five as observed evasion events.
Unknown custody, counts, governance details and outcomes remain unknown.

`review/dual-coding-status.json` records zero completed independent codings and
lists promotion requirements. Each independent coder should produce a dated,
source-located field-level coding without seeing the other's labels; retain both
versions, disagreements, reconciliation decisions and dissent. No second coder,
consensus, inter-rater score or independent review has been fabricated.
`coding_standard: single_coder` denotes one AI drafting pass under the existing
enum; the adjacent status fields make clear that no human coding is claimed.

Build a **draft** archive from the repository root:

```bash
okpf validate examples/floss-maintainer-succession --strict-profile
okpf pack examples/floss-maintainer-succession out/floss-maintainer-succession.kpack
okpf-mcp --pack out/floss-maintainer-succession.kpack
okpf-tool review --pack out/floss-maintainer-succession.kpack \
  --proposal examples/floss-maintainer-succession/proposals/npm-release-council.md
```

The archive filename is stable for convenience; its manifest version and review
status explicitly say draft. The pack command validates structure, not dual-review
completion. Publication or promotion requires a separate human decision.

The synthetic proposal and semantic commitment are tooling exercises, not case
evidence. `semantics/release-review.json` and its retained baseline demonstrate
change detection with `okpf-tool check-semantics`; they do not authenticate history
or execute a review/rollback. See `docs/extensions/semantic-invariants-draft.md`
in the repository for the threat model.
