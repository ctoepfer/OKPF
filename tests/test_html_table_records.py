from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from okpf_prep.models import OKPFRecord
from okpf_prep.profiles import load_profile
from okpf_prep.runner import _ground_record, prepare_training_pack

PROFILES_DIR = Path(__file__).parent.parent / "profiles"


def _brewing_profile():
    return load_profile(PROFILES_DIR / "brewing_recipe.yaml")


def _general_profile():
    return load_profile(PROFILES_DIR / "general_knowledge.yaml")


def _write_html(tmp_path: Path, name: str, body: str) -> Path:
    source = tmp_path / name
    source.write_text(dedent(body).strip(), encoding="utf-8")
    return source


def _read_records(output_dir: Path) -> list[dict]:
    payload = json.loads((output_dir / "records.json").read_text(encoding="utf-8"))
    return payload["records"]


def test_one_table_row_produces_one_record(tmp_path: Path) -> None:
    profile = _brewing_profile()
    source = _write_html(
        tmp_path,
        "one-row.html",
        """
        <html><body><article>
          <table>
            <tr><th>Name</th><th>Amount</th><th>Notes</th></tr>
            <tr><td>Cascade</td><td>1.5 oz</td><td>Citrus</td></tr>
          </table>
        </article></body></html>
        """,
    )

    result = prepare_training_pack(source, PROFILES_DIR / "brewing_recipe.yaml", tmp_path / "out", backend="ollama")
    records = _read_records(result.output_dir)

    assert result.record_count == 1
    assert len(records) == 1
    assert records[0]["record_type"] == "ingredient_reference"


def test_145_rows_produce_145_deterministic_records(tmp_path: Path) -> None:
    profile = _brewing_profile()
    rows = "\n".join(
        f"<tr><td>Ingredient {i}</td><td>{i} g</td><td>Note {i}</td></tr>" for i in range(145)
    )
    source = _write_html(
        tmp_path,
        "145-rows.html",
        f"""
        <html><body><article>
          <table>
            <tr><th>Name</th><th>Amount</th><th>Notes</th></tr>
            {rows}
          </table>
        </article></body></html>
        """,
    )

    result = prepare_training_pack(source, PROFILES_DIR / "brewing_recipe.yaml", tmp_path / "out145", backend="ollama")
    records = _read_records(result.output_dir)

    assert result.record_count == 145
    assert len(records) == 145
    assert records[0]["title"] == "Ingredient 0"
    assert records[-1]["title"] == "Ingredient 144"


def test_comments_empty_cells_and_column_order_are_preserved(tmp_path: Path) -> None:
    source = _write_html(
        tmp_path,
        "preserve.html",
        """
        <html><body><article>
          <table>
            <tr><th>Name</th><th>Amount</th><th>Link</th><th>Notes</th></tr>
            <!-- <tr><td>ShouldNotAppear</td><td>99</td><td>X</td><td>Y</td></tr> -->
            <tr><td>Caramel 60</td><td></td><td><a href="/products/c60">product</a></td><td>Sweet</td></tr>
          </table>
        </article></body></html>
        """,
    )

    result = prepare_training_pack(
        source,
        PROFILES_DIR / "brewing_recipe.yaml",
        tmp_path / "out-preserve",
        backend="ollama",
        source_url="https://example.test/catalog/preserve.html",
    )
    records = _read_records(result.output_dir)
    row = records[0]["metadata"]["okpf"]

    assert result.record_count == 1
    assert records[0]["title"] == "Caramel 60"
    assert row["table_headers"] == ["Name", "Amount", "Link", "Notes"]
    assert row["source_row_values"] == ["Caramel 60", "product", "Sweet"]
    assert row["raw_row"]["columns"][1]["value"] is None
    assert row["row_links"][0]["href"] == "/products/c60"
    assert row["row_links"][0]["resolved_url"] == "https://example.test/products/c60"
    assert all("ShouldNotAppear" not in json.dumps(record) for record in records)


def test_relative_links_are_kept_only_as_metadata(tmp_path: Path) -> None:
    source = _write_html(
        tmp_path,
        "links.html",
        """
        <html><body><article>
          <table>
            <tr><th>Name</th><th>Source</th></tr>
            <tr><td>Row1</td><td><a href="/relative/path">link</a></td></tr>
          </table>
        </article></body></html>
        """,
    )

    result = prepare_training_pack(source, PROFILES_DIR / "brewing_recipe.yaml", tmp_path / "out-links", backend="ollama", source_url="https://example.test/page")
    records = _read_records(result.output_dir)
    okpf = records[0]["metadata"]["okpf"]

    assert result.record_count == 1
    assert okpf["row_links"][0]["href"] == "/relative/path"
    assert okpf["row_links"][0]["resolved_url"] == "https://example.test/relative/path"


def test_table_conversion_does_not_call_ollama_when_enrichment_is_optional(tmp_path: Path) -> None:
    source = _write_html(
        tmp_path,
        "no-ollama.html",
        """
        <html><body><article>
          <table>
            <tr><th>Name</th><th>Amount</th></tr>
            <tr><td>Saaz</td><td>2 oz</td></tr>
          </table>
        </article></body></html>
        """,
    )

    with patch("okpf_prep.ai.ollama.OllamaBackend.generate", side_effect=AssertionError("Ollama should not be called for deterministic tables")):
        result = prepare_training_pack(source, PROFILES_DIR / "brewing_recipe.yaml", tmp_path / "out-no-ollama", backend="ollama")

    assert result.record_count == 1
    assert result.validation_status == "pass"


def test_mixed_prose_and_table_content_preserves_both_paths(tmp_path: Path) -> None:
    source = _write_html(
        tmp_path,
        "mixed.html",
        """
        <html><body><article>
          <p>This paragraph explains the malt bill in general terms.</p>
          <table>
            <tr><th>Name</th><th>Amount</th></tr>
            <tr><td>Pilsner</td><td>8 lb</td></tr>
            <tr><td>Munich</td><td>2 lb</td></tr>
          </table>
        </article></body></html>
        """,
    )

    def fake_generate(**kwargs):
        return json.dumps({
            "records": [
                {
                    "type": "process_note",
                    "title": "Mash note",
                    "summary": "Use a single infusion mash.",
                    "content": "Use a single infusion mash.",
                    "source_refs": [{"source_file": "mixed.html", "chunk_id": "chunk-0000"}],
                    "confidence": 0.9,
                }
            ]
        })

    with patch("okpf_prep.ai.ollama.OllamaBackend.generate", side_effect=fake_generate):
        result = prepare_training_pack(source, PROFILES_DIR / "brewing_recipe.yaml", tmp_path / "out-mixed", backend="ollama")

    records = _read_records(result.output_dir)
    record_types = {record["record_type"] for record in records}

    assert result.record_count == 3
    assert "ingredient_reference" in record_types
    assert "process_note" in record_types


def test_reference_entry_alias_resolves_per_profile() -> None:
    brewing = _brewing_profile()
    general = _general_profile()

    assert brewing.resolve_record_type("reference_entry") == "ingredient_reference"
    assert general.resolve_record_type("reference_entry") == "reference"


def test_unsupported_numerical_claim_is_flagged() -> None:
    warnings, errors = _ground_record(
        OKPFRecord(
            type="ingredient_reference",
            title="Cascade",
            summary="Use 999 oz of hops.",
            content="Use 999 oz of hops.",
            source_refs=[{"source_file": "source.html", "chunk_id": "chunk-0000"}],
            confidence=1.0,
            metadata={"okpf": {"source_row_text": "Cascade | 1.5 oz | Citrus"}},
        ),
        "Cascade | 1.5 oz | Citrus",
    )

    assert any("unsupported numerical" in error for error in errors)


def test_promotional_text_is_flagged() -> None:
    from okpf_prep.models import OKPFRecord

    warnings, errors = _ground_record(
        OKPFRecord(
            type="reference_entry",
            title="Promo",
            summary="Click here to buy now.",
            content="Click here to buy now.",
            source_refs=[{"source_file": "source.html", "chunk_id": "chunk-0000"}],
            confidence=1.0,
            metadata={"okpf": {"source_row_text": "Row data"}},
        ),
        "Row data",
    )

    assert not warnings
    assert any("promotional/navigation" in error for error in errors)


def test_prose_chunk_can_legitimately_return_zero_records(tmp_path: Path) -> None:
    source = _write_html(
        tmp_path,
        "zero-prose.html",
        """
        <html><body><article>
          <p>This is generic prose with no extractable training facts.</p>
        </article></body></html>
        """,
    )

    with patch("okpf_prep.ai.ollama.OllamaBackend.generate", return_value=json.dumps({"records": []})):
        result = prepare_training_pack(source, PROFILES_DIR / "brewing_recipe.yaml", tmp_path / "out-zero", backend="ollama")

    assert result.record_count == 0
    assert result.validation_status == "pass"