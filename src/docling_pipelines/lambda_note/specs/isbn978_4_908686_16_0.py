from pathlib import Path

from ...models import BookSpec, Section
from ...paths import pdf_path


BOOK_ID = "978-4-908686-16-0"

SECTIONS: tuple[Section, ...] = (
    Section("frontmatter", "00-frontmatter.md", "表紙・前付け", (1, 6)),
    Section("toc", "01-toc.md", "目次", (7, 12)),
    Section(
        "chapter-01",
        "02-chapter-01.md",
        "1章 CPU は如何にしてソフトウェアを高速に実行するのか",
        (13, 22),
    ),
    Section("chapter-02", "03-chapter-02.md", "2章 命令の密度を上げるさまざまな工夫", (23, 38)),
    Section("chapter-03", "04-chapter-03.md", "3章 データ依存関係", (39, 56)),
    Section("chapter-04", "05-chapter-04.md", "4章 分岐命令", (57, 76)),
    Section("chapter-05", "06-chapter-05.md", "5章 キャッシュメモリ", (77, 98)),
    Section("chapter-06", "07-chapter-06.md", "6章 仮想記憶", (99, 112)),
    Section("chapter-07", "08-chapter-07.md", "7章 I/O", (113, 130)),
    Section("chapter-08", "09-chapter-08.md", "8章 システムコール、例外、割り込み", (131, 152)),
    Section("chapter-09", "10-chapter-09.md", "9章 マルチプロセッサ", (153, 168)),
    Section("chapter-10", "11-chapter-10.md", "10章 キャッシュコヒーレンス制御", (169, 188)),
    Section("chapter-11", "12-chapter-11.md", "11章 メモリ順序付け", (189, 214)),
    Section("chapter-12", "13-chapter-12.md", "12章 不可分操作", (215, 242)),
    Section("chapter-13", "14-chapter-13.md", "13章 高速なソフトウェアを書く際には何に注目すべきか", (243, 248)),
    Section("appendix-a", "15-appendix-a.md", "付録 A", (249, 258)),
    Section("appendix-b", "16-appendix-b.md", "付録 B", (259, 268)),
    Section("appendix-c", "17-appendix-c.md", "付録 C", (269, 274)),
    Section("appendix-d", "18-appendix-d.md", "付録 D", (275, 280)),
    Section("appendix-e", "19-appendix-e.md", "付録 E", (281, 286)),
    Section("appendix-f", "20-appendix-f.md", "付録 F", (287, 292)),
    Section("afterword", "21-afterword.md", "あとがき", (293, 294)),
    Section("references", "22-references.md", "参考文献", (295, 300)),
    Section("index", "23-index.md", "索引", (301, 312)),
)

SPEC = BookSpec(
    book_id=BOOK_ID,
    pdf_path=pdf_path("ISBN978-4-908686-16-0.pdf"),
    sections=SECTIONS,
    output_root=Path("books") / BOOK_ID,
    image_output_dir=Path("books") / BOOK_ID / "images",
)
