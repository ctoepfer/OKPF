# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Auto-generate Q&A evaluation pairs from document text using simple heuristics."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class EvalQuestion:
    id: str
    question: str
    expected_answer: str


def extract_sentences(text: str) -> list[str]:
    """Extract sentences from text, cleaning up whitespace."""
    sentences = re.split(r'[.!?]+', text)
    result = []
    for sentence in sentences:
        cleaned = sentence.strip()
        if cleaned and len(cleaned) > 10:
            result.append(cleaned)
    return result


def extract_sections(text: str) -> dict[str, str]:
    """Extract sections by markdown headers and their content."""
    sections = {}
    current_section = "general"
    current_content = []

    lines = text.split('\n')
    for line in lines:
        header_match = re.match(r'^#+\s+(.+)$', line)
        if header_match:
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = header_match.group(1)
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def auto_generate_questions(
    source_text: str,
    max_questions: int = 3,
) -> list[EvalQuestion]:
    """Generate Q&A pairs from document text using simple heuristics.

    For each section (or up to max_questions):
    - Extract the first substantial sentence
    - Create a question from it
    - Use the sentence as the expected answer

    Args:
        source_text: The full document text
        max_questions: Maximum number of questions to generate (default 3)

    Returns:
        List of EvalQuestion objects
    """
    sections = extract_sections(source_text)
    questions = []

    for section_name, content in list(sections.items())[:max_questions]:
        if not content:
            continue

        sentences = extract_sentences(content)
        if not sentences:
            continue

        first_sentence = sentences[0]
        section_label = section_name if section_name != "general" else "Content"

        question_text = _make_question(first_sentence, section_label)
        q = EvalQuestion(
            id=f"q{len(questions) + 1}",
            question=question_text,
            expected_answer=first_sentence,
        )
        questions.append(q)

    return questions[:max_questions]


def _make_question(statement: str, topic: str) -> str:
    """Convert a statement into a question."""
    statement_clean = statement.rstrip('.!?').strip()
    if not statement_clean:
        return f"What is {topic}?"

    if len(statement_clean) > 80:
        statement_clean = statement_clean[:77] + "..."

    return f"What does the text say about {topic}?"
