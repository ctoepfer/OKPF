# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXECUTABLE = str(Path(sys.executable).with_name("okpf-mcp"))

# Audit the actual child process too, from before any server imports. Loopback
# and DNS are blocked along with remote network calls; stdio still works.
GUARD = """
import sys
def guard(event, args):
    if event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo', 'socket.sendto'}:
        raise RuntimeError('NETWORK ATTEMPT: ' + event)
sys.addaudithook(guard)
from okpf_mcp.server import main
raise SystemExit(main())
"""


@pytest.mark.parametrize("guarded", [False, True])
def test_real_sdk_stdio(pack, tmp_path, guarded):
    async def run():
        params = StdioServerParameters(
            command=sys.executable if guarded else EXECUTABLE,
            args=(["-c", GUARD] if guarded else []) + ["--pack", str(pack)],
            cwd=tmp_path,
            env={"OKPF_PACK_PATHS": "invalid ignored environment"},
        )
        with (tmp_path / "stderr.log").open("w+") as errlog:
            async with stdio_client(params, errlog=errlog) as (read, write):  # noqa: SIM117
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    assert initialized.serverInfo.name == "okpf-mcp"
                    tools = await session.list_tools()
                    assert len(tools.tools) == 5
                    assert all(t.annotations.readOnlyHint for t in tools.tools)
                    assert all(t.outputSchema for t in tools.tools)
                    result = await session.call_tool("okpf_list_mounted_packs", {})
                    assert result.structuredContent["total"] == 1
                    cases = await session.call_tool("okpf_find_structural_analogs", {"limit": 1})
                    data = cases.structuredContent
                    assert data["truncated"]
                    case_id = data["items"][0]["case_id"]
                    case = await session.call_tool("okpf_inspect_case", {"case_id": case_id})
                    assert case.structuredContent["returned"] == 1
                    for tool in ("okpf_audit_evasion_vectors", "okpf_get_pre_mortem_benchmarks"):
                        response = await session.call_tool(tool, {})
                        assert response.structuredContent["total"] == 1
                    invalid = await session.call_tool("okpf_find_structural_analogs", {"limit": 0})
                    assert invalid.structuredContent["error"]["code"] == "invalid_argument"
                    unknown = await session.call_tool("okpf_inspect_case", {"case_id": "missing"})
                    assert unknown.structuredContent["error"]["code"] == "unknown_case"
                    assert not (await session.call_tool("okpf_list_mounted_packs", {})).isError
            errlog.seek(0)
            assert "NETWORK ATTEMPT" not in errlog.read()

    asyncio.run(asyncio.wait_for(run(), timeout=30))


def test_startup_and_stdout(pack, tmp_path):
    requests = (
        "\n".join(
            json.dumps(x)
            for x in [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1"},
                    },
                },
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            ]
        )
        + "\n"
    )
    env = {**os.environ, "OKPF_PACK_PATHS": "[]"}
    for args in ([], ["--pack", str(tmp_path / "missing"), "--pack", str(pack)]):
        p = subprocess.run(
            [EXECUTABLE, *args],
            input=requests,
            check=False,
            capture_output=True,
            text=True,
            cwd=tmp_path,
            env=env,
            timeout=20,
        )
        assert p.returncode == 0, p.stderr
        assert p.stdout
        for line in p.stdout.splitlines():
            assert json.loads(line)["jsonrpc"] == "2.0"
        if args:
            assert "rejected mount" in p.stderr
    p = subprocess.run(
        [EXECUTABLE, "--pack", str(tmp_path / "missing")],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=10,
        env=env,
    )
    assert p.returncode == 2
    assert not p.stdout
    assert "no configured packs" in p.stderr
