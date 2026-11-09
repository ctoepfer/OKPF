# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
import yaml
from jsonschema import Draft202012Validator

from okpf.proposal_lint import lint_proposal, read_proposal
from okpf.review import ReviewError
from okpf.institutional import validate_institutional_pack

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'schemas/profiles/institutional/v1'

@pytest.fixture
def proposal():
    return {'resource_type': 'test_resource', 'evasion_vectors': [{
        'tactic_category': 'nominal_compliance', 'mechanism': 'Passive multisig signers',
        'telemetry_impact': 'Overstates independent approvals'}],
        'pre_mortem_falsification': {'leading_indicator_failure': 'Unreviewed releases exceed 2',
        'evaluation_horizon_months': 6, 'automated_off_ramp': {
            'trigger_condition': 'More than 2 unreviewed releases at month 6',
            'fallback_action': 'Suspend releases pending independent review'}}}

@pytest.mark.parametrize('suffix', ['.json', '.yaml', '.yml', '.md'])
def test_formats(tmp_path, proposal, suffix):
    path = tmp_path / ('proposal' + suffix)
    text = json.dumps(proposal) if suffix == '.json' else yaml.safe_dump(proposal)
    path.write_text('---\n' + text + '---\nBody' if suffix == '.md' else text)
    assert lint_proposal(path)['valid']

@pytest.mark.parametrize('mutation', [
    lambda p: p.pop('evasion_vectors'),
    lambda p: p.update(evasion_vectors=[]),
    lambda p: p['evasion_vectors'][0].update(tactic_category='invented'),
    lambda p: p['evasion_vectors'][0].pop('telemetry_impact'),
    lambda p: p['evasion_vectors'][0].update(mechanism='   '),
    lambda p: p.pop('pre_mortem_falsification'),
    lambda p: p['pre_mortem_falsification'].pop('leading_indicator_failure'),
    lambda p: p['pre_mortem_falsification'].pop('evaluation_horizon_months'),
    lambda p: p['pre_mortem_falsification'].pop('automated_off_ramp'),
    lambda p: p['pre_mortem_falsification'].update(evaluation_horizon_months=0),
    lambda p: p['pre_mortem_falsification'].update(evaluation_horizon_months=True),
    lambda p: p['pre_mortem_falsification'].update(evaluation_horizon_months='6'),
    lambda p: p['pre_mortem_falsification']['automated_off_ramp'].pop('trigger_condition'),
    lambda p: p['pre_mortem_falsification']['automated_off_ramp'].pop('fallback_action'),
    lambda p: p['pre_mortem_falsification']['automated_off_ramp'].update(fallback_action=''),
])
def test_structural_failures(tmp_path, proposal, mutation):
    mutation(proposal)
    path = tmp_path / 'p.json'
    path.write_text(json.dumps(proposal))
    result = lint_proposal(path)
    assert not result['valid']
    assert any(d['code'] == 'schema' for d in result['diagnostics'])

@pytest.mark.parametrize('suffix,text', [('.json', '{"x":1,"x":2}'),
    ('.json', '{"x":NaN}'), ('.yaml', 'x: 1\nx: 2'),
    ('.yaml', '!!python/object/apply:os.system [false]'),
    ('.yaml', 'x: 1\n---\nx: 2'), ('.json', '[]'),
    ('.md', '---\nunclosed: true')])
def test_bad_inputs(tmp_path, suffix, text):
    path = tmp_path / ('p' + suffix)
    path.write_text(text)
    with pytest.raises((ReviewError, ValueError)):
        read_proposal(path)


def make_pack(tmp_path, proposal):
    pack = tmp_path / 'pack'
    (pack / 'cases').mkdir(parents=True)
    manifest = json.loads((ROOT / 'examples/institutional/manifest.json').read_text())
    manifest['artifacts'] = [{'path': 'cases/test.json'}]
    (pack / 'manifest.json').write_text(json.dumps(manifest))
    case = yaml.safe_load((ROOT / 'examples/institutional/cases/floss-event-stream-2018.yaml').read_text())
    case['id'] = 'SyntheticLintTest'
    case['topology']['resource_type'] = 'test_resource'
    case.update(copy.deepcopy(proposal))
    (pack / 'cases/test.json').write_text(json.dumps(case))
    return pack, case


def test_case_validation_and_archive_cross_reference(tmp_path, proposal):
    pack, case = make_pack(tmp_path, proposal)
    assert validate_institutional_pack(pack).valid
    p = tmp_path / 'p.json'
    p.write_text(json.dumps(proposal))
    result = lint_proposal(p, pack)
    assert result['candidate_vectors'][0]['case_id'] == 'SyntheticLintTest'
    archive = tmp_path / 'pack.kpack'
    with zipfile.ZipFile(archive, 'w') as z:
        for path in pack.rglob('*'):
            if path.is_file():
                z.write(path, path.relative_to(pack))
    assert lint_proposal(p, archive) == result
    case['evasion_vectors'][0]['tactic_category'] = 'bad'
    (pack / 'cases/test.json').write_text(json.dumps(case))
    assert not validate_institutional_pack(pack).valid


def test_no_match_and_tombstone(tmp_path, proposal):
    pack, case = make_pack(tmp_path, proposal)
    p = tmp_path / 'p.json'
    proposal['resource_type'] = 'unrelated'
    p.write_text(json.dumps(proposal))
    assert lint_proposal(p, pack)['candidate_vectors'] == []
    proposal['resource_type'] = 'test_resource'
    p.write_text(json.dumps(proposal))
    case['tombstone'] = {'superseded_by': 'other', 'revocation_signature': 'not_verified'}
    (pack / 'cases/test.json').write_text(json.dumps(case))
    result = lint_proposal(p, pack)
    assert not result['candidate_vectors']
    assert 'not verified' in result['excluded_cases'][0]['reason']


def test_legacy_layouts_and_optional_fields():
    assert validate_institutional_pack(ROOT / 'examples/institutional').valid
    for file in SCHEMAS.glob('*.json'):
        Draft202012Validator.check_schema(json.loads(file.read_text()))


def test_cli_exit_codes_and_plain_prose(tmp_path, proposal):
    path = tmp_path / 'p.json'
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'reference/python')}
    cmd = [sys.executable, '-m', 'okpf', 'lint-proposal', '--proposal', str(path), '--json']
    for contents, expected in [(json.dumps(proposal), 0), ('{}', 1), ('{', 2)]:
        path.write_text(contents)
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert result.returncode == expected, result.stderr
        assert json.loads(result.stdout)['valid'] == (expected == 0)
        assert 'Traceback' not in result.stderr
    path = tmp_path / 'p.txt'
    path.write_text('We do not use multisig. We promise to roll back after six months.')
    result = lint_proposal(path)
    assert not result['valid']
    assert result['metric_mentions'] == ['multisig']
    assert not result['candidate_vectors']
