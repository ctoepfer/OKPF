# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Source/qualification contracts of the draft, not factual or human-review certification."""
import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from okpf.cli import _pack
from okpf.institutional import validate_institutional_pack

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'examples/floss-maintainer-succession'


def test_draft_pack_and_archive(tmp_path):
    result = validate_institutional_pack(PACK)
    assert result.valid
    assert result.records_checked == 5
    archive = tmp_path / 'floss-maintainer-succession.kpack'
    assert _pack(str(PACK), str(archive)) == 0
    assert validate_institutional_pack(archive).valid
    manifest = json.loads((PACK/'manifest.json').read_text())
    assert manifest['review_status'] == 'pending_dual_review'
    assert manifest['release_ready'] is False
    assert manifest['coding_status'] == 'pending_dual_review'
    assert manifest['institutional_profile']['coding_standard'] != 'dual_coder_reconciled'
    for artifact in manifest['artifacts']:
        assert hashlib.sha256((PACK/artifact['path']).read_bytes()).hexdigest() == artifact['sha256']


def test_every_case_preserves_draft_evidence_boundaries():
    schema = json.loads((ROOT/'schemas/profiles/institutional/v1/proposal_lint.json').read_text())
    for path in (PACK/'cases').glob('*.yaml'):
        case = yaml.safe_load(path.read_text())
        Draft202012Validator(schema).validate(case)
        assert case['coding_status']['independent_coders'] == []
        assert case['coding_status']['reconciliation'] is None
        assert case['pre_mortem_falsification']['historical_precommitment'] is False
        assert case['pre_mortem_falsification']['epistemic_status'] == 'proposed_retrospective_example'
        for source in case['evidence_sources']:
            assert source['url'].startswith('https://')
            assert source['locator']
        for vector in case['evasion_vectors']:
            if vector['epistemic_status'] == 'hypothetical_not_observed':
                assert vector['source_references'] == []
                assert 'Hypothesis only' in vector['mechanism']
        assert case['unobserved_variables']
    status = json.loads((PACK/'review/dual-coding-status.json').read_text())
    assert status['completed_independent_codings'] == 0
    assert not status['release_ready']
