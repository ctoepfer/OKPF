from __future__ import annotations

from okpf_prep.text_cleanup import normalize_extracted_text, replacement_char_count


def test_replacement_characters_are_stripped():
    text = "Weyermann� Pilsner Malt"
    normalized = normalize_extracted_text(text)
    assert "�" not in normalized


def test_replacement_char_count_reports_original_damage():
    text = "A�B�C"
    assert replacement_char_count(text) == 2


def test_replacement_char_count_zero_for_clean_text():
    assert replacement_char_count("Clean text with no damage.") == 0


def test_nfkc_normalizes_compatibility_characters():
    # U+FB01 LATIN SMALL LIGATURE FI -> "fi"
    text = "speciﬁc malt profile"
    normalized = normalize_extracted_text(text)
    assert "ﬁ" not in normalized
    assert "specific" in normalized


def test_trademark_symbol_survives_but_is_normalized_form():
    # NFKC folds the "TM" compatibility character to plain "TM", it does
    # not delete trademark meaning outright.
    text = "BrandName™ Malt"
    normalized = normalize_extracted_text(text)
    assert "BrandName" in normalized


def test_excessive_blank_lines_collapsed():
    text = "Paragraph one.\n\n\n\n\n\nParagraph two."
    normalized = normalize_extracted_text(text)
    assert "\n\n\n" not in normalized
    assert "Paragraph one." in normalized
    assert "Paragraph two." in normalized


def test_trailing_whitespace_before_newline_stripped():
    text = "Line one.   \nLine two.\t\n"
    normalized = normalize_extracted_text(text)
    assert "one.   \n" not in normalized
    assert "two.\t\n" not in normalized


def test_empty_text_returns_empty():
    assert normalize_extracted_text("") == ""


def test_normal_text_unchanged_in_content():
    text = "This is ordinary clean prose about brewing grains."
    assert normalize_extracted_text(text) == text
