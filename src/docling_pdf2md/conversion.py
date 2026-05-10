from pathlib import Path
from time import perf_counter
from typing import Callable

from docling.document_converter import DocumentConverter

from .converter import convert_pdf_to_document
from .images import save_document_images
from .markdown import export_markdown_for_range
from .models import ImageExportConfig, ImageExportResult, MarkdownExportConfig

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
) -> tuple[float, ImageExportResult]:
    started_at = perf_counter()
    document = convert_pdf_to_document(converter, input_pdf, page_range)
    if transform:
        transform(document)
    image_result = save_document_images(
        document,
        output_markdown,
        page_range,
        section_key,
        images,
    )
    markdown_text = export_markdown_for_range(document, markdown, images)
    if apply_render_markdown and render_markdown:
        markdown_text = render_markdown(document, markdown_text)
    elapsed = perf_counter() - started_at

    write_markdown(output_markdown, markdown_text)
    return elapsed, image_result
