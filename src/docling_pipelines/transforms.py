from pathlib import Path

from .code.detection import is_code_like_text, is_docling_code_label
from .models import ConversionConfig, DocumentRepair
from .text_utils import repair_japanese_spacing_in_line


def normalize_text_items(document: object) -> None:
    for item in getattr(document, "texts", []):
        text = str(getattr(item, "text", ""))
        if not text.strip():
            continue
        if (
            is_docling_code_label(getattr(item, "label", None))
            or is_code_like_text(text)
        ):
            continue

        item.text = repair_japanese_spacing_in_line(text)


def normalize_table_cells(document: object) -> None:
    for table in getattr(document, "tables", []):
        data = getattr(table, "data", None)
        grid = getattr(data, "grid", None)
        if not grid:
            continue

        for row in grid:
            for cell in row:
                text = str(getattr(cell, "text", ""))
                if text.strip():
                    cell.text = repair_japanese_spacing_in_line(text)


def transform_document(
    document: object,
    input_pdf: Path,
    config: ConversionConfig,
    document_repairs: tuple[DocumentRepair, ...] = (),
    normalize_tables: bool = True,
) -> None:
    if config.apply_pdf_repairs:
        for repair in document_repairs:
            repair(document, input_pdf)
    normalize_text_items(document)
    if normalize_tables:
        normalize_table_cells(document)
