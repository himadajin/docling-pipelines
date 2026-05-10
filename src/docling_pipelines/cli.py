import argparse
from dataclasses import dataclass
from pathlib import Path

from docling_pdf2md.converter import build_converter
from .models import ConversionConfig, ImageExportConfig
from .pipeline import BookPipeline


@dataclass(frozen=True)
class CliArgs:
    output_markdown: Path | None
    page_range: tuple[int, int] | None
    section_key: str | None
    all_sections: bool
    conversion: ConversionConfig


def parse_page_range(value: str) -> tuple[int, int]:
    try:
        start_text, end_text = value.split("-", maxsplit=1)
        start = int(start_text)
        end = int(end_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use START-END, for example: 1-10") from exc

    if start < 1:
        raise argparse.ArgumentTypeError("Page range start must be 1 or greater")
    if end < start:
        raise argparse.ArgumentTypeError(
            "Page range end must be greater than or equal to start"
        )

    return start, end


def build_parser() -> argparse.ArgumentParser:
    raise RuntimeError("Use build_book_parser() for book-specific commands")


def build_book_parser(pipeline: BookPipeline) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            f"Convert {pipeline.spec.book_id} sections or page ranges to Markdown "
            "with Docling."
        ),
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--pages",
        type=parse_page_range,
        metavar="START-END",
        help="Convert only an inclusive 1-based page range, for example: 1-10",
    )
    mode.add_argument(
        "--section",
        metavar="KEY",
        help="Convert one configured section, for example: chapter-01",
    )
    mode.add_argument(
        "--all-sections",
        action="store_true",
        help="Convert all configured sections to md.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Markdown output path for single-output conversions. Defaults to "
            "the full output path, output/<book-id>/ranges for --pages, or "
            "books/<book-id> for --section."
        ),
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable OCR for image regions in the PDF conversion pipeline.",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Keep Docling image placeholders instead of extracting linked images.",
    )
    parser.add_argument(
        "--no-pdf-repairs",
        action="store_true",
        help="Disable PDF-specific document repairs for comparison.",
    )
    parser.add_argument(
        "--no-markdown-polish",
        action="store_true",
        help="Disable final Markdown polish for comparison.",
    )
    parser.add_argument(
        "--markdown-spacing",
        action="store_true",
        help="Enable legacy final Markdown Japanese spacing repair for comparison.",
    )
    return parser


def parse_args_for_pipeline(pipeline: BookPipeline) -> CliArgs:
    parser = build_book_parser(pipeline)
    args = parser.parse_args()
    if args.all_sections and args.output:
        parser.error("--output cannot be used with --all-sections")

    return CliArgs(
        output_markdown=args.output,
        page_range=args.pages,
        section_key=args.section,
        all_sections=args.all_sections,
        conversion=ConversionConfig(
            do_ocr=args.ocr,
            apply_pdf_repairs=not args.no_pdf_repairs,
            apply_markdown_polish=not args.no_markdown_polish,
            apply_markdown_spacing=args.markdown_spacing,
            images=ImageExportConfig(
                enabled=not args.no_images,
                output_dir=pipeline.spec.image_output_dir,
            ),
        ),
    )


def run_book_cli(pipeline: BookPipeline) -> None:
    args = parse_args_for_pipeline(pipeline)
    if not pipeline.spec.pdf_path.is_file():
        raise FileNotFoundError(
            "Input PDF was not found. Place your legally obtained PDF at: "
            f"{pipeline.spec.pdf_path}"
        )

    converter = build_converter(
        args.conversion.do_ocr,
        args.conversion.images.enabled,
        args.conversion.images.images_scale,
    )

    if args.all_sections:
        if not pipeline.spec.sections:
            raise ValueError(
                f"No sections are configured for book: {pipeline.spec.book_id}"
            )
        for section in pipeline.spec.sections:
            pipeline.convert(converter, args.conversion, section=section)
            print()
        return

    if args.section_key:
        pipeline.convert(
            converter=converter,
            config=args.conversion,
            section=pipeline.spec.get_section(args.section_key),
            output_markdown=args.output_markdown,
        )
        return

    pipeline.convert(
        converter=converter,
        config=args.conversion,
        page_range=args.page_range,
        output_markdown=args.output_markdown,
    )


def main() -> None:
    raise SystemExit(
        "Use book-specific commands: "
        "docling-books-758-4, docling-books-836-9, docling-books-906-9"
    )


if __name__ == "__main__":
    main()
