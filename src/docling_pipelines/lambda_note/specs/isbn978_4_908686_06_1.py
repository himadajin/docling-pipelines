from pathlib import Path

from ...models import BookSpec, Section
from ...paths import pdf_path


BOOK_ID = "978-4-908686-06-1"

SECTIONS: tuple[Section, ...] = (
    Section("frontmatter", "00-frontmatter.md", "表紙・前付け", (1, 8)),
    Section("toc", "01-toc.md", "目次", (9, 12)),
    Section("chapter-01", "02-chapter-01.md", "1章 イントロダクション", (13, 36)),
    Section("chapter-02", "03-chapter-02.md", "2章 配列を使ったリスト", (37, 66)),
    Section("chapter-03", "04-chapter-03.md", "3章 連結リスト", (67, 86)),
    Section("chapter-04", "05-chapter-04.md", "4章 スキップリスト", (87, 102)),
    Section("chapter-05", "06-chapter-05.md", "5章 ハッシュテーブル", (103, 124)),
    Section("chapter-06", "07-chapter-06.md", "6章 二分木", (125, 140)),
    Section("chapter-07", "08-chapter-07.md", "7章 ランダム二分探索木", (141, 158)),
    Section("chapter-08", "09-chapter-08.md", "8章 スケープゴート木", (159, 168)),
    Section("chapter-09", "10-chapter-09.md", "9章 赤黒木", (169, 190)),
    Section("chapter-10", "11-chapter-10.md", "10章 ヒープ", (191, 202)),
    Section("chapter-11", "12-chapter-11.md", "11章 整列アルゴリズム", (203, 222)),
    Section("chapter-12", "13-chapter-12.md", "12章 グラフ", (223, 236)),
    Section("chapter-13", "14-chapter-13.md", "13章 整数を扱うデータ構造", (237, 252)),
    Section("chapter-14", "15-chapter-14.md", "14章 外部メモリの探索", (253, 273)),
    Section("references", "16-references.md", "参考文献", (274, 279)),
    Section("index", "17-index.md", "索引", (280, 288)),
)

SPEC = BookSpec(
    book_id=BOOK_ID,
    pdf_path=pdf_path("ISBN978-4-908686-06-1.pdf"),
    sections=SECTIONS,
    output_root=Path("books") / BOOK_ID,
    image_output_dir=Path("books") / BOOK_ID / "images",
)
