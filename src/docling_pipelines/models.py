from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from docling_pdf2md.cache import DoclingCacheConfig
from docling_pdf2md.models import ImageExportConfig, MarkdownExportConfig, TableMode


@dataclass(frozen=True)
class Section:
    key: str
    filename: str
    title: str
    page_range: tuple[int, int]


DocumentRepair = Callable[[object, Path], None]
MarkdownRepair = Callable[[str], str]
TocRepair = Callable[[list["TocEntry"]], list["TocEntry"]]
IndexRepair = Callable[[list["IndexEntry"]], list["IndexEntry"]]
PendingIndexTermSplitter = Callable[[str], list[str] | None]


@dataclass(frozen=True)
class TocEntry:
    number: str | None
    title: str
    page: str | None


@dataclass(frozen=True)
class IndexEntry:
    heading: str | None
    term: str | None
    pages: str | None


@dataclass(frozen=True)
class CodeRepair:
    item_ref: str | None
    page_no: int
    bbox: object
    text: str


@dataclass(frozen=True)
class ConversionConfig:
    do_ocr: bool
    table_mode: TableMode = TableMode.ACCURATE
    apply_pdf_repairs: bool = True
    apply_markdown_polish: bool = True
    apply_markdown_spacing: bool = False
    profile: bool = False
    markdown: MarkdownExportConfig = MarkdownExportConfig()
    images: ImageExportConfig = ImageExportConfig()
    cache: DoclingCacheConfig = DoclingCacheConfig()


@dataclass(frozen=True)
class BookSpec:
    book_id: str
    pdf_path: Path
    sections: tuple[Section, ...]
    output_root: Path
    image_output_dir: Path

    def get_section(self, key: str) -> Section:
        for section in self.sections:
            if section.key == key:
                return section

        valid_keys = ", ".join(section.key for section in self.sections)
        raise ValueError(f"Unknown section: {key}. Valid sections: {valid_keys}")
