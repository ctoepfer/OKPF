# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Offline structural linting; no inference of commitments from free prose."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from okpf.review import ReviewError, load_cases, match_cases, parse_proposal

# Mentions are review prompts, never evidence of an adopted safeguard or evasion.
METRICS = {
    'multisig': (r'\b(?:multi[- ]?sig|multi[- ]signature|\d+[- ]of[- ]\d+)\b',
                 ('nominal_compliance', 'channel_shifting')),
    'retention': (r'\b(?:housing|housed|retention|attrition)\b',
                  ('definition_dilution', 'selective_reporting')),
    'threshold': (r'\b(?:threshold|quota|target)\b',
                  ('threshold_gaming', 'selective_reporting')),
    'audit': (r'\b(?:audit|approval|consensus)\b',
              ('nominal_compliance', 'channel_shifting')),
}


def read_proposal(path: Path) -> tuple[str, dict[str, Any]]:
    text = path.read_text(encoding='utf-8')
    if path.suffix.lower() == '.json':
        def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ReviewError(f'Duplicate proposal key: {key}')
                result[key] = value
            return result
        def invalid_constant(value: str) -> None:
            raise ReviewError(f'Invalid JSON constant: {value}')
        proposal = json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant)
        # Reuse the review declaration checks without accepting non-JSON syntax.
        proposal = parse_proposal('---\n' + json.dumps(proposal) + '\n---')
    elif path.suffix.lower() in {'.yaml', '.yml'}:
        lines = text.splitlines()
        if lines and lines[0].strip() == '---':
            lines = lines[1:]
        if lines and lines[-1].strip() == '...':
            lines = lines[:-1]
        if any(line.strip() in {'---', '...'} for line in lines):
            raise ReviewError('Expected one YAML document')
        proposal = parse_proposal('---\n' + '\n'.join(lines) + '\n---')
    else:
        proposal = parse_proposal(text)
    return text, proposal


def lint_proposal(proposal_path: str | Path, pack_path: str | Path | None = None) -> dict[str, Any]:
    text, proposal = read_proposal(Path(proposal_path))
    schema = json.loads((Path(__file__).parent / 'schemas/profiles/institutional/v1/proposal_lint.json')
                        .read_text(encoding='utf-8'))
    diagnostics: list[dict[str, Any]] = []
    for error in sorted(Draft202012Validator(schema).iter_errors(proposal),
                        key=lambda e: (str(list(e.absolute_path)), e.message)):
        path = '/' + '/'.join(str(p).replace('~', '~0').replace('/', '~1') for p in error.absolute_path)
        diagnostics.append({'severity': 'error', 'code': 'schema', 'path': path,
                            'message': error.message})
    mentions = [key for key, (pattern, _) in METRICS.items() if re.search(pattern, text, re.I)]
    categories = {category for key in mentions for category in METRICS[key][1]}
    for key in mentions:
        diagnostics.append({'severity': 'warning', 'code': 'metric-mention', 'path': '/',
                            'message': f'{key} mentioned: inspect {", ".join(METRICS[key][1])}. '
                            'Lexical hint only; negation, quotations and examples are not interpreted.'})
    candidates = []
    excluded = []
    if pack_path is not None:
        _, cases = load_cases(pack_path)
        for match in match_cases(proposal, cases):
            if not match.matching:
                continue
            case = match.case
            if 'tombstone' in case:
                excluded.append({'case_id': case['id'], 'path': match.path,
                                 'reason': 'Tombstone declared; signature and replacement not verified.'})
                continue
            for vector in case.get('evasion_vectors', []):
                if vector['tactic_category'] in categories:
                    candidates.append({'case_id': case['id'], 'path': match.path,
                                       'matching_fields': list(match.matching), 'vector': vector,
                                       'review_status': case.get('review_status', 'not documented'),
                                       'evidence_sources': case.get('evidence_sources', []),
                                       'unobserved_variables': case['unobserved_variables']})
        if not candidates:
            diagnostics.append({'severity': 'warning', 'code': 'no-case-evidence', 'path': '/',
                                'message': 'No matching active case vectors; absence is not evidence of safety.'})
    else:
        diagnostics.append({'severity': 'warning', 'code': 'no-pack', 'path': '/',
                            'message': 'No pack supplied; historical evasion cross-reference not performed.'})
    return {'experimental': True, 'valid': not any(d['severity'] == 'error' for d in diagnostics),
            'diagnostics': diagnostics, 'metric_mentions': mentions,
            'candidate_vectors': candidates, 'excluded_cases': excluded,
            'limitations': 'Checks structure only, not metric measurability, temporal pre-commitment, '
            'rollback execution, factual accuracy, independent precedent counts, baseline hazard '
            'rates or cryptographic revocation. Candidate vectors are source assertions.'}


def format_report(result: dict[str, Any]) -> str:
    lines = ['Institutional proposal lint (experimental)', '', 'Pre-Mortem Commitment Check / Schema']
    for item in result['diagnostics']:
        lines.append(f"[{item['severity'].upper()}] {item['code']} {item['path']}: {item['message']}")
    lines += ['', 'Adversarial Gaming Audit']
    for candidate in result['candidate_vectors']:
        # JSON escaping keeps untrusted multiline/terminal control characters inert.
        lines.append(json.dumps(candidate, ensure_ascii=True))
    for case in result['excluded_cases']:
        lines.append('Excluded: ' + json.dumps(case, ensure_ascii=True))
    lines += ['PASS (structure only)' if result['valid'] else 'FAIL', result['limitations']]
    return '\n'.join(lines) + '\n'
