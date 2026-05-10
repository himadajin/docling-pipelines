import argparse
from pathlib import Path
import unittest

from docling_pipelines.oreilly.catalog import get_book
from docling_pipelines.oreilly.isbn978_4_87311_758_4.pipeline import (
    PIPELINE as PIPELINE_758_4,
)
from docling_pipelines.oreilly.isbn978_4_87311_836_9.pipeline import (
    PIPELINE as PIPELINE_836_9,
)
from docling_pipelines.oreilly.isbn978_4_87311_906_9.pipeline import (
    PIPELINE as PIPELINE_906_9,
)
from docling_pipelines.oreilly.repairs.isbn978_4_87311_758_4.markdown import (
    apply_markdown_repairs,
)
from docling_pipelines.cli import parse_page_range
from docling_pdf2md.images import image_export_prefix
from docling_pipelines.models import ConversionConfig
from docling_pipelines.oreilly.markdown.index import extract_index_entries_from_markdown
from docling_pipelines.oreilly.markdown.polish import (
    polish_markdown,
    repair_markdown_heading_spacing,
    trim_markdown_table_cell_padding,
)
from docling_pipelines.paths import PROJECT_ROOT


class ParsePageRangeTest(unittest.TestCase):
    def test_valid_page_range(self) -> None:
        self.assertEqual(parse_page_range("1-10"), (1, 10))

    def test_rejects_invalid_shape(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_page_range("1")

    def test_rejects_zero_start(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_page_range("0-1")

    def test_rejects_descending_range(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_page_range("10-1")


class BookSpecTest(unittest.TestCase):
    def test_get_section_and_pipeline_special_page_ranges(self) -> None:
        book = get_book("758-4")
        self.assertEqual(
            book.pdf_path,
            PROJECT_ROOT / "pdf" / "ISBN978-4-87311-758-4.pdf",
        )
        self.assertEqual(book.output_root, Path("books") / book.book_id)
        self.assertEqual(
            book.image_output_dir,
            Path("books") / book.book_id / "images",
        )
        self.assertEqual(book.get_section("toc").page_range, (13, 20))
        self.assertEqual(book.get_section("index").page_range, (313, 320))
        self.assertTrue(PIPELINE_758_4.is_toc_target(None, (13, 20)))
        self.assertTrue(PIPELINE_758_4.is_index_target("index", None))
        self.assertEqual(PIPELINE_758_4.index_source, "docling-tables")

    def test_generic_pipeline_does_not_import_oreilly_style_modules(self) -> None:
        pipeline_source = (
            PROJECT_ROOT / "src" / "docling_pipelines" / "pipeline.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("docling_pipelines.oreilly", pipeline_source)
        self.assertNotIn(".oreilly", pipeline_source)
        self.assertNotIn(".markdown.index", pipeline_source)
        self.assertNotIn(".markdown.toc", pipeline_source)
        self.assertNotIn(".markdown.polish", pipeline_source)

    def test_second_and_third_books_format_toc_and_index(self) -> None:
        book = get_book("836-9")
        self.assertEqual(book.get_section("toc").page_range, (11, 18))
        self.assertEqual(book.get_section("index").page_range, (425, 432))
        self.assertTrue(PIPELINE_836_9.is_toc_target("toc", (11, 18)))
        self.assertTrue(PIPELINE_836_9.is_index_target("index", (425, 432)))
        self.assertEqual(PIPELINE_836_9.index_source, "pdf-layout")

        book = get_book("906-9")
        self.assertEqual(book.get_section("toc").page_range, (11, 22))
        self.assertEqual(book.get_section("index").page_range, (543, 552))
        self.assertTrue(PIPELINE_906_9.is_toc_target("toc", (11, 22)))
        self.assertTrue(PIPELINE_906_9.is_index_target("index", (543, 552)))
        self.assertEqual(PIPELINE_906_9.index_source, "pdf-layout")

    def test_index_markdown_parser_handles_tables_and_text_fragments(self) -> None:
        markdown = """## 記号・数字

term only
12

| AdaGrad | 1 |
|---|---|
| BPTT | 2 |
"""
        entries = extract_index_entries_from_markdown(markdown)
        self.assertEqual(entries[0].heading, "記号")
        self.assertIn(("term only", "12"), [(entry.term, entry.pages) for entry in entries])
        self.assertIn(("AdaGrad", "1"), [(entry.term, entry.pages) for entry in entries])
        self.assertIn(("BPTT", "2"), [(entry.term, entry.pages) for entry in entries])


class MarkdownPolishTest(unittest.TestCase):
    def test_repairs_heading_spacing(self) -> None:
        self.assertEqual(repair_markdown_heading_spacing("## ）\n"), "##）\n")

    def test_trims_markdown_table_cell_padding(self) -> None:
        markdown = "|列。 |値） |\n|---|---|\n"
        self.assertEqual(
            trim_markdown_table_cell_padding(markdown),
            "|列。|値）|\n|---|---|\n",
        )

    def test_annotates_python_code_blocks(self) -> None:
        markdown = "def f(x):\n    return x\n"
        self.assertIn(
            "```python",
            polish_markdown(markdown, ConversionConfig(False)),
        )

    def test_758_4_markdown_repair(self) -> None:
        markdown = "また、各変数に関する微分は、で求めることができます。"
        self.assertEqual(
            apply_markdown_repairs(markdown),
            "また、各変数に関する微分は、backward() で求めることができます。",
        )


class ImagesTest(unittest.TestCase):
    def test_image_export_prefix(self) -> None:
        self.assertEqual(image_export_prefix((1, 2), None), "range-p001-p002")
        self.assertEqual(image_export_prefix(None, "chapter-01"), "chapter-01")
        self.assertEqual(image_export_prefix(None, None), "full")


if __name__ == "__main__":
    unittest.main()
