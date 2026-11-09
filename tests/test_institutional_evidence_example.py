# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Fixture integrity and export context, not historical or consumer accuracy."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from okpf.export import build_citation_rows, build_rag_rows
from okpf_validate import validate_pack

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'examples/institutional-evidence-npm'
NS = 'org.okpf.examples.institutional_evidence'


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def records() -> dict[str, dict]:
    values = [json.loads(line) for line in
              (PACK / 'records/evidence.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len({r['id'] for r in values}) == len(values)
    return {r['id']: r for r in values}


def assert_context_closed(context: dict, original: dict[str, dict]) -> None:
    index = context['extensions'][NS]['record_context']
    evidence = context['evidence_index']
    assert set(index) == set(original)
    for record_id, entry in index.items():
        # Prevent mirrored projection drift: otherwise citations could carry
        # stale qualifications even though the underlying record is corrected.
        assert entry == {'record_path': 'records/evidence.jsonl',
                         'title': original[record_id]['title'],
                         **original[record_id]['metadata'][NS]}
        assert (PACK / entry['record_path']).is_file()
        assert set(entry['evidence_refs']) <= evidence.keys()
        for field in ('qualification_refs', 'related_refs', 'supporting_refs', 'contrary_refs'):
            assert set(entry.get(field, [])) <= index.keys()
        for field in ('candidate_ref', 'corrected_ref', 'supersedes', 'superseded_by', 'outcome_ref'):
            if field in entry:
                assert entry[field] in index
    for source in evidence.values():
        assert source['url'].startswith('https://')
        assert all(source[key] for key in ('locator', 'published', 'accessed',
                                           'limitations', 'availability', 'redistribution'))


def test_pack_records_and_evaluations_conform_to_existing_schemas() -> None:
    result = validate_pack(str(PACK))
    assert result.valid, result.errors
    manifest = read_json(PACK / 'manifest.json')
    assert manifest['profiles'] == ['okpf-core']
    assert manifest['records'][0]['record_count'] == len(records())
    schema = Draft202012Validator(read_json(ROOT / 'schemas/record.schema.json'))
    for record in records().values():
        schema.validate(record)
    Draft202012Validator(read_json(ROOT / 'schemas/evaluation.schema.json')).validate(
        read_json(PACK / 'evals/questions.json'))


@pytest.mark.parametrize('archive', [False, True])
def test_exports_preserve_evidence_qualification_and_disagreement_connections(tmp_path, archive) -> None:
    path = PACK
    if archive:
        path = tmp_path / 'institutional.kpack'
        with zipfile.ZipFile(path, 'w') as zf:
            for file in PACK.rglob('*'):
                if file.is_file():
                    zf.write(file, file.relative_to(PACK))
        assert validate_pack(str(path)).valid
    original = records()
    rag = build_rag_rows(str(path))
    citations = build_citation_rows(rag)
    assert {row['record_id'] for row in rag} == set(original)
    assert len(citations) == len(original)
    for row, citation in zip(rag, citations, strict=True):
        assert row['text'] == original[row['record_id']]['text']
        assert row['artifact_path'] == 'records/evidence.jsonl'
        assert row['source_path'] is None  # Intentional whole-provenance fallback.
        assert row['schema_version'] == 'okpf.rag_export.v0.1'
        assert citation == {key: value for key, value in row.items() if key != 'text'}
        assert_context_closed(citation['provenance'], original)
    index = citations[0]['provenance']['extensions'][NS]['record_context']
    assert 'es-assess-users' in index['es-assess-containment']['related_refs']
    assert 'es-assess-containment' in index['es-assess-users']['related_refs']
    assert 'ua-dispute' in index['ua-transition']['related_refs']
    assert index['comparison']['rejection_conditions']
    assert 'user recovery' in index['es-limit']['qualification_summary']
    assert 'no denominator' in index['selection']['qualification_summary']
    # Critical caveat travels with the claim even for text-only retrieval.
    assert 'unmeasured' in original['es-response']['text']
    assert 'not independently' in original['es-rule']['metadata'][NS]['observed_practice']


def test_supersession_is_resolvable_and_explicitly_synthetic_in_citations() -> None:
    rows = build_citation_rows(build_rag_rows(str(PACK)))
    index = rows[0]['provenance']['extensions'][NS]['record_context']
    candidate = index['candidate-synthetic']
    replacement = index[candidate['superseded_by']]
    event = index['correction-synthetic']
    assert candidate['status'] == 'superseded'
    assert replacement['supersedes'] == event['candidate_ref'] == 'candidate-synthetic'
    assert event['corrected_ref'] == 'corrected-synthetic'
    assert event['feedback_summary']
    assert event['contributor_context']['human_reviewer'] is None
    assert all(index[key]['synthetic'] for key in
               ('candidate-synthetic', 'corrected-synthetic', 'correction-synthetic'))
    assert 'SUPERSEDED' in records()['candidate-synthetic']['text']


def test_evaluation_references_cover_the_rubrics_without_measured_results() -> None:
    evaluations = read_json(PACK / 'evals/questions.json')
    context = read_json(PACK / 'provenance/context.json')
    index = context['extensions'][NS]['record_context']
    artifact_ids = {a['id'] for a in read_json(PACK / 'manifest.json')['artifacts']}
    assert {e['id'] for e in evaluations['evaluations']} == {
        'qualified-retrieval', 'conflicting-interpretation', 'rule-practice',
        'mismatch', 'trace', 'abstain', 'supersession'}
    for evaluation in evaluations['evaluations']:
        assert evaluation['expected_record_refs']
        assert set(evaluation['expected_record_refs']) <= index.keys()
        assert set(evaluation['expected_evidence_refs']) <= context['evidence_index'].keys()
        assert set(evaluation['source_artifacts']) <= artifact_ids
        assert evaluation['expected_answer']['rubric']
        assert 'score' not in evaluation and 'actual_answer' not in evaluation
    assert 'AI-authored' in evaluations['description']


def test_distinct_limits_and_assessment_objects_are_retained() -> None:
    values = records()
    assert {'unknown', 'inference', 'disputed', 'checked_no_result',
            'uncertain_transferability', 'source_attested'} <= {
                r['metadata'][NS]['status'] for r in values.values()}
    assert values['selection']['metadata'][NS]['denominator'] is None
    assert values['search-scope']['metadata'][NS]['not_yet_checked']
    for record in values.values():
        if record['record_type'] == 'outcome_assessment':
            assessment = record['metadata'][NS]['assessment']
            assert all(assessment.get(field) for field in (
                'object', 'affected_group', 'baseline', 'observation', 'horizon',
                'assessor', 'rationale', 'uncertainty'))
