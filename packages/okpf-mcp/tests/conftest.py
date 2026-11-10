# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import json
import shutil
import socket
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Network attempt during offline test")

    for name in ("connect", "connect_ex", "bind", "sendto"):
        monkeypatch.setattr(socket.socket, name, deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)


@pytest.fixture
def pack(tmp_path):
    path = tmp_path / "pack"
    shutil.copytree(ROOT / "examples/institutional", path)
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["artifacts"]:
        entry.pop("sha256", None)
    manifest["license"] = {"type": "Apache-2.0"}
    manifest["usage_policy"] = {"allow_training": False}
    manifest_path.write_text(json.dumps(manifest))
    case_path = path / "cases/floss-event-stream-2018.yaml"
    case = yaml.safe_load(case_path.read_text())
    case["topology"]["credential_custody"] = "multisig_threshold"
    case["topology"]["exit_barrier"] = "costly_migration"
    case["evasion_vectors"] = [
        {
            "tactic_category": "nominal_compliance",
            "mechanism": "Synthetic passive signers",
            "telemetry_impact": "Synthetic inflated independence",
            "detection_signature": "Synthetic missing review notes",
        }
    ]
    case["pre_mortem_falsification"] = {
        "leading_indicator_failure": "Synthetic unreviewed releases exceed two",
        "evaluation_horizon_months": 6,
        "automated_off_ramp": {
            "trigger_condition": "Synthetic review threshold exceeded",
            "fallback_action": "Synthetic freeze",
        },
        "status": "proposed_synthetic",
    }
    case["review_status"] = "synthetic_test_only"
    case_path.write_text(yaml.safe_dump(case))
    return path
