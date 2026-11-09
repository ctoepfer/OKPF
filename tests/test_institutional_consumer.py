# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Consumer context construction checks, not automated answer grading."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys

from okpf.export import build_rag_rows

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('institutional_consumer', ROOT / 'tools/institutional_consumer.py')
consumer_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = consumer_module
spec.loader.exec_module(consumer_module)
Consumer, Limits = consumer_module.Consumer, consumer_module.Limits
prepare, coverage_report = consumer_module.prepare, consumer_module.coverage_report
NS = consumer_module.NS
PACK = ROOT / 'examples/institutional-evidence-npm'


def rows():
    return build_rag_rows(str(PACK))


class QuestionOnly(dict):
    def __getitem__(self, key):
        assert key in ('id', 'question'), f'Expectation leakage: {key}'
        return super().__getitem__(key)

    def get(self, key, default=None):
        assert key in ('id', 'question'), f'Expectation leakage: {key}'
        return super().get(key, default)

    def items(self):
        raise AssertionError('Do not inspect all evaluation fields')


def test_retrieval_never_accesses_expectations_or_uses_question_ids():
    question = QuestionOnly(id='any-id', question='Does publishing a patched version prove machines clean?',
                            expected_answer='LEAK_SENTINEL', expected_record_refs=['secret-target'])
    result = prepare(rows(), [question])
    changed = QuestionOnly(id='unrelated-id', question=question['question'],
                           expected_answer='totally different', expected_record_refs=['other'])
    other = prepare(rows(), [changed])
    for first, second in zip(result['trials'], other['trials']):
        assert first['initial_retrieval'] == second['initial_retrieval']
        assert first['generation_input'] == second['generation_input']
        assert 'LEAK_SENTINEL' not in json.dumps(first)
        assert 'expected_answer' not in first


def test_both_conditions_have_identical_initial_retrieval_but_different_supplied_context():
    result = prepare(rows(), [{'id': 'q', 'question': 'What does event-stream containment establish?'}])
    a, b = result['trials']
    assert a['initial_retrieval'] == b['initial_retrieval']
    assert a['limits'] == b['limits']
    assert a['generation_input']['system'] == b['generation_input']['system']
    assert a['context']['evidence'] == []
    assert all(set(r) == {'record_id', 'text'} for r in a['context']['records'])
    assert all('annotation' in r for r in b['context']['records'])
    assert 'record_context' not in json.dumps(b['context'])  # No whole index supplied.
    assert len(a['included_record_ids']) == 2
    assert len(b['included_record_ids']) < len(rows())


def test_qualification_and_supersession_expansion_follows_exported_relationships():
    consumer = Consumer(rows(), Limits(max_records=8, max_expansions=14, max_chars=14000))
    result = consumer.bundle([{'record_id': 'candidate-synthetic', 'score': 1}], True)
    assert {'ua-limit', 'corrected-synthetic', 'correction-synthetic'} <= set(result['included_record_ids'])
    assert 'advisory2021' in result['included_evidence_ids']
    assert any(a['reason'] == 'superseded_by' and a['status'] == 'included' for a in result['audit'])
    assert any(a['reason'] == 'qualification_refs' and a['status'] == 'included' for a in result['audit'])
    assert any(a['status'] == 'already_included' for a in result['audit'])


def test_missing_targets_and_cycles_terminate_visibly():
    data = copy.deepcopy(rows())
    for row in data:
        index = row['provenance']['extensions'][NS]['record_context']
        index['candidate-synthetic']['qualification_refs'].append('missing-target')
        index['candidate-synthetic']['related_refs'].append('candidate-synthetic')
    result = Consumer(data).bundle([{'record_id': 'candidate-synthetic', 'score': 1}], True)
    assert any(a['target'] == 'missing-target' for a in result['unresolved'])
    assert len(result['audit']) < 100
    assert len(result['included_record_ids']) == len(set(result['included_record_ids']))


def test_context_character_record_expansion_and_depth_limits():
    limits = Limits(max_chars=1500, max_records=2, max_expansions=1, max_depth=1)
    bundle = Consumer(rows(), limits).bundle([{'record_id': 'candidate-synthetic', 'score': 1}], True)
    assert bundle['context_chars'] == len(bundle['context_text']) <= limits.max_chars
    assert len(bundle['included_record_ids']) <= limits.max_records
    assert bundle['expansions_included'] <= limits.max_expansions
    assert bundle['truncated']
    assert any(e['status'] == 'truncated' and e['limit'] for e in bundle['audit'])
    assert all(e['depth'] <= limits.max_depth for e in bundle['audit'] if e['status'] == 'included')


def test_posthoc_coverage_does_not_count_global_metadata_as_evidence():
    expected = [{'id': 'q', 'expected_record_refs': ['es-limit'],
                 'expected_evidence_refs': ['npm2018']}]
    inputs = prepare(rows(), [{'id': 'q', 'question': 'event-stream response'}])
    report = coverage_report(inputs, expected)
    text_only = inputs['trials'][0]
    assert 'npm2018' in text_only['metadata_available_evidence_ids']
    assert 'npm2018' in report[0]['expected_citations_missing']
    assert not report[0]['source_bodies_available']
    assert 'expected_record_refs' not in json.dumps(inputs)
    assert 'raw_answer' not in json.dumps(inputs)
    assert all('accuracy' not in item for item in report)


def test_irrelevant_question_does_not_receive_the_whole_pack():
    inputs = prepare(rows(), [{'id': 'q', 'question': 'xyzzynonexistenttopic'}])
    assert all(t['context']['records'] == [] for t in inputs['trials'])
    assert all(t['initial_retrieval'] == [] for t in inputs['trials'])



def test_recorded_prompts_and_measured_outputs_are_separate():
    run = ROOT / 'docs/experiments/institutional-consumer/run-2026-11-08'
    inputs = json.loads((run / 'inputs.json').read_text())
    measured = json.loads((run / 'answers.json').read_text())
    assert measured['status'] == 'completed'
    assert len(measured['answers']) == len(inputs['trials']) == 14
    assert len({(a['question_id'], a['condition']) for a in measured['answers']}) == 14
    assert all(a['status'] == 'completed' and a['raw_answer'] for a in measured['answers'])
    assert 'expected_answer' not in json.dumps(measured)
    assert 'rubric_judgments' not in json.dumps(measured)
    for trial in inputs['trials']:
        assert trial['context_text'] in trial['generation_input']['prompt']
        assert trial['context_chars'] <= trial['limits']['max_chars']
        assert 'expected_record_refs' not in json.dumps(trial['generation_input'])
