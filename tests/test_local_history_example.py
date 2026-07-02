# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests specific to examples/local-history-lost-electric-sign.

Beyond generic pack validity (covered in tests/test_pack_archive.py), this
example is a worked demonstration of preserving incomplete historical
evidence trails. These tests check the properties that actually matter for
that use case: the source image is present and self-contained, every
record file parses and carries the required uncertainty-tracking facets,
and export-rag treats the records (not the raw artifacts) as the RAG-ready
form, per docs/rag-export.md's records-first chunking rule.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import export  # noqa: E402
from okpf_validate import validate_pack  # noqa: E402

PACK_DIR = REPO_ROOT / "examples" / "local-history-lost-electric-sign"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_pack_validates() -> None:
    result = validate_pack(str(PACK_DIR))
    assert result.valid, [str(issue) for issue in result.issues]


def test_source_image_is_self_contained_in_the_example() -> None:
    image_path = PACK_DIR / "sources" / "newspaper-clipping" / "bonita-electric-sign-article.jpeg"
    assert image_path.is_file()
    assert image_path.stat().st_size > 0


def test_claims_carry_confidence_and_status_facets() -> None:
    claims = _read_jsonl(PACK_DIR / "records" / "claims.jsonl")
    assert len(claims) == 7
    for claim in claims:
        assert claim["record_type"] == "historical_claim"
        assert claim["facets"]["status"] == "source_attested"
        assert claim["facets"]["confidence"] in {"low", "medium", "high"}


def test_timeline_marks_uncertainty_explicitly() -> None:
    events = _read_jsonl(PACK_DIR / "records" / "timeline.jsonl")
    certainties = {event["facets"]["certainty"] for event in events}
    # The whole point of this pack is that not everything is confirmed.
    assert "unconfirmed" in certainties
    assert "confirmed" in certainties


def test_no_claim_or_timeline_record_asserts_installation_as_fact() -> None:
    # Scoped to claims.jsonl and timeline.jsonl -- the two files that make
    # historical assertions. research-leads.jsonl legitimately contains
    # phrases like "confirm whether the sign was installed" (a question),
    # which is exactly the uncertainty this pack is supposed to preserve.
    asserting_records = _read_jsonl(PACK_DIR / "records" / "claims.jsonl")
    asserting_records += _read_jsonl(PACK_DIR / "records" / "timeline.jsonl")

    for record in asserting_records:
        text = record["text"].lower()
        assert "was installed" not in text
        assert "has been installed" not in text


def test_negative_search_records_do_not_claim_exhaustive_research() -> None:
    negative_searches = _read_jsonl(PACK_DIR / "records" / "negative-searches.jsonl")
    assert negative_searches
    for record in negative_searches:
        assert record["facets"]["status"] == "not_yet_checked"


def test_research_leads_are_all_unchecked() -> None:
    leads = _read_jsonl(PACK_DIR / "records" / "research-leads.jsonl")
    assert len(leads) == 8
    assert all(lead["facets"]["status"] == "not_yet_checked" for lead in leads)


def test_export_rag_uses_records_not_raw_artifacts() -> None:
    rows = export.build_rag_rows(str(PACK_DIR))

    # Records-first chunking rule: since this pack declares records, every
    # row should come from a records/*.jsonl file, not from artifacts/*.md.
    assert rows
    assert all(row["artifact_path"].startswith("records/") for row in rows)
    assert all(row["record_id"] is not None for row in rows)


def test_evals_test_uncertainty_not_just_facts() -> None:
    evals_path = PACK_DIR / "evals" / "historical-research-questions.json"
    data = json.loads(evals_path.read_text(encoding="utf-8"))
    questions = [item["question"].lower() for item in data["evaluations"]]

    assert any("not prove" in q for q in questions)
    assert any("photograph" in q for q in questions)
