import argparse
from pathlib import Path
import unittest

from docling_pipelines.oreilly.catalog import get_book
from docling_pipelines.lambda_note.catalog import get_book as get_lambda_note_book
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
from docling_pipelines.lambda_note.markdown import (
    normalize_cjk_radicals,
    polish_markdown as polish_lambda_note_markdown,
)
from docling_pipelines.lambda_note.audit import audit_paths, issue_totals
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

    def test_lambda_note_books_have_configured_sections(self) -> None:
        book = get_lambda_note_book("06-1")
        self.assertEqual(
            book.pdf_path,
            PROJECT_ROOT / "pdf" / "ISBN978-4-908686-06-1.pdf",
        )
        self.assertEqual(book.output_root, Path("books") / book.book_id)
        self.assertEqual(book.get_section("chapter-01").page_range, (13, 36))
        self.assertEqual(book.get_section("chapter-14").page_range, (253, 273))
        self.assertEqual(book.get_section("index").page_range, (280, 288))

        book = get_lambda_note_book("16-0")
        self.assertEqual(
            book.pdf_path,
            PROJECT_ROOT / "pdf" / "ISBN978-4-908686-16-0.pdf",
        )
        self.assertEqual(book.output_root, Path("books") / book.book_id)
        self.assertEqual(book.get_section("chapter-01").page_range, (13, 22))
        self.assertEqual(book.get_section("chapter-13").page_range, (243, 248))
        self.assertEqual(book.get_section("index").page_range, (301, 312))

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


class LambdaNoteMarkdownPolishTest(unittest.TestCase):
    def test_normalizes_cjk_radicals_without_broad_nfkc_changes(self) -> None:
        self.assertEqual(
            normalize_cjk_radicals("⽣活 毎⽇ ⼊⼒ ①"),
            "生活 毎日 入力 ①",
        )

    def test_removes_watermarks_and_running_chapter_headers(self) -> None:
        markdown = "\n".join(
            [
                "本文",
                "★ ✵✽✵✻hash",
                "## 2 第 1 章 イントロダクション",
                "## 120000 ドル = 120 ヶ月 毎月 $1000",
                "続き",
            ]
        )
        self.assertEqual(
            polish_lambda_note_markdown(markdown),
            "本文\n## 120000 ドル = 120 ヶ月 毎月 $1000\n続き",
        )

    def test_repairs_glyph_list_markers(self) -> None:
        markdown = "\n".join(
            [
                "- glyph[a114] 親項目 glyph[a113] 子項目 glyph[a114] 次の親項目",
                "## glyph[a114] 見出し化された箇条書き",
                "- glyph[a113] 子項目だけ",
                "- URL glyph[a114] 次の親項目",
                "glyph[a114] 先頭glyph項目",
                "ALU glyph[a114] 5B205 ：階層構造のメモリシステム",
                "- 末尾glyph glyph[a114]",
                "本文 glyph[a114] はそのまま",
            ]
        )
        self.assertEqual(
            polish_lambda_note_markdown(markdown),
            "\n".join(
                [
                    "- 親項目",
                    "  - 子項目",
                    "- 次の親項目",
                    "- 見出し化された箇条書き",
                    "  - 子項目だけ",
                    "- URL",
                    "- 次の親項目",
                    "- 先頭glyph項目",
                    "- ALU",
                    "- 5B205 ：階層構造のメモリシステム",
                    "- 末尾glyph",
                    "本文 glyph[a114] はそのまま",
                ]
            ),
        )

    def test_repairs_command_frames_and_code_listing_headings(self) -> None:
        markdown = "\n".join(
            [
                "glyph[a0]",
                "## $ gcc -S -masm=intel example.c ✂ ✄ ✛",
                "✁",
                "## $ ./io\\_read\\_pci ✂ ✁ ✄ glyph[a0] ✛ Vendor ID = 8086",
                "$ ./syscall\\_write ✂ ✁ ✄ glyph[a0] ✛ hello, world",
                "✂ ✁ ✄ glyph[a0] ✛",
                "## リスト 3.5 ：真のデータ依存関係がある場合",
            ]
        )
        self.assertEqual(
            polish_lambda_note_markdown(markdown),
            "\n".join(
                [
                    "```console",
                    "$ gcc -S -masm=intel example.c",
                    "```",
                    "```console",
                    "$ ./io_read_pci",
                    "Vendor ID = 8086",
                    "```",
                    "```console",
                    "$ ./syscall_write",
                    "hello, world",
                    "```",
                    "**リスト 3.5 ：真のデータ依存関係がある場合**",
                ]
            ),
        )

    def test_repairs_lambda_note_japanese_spacing_without_touching_protected_lines(self) -> None:
        markdown = "\n".join(
            [
                "遅 くする",
                "影 響",
                "メモリアクセス 順序",
                "https://example.com/影 響",
                "| 影 響 |",
                "```python",
                "影 響",
                "```",
                "$ echo 影 響",
                "<!-- formula-not-decoded --> 影 響",
            ]
        )
        self.assertEqual(
            polish_lambda_note_markdown(markdown),
            "\n".join(
                [
                    "遅くする",
                    "影響",
                    "メモリアクセス順序",
                    "https://example.com/影 響",
                    "| 影 響 |",
                    "```python",
                    "影 響",
                    "```",
                    "$ echo 影 響",
                    "<!-- formula-not-decoded --> 影 響",
                ]
            ),
        )

    def test_repairs_visible_glyph_markers_after_code_fences_are_balanced(self) -> None:
        markdown = "\n".join(
            [
                "```",
                "glyph[a114] glyph[a114]",
                "```",
                "",
                "- glyph[a114] 本文側のリスト",
            ]
        )
        self.assertEqual(
            polish_lambda_note_markdown(markdown),
            "\n- 本文側のリスト",
        )


class LambdaNoteMarkdownAuditTest(unittest.TestCase):
    def test_audits_known_lambda_note_quality_issues(self) -> None:
        audit_file = PROJECT_ROOT / "output" / "lambda-note-audit-test.md"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        audit_file.write_text(
            "\n".join(
                [
                    "本文",
                    "glyph[a114]",
                    "⽣活",
                    "<!-- formula-not-decoded -->",
                    "## $ ./example",
                    "## リスト 3.1 ： example.S",
                    "## ▲ 図 1.1 例",
                    "遅 くする",
                ]
            ),
            encoding="utf-8",
        )

        try:
            totals = issue_totals(audit_paths([audit_file]))
        finally:
            audit_file.unlink()

        self.assertEqual(totals["glyph"], 1)
        self.assertEqual(totals["cjk_radical"], 1)
        self.assertEqual(totals["japanese_spacing"], 1)
        self.assertEqual(totals["formula_not_decoded"], 1)
        self.assertEqual(totals["command_heading"], 1)
        self.assertEqual(totals["code_listing_heading"], 1)
        self.assertEqual(totals["figure_caption_heading"], 1)


class ImagesTest(unittest.TestCase):
    def test_image_export_prefix(self) -> None:
        self.assertEqual(image_export_prefix((1, 2), None), "range-p001-p002")
        self.assertEqual(image_export_prefix(None, "chapter-01"), "chapter-01")
        self.assertEqual(image_export_prefix(None, None), "full")


if __name__ == "__main__":
    unittest.main()
