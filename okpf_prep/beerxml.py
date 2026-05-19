"""BeerXML parsing and OKPF record generation.

Parses BeerXML v1 files (http://www.beerxml.com/) using the stdlib
xml.etree.ElementTree — no additional dependencies required.

Public API:
  is_beerxml(path)                     → bool
  parse_beerxml_file(path)             → list[BeerXMLRecipe]
  beerxml_recipe_to_markdown(recipe)   → str
  beerxml_recipe_to_record(recipe, source_filename) → dict
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BeerXMLStyle:
    name: str = ""
    style_guide: str = ""
    category: str = ""
    style_letter: str = ""
    og_min: float | None = None
    og_max: float | None = None
    fg_min: float | None = None
    fg_max: float | None = None
    ibu_min: float | None = None
    ibu_max: float | None = None
    color_min: float | None = None
    color_max: float | None = None
    abv_min: float | None = None
    abv_max: float | None = None


@dataclass
class BeerXMLFermentable:
    name: str = ""
    amount_kg: float = 0.0
    fermentable_type: str = ""
    color_srm: float | None = None
    yield_pct: float | None = None
    origin: str = ""


@dataclass
class BeerXMLHop:
    name: str = ""
    amount_kg: float = 0.0
    use: str = ""
    time_min: float = 0.0
    alpha_pct: float | None = None
    form: str = ""


@dataclass
class BeerXMLYeast:
    name: str = ""
    laboratory: str = ""
    product_id: str = ""
    attenuation_pct: float | None = None
    form: str = ""
    flocculation: str = ""
    min_temperature_c: float | None = None
    max_temperature_c: float | None = None


@dataclass
class BeerXMLMisc:
    name: str = ""
    amount: float = 0.0
    amount_is_weight: bool = False
    use: str = ""
    time_min: float = 0.0
    misc_type: str = ""
    notes: str = ""


@dataclass
class BeerXMLWater:
    name: str = ""
    amount_l: float = 0.0
    calcium_ppm: float | None = None
    bicarbonate_ppm: float | None = None
    sulfate_ppm: float | None = None
    chloride_ppm: float | None = None
    sodium_ppm: float | None = None
    magnesium_ppm: float | None = None


@dataclass
class BeerXMLMashStep:
    name: str = ""
    step_type: str = ""
    step_temp_c: float | None = None
    step_time_min: float | None = None
    ramp_time_min: float | None = None


@dataclass
class BeerXMLRecipe:
    name: str = ""
    recipe_type: str = ""
    brewer: str = ""
    batch_size_l: float = 0.0
    boil_size_l: float = 0.0
    boil_time_min: float = 0.0
    efficiency_pct: float | None = None
    og: float | None = None
    fg: float | None = None
    ibu: float | None = None
    color_srm: float | None = None
    carbonation: float | None = None
    primary_age_days: float | None = None
    primary_temp_c: float | None = None
    abv: float | None = None
    notes: str = ""
    style: BeerXMLStyle = field(default_factory=BeerXMLStyle)
    fermentables: list[BeerXMLFermentable] = field(default_factory=list)
    hops: list[BeerXMLHop] = field(default_factory=list)
    yeasts: list[BeerXMLYeast] = field(default_factory=list)
    miscs: list[BeerXMLMisc] = field(default_factory=list)
    waters: list[BeerXMLWater] = field(default_factory=list)
    mash_steps: list[BeerXMLMashStep] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def is_beerxml(path: Path) -> bool:
    """Return True if path is a BeerXML file (root element is RECIPES or RECIPE)."""
    try:
        for _event, elem in ET.iterparse(str(path), events=("start",)):
            tag = elem.tag.upper()
            return tag in ("RECIPES", "RECIPE")
    except ET.ParseError:
        return False
    return False


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _text(elem: ET.Element | None, tag: str, default: str = "") -> str:
    if elem is None:
        return default
    child = elem.find(tag)
    return (child.text or "").strip() if child is not None else default


def _float(elem: ET.Element | None, tag: str, default: float | None = None) -> float | None:
    val = _text(elem, tag)
    if not val:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _bool_tag(elem: ET.Element | None, tag: str) -> bool:
    return _text(elem, tag).upper() in ("TRUE", "YES", "1")


def _parse_style(style_elem: ET.Element | None) -> BeerXMLStyle:
    if style_elem is None:
        return BeerXMLStyle()
    return BeerXMLStyle(
        name=_text(style_elem, "NAME"),
        style_guide=_text(style_elem, "STYLE_GUIDE"),
        category=_text(style_elem, "CATEGORY"),
        style_letter=_text(style_elem, "STYLE_LETTER"),
        og_min=_float(style_elem, "OG_MIN"),
        og_max=_float(style_elem, "OG_MAX"),
        fg_min=_float(style_elem, "FG_MIN"),
        fg_max=_float(style_elem, "FG_MAX"),
        ibu_min=_float(style_elem, "IBU_MIN"),
        ibu_max=_float(style_elem, "IBU_MAX"),
        color_min=_float(style_elem, "COLOR_MIN"),
        color_max=_float(style_elem, "COLOR_MAX"),
        abv_min=_float(style_elem, "ABV_MIN"),
        abv_max=_float(style_elem, "ABV_MAX"),
    )


def _parse_fermentables(recipe_elem: ET.Element) -> list[BeerXMLFermentable]:
    fermentables: list[BeerXMLFermentable] = []
    ferms_elem = recipe_elem.find("FERMENTABLES")
    if ferms_elem is None:
        return fermentables
    for f in ferms_elem.findall("FERMENTABLE"):
        fermentables.append(BeerXMLFermentable(
            name=_text(f, "NAME"),
            amount_kg=_float(f, "AMOUNT") or 0.0,
            fermentable_type=_text(f, "TYPE"),
            color_srm=_float(f, "COLOR"),
            yield_pct=_float(f, "YIELD"),
            origin=_text(f, "ORIGIN"),
        ))
    return fermentables


def _parse_hops(recipe_elem: ET.Element) -> list[BeerXMLHop]:
    hops: list[BeerXMLHop] = []
    hops_elem = recipe_elem.find("HOPS")
    if hops_elem is None:
        return hops
    for h in hops_elem.findall("HOP"):
        hops.append(BeerXMLHop(
            name=_text(h, "NAME"),
            amount_kg=_float(h, "AMOUNT") or 0.0,
            use=_text(h, "USE"),
            time_min=_float(h, "TIME") or 0.0,
            alpha_pct=_float(h, "ALPHA"),
            form=_text(h, "FORM"),
        ))
    return hops


def _parse_yeasts(recipe_elem: ET.Element) -> list[BeerXMLYeast]:
    yeasts: list[BeerXMLYeast] = []
    yeasts_elem = recipe_elem.find("YEASTS")
    if yeasts_elem is None:
        return yeasts
    for y in yeasts_elem.findall("YEAST"):
        yeasts.append(BeerXMLYeast(
            name=_text(y, "NAME"),
            laboratory=_text(y, "LABORATORY"),
            product_id=_text(y, "PRODUCT_ID"),
            attenuation_pct=_float(y, "ATTENUATION"),
            form=_text(y, "FORM"),
            flocculation=_text(y, "FLOCCULATION"),
            min_temperature_c=_float(y, "MIN_TEMPERATURE"),
            max_temperature_c=_float(y, "MAX_TEMPERATURE"),
        ))
    return yeasts


def _parse_miscs(recipe_elem: ET.Element) -> list[BeerXMLMisc]:
    miscs: list[BeerXMLMisc] = []
    miscs_elem = recipe_elem.find("MISCS")
    if miscs_elem is None:
        return miscs
    for m in miscs_elem.findall("MISC"):
        miscs.append(BeerXMLMisc(
            name=_text(m, "NAME"),
            amount=_float(m, "AMOUNT") or 0.0,
            amount_is_weight=_bool_tag(m, "AMOUNT_IS_WEIGHT"),
            use=_text(m, "USE"),
            time_min=_float(m, "TIME") or 0.0,
            misc_type=_text(m, "TYPE"),
            notes=_text(m, "NOTES"),
        ))
    return miscs


def _parse_waters(recipe_elem: ET.Element) -> list[BeerXMLWater]:
    waters: list[BeerXMLWater] = []
    waters_elem = recipe_elem.find("WATERS")
    if waters_elem is None:
        return waters
    for w in waters_elem.findall("WATER"):
        waters.append(BeerXMLWater(
            name=_text(w, "NAME"),
            amount_l=_float(w, "AMOUNT") or 0.0,
            calcium_ppm=_float(w, "CALCIUM"),
            bicarbonate_ppm=_float(w, "BICARBONATE"),
            sulfate_ppm=_float(w, "SULFATE"),
            chloride_ppm=_float(w, "CHLORIDE"),
            sodium_ppm=_float(w, "SODIUM"),
            magnesium_ppm=_float(w, "MAGNESIUM"),
        ))
    return waters


def _parse_mash_steps(recipe_elem: ET.Element) -> list[BeerXMLMashStep]:
    steps: list[BeerXMLMashStep] = []
    mash_elem = recipe_elem.find("MASH")
    if mash_elem is None:
        return steps
    steps_elem = mash_elem.find("MASH_STEPS")
    if steps_elem is None:
        return steps
    for s in steps_elem.findall("MASH_STEP"):
        steps.append(BeerXMLMashStep(
            name=_text(s, "NAME"),
            step_type=_text(s, "TYPE"),
            step_temp_c=_float(s, "STEP_TEMP"),
            step_time_min=_float(s, "STEP_TIME"),
            ramp_time_min=_float(s, "RAMP_TIME"),
        ))
    return steps


def _parse_recipe_elem(recipe_elem: ET.Element) -> BeerXMLRecipe:
    return BeerXMLRecipe(
        name=_text(recipe_elem, "NAME"),
        recipe_type=_text(recipe_elem, "TYPE"),
        brewer=_text(recipe_elem, "BREWER"),
        batch_size_l=_float(recipe_elem, "BATCH_SIZE") or 0.0,
        boil_size_l=_float(recipe_elem, "BOIL_SIZE") or 0.0,
        boil_time_min=_float(recipe_elem, "BOIL_TIME") or 0.0,
        efficiency_pct=_float(recipe_elem, "EFFICIENCY"),
        og=_float(recipe_elem, "OG"),
        fg=_float(recipe_elem, "FG"),
        ibu=_float(recipe_elem, "IBU"),
        color_srm=_float(recipe_elem, "EST_COLOR"),
        carbonation=_float(recipe_elem, "CARBONATION"),
        primary_age_days=_float(recipe_elem, "PRIMARY_AGE"),
        primary_temp_c=_float(recipe_elem, "PRIMARY_TEMP"),
        abv=_float(recipe_elem, "ABV"),
        notes=_text(recipe_elem, "NOTES"),
        style=_parse_style(recipe_elem.find("STYLE")),
        fermentables=_parse_fermentables(recipe_elem),
        hops=_parse_hops(recipe_elem),
        yeasts=_parse_yeasts(recipe_elem),
        miscs=_parse_miscs(recipe_elem),
        waters=_parse_waters(recipe_elem),
        mash_steps=_parse_mash_steps(recipe_elem),
    )


# ---------------------------------------------------------------------------
# Public parsing API
# ---------------------------------------------------------------------------

def parse_beerxml_file(path: Path) -> list[BeerXMLRecipe]:
    """Parse a BeerXML file and return a list of BeerXMLRecipe objects."""
    try:
        tree = ET.parse(str(path))
    except ET.ParseError as exc:
        raise ValueError(f"Failed to parse BeerXML file '{path}': {exc}") from exc

    root = tree.getroot()
    tag = root.tag.upper()

    if tag == "RECIPES":
        return [_parse_recipe_elem(r) for r in root.findall("RECIPE")]
    if tag == "RECIPE":
        return [_parse_recipe_elem(root)]

    raise ValueError(
        f"Not a valid BeerXML file (root element is <{root.tag}>, expected <RECIPES> or <RECIPE>)"
    )


# ---------------------------------------------------------------------------
# Markdown serialisation
# ---------------------------------------------------------------------------

def _fmt_gravity(g: float | None) -> str:
    if g is None:
        return "—"
    return f"{g:.3f}"


def _fmt_f(value: float | None, decimals: int = 1, unit: str = "") -> str:
    if value is None:
        return "—"
    formatted = f"{value:.{decimals}f}"
    return f"{formatted} {unit}".strip() if unit else formatted


def beerxml_recipe_to_markdown(recipe: BeerXMLRecipe) -> str:
    """Render a BeerXMLRecipe as a rich Markdown document."""
    lines: list[str] = []

    lines.append(f"# {recipe.name}")
    lines.append("")

    # Summary line
    parts = []
    if recipe.recipe_type:
        parts.append(recipe.recipe_type)
    if recipe.style.name:
        parts.append(recipe.style.name)
    if recipe.brewer:
        parts.append(f"by {recipe.brewer}")
    if parts:
        lines.append(" | ".join(parts))
        lines.append("")

    # Stats table
    lines.append("## Recipe Stats")
    lines.append("")
    lines.append("| Stat | Value |")
    lines.append("|------|-------|")
    lines.append(f"| Batch Size | {_fmt_f(recipe.batch_size_l, 2, 'L')} |")
    lines.append(f"| Boil Size | {_fmt_f(recipe.boil_size_l, 2, 'L')} |")
    lines.append(f"| Boil Time | {_fmt_f(recipe.boil_time_min, 0, 'min')} |")
    if recipe.efficiency_pct is not None:
        lines.append(f"| Efficiency | {_fmt_f(recipe.efficiency_pct, 1, '%')} |")
    lines.append(f"| OG | {_fmt_gravity(recipe.og)} |")
    lines.append(f"| FG | {_fmt_gravity(recipe.fg)} |")
    if recipe.abv is not None:
        lines.append(f"| ABV | {_fmt_f(recipe.abv, 1, '%')} |")
    lines.append(f"| IBU | {_fmt_f(recipe.ibu, 1)} |")
    lines.append(f"| Color | {_fmt_f(recipe.color_srm, 1, 'SRM')} |")
    if recipe.carbonation is not None:
        lines.append(f"| Carbonation | {_fmt_f(recipe.carbonation, 2, 'vol CO₂')} |")
    if recipe.primary_age_days is not None:
        lines.append(f"| Primary Fermentation | {_fmt_f(recipe.primary_age_days, 0, 'days')} at {_fmt_f(recipe.primary_temp_c, 1, '°C')} |")
    lines.append("")

    # Style
    if recipe.style.name:
        lines.append("## Style")
        lines.append("")
        if recipe.style.style_guide:
            lines.append(f"**{recipe.style.name}** ({recipe.style.style_guide})")
        else:
            lines.append(f"**{recipe.style.name}**")
        style_parts = []
        if recipe.style.og_min is not None and recipe.style.og_max is not None:
            style_parts.append(
                f"OG: {_fmt_gravity(recipe.style.og_min)}–{_fmt_gravity(recipe.style.og_max)}"
            )
        if recipe.style.ibu_min is not None and recipe.style.ibu_max is not None:
            style_parts.append(f"IBU: {recipe.style.ibu_min:.0f}–{recipe.style.ibu_max:.0f}")
        if recipe.style.abv_min is not None and recipe.style.abv_max is not None:
            style_parts.append(
                f"ABV: {recipe.style.abv_min:.1f}–{recipe.style.abv_max:.1f}%"
            )
        if style_parts:
            lines.append(" | ".join(style_parts))
        lines.append("")

    # Fermentables
    if recipe.fermentables:
        lines.append("## Fermentables")
        lines.append("")
        total_kg = sum(f.amount_kg for f in recipe.fermentables)
        lines.append("| Fermentable | Amount | % | Color | Type |")
        lines.append("|-------------|--------|---|-------|------|")
        for f in recipe.fermentables:
            pct = (f.amount_kg / total_kg * 100) if total_kg > 0 else 0.0
            color = _fmt_f(f.color_srm, 0, "°L") if f.color_srm is not None else "—"
            lines.append(
                f"| {f.name} | {f.amount_kg:.3f} kg | {pct:.1f}% | {color} | {f.fermentable_type} |"
            )
        lines.append(f"| **Total** | **{total_kg:.3f} kg** | | | |")
        lines.append("")

    # Hops
    if recipe.hops:
        lines.append("## Hops")
        lines.append("")
        lines.append("| Hop | Amount | Use | Time | Alpha |")
        lines.append("|-----|--------|-----|------|-------|")
        for h in recipe.hops:
            amount_g = h.amount_kg * 1000
            alpha = _fmt_f(h.alpha_pct, 1, "%") if h.alpha_pct is not None else "—"
            time_str = f"{h.time_min:.0f} min" if h.use.lower() != "dry hop" else f"{h.time_min:.0f} days"
            lines.append(f"| {h.name} | {amount_g:.0f} g | {h.use} | {time_str} | {alpha} |")
        lines.append("")

    # Yeast
    if recipe.yeasts:
        lines.append("## Yeast")
        lines.append("")
        for y in recipe.yeasts:
            lab_id = f"{y.laboratory} {y.product_id}".strip()
            lines.append(f"**{y.name}** ({lab_id})")
            yeast_parts = []
            if y.form:
                yeast_parts.append(y.form)
            if y.attenuation_pct is not None:
                yeast_parts.append(f"Attenuation: {y.attenuation_pct:.0f}%")
            if y.flocculation:
                yeast_parts.append(f"Flocculation: {y.flocculation}")
            if y.min_temperature_c is not None and y.max_temperature_c is not None:
                yeast_parts.append(
                    f"Temp: {y.min_temperature_c:.0f}–{y.max_temperature_c:.0f} °C"
                )
            if yeast_parts:
                lines.append(" | ".join(yeast_parts))
            lines.append("")

    # Mash
    if recipe.mash_steps:
        lines.append("## Mash")
        lines.append("")
        lines.append("| Step | Type | Temp | Time |")
        lines.append("|------|------|------|------|")
        for s in recipe.mash_steps:
            temp = _fmt_f(s.step_temp_c, 1, "°C")
            time = _fmt_f(s.step_time_min, 0, "min")
            lines.append(f"| {s.name} | {s.step_type} | {temp} | {time} |")
        lines.append("")

    # Water chemistry
    if recipe.waters:
        lines.append("## Water Chemistry")
        lines.append("")
        lines.append("| Water | Ca | HCO₃ | SO₄ | Cl | Na | Mg |")
        lines.append("|-------|-----|------|-----|-----|-----|-----|")
        for w in recipe.waters:
            lines.append(
                f"| {w.name} ({w.amount_l:.1f} L) "
                f"| {_fmt_f(w.calcium_ppm, 0)} "
                f"| {_fmt_f(w.bicarbonate_ppm, 0)} "
                f"| {_fmt_f(w.sulfate_ppm, 0)} "
                f"| {_fmt_f(w.chloride_ppm, 0)} "
                f"| {_fmt_f(w.sodium_ppm, 0)} "
                f"| {_fmt_f(w.magnesium_ppm, 0)} |"
            )
        lines.append("")

    # Misc additions
    if recipe.miscs:
        lines.append("## Other Additions")
        lines.append("")
        lines.append("| Addition | Type | Use | Amount | Time |")
        lines.append("|----------|------|-----|--------|------|")
        for m in recipe.miscs:
            unit = "g" if m.amount_is_weight else "mL"
            amount_display = f"{m.amount * 1000:.1f} {unit}" if m.amount < 1 else f"{m.amount:.1f} {unit}"
            lines.append(
                f"| {m.name} | {m.misc_type} | {m.use} | {amount_display} | {m.time_min:.0f} min |"
            )
        lines.append("")

    # Notes
    if recipe.notes.strip():
        lines.append("## Notes")
        lines.append("")
        lines.append(recipe.notes.strip())
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OKPF record generation
# ---------------------------------------------------------------------------

def beerxml_recipe_to_record(recipe: BeerXMLRecipe, source_filename: str) -> dict[str, Any]:
    """Convert a BeerXMLRecipe to an OKPF record dict (type='recipe', confidence=1.0)."""
    style_name = recipe.style.name if recipe.style else ""
    style_guide = recipe.style.style_guide if recipe.style else ""

    # Build summary line
    summary_parts = []
    if recipe.recipe_type:
        summary_parts.append(recipe.recipe_type)
    if style_name:
        summary_parts.append(style_name)
    if recipe.og is not None:
        summary_parts.append(f"OG {_fmt_gravity(recipe.og)}")
    if recipe.ibu is not None:
        summary_parts.append(f"{recipe.ibu:.0f} IBU")
    if recipe.batch_size_l:
        summary_parts.append(f"{recipe.batch_size_l:.1f} L batch")
    summary = " | ".join(summary_parts) if summary_parts else recipe.name

    content = beerxml_recipe_to_markdown(recipe)

    metadata: dict[str, Any] = {
        "source_format": "beerxml",
        "recipe_type": recipe.recipe_type,
        "brewer": recipe.brewer,
        "batch_size_l": recipe.batch_size_l,
        "boil_size_l": recipe.boil_size_l,
        "boil_time_min": recipe.boil_time_min,
    }
    if recipe.efficiency_pct is not None:
        metadata["efficiency_pct"] = recipe.efficiency_pct
    if recipe.og is not None:
        metadata["og"] = _fmt_gravity(recipe.og)
    if recipe.fg is not None:
        metadata["fg"] = _fmt_gravity(recipe.fg)
    if recipe.abv is not None:
        metadata["abv"] = recipe.abv
    if recipe.ibu is not None:
        metadata["ibu"] = recipe.ibu
    if recipe.color_srm is not None:
        metadata["color_srm"] = recipe.color_srm
    if style_name:
        metadata["style_name"] = style_name
    if style_guide:
        metadata["style_guide"] = style_guide

    if recipe.fermentables:
        metadata["fermentables"] = [
            {
                "name": f.name,
                "amount_kg": round(f.amount_kg, 4),
                "type": f.fermentable_type,
                **({"color_srm": f.color_srm} if f.color_srm is not None else {}),
                **({"yield_pct": f.yield_pct} if f.yield_pct is not None else {}),
            }
            for f in recipe.fermentables
        ]

    if recipe.hops:
        metadata["hops"] = [
            {
                "name": h.name,
                "amount_g": round(h.amount_kg * 1000, 2),
                "use": h.use,
                "time_min": h.time_min,
                **({"alpha_pct": h.alpha_pct} if h.alpha_pct is not None else {}),
            }
            for h in recipe.hops
        ]

    if recipe.yeasts:
        metadata["yeasts"] = [
            {
                "name": y.name,
                "laboratory": y.laboratory,
                **({"attenuation_pct": y.attenuation_pct} if y.attenuation_pct is not None else {}),
                "form": y.form,
                "flocculation": y.flocculation,
            }
            for y in recipe.yeasts
        ]

    if recipe.miscs:
        metadata["miscs"] = [
            {
                "name": m.name,
                "type": m.misc_type,
                "use": m.use,
            }
            for m in recipe.miscs
        ]

    if recipe.mash_steps:
        metadata["mash_steps"] = [
            {
                "name": s.name,
                "type": s.step_type,
                **({"step_temp_c": s.step_temp_c} if s.step_temp_c is not None else {}),
                **({"step_time_min": s.step_time_min} if s.step_time_min is not None else {}),
            }
            for s in recipe.mash_steps
        ]

    return {
        "type": "recipe",
        "title": recipe.name,
        "summary": summary,
        "content": content,
        "source_refs": [{"source_file": source_filename}],
        "confidence": 1.0,
        "metadata": metadata,
    }
