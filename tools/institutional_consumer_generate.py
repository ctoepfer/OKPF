# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Run prepared prompts on an already-installed loopback Ollama model only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--model', required=True)
    parser.add_argument('--timeout', type=float, default=180)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; choose a new run path to retain the prior measurement')
    base = os.environ.get('OLLAMA_API_BASE') or os.environ.get('OLLAMA_HOST') or 'http://localhost:11434'
    if '://' not in base:
        base = 'http://' + base
    url = urlsplit(base)
    if url.hostname not in ('127.0.0.1', 'localhost', '::1') or url.username or url.password:
        parser.error('Only an already-configured loopback service without embedded credentials is supported')
    if url.scheme not in ('http', 'https') or url.query or url.fragment:
        parser.error('Invalid local endpoint')
    base = base.rstrip('/')
    opener = build_opener(ProxyHandler({}))

    def request(route: str, payload: dict | None = None) -> dict:
        data = json.dumps(payload).encode('utf-8') if payload is not None else None
        req = Request(base + route, data=data, headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=args.timeout) as response:
            return json.load(response)

    models = request('/api/tags').get('models', [])
    available = next((m for m in models if m.get('name') == args.model), None)
    if available is None:
        parser.error('Requested model is not installed; this command never pulls models')
    version = request('/api/version')
    prepared = json.loads(args.inputs.read_text(encoding='utf-8'))
    options = {'temperature': 0, 'seed': 42, 'num_predict': 384, 'num_ctx': 4096}
    output = {'$comment': 'SPDX-License-Identifier: Apache-2.0 | Copyright 2026 OKPF Contributors',
              'status': 'running', 'model': args.model, 'model_digest': available.get('digest'),
              'service_version': version, 'options': options, 'timeout_seconds': args.timeout,
              'provider_scope': 'Already-configured loopback Ollama; no model installation or paid provider configured by this experiment',
              'started_at': datetime.now(timezone.utc).isoformat(),
              'inputs_export_sha256': prepared['export_sha256'], 'answers': []}

    def save() -> None:
        args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    save()
    for trial in prepared['trials']:
        payload = {'model': args.model, **trial['generation_input'], 'stream': False, 'options': options}
        item = {'question_id': trial['question_id'], 'condition': trial['condition']}
        started = time.monotonic()
        try:
            response = request('/api/generate', payload)
            item.update(status='completed', raw_answer=response.get('response', ''),
                        response_metadata={k: v for k, v in response.items() if k not in ('response', 'context')})
        except Exception as exc:
            item.update(status='error', raw_answer=None, error_type=type(exc).__name__, error=str(exc))
        item['elapsed_seconds'] = round(time.monotonic()-started, 3)
        output['answers'].append(item)
        save()
        print(f"{item['question_id']} {item['condition']}: {item['status']} ({item['elapsed_seconds']}s)", flush=True)
    output['status'] = 'completed_with_errors' if any(a['status'] == 'error' for a in output['answers']) else 'completed'
    output['finished_at'] = datetime.now(timezone.utc).isoformat()
    save()
    return 0 if output['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
