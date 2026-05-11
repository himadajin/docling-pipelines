from dataclasses import dataclass
from pathlib import Path

from docling.document_converter import DocumentConverter

from docling_pdf2md.conversion import convert_to_markdown

from .models import BookSpec, ConversionConfig, Section
from .reporting import print_result


@dataclass(frozen=True)
class BookPipeline:
    spec: BookSpec
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

        def render(document: object, markdown: str) -> str:
            return self.render_markdown(
                document,
                markdown,
                effective_page_range,
                section_key,
                config,
            )

        elapsed, image_result, profile = convert_to_markdown(
            converter=converter,
            input_pdf=self.spec.pdf_path,
            output_markdown=output_path,
            page_range=effective_page_range,
            markdown=config.markdown,
            images=config.images,
            section_key=section_key,
            transform=lambda document: self.transform_document(
                document,
                effective_page_range,
                section_key,
                config,
            ),
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
            profile,
        )

    def render_markdown(
        self,
        document: object,
        markdown: str,
        page_range: tuple[int, int] | None,
        section_key: str | None,
        config: ConversionConfig,
    ) -> str:
        return markdown

    def transform_document(
        self,
        document: object,
        page_range: tuple[int, int] | None,
        section_key: str | None,
        config: ConversionConfig,
    ) -> None:
        return None
