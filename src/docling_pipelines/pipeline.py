from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from docling.document_converter import DocumentConverter

from docling_pdf2md.conversion import convert_to_markdown

from .models import (
    BookSpec,
    ConversionConfig,
    DocumentRepair,
    IndexRepair,
    MarkdownRepair,
    PendingIndexTermSplitter,
    Section,
    TocRepair,
)
from .reporting import print_result
from .markdown.index import (
    IndexExtractionOptions,
    extract_index_entries_from_docling_tables,
    extract_index_entries_from_markdown,
    extract_index_entries_from_pdf_layout,
    format_index_markdown,
)
from .markdown.polish import polish_markdown
from .markdown.toc import extract_toc_entries, render_toc_markdown
from .transforms import transform_document

IndexSource = Literal["docling-tables", "pdf-layout"]


@dataclass(frozen=True)
class BookPipeline:
    spec: BookSpec
    index_source: IndexSource
    document_repairs: tuple[DocumentRepair, ...] = ()
    markdown_repairs: tuple[MarkdownRepair, ...] = ()
    toc_repairs: tuple[TocRepair, ...] = ()
    index_repairs: tuple[IndexRepair, ...] = ()
    pending_index_term_splitter: PendingIndexTermSplitter | None = None
    toc_section_key: str = "toc"
    index_section_key: str = "index"

    def section_page_range(self, section_key: str) -> tuple[int, int] | None:
        try:
            return self.spec.get_section(section_key).page_range
        except ValueError:
            return None

    @property
    def toc_page_range(self) -> tuple[int, int] | None:
        return self.section_page_range(self.toc_section_key)

    @property
    def index_page_range(self) -> tuple[int, int] | None:
        return self.section_page_range(self.index_section_key)

    def is_toc_target(
        self,
        section_key: str | None,
        page_range: tuple[int, int] | None,
    ) -> bool:
        return section_key == self.toc_section_key or page_range == self.toc_page_range

    def is_index_target(
        self,
        section_key: str | None,
        page_range: tuple[int, int] | None,
    ) -> bool:
        return (
            section_key == self.index_section_key
            or page_range == self.index_page_range
        )

    def output_path(
        self,
        page_range: tuple[int, int] | None,
        section: Section | None,
        output_markdown: Path | None,
    ) -> Path:
        if output_markdown:
            return output_markdown
        if section:
            return self.spec.output_root / section.filename
        if page_range:
            start, end = page_range
            return (
                Path("output")
                / self.spec.book_id
                / "ranges"
                / f"{self.spec.book_id}_p{start:03d}-p{end:03d}.md"
            )
        return Path("output") / self.spec.book_id / f"{self.spec.book_id}.md"

    def convert(
        self,
        converter: DocumentConverter,
        config: ConversionConfig,
        page_range: tuple[int, int] | None = None,
        section: Section | None = None,
        output_markdown: Path | None = None,
    ) -> None:
        section_key = section.key if section else None
        output_path = self.output_path(page_range, section, output_markdown)
        effective_page_range = section.page_range if section else page_range

        def apply_transforms(document: object) -> None:
            transform_document(
                document,
                self.spec.pdf_path,
                config,
                document_repairs=self.document_repairs,
                normalize_tables=not self.is_index_target(
                    section_key,
                    effective_page_range,
                ),
            )

        def render(document: object, markdown: str) -> str:
            return self.render_markdown(
                document,
                markdown,
                effective_page_range,
                section_key,
                config,
            )

        elapsed, image_result = convert_to_markdown(
            converter=converter,
            input_pdf=self.spec.pdf_path,
            output_markdown=output_path,
            page_range=effective_page_range,
            markdown=config.markdown,
            images=config.images,
            section_key=section_key,
            transform=apply_transforms,
            render_markdown=render,
            apply_render_markdown=config.apply_markdown_polish,
        )
        print_result(
            self.spec.book_id,
            self.spec.pdf_path,
            output_path,
            effective_page_range,
            elapsed,
            config,
            image_result,
            section,
        )

    def render_markdown(
        self,
        document: object,
        markdown: str,
        page_range: tuple[int, int] | None,
        section_key: str | None,
        config: ConversionConfig,
    ) -> str:
        if self.is_toc_target(section_key, page_range):
            entries = extract_toc_entries(document)
            if not entries:
                return markdown
            for repair in self.toc_repairs:
                entries = repair(entries)
            return render_toc_markdown(entries)

        if self.is_index_target(section_key, page_range):
            options = IndexExtractionOptions(
                pending_term_splitter=self.pending_index_term_splitter,
            )
            if self.index_source == "pdf-layout" and self.index_page_range:
                entries = extract_index_entries_from_pdf_layout(
                    self.spec.pdf_path,
                    self.index_page_range,
                    options,
                )
                if not entries:
                    entries = extract_index_entries_from_markdown(markdown, options)
            else:
                entries = extract_index_entries_from_docling_tables(document, options)

            for repair in self.index_repairs:
                entries = repair(entries)
            return format_index_markdown(entries, markdown)

        return polish_markdown(markdown, config, self.markdown_repairs)
