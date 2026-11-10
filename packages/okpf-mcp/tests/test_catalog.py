# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import json
import shutil
import zipfile
from pathlib import Path

import pytest

from okpf_mcp.catalog import Catalog
from okpf_mcp.query import Queries
from okpf_mcp.server import configured_paths

ROOT = Path(__file__).resolve().parents[3]


def query(path):
    catalog = Catalog([str(path)])
    assert not catalog.errors
    return Queries(catalog)


def test_real_example_and_support_boundaries():
    q = query(ROOT / "examples/institutional")
    assert q.list_packs().items[0]["integrity"]["status"] == "verified"
    assert q.list_packs().items[0]["signature"]["status"] == "absent"
    result = q.find()
    assert result.total == 2
    assert any("outcomes" in i["data"] for i in result.items)
    assert any("telemetry" in i["data"] for i in result.items)
    assert q.audit().total == q.benchmarks().total == 0
    q = query(ROOT / "examples/institutional-evidence-npm")
    assert q.list_packs().total == 1
    assert not q.find().items
    assert "Catalog only" in q.list_packs().items[0]["warnings"][-1]


def test_queries_and_optional_context(pack):
    q = query(pack)
    match = q.find(credential_custody="multisig_threshold", exit_barrier="costly_migration")
    assert match.total == 1
    item = match.items[0]
    assert item["artifact_path"].startswith("cases/")
    assert item["context"]["review_status"] == "synthetic_test_only"
    assert item["context"]["unobserved_variables"]
    assert item["evidence_sources"]
    assert item["matched_fields"][0]["pointer"] == "/topology/credential_custody"
    assert q.find(domain="other", credential_custody="multisig_threshold").total == 0
    assert q.find(resource_type=item["data"]["topology"]["resource_type"]).total >= 1
    assert q.find(limit=1).truncated
    assert q.find().items == q.find().items
    assert q.audit(tactic_category="nominal_compliance").total == 1
    assert q.audit(intervention_type="other").total == 0
    assert q.audit().items[0]["pointer"] == "/evasion_vectors/0"
    assert q.benchmarks().items[0]["data"]["status"] == "proposed_synthetic"
    assert q.benchmarks(domain="other").total == 0
    assert q.inspect(item["case_id"]).items[0]["data"] == item["data"]
    assert q.inspect("missing").error["code"] == "unknown_case"
    summary = q.list_packs().items[0]
    assert summary["metadata"]["usage_policy"]["allow_training"] is False
    assert summary["metadata"]["license"] == {"type": "Apache-2.0"}
    # Snapshot remains valid without source files and returns the same evidence.
    shutil.rmtree(pack)
    assert q.inspect(item["case_id"]).items[0]["data"] == item["data"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": True},
        {"credential_custody": "invented"},
        {"exit_barrier": "invented"},
        {"domain": ""},
    ],
)
def test_invalid_arguments(pack, kwargs):
    assert query(pack).find(**kwargs).error["code"] == "invalid_argument"


def test_invalid_audit_argument(pack):
    assert query(pack).audit(tactic_category="invented").error


def test_duplicate_ids_and_disambiguation(pack, tmp_path):
    other = tmp_path / "other"
    shutil.copytree(pack, other)
    c = Catalog([str(pack), str(other), str(pack)])
    q = Queries(c)
    assert q.list_packs().total == 2
    case_id = c.cases[0].data["id"]
    assert q.inspect(case_id).error["code"] == "ambiguous_case_id"
    assert q.inspect(case_id, c.cases[0].pack_ref).returned == 1


def test_archive_equivalence(pack, tmp_path):
    archive = tmp_path / "pack.kpack"
    with zipfile.ZipFile(archive, "w") as z:
        for f in pack.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(pack))
    a, b = query(pack), query(archive)
    left, right = a.find().model_dump(), b.find().model_dump()
    for result in (left, right):
        for item in result["items"]:
            item.pop("pack_ref")
    assert left == right


def test_mixed_invalid_integrity_and_alias(pack, tmp_path):
    bad = tmp_path / "bad"
    shutil.copytree(pack, bad)
    m = bad / "manifest.json"
    manifest = json.loads(m.read_text())
    manifest["artifacts"][0]["sha256"] = "0" * 64
    m.write_text(json.dumps(manifest))
    c = Catalog([str(bad), str(pack)])
    assert len(c.mounts) == len(c.errors) == 1
    assert "SHA-256 mismatch" in c.errors[0]
    manifest["artifacts"][0].pop("sha256")
    manifest["id"] = manifest.pop("package_id")
    manifest["signature"] = "ed25519:unverified"
    m.write_text(json.dumps(manifest))
    summary = query(bad).list_packs().items[0]
    assert summary["identity_fields"] == {"id": summary["package_id"]}
    assert summary["signature"]["status"] == "unsupported"
    assert summary["signature"]["signer_trust"] == "not_checked"


def test_schema_failure_and_unsupported_layout(pack):
    p = pack / "cases/floss-node-event-stream.yaml"
    import yaml

    data = yaml.safe_load(p.read_text())
    data["case_layout"] = "future-layout"
    p.write_text(yaml.safe_dump(data))
    q = query(pack)
    assert q.inspect(data["id"]).error["code"] == "unsupported_case"
    del data["perspectives"]["shadow_practice"]
    p.write_text(yaml.safe_dump(data))
    assert not Catalog([str(pack)]).mounts


def test_env_and_override(monkeypatch):
    monkeypatch.setenv("OKPF_PACK_PATHS", '["a", "b"]')
    assert configured_paths(None) == ["a", "b"]
    monkeypatch.setenv("OKPF_PACK_PATHS", "not JSON")
    assert configured_paths(["explicit"]) == ["explicit"]
    with pytest.raises(ValueError):
        configured_paths(None)
    monkeypatch.setenv("OKPF_PACK_PATHS", '{"path": "a"}')
    with pytest.raises(ValueError):
        configured_paths(None)


def test_response_bound(pack, monkeypatch):
    import okpf_mcp.query as module

    monkeypatch.setattr(module, "MAX_RESPONSE", 1)
    q = query(pack)
    assert q.find().truncated
    assert q.inspect(q.catalog.cases[0].data["id"]).error["code"] == "response_too_large"


def test_integrity_metadata_hash_and_aggregate_rejection(pack):
    path = pack / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["integrity"] = {
        "algorithm": "sha256",
        "artifacts": [{"path": manifest["artifacts"][0]["path"], "sha256": "0" * 64}],
    }
    path.write_text(json.dumps(manifest))
    assert "SHA-256 mismatch" in Catalog([str(pack)]).errors[0]
    manifest["integrity"] = {"algorithm": "sha256", "manifest_sha256": "0" * 64}
    path.write_text(json.dumps(manifest))
    assert "Aggregate" in Catalog([str(pack)]).errors[0]


def test_remote_references_are_data_and_opaque_trust(pack):
    path = pack / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["$schema"] = "https://must-not-fetch.invalid/schema"
    manifest["trust"] = {"opaque": "https://must-not-fetch.invalid/key"}
    path.write_text(json.dumps(manifest))
    q = query(pack)  # autouse socket guards would reject remote resolution
    assert q.list_packs().items[0]["signature"]["status"] == "not_checked"


def test_encrypted_generic_artifact_remains_opaque(tmp_path):
    pack = tmp_path / "opaque"
    pack.mkdir()
    (pack / "secret.json").write_bytes(b"not JSON: encrypted bytes")
    manifest = {
        "okpf_version": "0.1",
        "id": "opaque",
        "name": "Opaque",
        "version": "1",
        "domain": "test",
        "license": {"type": "Apache-2.0"},
        "artifacts": [{"path": "secret.json", "disclosure": "encrypted"}],
    }
    (pack / "manifest.json").write_text(json.dumps(manifest))
    q = query(pack)
    assert q.list_packs().items[0]["artifact_metadata"][0]["disclosure"] == "encrypted"
    assert not q.find().items


def test_no_declared_profile_does_not_infer_from_cases(pack):
    path = pack / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest.pop("profile")
    manifest["profiles"] = ["some.future.profile"]
    path.write_text(json.dumps(manifest))
    assert not query(pack).find().items
