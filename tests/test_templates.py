# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Every built-in okpf init template must render into a valid OKPF pack."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import scaffold  # noqa: E402
from okpf_validate import validate_pack  # noqa: E402


def test_list_templates_returns_all_built_ins() -> None:
    ids = {info.id for info in scaffold.list_templates()}
    assert ids == {
        "minimal",
        "software-onboarding",
        "rag-source",
        "local-org-knowledge",
        "field-repair-checklist",
    }


def test_load_unknown_template_raises_with_available_list() -> None:
    with pytest.raises(scaffold.TemplateError, match="Unknown template"):
        scaffold.load_template("does-not-exist")


@pytest.mark.parametrize(
    "template_id",
    ["minimal", "software-onboarding", "rag-source", "local-org-knowledge", "field-repair-checklist"],
)
def test_template_renders_to_a_valid_pack(tmp_path: Path, template_id: str) -> None:
    template = scaffold.load_template(template_id)
    dest = tmp_path / template_id
    dest.mkdir()

    written = scaffold.render_template(template, dest, {})

    assert written
    assert (dest / "manifest.json").is_file()
    assert not list(dest.rglob("*.tmpl")), "no .tmpl files should remain after rendering"

    result = validate_pack(str(dest))
    assert result.valid, [str(issue) for issue in result.errors]


def test_render_template_applies_variable_overrides(tmp_path: Path) -> None:
    template = scaffold.load_template("minimal")
    dest = tmp_path / "overridden"
    dest.mkdir()

    scaffold.render_template(template, dest, {"package_id": "org.example.custom", "name": "Custom Pack"})

    manifest_text = (dest / "manifest.json").read_text(encoding="utf-8")
    assert "org.example.custom" in manifest_text
    assert "Custom Pack" in manifest_text


def test_declared_but_unreferenced_variable_does_not_break_rendering(tmp_path: Path) -> None:
    template = scaffold.load_template("minimal")
    template.variables.append(scaffold.TemplateVariable(name="not_a_real_field", prompt="x", default="y"))
    dest = tmp_path / "unused-var"
    dest.mkdir()

    scaffold.render_template(template, dest, {})
    assert (dest / "manifest.json").is_file()


def test_substitute_raises_on_undefined_referenced_variable() -> None:
    with pytest.raises(scaffold.TemplateError, match="undefined variable"):
        scaffold._substitute("{{ nonexistent }}", {"name": "value"})


def test_substitute_replaces_known_variables() -> None:
    assert scaffold._substitute("hello {{ name }}", {"name": "world"}) == "hello world"
