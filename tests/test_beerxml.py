"""Tests for okpf_prep.beerxml — parsing, markdown generation, and record building."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from okpf_prep.beerxml import (
    BeerXMLRecipe,
    beerxml_recipe_to_markdown,
    beerxml_recipe_to_record,
    is_beerxml,
    parse_beerxml_file,
)
from okpf_prep.extractors import extract_text
from okpf_prep.profiles import load_profile
from okpf_prep.runner import prepare_training_pack

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
PROFILES_DIR = Path(__file__).parent.parent / "profiles"
BEERXML_EXAMPLE = EXAMPLES_DIR / "beerxml" / "island_optimized_west_coast_ipa.xml"


# ---------------------------------------------------------------------------
# Fixture XML (minimal valid BeerXML)
# ---------------------------------------------------------------------------

_MINIMAL_BEERXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<RECIPES>
  <RECIPE>
    <NAME>Test Pale Ale</NAME>
    <VERSION>1</VERSION>
    <TYPE>All Grain</TYPE>
    <BREWER>Test Brewer</BREWER>
    <BATCH_SIZE>20.0</BATCH_SIZE>
    <BOIL_SIZE>25.0</BOIL_SIZE>
    <BOIL_TIME>60.0</BOIL_TIME>
    <EFFICIENCY>75.0</EFFICIENCY>
    <OG>1.052</OG>
    <FG>1.010</FG>
    <IBU>35.0</IBU>
    <EST_COLOR>5.5</EST_COLOR>
  </RECIPE>
</RECIPES>
"""

_FULL_BEERXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<RECIPES>
  <RECIPE>
    <NAME>Full Recipe Stout</NAME>
    <VERSION>1</VERSION>
    <TYPE>All Grain</TYPE>
    <BREWER>Brewer A</BREWER>
    <BATCH_SIZE>23.0</BATCH_SIZE>
    <BOIL_SIZE>28.0</BOIL_SIZE>
    <BOIL_TIME>60.0</BOIL_TIME>
    <EFFICIENCY>72.0</EFFICIENCY>
    <OG>1.065</OG>
    <FG>1.016</FG>
    <IBU>40.0</IBU>
    <EST_COLOR>35.0</EST_COLOR>
    <NOTES>A rich Irish-style dry stout.</NOTES>
    <STYLE>
      <NAME>Dry Stout</NAME>
      <STYLE_GUIDE>BJCP 2021</STYLE_GUIDE>
      <OG_MIN>1.036</OG_MIN>
      <OG_MAX>1.050</OG_MAX>
      <IBU_MIN>30</IBU_MIN>
      <IBU_MAX>45</IBU_MAX>
    </STYLE>
    <FERMENTABLES>
      <FERMENTABLE>
        <NAME>Pale 2-Row</NAME>
        <AMOUNT>4.500</AMOUNT>
        <TYPE>Grain</TYPE>
        <COLOR>2.0</COLOR>
        <YIELD>79.0</YIELD>
      </FERMENTABLE>
      <FERMENTABLE>
        <NAME>Roasted Barley</NAME>
        <AMOUNT>0.450</AMOUNT>
        <TYPE>Grain</TYPE>
        <COLOR>300.0</COLOR>
        <YIELD>60.0</YIELD>
      </FERMENTABLE>
    </FERMENTABLES>
    <HOPS>
      <HOP>
        <NAME>East Kent Goldings</NAME>
        <AMOUNT>0.050</AMOUNT>
        <USE>Boil</USE>
        <TIME>60</TIME>
        <ALPHA>5.0</ALPHA>
        <FORM>Pellet</FORM>
      </HOP>
    </HOPS>
    <YEASTS>
      <YEAST>
        <NAME>Irish Ale</NAME>
        <LABORATORY>Wyeast</LABORATORY>
        <PRODUCT_ID>1084</PRODUCT_ID>
        <ATTENUATION>73.0</ATTENUATION>
        <FORM>Liquid</FORM>
        <FLOCCULATION>Medium</FLOCCULATION>
        <MIN_TEMPERATURE>16.0</MIN_TEMPERATURE>
        <MAX_TEMPERATURE>22.0</MAX_TEMPERATURE>
      </YEAST>
    </YEASTS>
    <MISCS>
      <MISC>
        <NAME>Irish Moss</NAME>
        <TYPE>Fining</TYPE>
        <USE>Boil</USE>
        <TIME>15</TIME>
        <AMOUNT>0.005</AMOUNT>
        <AMOUNT_IS_WEIGHT>TRUE</AMOUNT_IS_WEIGHT>
      </MISC>
    </MISCS>
    <WATERS>
      <WATER>
        <NAME>Dublin Profile</NAME>
        <AMOUNT>28.0</AMOUNT>
        <CALCIUM>115.0</CALCIUM>
        <BICARBONATE>200.0</BICARBONATE>
        <SULFATE>55.0</SULFATE>
        <CHLORIDE>60.0</CHLORIDE>
        <SODIUM>12.0</SODIUM>
        <MAGNESIUM>4.0</MAGNESIUM>
      </WATER>
    </WATERS>
    <MASH>
      <MASH_STEPS>
        <MASH_STEP>
          <NAME>Saccharification</NAME>
          <TYPE>Infusion</TYPE>
          <STEP_TEMP>67.0</STEP_TEMP>
          <STEP_TIME>60</STEP_TIME>
        </MASH_STEP>
      </MASH_STEPS>
    </MASH>
  </RECIPE>
</RECIPES>
"""

_MULTI_RECIPE_BEERXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<RECIPES>
  <RECIPE>
    <NAME>Recipe One</NAME>
    <VERSION>1</VERSION>
    <TYPE>All Grain</TYPE>
    <BATCH_SIZE>20.0</BATCH_SIZE>
    <BOIL_SIZE>25.0</BOIL_SIZE>
    <BOIL_TIME>60.0</BOIL_TIME>
    <OG>1.048</OG>
  </RECIPE>
  <RECIPE>
    <NAME>Recipe Two</NAME>
    <VERSION>1</VERSION>
    <TYPE>All Grain</TYPE>
    <BATCH_SIZE>19.0</BATCH_SIZE>
    <BOIL_SIZE>24.0</BOIL_SIZE>
    <BOIL_TIME>60.0</BOIL_TIME>
    <OG>1.055</OG>
  </RECIPE>
</RECIPES>
"""

_NOT_BEERXML = """\
<?xml version="1.0" encoding="UTF-8"?>
<catalog>
  <item>Not a recipe</item>
</catalog>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# is_beerxml
# ---------------------------------------------------------------------------

def test_is_beerxml_valid(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    assert is_beerxml(p) is True


def test_is_beerxml_false_for_non_beerxml(tmp_path):
    p = _write(tmp_path, "catalog.xml", _NOT_BEERXML)
    assert is_beerxml(p) is False


def test_is_beerxml_false_for_plain_text(tmp_path):
    p = _write(tmp_path, "notes.txt", "Not XML at all.")
    assert is_beerxml(p) is False


def test_is_beerxml_example_file():
    assert is_beerxml(BEERXML_EXAMPLE) is True


# ---------------------------------------------------------------------------
# parse_beerxml_file
# ---------------------------------------------------------------------------

def test_parse_minimal(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipes = parse_beerxml_file(p)
    assert len(recipes) == 1
    r = recipes[0]
    assert r.name == "Test Pale Ale"
    assert r.recipe_type == "All Grain"
    assert r.brewer == "Test Brewer"
    assert r.batch_size_l == pytest.approx(20.0)
    assert r.boil_size_l == pytest.approx(25.0)
    assert r.boil_time_min == pytest.approx(60.0)
    assert r.efficiency_pct == pytest.approx(75.0)
    assert r.og == pytest.approx(1.052)
    assert r.fg == pytest.approx(1.010)
    assert r.ibu == pytest.approx(35.0)
    assert r.color_srm == pytest.approx(5.5)


def test_parse_full_fermentables(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert len(r.fermentables) == 2
    assert r.fermentables[0].name == "Pale 2-Row"
    assert r.fermentables[0].amount_kg == pytest.approx(4.5)
    assert r.fermentables[1].name == "Roasted Barley"
    assert r.fermentables[1].color_srm == pytest.approx(300.0)


def test_parse_full_hops(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert len(r.hops) == 1
    h = r.hops[0]
    assert h.name == "East Kent Goldings"
    assert h.use == "Boil"
    assert h.time_min == pytest.approx(60.0)
    assert h.alpha_pct == pytest.approx(5.0)


def test_parse_full_yeast(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert len(r.yeasts) == 1
    y = r.yeasts[0]
    assert y.name == "Irish Ale"
    assert y.laboratory == "Wyeast"
    assert y.product_id == "1084"
    assert y.attenuation_pct == pytest.approx(73.0)
    assert y.flocculation == "Medium"


def test_parse_full_miscs(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert len(r.miscs) == 1
    assert r.miscs[0].name == "Irish Moss"
    assert r.miscs[0].misc_type == "Fining"
    assert r.miscs[0].amount_is_weight is True


def test_parse_full_water(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert len(r.waters) == 1
    w = r.waters[0]
    assert w.name == "Dublin Profile"
    assert w.calcium_ppm == pytest.approx(115.0)
    assert w.bicarbonate_ppm == pytest.approx(200.0)


def test_parse_full_mash(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert len(r.mash_steps) == 1
    s = r.mash_steps[0]
    assert s.name == "Saccharification"
    assert s.step_temp_c == pytest.approx(67.0)
    assert s.step_time_min == pytest.approx(60.0)


def test_parse_full_style(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipes = parse_beerxml_file(p)
    r = recipes[0]
    assert r.style.name == "Dry Stout"
    assert r.style.style_guide == "BJCP 2021"
    assert r.style.og_min == pytest.approx(1.036)
    assert r.style.ibu_min == pytest.approx(30.0)


def test_parse_multi_recipe(tmp_path):
    p = _write(tmp_path, "multi.xml", _MULTI_RECIPE_BEERXML)
    recipes = parse_beerxml_file(p)
    assert len(recipes) == 2
    assert recipes[0].name == "Recipe One"
    assert recipes[1].name == "Recipe Two"


def test_parse_invalid_xml_raises(tmp_path):
    p = _write(tmp_path, "bad.xml", "<<not xml>>")
    with pytest.raises(ValueError, match="Failed to parse BeerXML"):
        parse_beerxml_file(p)


def test_parse_non_beerxml_raises(tmp_path):
    p = _write(tmp_path, "catalog.xml", _NOT_BEERXML)
    with pytest.raises(ValueError, match="Not a valid BeerXML"):
        parse_beerxml_file(p)


def test_parse_example_file():
    recipes = parse_beerxml_file(BEERXML_EXAMPLE)
    assert len(recipes) == 1
    r = recipes[0]
    assert r.name == "Island Optimized West Coast IPA"
    assert r.batch_size_l == pytest.approx(60.567)
    assert r.og == pytest.approx(1.060)
    assert r.ibu == pytest.approx(65.0)
    assert len(r.fermentables) == 4
    assert len(r.hops) == 5
    assert len(r.yeasts) == 1
    assert len(r.mash_steps) == 2


# ---------------------------------------------------------------------------
# beerxml_recipe_to_markdown
# ---------------------------------------------------------------------------

def test_markdown_contains_recipe_name(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Test Pale Ale" in md


def test_markdown_contains_stats(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "OG" in md
    assert "1.052" in md
    assert "IBU" in md


def test_markdown_contains_fermentables(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Fermentables" in md
    assert "Pale 2-Row" in md
    assert "Roasted Barley" in md


def test_markdown_contains_hops(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Hops" in md
    assert "East Kent Goldings" in md


def test_markdown_contains_yeast(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Yeast" in md
    assert "Irish Ale" in md


def test_markdown_contains_mash(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Mash" in md
    assert "Saccharification" in md


def test_markdown_contains_water(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Water" in md
    assert "Dublin Profile" in md


def test_markdown_contains_notes(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "dry stout" in md.lower()


def test_markdown_example_file():
    recipe = parse_beerxml_file(BEERXML_EXAMPLE)[0]
    md = beerxml_recipe_to_markdown(recipe)
    assert "Island Optimized West Coast IPA" in md
    assert "Centennial" in md
    assert "Citra" in md
    assert "Dry Hop" in md


# ---------------------------------------------------------------------------
# beerxml_recipe_to_record
# ---------------------------------------------------------------------------

def test_record_type_is_recipe(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    assert rec["type"] == "recipe"


def test_record_title_matches_name(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    assert rec["title"] == "Test Pale Ale"


def test_record_confidence_is_one(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    assert rec["confidence"] == pytest.approx(1.0)


def test_record_source_refs(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    assert rec["source_refs"] == [{"source_file": "recipe.xml"}]


def test_record_has_content(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    assert rec.get("content"), "record must have content"
    assert "Test Pale Ale" in rec["content"]


def test_record_has_summary(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    assert rec.get("summary"), "record must have summary"


def test_record_metadata_source_format(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    meta = rec["metadata"]
    assert meta["source_format"] == "beerxml"


def test_record_metadata_stats(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "recipe.xml")
    meta = rec["metadata"]
    assert meta["batch_size_l"] == pytest.approx(20.0)
    assert meta["og"] == "1.052"
    assert meta["ibu"] == pytest.approx(35.0)


def test_record_metadata_fermentables(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "stout.xml")
    ferms = rec["metadata"]["fermentables"]
    assert len(ferms) == 2
    assert ferms[0]["name"] == "Pale 2-Row"
    assert ferms[1]["name"] == "Roasted Barley"


def test_record_metadata_hops(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "stout.xml")
    hops = rec["metadata"]["hops"]
    assert len(hops) == 1
    assert hops[0]["name"] == "East Kent Goldings"
    assert hops[0]["alpha_pct"] == pytest.approx(5.0)


def test_record_metadata_yeasts(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "stout.xml")
    yeasts = rec["metadata"]["yeasts"]
    assert len(yeasts) == 1
    assert yeasts[0]["laboratory"] == "Wyeast"


def test_record_metadata_mash_steps(tmp_path):
    p = _write(tmp_path, "stout.xml", _FULL_BEERXML)
    recipe = parse_beerxml_file(p)[0]
    rec = beerxml_recipe_to_record(recipe, "stout.xml")
    steps = rec["metadata"]["mash_steps"]
    assert len(steps) == 1
    assert steps[0]["step_temp_c"] == pytest.approx(67.0)


def test_record_example_file():
    recipe = parse_beerxml_file(BEERXML_EXAMPLE)[0]
    rec = beerxml_recipe_to_record(recipe, BEERXML_EXAMPLE.name)
    assert rec["title"] == "Island Optimized West Coast IPA"
    assert rec["metadata"]["batch_size_l"] == pytest.approx(60.567)
    assert rec["metadata"]["og"] == "1.060"
    assert rec["metadata"]["ibu"] == pytest.approx(65.0)
    assert rec["metadata"]["style_name"] == "American IPA"
    assert rec["metadata"]["style_guide"] == "BJCP 2021"
    assert len(rec["metadata"]["hops"]) == 5
    dry_hops = [h for h in rec["metadata"]["hops"] if h["use"] == "Dry Hop"]
    assert len(dry_hops) == 2


# ---------------------------------------------------------------------------
# extract_text integration
# ---------------------------------------------------------------------------

def test_extract_text_beerxml_source_type(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    result = extract_text(p)
    assert result.source_type == "beerxml"


def test_extract_text_beerxml_filename(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    result = extract_text(p)
    assert result.source_filename == "recipe.xml"


def test_extract_text_beerxml_text_contains_name(tmp_path):
    p = _write(tmp_path, "recipe.xml", _MINIMAL_BEERXML)
    result = extract_text(p)
    assert "Test Pale Ale" in result.text


def test_extract_text_beerxml_extension(tmp_path):
    p = tmp_path / "recipe.beerxml"
    p.write_text(_MINIMAL_BEERXML, encoding="utf-8")
    result = extract_text(p)
    assert result.source_type == "beerxml"


def test_extract_text_non_beerxml_xml_raises(tmp_path):
    p = _write(tmp_path, "catalog.xml", _NOT_BEERXML)
    with pytest.raises(ValueError, match="does not appear to be a valid BeerXML"):
        extract_text(p)


def test_extract_text_multi_recipe_warning(tmp_path):
    p = _write(tmp_path, "multi.xml", _MULTI_RECIPE_BEERXML)
    result = extract_text(p)
    assert any("2 recipes" in w for w in result.warnings)
    assert "Recipe One" in result.text
    assert "Recipe Two" in result.text


# ---------------------------------------------------------------------------
# Runner integration (prepare_training_pack with BeerXML)
# ---------------------------------------------------------------------------

def test_runner_beerxml_produces_output(tmp_path):
    result = prepare_training_pack(
        source_path=BEERXML_EXAMPLE,
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        output_dir=tmp_path / "out",
        backend="mock",
    )
    assert result.manifest_path.exists()
    assert result.records_path.exists()
    assert result.extracted_text_path.exists()
    assert result.report_path.exists()


def test_runner_beerxml_record_count(tmp_path):
    result = prepare_training_pack(
        source_path=BEERXML_EXAMPLE,
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        output_dir=tmp_path / "out",
        backend="mock",
    )
    assert result.record_count == 1


def test_runner_beerxml_validation_passes(tmp_path):
    result = prepare_training_pack(
        source_path=BEERXML_EXAMPLE,
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        output_dir=tmp_path / "out",
        backend="mock",
    )
    assert result.validation_status == "pass"
    assert result.errors == []


def test_runner_beerxml_records_json(tmp_path):
    result = prepare_training_pack(
        source_path=BEERXML_EXAMPLE,
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        output_dir=tmp_path / "out",
        backend="mock",
    )
    data = json.loads(result.records_path.read_text())
    assert "records" in data
    assert len(data["records"]) == 1
    rec = data["records"][0]
    assert rec["record_type"] == "recipe"
    assert rec["title"] == "Island Optimized West Coast IPA"
    assert rec["confidence"] == pytest.approx(1.0)
    assert "metadata" in rec
    assert rec["metadata"]["source_format"] == "beerxml"


def test_runner_beerxml_deterministic_same_result(tmp_path):
    """Running twice on the same file must produce identical records."""
    kwargs = dict(
        source_path=BEERXML_EXAMPLE,
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        backend="mock",
    )
    r1 = prepare_training_pack(**kwargs, output_dir=tmp_path / "out1")
    r2 = prepare_training_pack(**kwargs, output_dir=tmp_path / "out2")
    records1 = json.loads(r1.records_path.read_text())
    records2 = json.loads(r2.records_path.read_text())
    assert records1 == records2


def test_runner_beerxml_multi_recipe(tmp_path):
    p = tmp_path / "multi.xml"
    p.write_text(_MULTI_RECIPE_BEERXML, encoding="utf-8")
    result = prepare_training_pack(
        source_path=p,
        profile_path=PROFILES_DIR / "brewing_recipe.yaml",
        output_dir=tmp_path / "out",
        backend="mock",
    )
    assert result.record_count == 2
