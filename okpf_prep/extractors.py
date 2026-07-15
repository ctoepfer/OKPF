from __future__ import annotations

from pathlib import Path

from .models import ExtractedSource

SUPPORTED_TYPES = {"txt", "md", "pdf", "xml", "beerxml"}


def extract_text(source_path: str | Path) -> ExtractedSource:
    path = Path(source_path)
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from .models import ExtractedSource, PreChunkBlock
from .text_cleanup import normalize_extracted_text, replacement_char_count

SUPPORTED_TYPES = {"txt", "md", "pdf", "xml", "beerxml", "html", "htm"}

_HTML_SIGNATURE_RE = re.compile(
    r"<(?:!doctype\s+html|html\b|head\b|body\b|article\b|main\b|section\b|table\b|p\b)",
    re.IGNORECASE,
)

_DROP_TAGS = {
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "button",
    "svg",
    "canvas",
    "iframe",
    "object",
    "embed",
    "template",
    "link",
    "meta",
}

_CHROME_HINT_RE = re.compile(
    r"(cookie|consent|banner|promo|newsletter|subscribe|breadcrumbs?|breadcrumb|"
    r"navigation|nav|menu|toolbar|header|footer|sidebar|social|share|cart|search)",
    re.IGNORECASE,
)

_TABLE_BATCH_ROWS = 25
_MAX_HTML_NODES = 200_000


def extract_text(
    source_path: str | Path,
    *,
    source_url: str | None = None,
    source_content_type: str | None = None,
) -> ExtractedSource:
    path = Path(source_path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    ext = path.suffix.lstrip(".").lower()
    if ext not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported source type '{ext}'. Supported: {sorted(SUPPORTED_TYPES)}"
        )

    if ext == "txt":
        return _extract_txt(path)
    if ext == "md":
        return _extract_md(path)
    if ext == "pdf":
        return _extract_pdf(path)
    if ext in ("xml", "beerxml"):
        return _extract_xml(path, ext)
    if ext in ("html", "htm"):
        return _extract_html(path, source_url=source_url, source_content_type=source_content_type)

    raise RuntimeError(f"Unhandled extension: {ext}")  # unreachable


def _extract_txt(path: Path) -> ExtractedSource:
    text = path.read_text(encoding="utf-8", errors="replace")
    return ExtractedSource(
        source_path=path,
        source_filename=path.name,
        source_type="txt",
        text=text,
    )


def _extract_md(path: Path) -> ExtractedSource:
    text = path.read_text(encoding="utf-8", errors="replace")
    return ExtractedSource(
        source_path=path,
        source_filename=path.name,
        source_type="md",
        text=text,
    )


def _extract_pdf(path: Path) -> ExtractedSource:
    warnings: list[str] = []
    try:
        import pypdf  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError(
            "pypdf is required for PDF extraction. Install it with: pip install pypdf"
        )

    pages: list[str] = []
    page_count = 0
    try:
        reader = pypdf.PdfReader(str(path))
        page_count = len(reader.pages)
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                pages.append(page_text)
            except Exception as exc:
                warnings.append(f"Page {i + 1} extraction failed: {exc}")
                pages.append("")
    except Exception as exc:
        raise ValueError(f"Failed to read PDF '{path}': {exc}") from exc

    text = "\n\n".join(pages)
    if not text.strip():
        warnings.append("PDF produced no extractable text — it may be image-only.")

    damage = replacement_char_count(text)
    if damage:
        warnings.append(
            f"PDF text extraction produced {damage} unrecognized character(s) "
            "(replaced during normalization) — font encoding may not have "
            "mapped cleanly for parts of this document."
        )
    text = normalize_extracted_text(text)

    return ExtractedSource(
        source_path=path,
        source_filename=path.name,
        source_type="pdf",
        text=text,
        page_count=page_count,
        warnings=warnings,
    )


def _extract_xml(path: Path, declared_ext: str) -> ExtractedSource:
    from .beerxml import is_beerxml, parse_beerxml_file, beerxml_recipe_to_markdown

    warnings: list[str] = []

    if not is_beerxml(path):
        raise ValueError(
            f"File '{path.name}' does not appear to be a valid BeerXML file "
            f"(expected root element <RECIPES> or <RECIPE>)."
        )

    try:
        recipes = parse_beerxml_file(path)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    if not recipes:
        warnings.append(f"BeerXML file '{path.name}' contains no recipes.")
        text = f"# {path.stem}\n\n*(No recipes found in BeerXML file.)*\n"
    else:
        sections = [beerxml_recipe_to_markdown(r) for r in recipes]
        text = "\n\n---\n\n".join(sections)
        if len(recipes) > 1:
            warnings.append(
                f"BeerXML file contains {len(recipes)} recipes; "
                "all will be processed as separate OKPF records."
            )

    return ExtractedSource(
        source_path=path,
        source_filename=path.name,
        source_type="beerxml",
        text=text,
        warnings=warnings,
    )


def _extract_html(
    path: Path,
    *,
    source_url: str | None,
    source_content_type: str | None,
) -> ExtractedSource:
    try:
        from bs4 import BeautifulSoup, NavigableString, Tag
    except ImportError as exc:
        raise ImportError(
            "beautifulsoup4 is required for HTML extraction. Install it with: "
            "pip install beautifulsoup4"
        ) from exc

    warnings: list[str] = []
    provenance: list[dict[str, Any]] = []
    prechunked_blocks: list[PreChunkBlock] = []

    raw = path.read_bytes()
    if not _looks_like_html(raw):
        warnings.append(
            "HTML extension detected but file signature is weak; attempting "
            "best-effort HTML parse."
        )

    if source_content_type and "html" not in source_content_type.lower():
        warnings.append(
            f"Upload content type '{source_content_type}' does not indicate HTML; "
            "using extension+content parsing instead of MIME trust."
        )

    decoded = raw.decode("utf-8", errors="replace")
    damage = replacement_char_count(decoded)
    if damage:
        warnings.append(
            f"HTML decoding encountered {damage} replacement character(s); "
            "text was normalized with best-effort recovery."
        )
    decoded = normalize_extracted_text(decoded)

    soup = BeautifulSoup(decoded, "html.parser")

    node_count = sum(1 for _ in soup.descendants)
    if node_count > _MAX_HTML_NODES:
        raise ValueError(
            f"HTML document is too large/complex to parse safely "
            f"({node_count} nodes > {_MAX_HTML_NODES})."
        )

    _strip_non_content_chrome(soup)
    root = _select_content_root(soup)

    state: dict[str, Any] = {
        "current_heading": None,
        "table_index": 0,
    }

    def _walk(node: Any) -> None:
        if isinstance(node, NavigableString):
            return
        if not isinstance(node, Tag):
            return

        if node.name in _DROP_TAGS:
            return

        name = node.name.lower()

        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading_text = _clean_ws(node.get_text(" ", strip=True))
            if heading_text:
                level = int(name[1])
                prechunked_blocks.append(
                    PreChunkBlock(text=f"{'#' * level} {heading_text}", heading=heading_text)
                )
                state["current_heading"] = heading_text
            return

        if name == "p":
            paragraph = _extract_text_with_links(node, source_url, provenance)
            if paragraph:
                prechunked_blocks.append(
                    PreChunkBlock(text=paragraph, heading=state.get("current_heading"))
                )
            return

        if name in {"ul", "ol"}:
            list_text = _render_list(node, source_url, provenance)
            if list_text:
                prechunked_blocks.append(
                    PreChunkBlock(text=list_text, heading=state.get("current_heading"))
                )
            return

        if name == "table":
            state["table_index"] += 1
            table_blocks = _render_table_batches(
                node,
                table_index=state["table_index"],
                source_filename=path.name,
                section_heading=state.get("current_heading"),
                source_url=source_url,
                provenance=provenance,
            )
            prechunked_blocks.extend(table_blocks)
            return

        for child in node.children:
            _walk(child)

    _walk(root)

    body_parts = [b.text for b in prechunked_blocks if b.text.strip()]
    text = "\n\n".join(body_parts).strip()
    text = normalize_extracted_text(text)

    return ExtractedSource(
        source_path=path,
        source_filename=path.name,
        source_type="html",
        text=text,
        warnings=warnings,
        source_url=source_url,
        provenance=provenance,
        prechunked_blocks=prechunked_blocks,
    )


def _looks_like_html(raw: bytes) -> bool:
    head = raw[:8192]
    lower = head.lower()
    if b"<!doctype html" in lower or b"<html" in lower:
        return True
    text = head.decode("utf-8", errors="ignore")
    return bool(_HTML_SIGNATURE_RE.search(text))


def _clean_ws(text: str) -> str:
    return " ".join(text.split())


def _strip_non_content_chrome(soup: Any) -> None:
    for tag in soup.find_all(_DROP_TAGS):
        tag.decompose()

    for tag in soup.find_all(True):
        attrs = getattr(tag, "attrs", None) or {}
        classes_raw = attrs.get("class") or []
        classes = " ".join(classes_raw) if isinstance(classes_raw, list) else str(classes_raw)
        ident = str(attrs.get("id") or "")
        label = f"{classes} {ident}".strip()
        if label and _CHROME_HINT_RE.search(label):
            tag.decompose()


def _select_content_root(soup: Any) -> Any:
    for selector in ("main", "article", "[role='main']"):
        node = soup.select_one(selector)
        if node is not None:
            return node
    return soup.body or soup


def _extract_text_with_links(node: Any, source_url: str | None, provenance: list[dict[str, Any]]) -> str:
    for anchor in node.find_all("a"):
        link_text = _clean_ws(anchor.get_text(" ", strip=True))
        href = (anchor.get("href") or "").strip()
        if href and source_url and not href.startswith(("javascript:", "data:", "mailto:", "tel:")):
            resolved = urljoin(source_url, href)
            is_relative = not bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", href))
            if is_relative:
                provenance.append(
                    {
                        "kind": "link",
                        "text": link_text,
                        "href": href,
                        "resolved_url": resolved,
                    }
                )
        anchor.replace_with(link_text)

    return _clean_ws(node.get_text(" ", strip=True))


def _render_list(node: Any, source_url: str | None, provenance: list[dict[str, Any]]) -> str:
    items: list[str] = []
    ordered = node.name.lower() == "ol"
    for idx, li in enumerate(node.find_all("li", recursive=False), start=1):
        text = _extract_text_with_links(li, source_url, provenance)
        if not text:
            continue
        prefix = f"{idx}." if ordered else "-"
        items.append(f"{prefix} {text}")
    return "\n".join(items)


def _render_table_batches(
    table: Any,
    *,
    table_index: int,
    source_filename: str,
    section_heading: str | None,
    source_url: str | None,
    provenance: list[dict[str, Any]],
) -> list[PreChunkBlock]:
    rows = table.find_all("tr")
    parsed_rows: list[list[str]] = []
    header: list[str] = []

    for tr in rows:
        cells = tr.find_all(["th", "td"], recursive=False) or tr.find_all(["th", "td"])
        values = [_clean_ws(cell.get_text(" ", strip=True)) for cell in cells]
        if not values or all(not v for v in values):
            continue
        has_header_cells = any((getattr(cell, "name", "") or "").lower() == "th" for cell in cells)
        if has_header_cells and not header:
            header = values
        else:
            parsed_rows.append(values)

    if not header and parsed_rows:
        header = parsed_rows[0]
        parsed_rows = parsed_rows[1:]

    if not header and parsed_rows:
        width = max(len(r) for r in parsed_rows)
        header = [f"column_{i}" for i in range(1, width + 1)]

    if not header and not parsed_rows:
        return []

    norm_rows: list[list[str]] = []
    width = len(header)
    for r in parsed_rows:
        norm = list(r[:width])
        if len(norm) < width:
            norm.extend([""] * (width - len(norm)))
        norm_rows.append(norm)

    caption_text = _clean_ws((table.find("caption") or {}).get_text(" ", strip=True) if table.find("caption") else "")
    table_title = caption_text or f"Table {table_index}"

    blocks: list[PreChunkBlock] = []
    for start in range(0, len(norm_rows), _TABLE_BATCH_ROWS):
        end = min(start + _TABLE_BATCH_ROWS, len(norm_rows))
        batch_rows = norm_rows[start:end]
        row_start = start + 1
        row_end = end
        markdown_lines = [
            f"### {table_title}",
            f"Table provenance: table_index={table_index}; row_range={row_start}-{row_end}",
            f"Source file: {source_filename}",
        ]
        if section_heading:
            markdown_lines.append(f"Section heading: {section_heading}")
        if source_url:
            markdown_lines.append(f"Source URL: {source_url}")
        markdown_lines.append("| " + " | ".join(header) + " |")
        markdown_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        for row in batch_rows:
            markdown_lines.append("| " + " | ".join(row) + " |")

        source_ref = {
            "table_index": table_index,
            "row_range": [row_start, row_end],
            "section_heading": section_heading,
            "source_file": source_filename,
        }
        if source_url:
            source_ref["source_url"] = source_url

        blocks.append(
            PreChunkBlock(
                text="\n".join(markdown_lines),
                heading=section_heading,
                is_table_like=True,
                source_ref=source_ref,
            )
        )

    provenance.append(
        {
            "kind": "table",
            "table_index": table_index,
            "title": table_title,
            "header": header,
            "rows": len(norm_rows),
            "section_heading": section_heading,
        }
    )
    return blocks
