# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Ordering controls, not automatic grading of answer quality."""
import importlib
import json
from pathlib import Path

import pytest
from okpf.export import build_rag_rows

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ordering(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools'))
    return importlib.import_module('institutional_ordering')


def test_only_record_order_changes_and_expectations_are_not_read(ordering):
    class QuestionOnly(dict):
        def __getitem__(self, key):
            assert key in ('id', 'question')
            return super().__getitem__(key)

    rows = build_rag_rows(str(ROOT / 'examples/institutional-evidence-npm'))
    questions = json.loads((ROOT / 'examples/institutional-evidence-npm/evals/questions.json').read_text())['evaluations']
    trials = ordering.build_inputs(rows, [QuestionOnly(q) for q in questions])
    assert len(trials) == 14
    for a, b in zip(trials[::2], trials[1::2], strict=True):
        assert a['initial_retrieval'] == b['initial_retrieval']
        assert a['selection_audit'] == b['selection_audit']
        assert a['included_record_ids'] == b['included_record_ids']
        assert sorted(a['context']['records'], key=lambda r: r['record_id']) == sorted(
            b['context']['records'], key=lambda r: r['record_id'])
        assert a['context']['evidence'] == b['context']['evidence']
        assert a['context_chars'] == b['context_chars'] <= 9000
        assert a['generation_input']['system'] == b['generation_input']['system']
        assert a['conservative_token_bound'] <= ordering.OPTIONS['num_ctx']
        assert b['context']['records'] == sorted(a['context']['records'], key=lambda r: (
            -a['scores'][r['record_id']], r['record_id']))
        for trial in (a, b):
            assert trial['generation_input']['prompt'].endswith(ordering.serialized(trial['context']))
            assert 'expected_answer' not in trial['generation_input']['prompt']
    assert any(a['generation_input'] != b['generation_input'] for a, b in zip(trials[::2], trials[1::2]))


def test_freeze_rejects_modified_inputs(ordering, tmp_path):
    path = tmp_path / 'inputs.json'
    path.write_text('{}')
    ordering.write(tmp_path / 'freeze.json', {'files': {'inputs.json': ordering.digest(path.read_bytes())}})
    ordering.verify(tmp_path)
    path.write_text('{"changed":true}')
    with pytest.raises(ValueError, match='Frozen input changed'):
        ordering.verify(tmp_path)


def test_generation_refuses_overwrite_before_connecting(ordering, tmp_path, monkeypatch):
    ordering.write(tmp_path / 'freeze.json', {'files': {}})
    (tmp_path / 'pilot.jsonl').write_text('existing measurement')
    monkeypatch.setattr(ordering, 'client', lambda: pytest.fail('Should not connect'))
    with pytest.raises(ValueError, match='overwrite'):
        ordering.run(tmp_path, 'pilot')
