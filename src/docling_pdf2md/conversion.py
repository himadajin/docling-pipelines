from pathlib import Path
from time import perf_counter
from typing import Callable

from docling.document_converter import DocumentConverter

from .converter import convert_pdf_to_document
from .images import save_document_images
from .markdown import export_markdown_for_range
from .models import (
    ConversionProfile,
    ImageExportConfig,
    ImageExportResult,
    MarkdownExportConfig,
)

DocumentTransform = Callable[[object], None]
MarkdownRenderer = Callable[[object, str], str]


def write_markdown(output_markdown: Path, markdown: str) -> None:
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(markdown, encoding="utf-8")


def convert_to_markdown(
    converter: DocumentConverter,
    input_pdf: Path,
    output_markdown: Path,
    page_range: tuple[int, int] | None,
    markdown: MarkdownExportConfig,
    images: ImageExportConfig,
    section_key: str | None = None,
    transform: DocumentTransform | None = None,
    render_markdown: MarkdownRenderer | None = None,
    apply_render_markdown: bool = True,
) -> tuple[float, ImageExportResult, ConversionProfile]:
    started_at = perf_counter()

    docling_started_at = perf_counter()
    document = convert_pdf_to_document(converter, input_pdf, page_range)
    docling_elapsed = perf_counter() - docling_started_at

    transform_started_at = perf_counter()
    if transform:
        transform(document)
    transform_elapsed = perf_counter() - transform_started_at

    image_started_at = perf_counter()
    image_result = save_document_images(
        document,
        output_markdown,
        page_range,
        section_key,
        images,
    )
    image_elapsed = perf_counter() - image_started_at

    markdown_export_started_at = perf_counter()
    markdown_text = export_markdown_for_range(document, markdown, images)
    markdown_export_elapsed = perf_counter() - markdown_export_started_at

    markdown_render_started_at = perf_counter()
    if apply_render_markdown and render_markdown:
        markdown_text = render_markdown(document, markdown_text)
    markdown_render_elapsed = perf_counter() - markdown_render_started_at

    write_started_at = perf_counter()
    write_markdown(output_markdown, markdown_text)
    write_elapsed = perf_counter() - write_started_at

    elapsed = perf_counter() - started_at
    profile = ConversionProfile(
        docling_convert_seconds=docling_elapsed,
        document_transform_seconds=transform_elapsed,
        image_save_seconds=image_elapsed,
        markdown_export_seconds=markdown_export_elapsed,
        markdown_render_seconds=markdown_render_elapsed,
        markdown_write_seconds=write_elapsed,
    )
    return elapsed, image_result, profile
