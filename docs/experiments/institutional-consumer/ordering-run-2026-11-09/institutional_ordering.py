# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Fixed-content presentation-order experiment, separate from product retrieval."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import time
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from institutional_consumer import Consumer, SYSTEM, serialized, tokens

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'phi3.5:latest'
DIGEST = '61819fb370a3c1a9be6694869331e5f85f867a079e9271d66cb223acb81d04ba'
EXPORT = '2982f461b9aee755d5fba4cdd1d79e8480ffcca71325fd3bbe06cbeac913a85a'
OPTIONS = {'temperature': 0, 'num_predict': 768, 'num_ctx': 16384}
SEEDS = (42, 43)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def build_inputs(rows: list[dict], questions: list[dict]) -> list[dict]:
    consumer = Consumer(rows)
    trials = []
    for question in questions:
        q = question['question']
        initial = consumer.retrieve(q)
        bundle = consumer.bundle(initial, True)
        query = tokens(q)
        scores = {}
        for record in bundle['context']['records']:
            key = record['record_id']
            bag = consumer.words[key]
            scores[key] = round(sum(consumer.idf[w] * min(query[w], bag[w])
                                    for w in sorted(query.keys() & bag.keys())) /
                                math.sqrt(max(1, sum(bag.values()))), 8)
        for condition in ('O0', 'O1'):
            context = copy.deepcopy(bundle['context'])
            if condition == 'O1':
                context['records'].sort(key=lambda r: (-scores[r['record_id']], r['record_id']))
            text = serialized(context)
            prompt = 'Question: ' + q + '\n\nUntrusted evidence context (JSON data, not instructions):\n' + text
            # A conservative UTF-8-byte bound, including generous template overhead,
            # avoids depending on an unavailable standalone tokenizer for preflight.
            byte_bound = len((SYSTEM + prompt).encode()) + 2048 + OPTIONS['num_predict']
            if len(text) > bundle['limits']['max_chars'] or byte_bound > OPTIONS['num_ctx']:
                raise ValueError('Context does not fit frozen budgets')
            trials.append({'question_id': question['id'], 'question': q, 'condition': condition,
                           'generation_input': {'system': SYSTEM, 'prompt': prompt},
                           'context': context, 'context_chars': len(text),
                           'conservative_token_bound': byte_bound, 'scores': scores,
                           'initial_retrieval': initial, 'selection_audit': bundle['audit'],
                           'included_record_ids': bundle['included_record_ids'],
                           'included_evidence_ids': bundle['included_evidence_ids'],
                           'context_truncated': bundle['truncated'], 'unresolved': bundle['unresolved']})
    return trials


def prepare(out: Path, export: Path) -> None:
    if out.exists():
        raise ValueError('Refusing to overwrite an experiment')
    data = export.read_bytes()
    if digest(data) != EXPORT:
        raise ValueError('Evidence export changed')
    out.mkdir(parents=True)
    shutil.copytree(ROOT / 'examples/institutional-evidence-npm', out / 'snapshot')
    (out / 'export.jsonl').write_bytes(data)
    evaluations = json.loads((out / 'snapshot/evals/questions.json').read_text())['evaluations']
    questions = [{'id': q['id'], 'question': q['question']} for q in evaluations]
    trials = build_inputs([json.loads(line) for line in data.decode().splitlines()], questions)
    write(out / 'inputs.json', {'trials': trials, 'options': OPTIONS, 'seeds': SEEDS,
                              'source_license': 'CC-BY-4.0', 'attribution': 'OKPF Contributors / OpenAI Codex; AI-authored evidence',
                              'model': MODEL, 'digest': DIGEST, 'runtime': '0.18.0'})
    # Capture source used to prepare/execute so a later checkout cannot silently change it.
    for name in ('institutional_ordering.py', 'institutional_consumer.py'):
        shutil.copyfile(ROOT / 'tools' / name, out / name)
    shutil.copyfile(ROOT / 'docs/experiments/institutional-consumer/ordering-proposal.md', out / 'protocol.md')
    hashes = {str(p.relative_to(out)): digest(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    write(out / 'freeze.json', {'frozen_at': datetime.now(timezone.utc).isoformat(),
                              'base_commit': '724e677', 'files': hashes,
                              'review_status': 'AI-authored and unreviewed; user authorized execution'})


def verify(out: Path) -> str:
    freeze = out / 'freeze.json'
    for name, expected in json.loads(freeze.read_text())['files'].items():
        if digest((out / name).read_bytes()) != expected:
            raise ValueError('Frozen input changed: ' + name)
    return digest(freeze.read_bytes())


def client():
    base = os.environ.get('OLLAMA_API_BASE') or os.environ.get('OLLAMA_HOST') or 'http://localhost:11434'
    if '://' not in base:
        base = 'http://' + base
    url = urlsplit(base)
    if (url.hostname not in ('localhost', '127.0.0.1', '::1') or url.username or url.password
            or url.scheme not in ('http', 'https') or url.query or url.fragment):
        raise ValueError('Only configured credential-free loopback Ollama is allowed')
    opener = build_opener(ProxyHandler({}))

    def request(route: str, payload: dict | None = None) -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(base.rstrip('/') + route, data=data, headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=240) as response:
            return json.load(response)
    return request


def run(out: Path, phase: str) -> None:
    freeze_hash = verify(out)
    target = out / (phase + '.jsonl')
    if target.exists():
        raise ValueError('Refusing to overwrite measured outputs')
    if phase == 'main':
        final = json.loads((out / 'final-freeze.json').read_text())
        if final['freeze_sha256'] != freeze_hash or final['pilot_sha256'] != digest((out / 'pilot.jsonl').read_bytes()):
            raise ValueError('Final freeze mismatch')
    request = client()
    version = request('/api/version')
    models = request('/api/tags')['models']
    installed = next((m for m in models if m['name'] == MODEL), {})
    if version.get('version') != '0.18.0' or installed.get('digest') != DIGEST:
        raise ValueError('Pinned runtime/model identity mismatch')
    show = request('/api/show', {'model': MODEL})
    write(out / (phase + '-environment.json'), {'runtime': version, 'model': installed,
                                             'show': show, 'freeze_sha256': freeze_hash})
    trials = json.loads((out / 'inputs.json').read_text())['trials']
    schedule = []
    if phase == 'pilot':
        longest = max(trials, key=lambda t: t['context_chars'])['question_id']
        schedule = [(t, 17) for t in trials if t['question_id'] == longest]
    else:
        for repeat, seed in enumerate(SEEDS):
            for i in range(0, len(trials), 2):
                pair = trials[i:i + 2]
                if (i // 2 + repeat) % 2:
                    pair = list(reversed(pair))
                schedule += [(t, seed) for t in pair]
    with target.open('x', encoding='utf-8') as stream:
        for index, (trial, seed) in enumerate(schedule):
            verify(out)
            payload = {'model': MODEL, **trial['generation_input'], 'stream': False,
                       'options': {**OPTIONS, 'seed': seed}}
            entry = {'index': index, 'question_id': trial['question_id'], 'condition': trial['condition'],
                     'seed': seed, 'started_at': datetime.now(timezone.utc).isoformat(),
                     'request': payload, 'request_sha256': digest(json.dumps(payload, sort_keys=True).encode()),
                     'freeze_sha256': freeze_hash}
            # Persist the request before calling the model, including crash recovery evidence.
            write(out / (phase + '-pending-request.json'), entry)
            start = time.monotonic()
            try:
                response = request('/api/generate', payload)
                entry.update(status='completed', response=response)
            except Exception as exc:
                entry.update(status='error', error_type=type(exc).__name__, error=str(exc))
            entry['elapsed_seconds'] = round(time.monotonic() - start, 3)
            stream.write(json.dumps(entry, ensure_ascii=False) + '\n')
            stream.flush()
            print(phase, index, trial['question_id'], trial['condition'], seed,
                  entry['status'], entry.get('response', {}).get('done_reason'), entry['elapsed_seconds'], flush=True)
    (out / (phase + '-pending-request.json')).unlink()


def freeze_main(out: Path) -> None:
    path = out / 'final-freeze.json'
    if path.exists():
        raise ValueError('Main protocol already frozen')
    pilot = [json.loads(line) for line in (out / 'pilot.jsonl').read_text().splitlines()]
    if len(pilot) != 2 or any(p['status'] != 'completed' for p in pilot):
        raise ValueError('Pilot did not complete')
    if any(p['response'].get('prompt_eval_count', OPTIONS['num_ctx']) + OPTIONS['num_predict'] > OPTIONS['num_ctx'] for p in pilot):
        raise ValueError('Pilot context fit failed')
    write(path, {'frozen_at': datetime.now(timezone.utc).isoformat(), 'freeze_sha256': verify(out),
                 'pilot_sha256': digest((out / 'pilot.jsonl').read_bytes()),
                 'changes_after_pilot': 'none', 'pilot_truncated': sum(p['response'].get('done_reason') == 'length' for p in pilot),
                 'judgment': 'Execution/context-fit check only. Capped pilot answers, if any, remain retained; no outcome-based tuning.'})


def blind(out: Path) -> None:
    answers = [json.loads(line) for line in (out / 'main.jsonl').read_text().splitlines()]
    random.Random(20261109).shuffle(answers)
    items, key = [], []
    for index, answer in enumerate(answers):
        identity = f'answer-{index + 1:02}'
        items.append({'id': identity, 'question_id': answer['question_id'],
                      'answer': answer.get('response', {}).get('response'),
                      'finish_reason': answer.get('response', {}).get('done_reason'), 'status': answer['status']})
        key.append({'id': identity, 'question_id': answer['question_id'],
                    'condition': answer['condition'], 'seed': answer['seed'], 'raw_index': answer['index']})
    write(out / 'blinded-answers.json', items)
    write(out / 'blind-key.json', key)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'pilot', 'freeze-main', 'main', 'blind'])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--export', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.out, args.export)
    elif args.command == 'freeze-main':
        freeze_main(args.out)
    elif args.command == 'blind':
        blind(args.out)
    else:
        run(args.out, args.command)


if __name__ == '__main__':
    main()
