"""Text-normalization helpers for damaged extraction output (PDF-heavy so far).

Kept separate from extractors.py so it's independently testable and usable
from chunking/prompt-building code without an extractor round-trip.
"""
from __future__ import annotations

import re
import unicodedata

_REPLACEMENT_CHAR = "�"
_BLANK_LINES_RE = re.compile(r"\n{3,}")
_TRAILING_WHITESPACE_RE = re.compile(r"[ \t]+\n")


def normalize_extracted_text(text: str) -> str:
    """Best-effort cleanup for text pulled out of damaged/degraded PDFs.

    - NFKC-normalizes Unicode (folds compatibility/ligature/trademark-symbol
      variants like the fi-ligature or ™ built from combining characters
      into their standard forms, which otherwise tokenize unpredictably).
    - Strips stray U+FFFD replacement characters (produced when the PDF's
      font encoding couldn't be mapped to a real character) rather than
      leaving them in the prompt, where they add noise without meaning.
    - Collapses 3+ blank lines down to a single blank line and strips
      trailing whitespace before newlines — common artifacts of per-page
      text concatenation.

    Does not attempt to deduplicate repeated page-boundary text (headers/
    footers repeated verbatim across pages) — no heuristic was found that
    reliably distinguishes intentional repetition (e.g. a recurring term)
    from a duplicated header without risking deleting real content.
    """
    if not text:
        return text
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace(_REPLACEMENT_CHAR, "")
    normalized = _TRAILING_WHITESPACE_RE.sub("\n", normalized)
    normalized = _BLANK_LINES_RE.sub("\n\n", normalized)
    return normalized


def replacement_char_count(text: str) -> int:
    """Count of U+FFFD replacement characters in the original text, before
    normalization — useful as a damage-severity diagnostic."""
    return text.count(_REPLACEMENT_CHAR)
