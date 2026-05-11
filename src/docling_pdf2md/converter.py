from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorOptions,
    PdfPipelineOptions,
    TableFormerMode,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

from .models import MarkdownExportConfig, TableMode


def build_converter(
    do_ocr: bool,
    extract_images: bool = True,
    images_scale: float = 2.0,
    table_mode: TableMode = TableMode.ACCURATE,
    num_threads: int | None = None,
) -> DocumentConverter:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = do_ocr
    pipeline_options.generate_page_images = extract_images
    pipeline_options.generate_picture_images = extract_images
    pipeline_options.images_scale = images_scale
    if table_mode == TableMode.OFF:
        pipeline_options.do_table_structure = False
    else:
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode(table_mode)
    if num_threads is not None:
        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=num_threads,
        )

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )


def convert_pdf_to_document(
    converter: DocumentConverter,
    input_pdf: Path,
    page_range: tuple[int, int] | None,
) -> object:
    if page_range:
        return converter.convert(input_pdf, page_range=page_range).document

    return converter.convert(input_pdf).document


def export_document_markdown(
    document: object,
    config: MarkdownExportConfig = MarkdownExportConfig(),
    include_images: bool = False,
) -> str:
    return document.export_to_markdown(
        escape_html=config.escape_html,
        escape_underscores=config.escape_underscores,
        image_mode=(
            ImageRefMode.REFERENCED if include_images else ImageRefMode.PLACEHOLDER
        ),
    )
