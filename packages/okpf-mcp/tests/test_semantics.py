# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import copy
import hashlib
import json
from pathlib import Path

import pytest

from okpf_mcp.semantics import check_semantics, commitment_errors

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "examples/floss-maintainer-succession/semantics/release-review.json"


def test_example_and_no_baseline_limit():
    assert not commitment_errors(json.loads(EXAMPLE.read_text()))
    result = check_semantics(EXAMPLE)
    assert result["valid"]
    assert not result["baseline_checked"]
    assert "self-consistency only" in result["warnings"][0]
    result = check_semantics(EXAMPLE, EXAMPLE)
    assert result["valid"]
    assert result["baseline_checked"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("threshold", "1"),
        ("denominator", "Exclude failed releases"),
        ("population", "Only successful deployments"),
        ("unit", "percent"),
        ("evaluation_horizon_months", 6),
        ("missing_data_policy", "Ignore missing"),
        ("measurement_method", "Count approvals, not review records"),
    ],
)
def test_baseline_detects_metric_boundary_changes(tmp_path, field, value):
    changed = json.loads(EXAMPLE.read_text())
    changed["operational_test"][field] = value
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed))
    result = check_semantics(path, EXAMPLE)
    assert not result["valid"]
    assert "/operational_test/" + field in result["changed_pointers"]


def test_hash_mismatch_and_rehash_does_not_evade_baseline(tmp_path):
    changed = json.loads(EXAMPLE.read_text())
    binding = changed["taxonomy_bindings"][0]
    binding["definition"] = "A rubber stamp counts as independent review."
    assert any("digest mismatch" in e for e in commitment_errors(changed))
    binding["definition_sha256"] = hashlib.sha256(binding["definition"].encode()).hexdigest()
    assert not commitment_errors(changed)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed))
    assert not check_semantics(path, EXAMPLE)["valid"]
    # Explicit limitation: replacing the trusted baseline defeats a plain comparison.
    assert check_semantics(path, path)["valid"]


def test_bound_concepts_duplicate_ids_and_invalid_threshold():
    value = json.loads(EXAMPLE.read_text())
    value["operational_test"]["concept_ids"] = ["not_bound"]
    assert "Unbound" in commitment_errors(value)[0]
    value = json.loads(EXAMPLE.read_text())
    value["taxonomy_bindings"].append(copy.deepcopy(value["taxonomy_bindings"][0]))
    assert "Duplicate" in commitment_errors(value)[0]
    value = json.loads(EXAMPLE.read_text())
    value["operational_test"]["threshold"] = 0.5
    assert commitment_errors(value)
