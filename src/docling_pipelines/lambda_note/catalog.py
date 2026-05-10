from ..models import BookSpec
from .specs.isbn978_4_908686_06_1 import SPEC as ISBN978_4_908686_06_1
from .specs.isbn978_4_908686_16_0 import SPEC as ISBN978_4_908686_16_0


BOOKS: dict[str, BookSpec] = {
    ISBN978_4_908686_06_1.book_id: ISBN978_4_908686_06_1,
    "06-1": ISBN978_4_908686_06_1,
    ISBN978_4_908686_16_0.book_id: ISBN978_4_908686_16_0,
    "16-0": ISBN978_4_908686_16_0,
}


def get_book(value: str) -> BookSpec:
    try:
        return BOOKS[value]
    except KeyError as exc:
        valid_books = ", ".join(sorted(BOOKS))
        raise ValueError(f"Unknown book: {value}. Valid books: {valid_books}") from exc
