from pathlib import Path

from ...models import BookSpec, Section
from ...paths import pdf_path


BOOK_ID = "978-4-87311-906-9"

SECTIONS: tuple[Section, ...] = (
    Section("frontmatter", "00-frontmatter.md", "表紙・奥付", (1, 2)),
    Section("preface", "01-preface.md", "まえがき", (3, 10)),
    Section("toc", "02-toc.md", "目次", (11, 22)),
    Section("stage-01", "03-stage-01.md", "第1ステージ 微分を自動で求める", (23, 88)),
    Section("stage-02", "04-stage-02.md", "第2ステージ 自然なコードで表現する", (89, 200)),
    Section("stage-03", "05-stage-03.md", "第3ステージ 高階微分を実現する", (201, 288)),
    Section("stage-04", "06-stage-04.md", "第4ステージ ニューラルネットワークを作る", (289, 430)),
    Section("stage-05", "07-stage-05.md", "第5ステージ DeZero で挑む", (431, 522)),
    Section("appendix-a", "08-appendix-a.md", "付録 A", (523, 526)),
    Section("appendix-b", "09-appendix-b.md", "付録 B", (527, 530)),
    Section("appendix-c", "10-appendix-c.md", "付録 C", (531, 534)),
    Section("afterword", "11-afterword.md", "おわりに", (535, 538)),
    Section("references", "12-references.md", "参考文献", (539, 542)),
    Section("index", "13-index.md", "索引", (543, 552)),
)

SPEC = BookSpec(
    book_id=BOOK_ID,
    pdf_path=pdf_path("ISBN978-4-87311-906-9.pdf"),
    sections=SECTIONS,
    output_root=Path("books") / BOOK_ID,
    image_output_dir=Path("books") / BOOK_ID / "images",
)
