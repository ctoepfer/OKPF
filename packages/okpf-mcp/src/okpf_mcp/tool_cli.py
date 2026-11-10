# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Optional consumer commands; the MCP server's stdout remains protocol-only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .operational_review import render, run_review
from .semantics import check_semantics


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="okpf-tool", description="Experimental local OKPF consumers"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    review = commands.add_parser(
        "review", help="Review a proposal through the installed MCP server"
    )
    review.add_argument("--proposal", type=Path, required=True)
    review.add_argument("--pack", action="append", required=True)
    review.add_argument("--limit", type=int, default=5)
    review.add_argument("--json", action="store_true")
    semantics = commands.add_parser("check-semantics", help="Check a draft semantic commitment")
    semantics.add_argument("--document", type=Path, required=True)
    semantics.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "review":
            result = run_review(args.proposal, args.pack, args.limit)
            print(json.dumps(result, indent=2) if args.json else render(result))
        else:
            result = check_semantics(args.document, args.baseline)
            print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1
    except Exception as exc:  # noqa: BLE001 -- CLI boundary includes MCP transport ExceptionGroups
        print(f"okpf-tool: {type(exc).__name__}: {str(exc)[:1000]}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
