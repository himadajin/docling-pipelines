from pathlib import Path

from ...models import BookSpec, Section
from ...paths import pdf_path


BOOK_ID = "978-4-87311-836-9"

SECTIONS: tuple[Section, ...] = (
    Section("frontmatter", "00-frontmatter.md", "表紙・奥付", (1, 2)),
    Section("preface", "01-preface.md", "まえがき", (3, 10)),
    Section("toc", "02-toc.md", "目次", (11, 18)),
    Section("chapter-01", "03-chapter-01.md", "1章 ニューラルネットワークの復習", (19, 74)),
    Section("chapter-02", "04-chapter-02.md", "2章 自然言語と単語の分散表現", (75, 110)),
    Section("chapter-03", "05-chapter-03.md", "3章 word2vec", (111, 148)),
    Section("chapter-04", "06-chapter-04.md", "4章 word2vec の高速化", (149, 192)),
    Section("chapter-05", "07-chapter-05.md", "5章 リカレントニューラルネットワーク（RNN）", (193, 240)),
    Section("chapter-06", "08-chapter-06.md", "6章 ゲート付き RNN", (241, 294)),
    Section("chapter-07", "09-chapter-07.md", "7章 RNN による文章生成", (295, 342)),
    Section("chapter-08", "10-chapter-08.md", "8章 Attention", (343, 398)),
    Section("appendix-a", "11-appendix-a.md", "付録 A", (399, 404)),
    Section("appendix-b", "12-appendix-b.md", "付録 B", (405, 410)),
    Section("appendix-c", "13-appendix-c.md", "付録 C", (411, 414)),
    Section("afterword", "14-afterword.md", "おわりに", (415, 418)),
    Section("references", "15-references.md", "参考文献", (419, 424)),
    Section("index", "16-index.md", "索引", (425, 432)),
)

SPEC = BookSpec(
    book_id=BOOK_ID,
    pdf_path=pdf_path("ISBN978-4-87311-836-9.pdf"),
    sections=SECTIONS,
    output_root=Path("books") / BOOK_ID,
    image_output_dir=Path("books") / BOOK_ID / "images",
)
