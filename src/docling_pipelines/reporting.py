from pathlib import Path

from docling_pdf2md.cache import DoclingCacheResult
from docling_pdf2md.models import ConversionProfile, ImageExportResult

from .models import ConversionConfig, Section


def print_result(
    book_id: str,
    input_pdf: Path,
    output_markdown: Path,
    page_range: tuple[int, int] | None,
    elapsed: float,
    config: ConversionConfig,
    image_result: ImageExportResult,
    section: Section | None = None,
    profile: ConversionProfile | None = None,
    cache_result: DoclingCacheResult | None = None,
) -> None:
    print(f"Book: {book_id}")
    print(f"Input: {input_pdf}")
    if section:
        print(f"Section: {section.key} ({section.title})")
    print(f"OCR: {'on' if config.do_ocr else 'off'}")
    print(f"Table mode: {config.table_mode.value}")
    print(f"PDF repairs: {'on' if config.apply_pdf_repairs else 'off'}")
    print(f"Markdown polish: {'on' if config.apply_markdown_polish else 'off'}")
    print(f"Markdown spacing: {'on' if config.apply_markdown_spacing else 'off'}")
    print(f"Images: {'on' if image_result.enabled else 'off'}")
    if image_result.enabled:
        print(f"Image output: {image_result.output_dir.resolve()}")
        print(f"Images saved: {image_result.saved_count}")
    if page_range:
        start, end = page_range
        print(f"Pages: {start}-{end}")
    else:
        print("Pages: all")
    if cache_result:
        print(f"Cache: {cache_result.status}")
        if cache_result.path:
            print(f"Cache path: {cache_result.path.resolve()}")
    print(f"Output: {output_markdown.resolve()}")
    print(f"Output size: {output_markdown.stat().st_size:,} bytes")
    print(f"Elapsed: {elapsed:.1f} seconds")
    if config.profile and profile:
        print("Profile:")
        print(f"  Docling convert: {profile.docling_convert_seconds:.3f}s")
        print(f"  Document repairs: {profile.document_transform_seconds:.3f}s")
        print(f"  Image save: {profile.image_save_seconds:.3f}s")
        print(f"  Markdown export: {profile.markdown_export_seconds:.3f}s")
        print(f"  Markdown render: {profile.markdown_render_seconds:.3f}s")
        print(f"  Markdown write: {profile.markdown_write_seconds:.3f}s")
        print(f"  Measured total: {profile.measured_seconds:.3f}s")
