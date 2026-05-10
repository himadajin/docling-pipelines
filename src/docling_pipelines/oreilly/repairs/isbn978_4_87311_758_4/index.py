from ....models import IndexEntry
from ..index_common import (
    insert_index_entry_after,
    insert_index_heading_before,
    remove_duplicate_index_headings,
    remove_index_terms,
    replace_index_entry,
)


KNOWN_PENDING_INDEX_SPLITS = {
    "Data Augmentation DCGAN": ["Data Augmentation", "DCGAN"],
    "Momentum （class": ["Momentum （class"],
    "） MulLayer （class）": ["MulLayer （class）"],
    "画像キャプション生成 出力層": ["画像キャプション生成", "出力層"],
}


def split_known_pending_index_terms(text: str) -> list[str] | None:
    return KNOWN_PENDING_INDEX_SPLITS.get(text)


def apply_known_index_repairs(entries: list[IndexEntry]) -> list[IndexEntry]:
    # The index is a dense two-column layout. Docling occasionally merges an
    # adjacent term/page pair into one cell; keep those PDF-specific repairs here.
    entries = insert_index_entry_after(
        entries,
        "__init__",
        IndexEntry(heading=None, term="2乗和誤差", pages="88"),
    )
    entries = remove_index_terms(entries, {"245", "245 267"})
    entries = replace_index_entry(
        entries,
        "Data Augmentation DCGAN",
        [
            IndexEntry(heading=None, term="Data Augmentation", pages="245"),
            IndexEntry(heading=None, term="DCGAN", pages="267"),
        ],
    )
    entries = remove_index_terms(entries, {"Data Augmentation", "DCGAN"})
    entries = replace_index_entry(
        entries,
        "Deep Belief Network",
        [
            IndexEntry(heading=None, term="Data Augmentation", pages="245"),
            IndexEntry(heading=None, term="DCGAN", pages="267"),
            IndexEntry(heading=None, term="Deep Belief Network", pages="268"),
        ],
    )
    entries = replace_index_entry(
        entries,
        "Deep Q-Network DQN",
        [
            IndexEntry(heading=None, term="Deep Q-Network", pages="269"),
            IndexEntry(heading=None, term="DQN", pages="270"),
        ],
    )
    entries = replace_index_entry(
        entries,
        "Dropout dtype",
        [
            IndexEntry(heading=None, term="Dropout", pages="195"),
            IndexEntry(heading=None, term="dtype", pages="13"),
        ],
    )
    entries = insert_index_heading_before(entries, "K", "KNN")
    entries = insert_index_heading_before(entries, "M", "Matplotlib")
    entries = insert_index_heading_before(entries, "N", "nan")
    entries = replace_index_entry(
        entries,
        "Momentum ( class",
        [IndexEntry(heading=None, term="Momentum（class）", pages="171")],
    )
    entries = replace_index_entry(
        entries,
        ") MulLayer ( class )",
        [IndexEntry(heading=None, term="MulLayer（class）", pages="137")],
    )
    entries = replace_index_entry(
        entries,
        "np.array np.dot()",
        [
            IndexEntry(heading=None, term="np.array", pages="12"),
            IndexEntry(heading=None, term="np.dot()", pages="55"),
        ],
    )
    entries = insert_index_entry_after(
        entries,
        "plt.title()",
        IndexEntry(heading=None, term="plt.xlabel()", pages="18"),
    )
    entries = insert_index_entry_after(
        entries,
        "Python 2 系",
        IndexEntry(heading=None, term="Python 3 系", pages="2"),
    )
    entries = replace_index_entry(
        entries,
        "relu() Relu ( class )",
        [
            IndexEntry(heading=None, term="relu()", pages="52"),
            IndexEntry(heading=None, term="Relu（class）", pages="142"),
        ],
    )
    entries = insert_index_heading_before(entries, "W", "Weight decay")
    entries = replace_index_entry(
        entries,
        "264 画像スタイル変換",
        [
            IndexEntry(heading=None, term="画像キャプション生成", pages="264"),
            IndexEntry(heading=None, term="画像スタイル変換", pages="266"),
        ],
    )
    entries = insert_index_heading_before(entries, "さ行", "再学習")
    entries = insert_index_heading_before(entries, "ま行", "丸め誤差")
    entries = replace_index_entry(
        entries,
        "ら行ランダムサンプリング",
        [
            IndexEntry(heading="ら行", term=None, pages=None),
            IndexEntry(heading=None, term="ランダムサンプリング", pages="200"),
        ],
    )
    return remove_duplicate_index_headings(entries)
