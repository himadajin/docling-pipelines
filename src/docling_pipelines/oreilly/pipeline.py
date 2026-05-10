from dataclasses import dataclass
from typing import Literal

from ..models import (
    ConversionConfig,
    DocumentRepair,
    IndexRepair,
    MarkdownRepair,
    PendingIndexTermSplitter,
    TocRepair,
)
from ..pipeline import BookPipeline
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
class OReillyBookPipeline(BookPipeline):
    index_source: IndexSource = "docling-tables"
    document_repairs: tuple[DocumentRepair, ...] = ()
    markdown_repairs: tuple[MarkdownRepair, ...] = ()
    toc_repairs: tuple[TocRepair, ...] = ()
    index_repairs: tuple[IndexRepair, ...] = ()
    pending_index_term_splitter: PendingIndexTermSplitter | None = None

    def transform_document(
        self,
        document: object,
        page_range: tuple[int, int] | None,
        section_key: str | None,
        config: ConversionConfig,
    ) -> None:
        transform_document(
            document,
            self.spec.pdf_path,
            config,
            document_repairs=self.document_repairs,
            normalize_tables=not self.is_index_target(section_key, page_range),
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
