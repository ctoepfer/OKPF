# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Built-in `okpf init` template registry and a tiny placeholder renderer.

Templates are plain, inspectable files under ``okpf/templates/<id>/`` — not
Python data literals — so they can be read, diffed, and edited like any
other OKPF pack. Rendering only substitutes ``{{ variable }}`` tokens; there
is no control flow. Loops/conditionals are unnecessary for starter packs and
would make templates harder to hand-inspect.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

import yaml

_TEMPLATE_TOKEN = re.compile(r"\{\{\s*(\w+)\s*\}\}")
_TMPL_SUFFIX = ".tmpl"


class TemplateError(Exception):
    """Raised for unknown templates or malformed template metadata."""


@dataclass
class TemplateVariable:
    name: str
    prompt: str
    default: str = ""


@dataclass
class TemplateInfo:
    id: str
    name: str
    description: str
    recommended_domain: str | None
    variables: list[TemplateVariable] = field(default_factory=list)
    _root: Path = field(repr=False, default=None)  # type: ignore[assignment]

    def default_variables(self) -> dict[str, str]:
        return {var.name: var.default for var in self.variables}


def _templates_root():
    return files("okpf.templates")


def list_templates() -> list[TemplateInfo]:
    """Return metadata for every built-in template, sorted by id."""
    root = _templates_root()
    infos: list[TemplateInfo] = []
    for entry in root.iterdir():
        if entry.is_dir() and entry.joinpath("template.yaml").is_file():
            infos.append(load_template(entry.name))
    return sorted(infos, key=lambda info: info.id)


def load_template(template_id: str) -> TemplateInfo:
    """Load metadata for a single built-in template by id."""
    root = _templates_root()
    entry = root.joinpath(template_id)
    metadata_ref = entry.joinpath("template.yaml")
    if not entry.is_dir() or not metadata_ref.is_file():
        available = ", ".join(sorted(child.name for child in root.iterdir() if child.is_dir()))
        raise TemplateError(
            f"Unknown template: '{template_id}'. Available templates: {available}"
        )

    with as_file(metadata_ref) as metadata_path:
        data: dict[str, Any] = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}

    variables = [
        TemplateVariable(name=var_name, prompt=var_data.get("prompt", var_name), default=str(var_data.get("default", "")))
        for var_name, var_data in (data.get("variables") or {}).items()
    ]

    with as_file(entry) as template_path:
        resolved_root = template_path

    return TemplateInfo(
        id=data.get("id", template_id),
        name=data.get("name", template_id),
        description=data.get("description", ""),
        recommended_domain=data.get("recommended_domain"),
        variables=variables,
        _root=resolved_root,
    )


def render_template(template: TemplateInfo, dest: Path, variables: dict[str, str]) -> list[Path]:
    """Render a template into `dest`, substituting variables. Returns written file paths."""
    merged = template.default_variables()
    merged.update({key: value for key, value in variables.items() if value is not None})

    written: list[Path] = []
    for source in sorted(template._root.rglob("*")):
        relative = source.relative_to(template._root)
        if relative.name == "template.yaml":
            continue
        target = dest / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == _TMPL_SUFFIX:
            target = target.with_suffix("")
            text = source.read_text(encoding="utf-8")
            target.write_text(_substitute(text, merged), encoding="utf-8")
        else:
            target.write_bytes(source.read_bytes())
        written.append(target)
    return written


def _substitute(text: str, variables: dict[str, str]) -> str:
    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in variables:
            raise TemplateError(f"Template references undefined variable: '{key}'")
        return variables[key]

    return _TEMPLATE_TOKEN.sub(replace, text)
