<!-- SPDX-License-Identifier: Apache-2.0 -->
# okpf-mcp

Optional Python >=3.11 stdio adapter using the official MCP SDK's FastMCP
interface (`mcp>=1.30,<2`, tested with 1.30.0). This is not the separate `fastmcp`
PyPI project. Install the matching repository reference package explicitly:

```bash
python3 -m venv /tmp/okpf-mcp-env
/tmp/okpf-mcp-env/bin/python -m pip install ./reference/python ./packages/okpf-mcp
/tmp/okpf-mcp-env/bin/okpf-mcp --pack /absolute/path/to/OKPF/examples/institutional
```

Run installation from the repository root. Both local project arguments are
required: `okpf==0.0.1` is a repository dependency, not an instruction to retrieve
an unrelated registry package. Do not install this adapter alone from a registry.
For deployment, build both wheels and supply both explicitly to pip.

The installed executable works outside the checkout. No PYTHONPATH or editable
install is required. Schemas ship in the reference wheel, not duplicated here.
Runtime is offline; dependency installation may use the network. No package
publication is part of this integration.

See [setup and contracts](../../docs/mcp-setup.md) and
[optional agent guidance](../../docs/agent-rules.md). Repository documentation
links refer to the source checkout, not installed wheel paths.

Tests (after installing both local projects and this package's test extra):

```bash
python -m pytest packages/okpf-mcp/tests
ruff check packages/okpf-mcp
mypy --config-file packages/okpf-mcp/pyproject.toml packages/okpf-mcp/src
```

The package also installs `okpf-tool review --proposal FILE --pack PACK` as an
experimental MCP consumer and `okpf-tool check-semantics --document FILE
[--baseline FILE]` for draft semantic commitments. See
[operational review](../../docs/operational-institutional-review.md). Raw proposal
hints are not asserted invariants; missing commitments produce lint failures even
when candidate evidence is retrieved. No model calls or rollback actions occur.
