# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Prepare an unscored evaluator-only packet; preserve all frozen artifacts."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

root = Path.cwd()
run = root / 'docs/experiments/institutional-consumer/ordering-run-2026-11-10-restart'
out = root / 'out/institutional-review-packet-2026-11-10'
out.mkdir(exist_ok=False)
answers = json.loads((run / 'blinded-answers.json').read_text())
key = {r['id']: r for r in json.loads((run / 'blind-key.json').read_text())}
raw = {r['index']: r for r in map(json.loads, (run / 'main.jsonl').read_text().splitlines())}
contexts = json.loads((run / 'assessment-context.json').read_text())
assert len(answers) == len(key) == len(raw) == 28
for answer in answers:
    retained = raw[key[answer['id']]['raw_index']]
    assert answer['answer'] == retained['response']['response']
    answer['completion_length'] = {
        'output_tokens': retained['response']['eval_count'],
        'characters': len(answer['answer']),
        'utf8_bytes': len(answer['answer'].encode()),
    }
    answer['truncated'] = answer['finish_reason'] == 'length'
    assert set(answer) == {'id', 'question_id', 'answer', 'finish_reason', 'status', 'completion_length', 'truncated'}

def write(name, value):
    (out / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

write('answers.json', answers)
write('assessment-context.json', contexts)
# Copy exact frozen question criteria, not the proposed new study criteria.
shutil.copyfile(run / 'snapshot/evals/questions.json', out / 'questions.json')
protocol = (run / 'protocol.md').read_text()
section = protocol.split('## Frozen rubric and assessment\n\n', 1)[1]
criteria = section.split('Blind answer presentation', 1)[0]
(out / 'rubric.md').write_text('<!-- SPDX-License-Identifier: Apache-2.0 -->\n\n# Frozen assessment criteria\n\n' + criteria)
by_question = {q['question_id']: q for q in contexts}
judgments = []
for answer in answers:
    judgments.append({'answer_id': answer['id'], 'question_id': answer['question_id'],
        'rubric_items': [{'criterion': criterion, 'rating': None, 'answer_excerpts': [],
                         'reason': None, 'omission_censored': None}
                        for criterion in by_question[answer['question_id']]['rubric']],
        'dimensions': {d: {'rating': None, 'answer_excerpts': [], 'reason': None,
                           'omission_censored': None} for d in
                       ('attribution', 'correction_tracing', 'uncertainty', 'substantive_accuracy')}})
write('unscored-worksheet.json', {'reviewer': None, 'affiliation': None, 'conflicts': None,
      'prior_exposure_to_outputs_or_labels': None, 'scoring_started_at': None,
      'scoring_completed_at': None, 'judgments': judgments})
(out / 'README.md').write_text('''<!-- SPDX-License-Identifier: Apache-2.0 -->

# Evaluator packet

This packet contains 28 verbatim returned answers, their questions, frozen
criteria, common reference context, and an empty worksheet. Evidence content
retains its CC-BY-4.0 attribution to OKPF Contributors / OpenAI Codex and its
AI-authored, human-review-pending status. Historical-source citations are retained;
they are not themselves immutable archived source pages.

Use only this packet for the first scoring pass. Record prior exposure and
conflicts before scoring. Do not seek condition keys, generation prompts,
repository results, or other reviewers' judgments before locking your scores.
Labels, seeds, generation order, model identity, timings and prior findings are
omitted. Answer text is unchanged and may itself reveal clues about its inputs;
masking does not guarantee successful blinding. The organizer must check prior
exposure because the source repository already contains keyed outputs.

Apply each exact question-specific criterion and each dimension separately.
Use met, partial, not_met, or not_assessable, as defined in rubric.md. Correction
tracing is not_applicable for questions other than supersession. Explain each
judgment using exact excerpts. For absence, leave excerpts empty and state which
required material is absent; do not invent quotations. Do not add an overall
accuracy score, stylistic score, or new substantive criterion.

Score only the returned text. Do not grade style or assume what an unfinished
answer would have said. Record omissions at the cutoff as censored. Completion
length and finish status are provided for explicit confound accounting, not as
quality scores. Unsupported assertions before cutoff remain assessable.

Save and hash the completed worksheet before receiving condition labels or any
other reviewer's scores. Resolve rating ambiguities before unmasking and keep a
revision trail; do not force agreement. An organizer should verify completeness,
allowed labels, and excerpt matches without changing your substantive judgments.

Independent human review is requested, not already completed. No findings,
condition comparison, adoption recommendation, or reconciliation conclusions are
included in this packet.
''')
write('reconciliation-template.json', {'status': 'not_started', 'independent_reviews': [],
    'locked_review_hashes': [], 'disagreements': [], 'resolutions': [],
    'unresolved': [], 'condition_key_released_at': None})
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}
write('packet-hashes.json', manifest)
archive = out.with_suffix('.zip')
with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.iterdir()): z.write(p, p.name)
print('Prepared packet:', out.relative_to(root))
print('Archive SHA-256:', hashlib.sha256(archive.read_bytes()).hexdigest())
