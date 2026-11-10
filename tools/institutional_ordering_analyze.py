# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Structural/descriptive reporting only; never automatic answer grading."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def analyze(run: Path) -> dict:
    inputs = json.loads((run / 'inputs.json').read_text())
    raw = [json.loads(line) for line in (run / 'main.jsonl').read_text().splitlines()]
    questions = json.loads((run / 'snapshot/evals/questions.json').read_text())['evaluations']
    expected = {q['id']: q for q in questions}
    contexts, coverage = [], []
    for a, b in zip(inputs['trials'][::2], inputs['trials'][1::2], strict=True):
        sort = lambda c: sorted(c['records'], key=lambda r: r['record_id'])
        assert sort(a['context']) == sort(b['context'])
        assert a['context']['evidence'] == b['context']['evidence']
        assert a['context_chars'] == b['context_chars']
        q = expected[a['question_id']]
        # A common canonical context avoids revealing condition presentation order.
        contexts.append({'question_id': a['question_id'], 'question': q['question'],
                         'rubric': q['expected_answer']['rubric'],
                         'context': {'records': sort(a['context']), 'evidence': a['context']['evidence']}})
        coverage.append({'question_id': a['question_id'], 'same_in_both_conditions': True,
                         'expected_bodies_present': sorted(set(a['included_record_ids']) & set(q['expected_record_refs'])),
                         'expected_bodies_missing': sorted(set(q['expected_record_refs']) - set(a['included_record_ids'])),
                         'context_truncated': a['context_truncated'],
                         'order_changed': a['generation_input'] != b['generation_input']})
    summaries = []
    for q in questions:
        for condition in ('O0', 'O1'):
            entries = [r for r in raw if r['question_id'] == q['id'] and r['condition'] == condition]
            complete = [r for r in entries if r['status'] == 'completed']
            hashes = [hashlib.sha256(r['response']['response'].encode()).hexdigest() for r in complete]
            summaries.append({'question_id': q['id'], 'condition': condition,
                              'scheduled': 2, 'recorded': len(entries), 'completed': len(complete),
                              'errors': len(entries) - len(complete),
                              'truncated': sum(r['response'].get('done_reason') == 'length' for r in complete),
                              'seeds': [r['seed'] for r in entries],
                              'distinct_answers': len(set(hashes)),
                              'response_sha256': hashes,
                              'prompt_tokens': [r['response'].get('prompt_eval_count') for r in complete],
                              'output_tokens': [r['response'].get('eval_count') for r in complete],
                              'elapsed_seconds': [r['elapsed_seconds'] for r in entries]})
    totals = {condition: {'scheduled': 14, 'recorded': sum(s['recorded'] for s in summaries if s['condition'] == condition),
                           'errors': sum(s['errors'] for s in summaries if s['condition'] == condition),
                           'truncated': sum(s['truncated'] for s in summaries if s['condition'] == condition)}
              for condition in ('O0', 'O1')}
    identities = [(r['question_id'], r['condition'], r['seed']) for r in raw]
    assert len(identities) == len(set(identities))
    (run / 'assessment-context.json').write_text(json.dumps(contexts, indent=2, ensure_ascii=False) + '\n')
    result = {'assessment': 'Structural checks and descriptive metrics only; no answer grading',
              'coverage': coverage, 'per_question': summaries, 'totals': totals,
              'finish_reasons': dict(Counter(r.get('response', {}).get('done_reason', 'error') for r in raw))}
    (run / 'metrics.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    analyze(parser.parse_args().run)
