<!-- SPDX-License-Identifier: Apache-2.0 -->
# Optional OKPF MCP adapter

`okpf-mcp` is a repository-maintained, read-only stdio consumer adapter. It does
not change OKPF Core or require MCP dependencies for other OKPF tools. The Python
>=3.11 package lives in `packages/okpf-mcp/` and uses the **official** Python MCP
SDK's `mcp.server.fastmcp.FastMCP` (`mcp>=1.30,<2`, tested at 1.30.0), not the
separate `fastmcp` distribution. The upper bound retains the SDK interface used
here. No additional signature-verification dependency is declared; the SDK may
itself install cryptographic libraries for its other transports.

## Install and launch

From the repository root, install **both local projects** into a dedicated
virtual environment:

```bash
python3 -m venv /tmp/okpf-mcp-env
/tmp/okpf-mcp-env/bin/python -m pip install ./reference/python ./packages/okpf-mcp
/tmp/okpf-mcp-env/bin/okpf-mcp --pack /absolute/path/to/OKPF/examples/institutional
```

Replace `/absolute/path/to/OKPF` with your checkout location. The installed server
can run from any working directory; it does not use PYTHONPATH, editable installs,
or repository-relative imports. The reference wheel supplies runtime schemas.
`okpf==0.0.1` is a dependency on **this repository's reference package**: always
supply it explicitly as a local project or wheel. Do not install the adapter alone
and allow pip to satisfy that name from a public registry. For wheel deployment:

```bash
python3 -m pip install build
python3 -m build --wheel --outdir /tmp/okpf-wheels ./reference/python
python3 -m build --wheel --outdir /tmp/okpf-wheels ./packages/okpf-mcp
/tmp/okpf-mcp-env/bin/python -m pip install \
  /tmp/okpf-wheels/okpf-0.0.1-py3-none-any.whl \
  /tmp/okpf-wheels/okpf_mcp-0.1.0-py3-none-any.whl
```

Installation/build isolation may download dependencies. **Server startup,
validation and tool calls are offline:** no telemetry, remote schemas, model
calls, dependency downloads, external source fetching or dependency resolution.
This guarantee does not govern an MCP client's model provider or installation.

## Explicit mounts and snapshots

```bash
/tmp/okpf-mcp-env/bin/okpf-mcp \
  --pack /absolute/path/to/OKPF/examples/institutional \
  --pack /absolute/path/to/OKPF/examples/hello-world
```

Or set `OKPF_PACK_PATHS` to a JSON array, not a colon-separated search path:

```bash
export OKPF_PACK_PATHS='["/absolute/path/to/pack-one", "/absolute/path/to/pack-two.kpack"]'
/tmp/okpf-mcp-env/bin/okpf-mcp
```

Any explicit `--pack` arguments override the entire environment value. Relative
paths resolve against the launch working directory. Use absolute paths in desktop
configurations. Repeated paths resolving to the same root are mounted once.
`pack_ref` is a stable hash of the resolved local mount path, not an assertion of
content identity; moving or copying a pack produces a new reference.

Only explicitly configured roots are mounted. Reading files within a root does
not discover additional packs. No file watchers, reload tools, arbitrary file-read
tools or content execution exist. Validated indexes are startup snapshots; edits
after startup require a restart. Use stable pack roots during startup: the adapter
prevents symlink escapes but does not promise an atomic snapshot across concurrent
legitimate file edits. Declared hashes are checked against the indexed bytes.

With no configured paths (including `[]`) the server starts an empty catalog.
Invalid mounts emit concise diagnostics to **stderr** and are excluded; valid
mounts continue serving. If configured paths are nonempty and all fail, startup
exits 2. Malformed configuration also exits 2. Tool-level domain errors use the
response envelope; protocol argument-type errors use SDK tool errors. Neither
terminates a healthy server. Stdout is reserved for MCP protocol messages.

### Portability and bounds

Directory mounts use descriptor-relative POSIX no-follow reads and reject all
symlink entries, special files, and unsafe paths. This implementation supports
directory mounts on Linux/macOS; on Windows, use `.kpack` archives. Native Windows
directory support and GUI client execution are not claimed as tested.

Create a real archive from the provided example:

```bash
/tmp/okpf-mcp-env/bin/okpf pack examples/institutional /tmp/institutional.kpack
/tmp/okpf-mcp-env/bin/okpf-mcp --pack /tmp/institutional.kpack
```

ZIPs are read without extraction. Traversal, absolute/drive/backslash/NUL names,
noncanonical paths, duplicates, symlinks, special entries and encrypted ZIP
containers are rejected. Fixed initial limits: 16 configured mounts, 2 MiB per
file, 32 MiB per archive container and expanded pack, 128 MiB total accepted raw
pack data, 2,048 entries per pack, depth 32, and 100,000 nodes per parsed structured
document. Parsed Python objects incur additional memory overhead. These bounds
apply to the explicit pack contents, including unindexed files. YAML is safely
parsed; aliases/anchors, duplicate keys and non-JSON values are rejected. The
adapter imposes consumer limits, not new Core conformance requirements.

## Support boundaries and tools

All Core-valid packs can appear in the catalog subject to consumer limits.
Institutional queries require an explicit `okpf.profile.institutional.v1`
declaration and successful validation against its actual manifest and case
schemas. The manifest's singular `profile` field remains required by that schema;
a `profiles` entry alone does not repair a missing required declaration.

- Original cases retain their `outcomes`, `credential_architecture` and other
  authored fields. Missing top-level topology custody/exit fields are not inferred.
- `case_layout: review-v1` retains `telemetry`, including its qualitative stages.
  No stages become fabricated elapsed-time observations.
- Unknown explicit layouts are cataloged as unsupported when schema-valid and
  cannot be inspected as supported cases. Invalid profile packs are rejected.
- `examples/institutional` supplies both layouts for one episode; these are not
  independent precedents. Optional evasion/pre-mortem blocks are absent there.
- `examples/institutional-evidence-npm` is catalog-only: its provisional Core
  records do not implement the case contract. Filenames never confer membership.

| Tool | Contract |
|---|---|
| `okpf_list_mounted_packs()` | Identities including aliases, profiles, institutional frame, rights/provenance/artifact metadata, validation/hash/signature states |
| `okpf_find_structural_analogs(domain?, resource_type?, credential_custody?, exit_barrier?, limit=5)` | Exact case-sensitive AND filters; omit domain for cross-domain matches; returns authored case and matched field pointers |
| `okpf_inspect_case(case_id, pack_ref?)` | Complete case or unknown/unsupported/ambiguous error; require `pack_ref` when IDs repeat across mounts |
| `okpf_audit_evasion_vectors(tactic_category?, intervention_type?, limit=20)` | Explicit recorded vectors only; includes intervention and evidence context |
| `okpf_get_pre_mortem_benchmarks(domain?, limit=20)` | Explicit authored criteria only, preserving recorded qualifications; never executes off-ramps |

Custody/exit and tactic arguments are checked against enums loaded from the
bundled institutional case schema. Explicit `unknown` matches only authored
`unknown`; an absent field does not match it. Omitted filters do not constrain
results. Stable case order is package ID, version, mount reference, case ID,
artifact path, then authored vector order. No embeddings or similarity scores.

Responses consistently contain `items`, `warnings`, `limit`, `total`, `returned`,
`truncated` and `error`. Search limits are 1–100; catalog limit is 16. A 4 MiB
serialized item budget additionally truncates at whole-item boundaries; warnings
and envelope metadata add a small overhead. An oversized inspect result returns
`response_too_large`, never a partial case. Total counts mean serialized records,
not independent historical observations. Case results carry pack/version, case
ID, artifact-relative path, JSON Pointer (empty means whole document), evidence
references and original context including missing variables, review/synthetic
status and other optional qualifiers. Case-level tombstones are preserved as
unverified source assertions, not interpreted as verified revocations.

## Integrity, signatures and rights

The reference validators run on bounded in-memory bytes using local schemas.
The adapter also checks `sha256` on all declared artifact/content/record/source
entries, including ciphertext, in addition to `integrity.artifacts`. A mismatch
rejects the mount. Missing hashes are `absent`, not failed. `verified` applies only
to declared per-file hashes; it is not whole-pack authenticity. Aggregate
`manifest_sha256`/`content_sha256` declarations are rejected because this adapter
has no supported canonical verification convention for them.

There is no reusable runtime signature verifier in the repository. Recognized
signature declarations or in-pack `.sig`/`.asc` files report `unsupported`; opaque
trust/extensions report `not_checked`; otherwise the status is `absent` within
that detection scope. External detached signatures are not searched or read.
Signer trust is always `not_checked`. No signature is reported `verified`.
Unsigned packs are allowed. None of these statuses proves factual accuracy.

Catalog metadata preserves license, usage_policy, attribution, provenance,
protection/disclosure and extension metadata separately. Unknown optional case
fields remain intact. No protected artifacts are decrypted; encrypted case data
that cannot pass profile validation cannot be mounted as a valid institutional
pack. Generic encrypted artifacts may remain opaque in the catalog.

Mounting is not a license grant. An MCP client may send returned evidence to its
configured model provider. Check licenses, operational usage intent, privacy,
attribution and disclosure constraints before mounting. Pack text is untrusted
data, never agent instructions. The adapter neither enforces model-client policy
nor guarantees redistribution permission.

## Client configurations

These JSON conventions were checked against the official documentation on
2026-11-09; GUI clients themselves were not exercised. Every `/absolute/...`
value below is a placeholder to replace with a real installed path.

For [Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers),
use Settings → Developer → Edit Config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "okpf": {
      "command": "/absolute/path/to/venv/bin/okpf-mcp",
      "args": ["--pack", "/absolute/path/to/OKPF/examples/institutional"]
    }
  }
}
```

For [Cursor](https://cursor.com/docs/mcp), the same object goes in project
`.cursor/mcp.json` or global `~/.cursor/mcp.json`. On Windows use the installed
`venv\\Scripts\\okpf-mcp.exe` and an absolute `.kpack` path, with backslashes
escaped in JSON. No configuration files are installed automatically.

[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) can launch
the installed stdio executable:

```bash
npx @modelcontextprotocol/inspector \
  /tmp/okpf-mcp-env/bin/okpf-mcp --pack /tmp/institutional.kpack
```

Build that archive with the earlier command first. Inspector is a separate client;
`npx` installation and Inspector itself may access the network and expose a local
web interface. This command follows official Inspector launch syntax; the SDK
stdio client is the integration test used here, not a tested GUI session.

## Verification

See [package README](../packages/okpf-mcp/README.md) for test commands. Tests include
real SDK initialization/discovery/calls, subprocess stdout checks, network-denial
hooks before server imports, schema/hash errors, path/ZIP attacks, optional-data
coverage, ambiguity, and archive/directory equivalence. CI has a separate optional
adapter job installing both local distributions; Core users retain their existing
dependency set.
