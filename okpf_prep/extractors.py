from __future__ import annotations

from pathlib import Path

from .models import ExtractedSource

SUPPORTED_TYPES = {"txt", "md", "pdf"}


def extract_text(source_path: str | Path) -> ExtractedSource:
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

    return ExtractedSource(
        source_path=path,
        source_filename=path.name,
        source_type="pdf",
        text=text,
        page_count=page_count,
        warnings=warnings,
    )
