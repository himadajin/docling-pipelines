from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from docling_core.types.doc import DoclingDocument, ImageRefMode

from .models import TableMode


@dataclass(frozen=True)
class DoclingCacheConfig:
    enabled: bool = True
    refresh: bool = False
    root: Path = Path(".cache") / "docling-pipelines" / "docling"
    book_id: str | None = None
    section_key: str | None = None


@dataclass(frozen=True)
class DoclingCacheResult:
    enabled: bool
    status: str
    path: Path | None = None


def docling_cache_key(
    input_pdf: Path,
    page_range: tuple[int, int] | None,
    config: DoclingCacheConfig,
    *,
    do_ocr: bool,
    extract_images: bool,
    images_scale: float,
    table_mode: TableMode,
    docling_version: str,
) -> str:
    stat = input_pdf.stat()
    payload: dict[str, Any] = {
        "book_id": config.book_id,
        "docling_version": docling_version,
        "extract_images": extract_images,
        "images_scale": images_scale,
        "input_pdf": str(input_pdf.resolve()),
        "page_range": page_range,
        "pdf_mtime_ns": stat.st_mtime_ns,
        "pdf_size": stat.st_size,
        "section_key": config.section_key,
        "table_mode": table_mode.value,
        "ocr": do_ocr,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def docling_cache_path(root: Path, book_id: str | None, key: str) -> Path:
    book_dir = book_id or "unknown-book"
    return root / book_dir / f"{key}.json"


def load_docling_document(path: Path) -> DoclingDocument:
    return DoclingDocument.load_from_json(path)


def save_docling_document(
    document: object,
    path: Path,
    *,
    include_images: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image_mode = ImageRefMode.EMBEDDED if include_images else ImageRefMode.PLACEHOLDER
    document.save_as_json(path, image_mode=image_mode)
