from pathlib import Path

from ...models import BookSpec, Section
from ...paths import pdf_path


BOOK_ID = "978-4-87311-758-4"

SECTIONS: tuple[Section, ...] = (
    Section("frontmatter", "00-frontmatter.md", "表紙・奥付", (1, 2)),
    Section("preface", "01-preface.md", "まえがき", (3, 12)),
    Section("toc", "02-toc.md", "目次", (13, 20)),
    Section("chapter-01", "03-chapter-01.md", "1章 Python 入門", (21, 40)),
    Section("chapter-02", "04-chapter-02.md", "2章 パーセプトロン", (41, 58)),
    Section("chapter-03", "05-chapter-03.md", "3章 ニューラルネットワーク", (59, 102)),
    Section("chapter-04", "06-chapter-04.md", "4章 ニューラルネットワークの学習", (103, 142)),
    Section("chapter-05", "07-chapter-05.md", "5章 誤差逆伝播法", (143, 184)),
    Section("chapter-06", "08-chapter-06.md", "6章 学習に関するテクニック", (185, 224)),
    Section("chapter-07", "09-chapter-07.md", "7章 畳み込みニューラルネットワーク", (225, 260)),
    Section("chapter-08", "10-chapter-08.md", "8章 ディープラーニング", (261, 294)),
    Section("appendix-a", "11-appendix-a.md", "付録 A", (295, 306)),
    Section("references", "12-references.md", "参考文献", (307, 312)),
    Section("index", "13-index.md", "索引", (313, 320)),
)

SPEC = BookSpec(
    book_id=BOOK_ID,
    pdf_path=pdf_path("ISBN978-4-87311-758-4.pdf"),
    sections=SECTIONS,
    output_root=Path("books") / BOOK_ID,
    image_output_dir=Path("books") / BOOK_ID / "images",
)
