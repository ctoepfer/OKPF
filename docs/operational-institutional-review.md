<!-- SPDX-License-Identifier: Apache-2.0 -->
# Experimental operational review through MCP

Install both repository packages as described in [MCP setup](mcp-setup.md).
The optional adapter now also installs `okpf-tool`; it does not replace the
reference `okpf review` or `okpf lint-proposal` commands.

```bash
okpf-tool review \
  --pack examples/floss-maintainer-succession \
  --proposal examples/floss-maintainer-succession/proposals/npm-release-council.md

okpf-tool review \
  --pack out/floss-maintainer-succession.kpack \
  --proposal examples/floss-maintainer-succession/proposals/raw-npm-proposal.md \
  --limit 5 --json
```

Build the archive first with `okpf pack`; see the
[draft pack README](../examples/floss-maintainer-succession/README.md).
Repeated `--pack` arguments mount multiple roots/archives. The consumer launches
only its own installed `okpf_mcp.server` through Python and MCP stdio. It does not
execute a server command from a pack or proposal. Stdio uses process pipes, not a
network socket. Runtime requires no network or model provider.

The consumer calls the catalog, structural query, case inspection, evasion audit,
and authored-criteria tools. Every call's arguments, result counts, warnings,
errors and truncation status appear in the report. The catalog carries rights and
provenance metadata; cases retain source references, paths, field pointers,
uncertainty, coding status, and synthetic/hypothetical qualifications.

## Classification and retrieval

Explicit YAML front matter (or the existing review parser's simple declarations)
provides asserted invariants. Free prose supplies **lexical resource hints only**:
npm/JavaScript/Node.js, Python/urllib3/PyPI, Java/Log4j/Maven, or OpenSSL/libssl.
Negated, quoted and hypothetical mentions can trigger these hints; the report
says so. No hint becomes an asserted custody, authority, exit-cost or feedback
classification. JSON/YAML proposal files are also accepted by the existing parser.

An explicit resource type takes precedence over hints. Each resource and any
explicit domain selects candidates through exact MCP filters. Multiple hints
form a bounded union, not a similarity score. Other declared invariants are
compared after retrieval so disagreements remain visible. A known difference is
`mismatch`; an absent or unknown value is `unavailable`, never agreement. With no
usable resource/domain filter, the consumer abstains instead of classifying an
arbitrary proposal or dumping the corpus.

The initial candidate and optional-data queries each request at most 100 rows.
Selected cases are ordered by package ID, version, mount reference and case ID;
`--limit` accepts 1–20. The server's byte limits still apply. A separate complete
inspection is requested for each selected case. Evasion vectors and authored
criteria are joined by both mount reference and case ID. Truncated global optional
data may omit a selected case's vector; the audit records that limitation rather
than implying absence. Cases are records, not independent precedents.

## Lint and epistemic limits

The existing proposal linter checks structured evasion/pre-mortem blocks. A raw
proposal can therefore retrieve candidates **and still fail lint**. Exit 0 means
structural lint success, exit 1 means missing/malformed commitments, and exit 2
means input or transport/tool failure. A successful lint is not deployment approval.
Output is Markdown by default and JSON with `--json`; diagnostics remain on stderr.
Proposal input is limited to 2 MiB; calls use timeouts.

The draft corpus's hypothetical vectors are prospective review questions, not
observed misconduct. Its pre-mortem criteria were authored retrospectively and
are not universal benchmarks or historical commitments. Review output preserves
these labels. The consumer neither executes off-ramps nor claims causal validity,
independent coding, verified signatures, or successful interventions.

The separate [semantic commitment checker](extensions/semantic-invariants-draft.md)
can detect changes against a supplied baseline. It is not automatically applied
by the review command and does not prove semantic stability.
