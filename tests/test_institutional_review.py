# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Experimental review behavior and optional detached signing interoperability."""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from okpf.cli import _pack
from okpf.institutional import validate_institutional_pack
from okpf.review import ReviewError, load_cases, match_cases, parse_proposal, review_pack

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'examples/institutional'
PROPOSAL = PACK / 'proposals/release-council.md'


def test_review_directory_and_archive_are_equivalent(tmp_path, capsys):
    archive = tmp_path / 'institutional.kpack'
    assert _pack(str(PACK), str(archive)) == 0
    assert validate_institutional_pack(archive).valid
    report = review_pack(archive, PROPOSAL)
    assert report == review_pack(PACK, PROPOSAL)
    for section in ('Detected Topology & Invariants', 'Closest Structural Post-Mortems',
                    'Boundary Condition Mismatch Warning', 'Distributional Stakeholder Matrix'):
        assert f'## {section}' in report
    assert 'comparison unavailable' in report
    assert 'not an independent precedent' in report
    assert 'Unobserved variables' in report
    assert 'Matches: 1; compared: 1/5' in report


def test_cli_review_and_invalid_proposal(tmp_path):
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'reference/python')
    command = [sys.executable, '-m', 'okpf', 'review', '--pack', str(PACK), '--proposal', str(PROPOSAL)]
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert '# Institutional review (experimental)' in result.stdout
    bad = tmp_path / 'bad.md'
    bad.write_text('---\ncredential_custody: [single_custody]\n---\n')
    result = subprocess.run(command[:-1] + [str(bad)], env=env, capture_output=True, text=True)
    assert result.returncode == 1
    assert 'must be a string' in result.stdout
    assert 'Traceback' not in result.stderr


def test_unknown_prose_abstains_and_does_not_infer_negated_custody(tmp_path):
    proposal = tmp_path / 'proposal.md'
    proposal.write_text('We must not use single custody. We may someday have a council.')
    assert parse_proposal(proposal.read_text()) == {}
    assert 'Abstain: no positive declared-variable match' in review_pack(PACK, proposal)


@pytest.mark.parametrize('text', [
    '---\ncredential_custody: a\ncredential_custody: b\n---',
    '- exit_barrier: a\n- exit_barrier: b',
    '---\nstakeholders: [someone]\n---',
    '---\nboundary_conditions: unknown\n---',
    '---\ncredential_custody: x',
    '---\n!!python/object/apply:os.system [false]\n---',
])
def test_ambiguous_or_unsafe_proposals_rejected(text):
    with pytest.raises(ReviewError):
        parse_proposal(text)


def test_structural_ranking_and_unknowns():
    _, cases = load_cases(PACK)
    base = cases[1][1]
    precise = copy.deepcopy(base)
    precise['id'] = 'precise'
    precise['topology']['credential_custody'] = 'multisig_threshold'
    other = copy.deepcopy(precise)
    other['id'] = 'other'
    other['topology']['credential_custody'] = 'single_custody'
    ranked = match_cases({'credential_custody': 'multisig_threshold'},
                         [('a.yaml', base), ('b.yaml', other), ('c.yaml', precise)])
    assert ranked[0].case['id'] == 'precise'
    assert ranked[0].matching == ('credential_custody',)
    assert next(m for m in ranked if m.case is base).compared == ()


def test_invalid_new_case_cannot_fall_back_to_legacy(tmp_path):
    target = tmp_path / 'pack'
    shutil.copytree(PACK, target)
    bad = json.loads((ROOT / 'tests/fixtures/institutional/review-missing-shadow-practice.json').read_text())
    (target / 'cases/invalid.json').write_text(json.dumps(bad))
    result = validate_institutional_pack(target)
    assert not result.valid
    assert 'shadow_practice' in str(result.errors)
    with pytest.raises(ReviewError, match='invalid'):
        review_pack(target, PROPOSAL)


def test_new_layout_metadata_and_required_fields(tmp_path):
    target = tmp_path / 'pack'
    shutil.copytree(PACK, target)
    path = target / 'manifest.json'
    manifest = json.loads(path.read_text())
    meta = manifest['institutional_profile']
    meta.update(layout='review-v1', coding_standard='panel_consensus')
    path.write_text(json.dumps(manifest))
    assert validate_institutional_pack(target).valid
    meta['domain_family'] = 'not_in_experimental_vocabulary'
    path.write_text(json.dumps(manifest))
    assert not validate_institutional_pack(target).valid


def test_rule_warnings_and_proposal_stakeholder_attribution(tmp_path):
    target = tmp_path / 'pack'
    shutil.copytree(PACK, target)
    case = yaml.safe_load((PACK / 'cases/floss-event-stream-2018.yaml').read_text())
    case['id'] = 'syntheticCustodyMismatch'
    case['topology']['credential_custody'] = 'single_custody'
    (target / 'cases/synthetic.json').write_text(json.dumps(case))
    proposal = tmp_path / 'proposal.md'
    proposal.write_text('''---
credential_custody: multisig_threshold
boundary_conditions: [automated_execution]
stakeholders:
  - group: council
    discretion: release approval
    residual_risk: "unmeasured | <script>"
---
# Synthetic test proposal
''')
    report = review_pack(target, proposal)
    assert 'Rule credential_custody:' in report
    assert 'Proposal-only tags' in report
    assert '| council | release approval |' in report
    assert '<script>' not in report
    assert 'Proposal assertions only' in report


@pytest.mark.skipif(shutil.which('ssh-keygen') is None, reason='Optional OpenSSH signing tool unavailable')
def test_pack_sign_verify_and_reject_tampering(tmp_path):
    archive = tmp_path / 'institutional.kpack'
    assert _pack(str(PACK), str(archive)) == 0
    assert validate_institutional_pack(archive).valid
    key = tmp_path / 'ephemeral'
    subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)], check=True)
    subprocess.run(['ssh-keygen', '-Y', 'sign', '-f', str(key), '-n', 'okpf-review-test',
                    str(archive)], check=True, capture_output=True)
    allowed = tmp_path / 'allowed_signers'
    allowed.write_text('fixture-signer ' + key.with_suffix('.pub').read_text())
    verify = ['ssh-keygen', '-Y', 'verify', '-f', str(allowed), '-I', 'fixture-signer',
              '-n', 'okpf-review-test', '-s', str(archive) + '.sig']
    original = archive.read_bytes()
    assert subprocess.run(verify, input=original, capture_output=True).returncode == 0
    assert subprocess.run(verify, input=original + b'tampered', capture_output=True).returncode != 0


@pytest.mark.parametrize('field', ['telemetry', 'unobserved_variables', 'perspectives'])
def test_review_layout_empty_required_structures_rejected(tmp_path, field):
    target = tmp_path / 'pack'
    shutil.copytree(PACK, target)
    case = yaml.safe_load((PACK / 'cases/floss-event-stream-2018.yaml').read_text())
    case['id'] = 'invalidCase'
    case[field] = [] if field == 'unobserved_variables' else {}
    (target / 'cases/bad.json').write_text(json.dumps(case))
    assert not validate_institutional_pack(target).valid


def test_code_examples_are_not_proposal_declarations():
    assert parse_proposal('```yaml\ncredential_custody: single_custody\n```') == {}


def test_non_case_files_are_rejected_in_cases_directory(tmp_path):
    target = tmp_path / 'pack'
    shutil.copytree(PACK, target)
    (target / 'cases/run.py').write_text('raise RuntimeError("must never execute")')
    result = validate_institutional_pack(target)
    assert not result.valid
    assert 'must be JSON or YAML' in str(result.errors)
