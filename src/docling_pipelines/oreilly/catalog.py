from ..models import BookSpec
from .specs.isbn978_4_87311_758_4 import SPEC as ISBN978_4_87311_758_4
from .specs.isbn978_4_87311_836_9 import SPEC as ISBN978_4_87311_836_9
from .specs.isbn978_4_87311_906_9 import SPEC as ISBN978_4_87311_906_9


BOOKS: dict[str, BookSpec] = {
    ISBN978_4_87311_758_4.book_id: ISBN978_4_87311_758_4,
    "758-4": ISBN978_4_87311_758_4,
    ISBN978_4_87311_836_9.book_id: ISBN978_4_87311_836_9,
    "836-9": ISBN978_4_87311_836_9,
    ISBN978_4_87311_906_9.book_id: ISBN978_4_87311_906_9,
    "906-9": ISBN978_4_87311_906_9,
}


def get_book(value: str) -> BookSpec:
    try:
        return BOOKS[value]
    except KeyError as exc:
        valid_books = ", ".join(sorted(BOOKS))
        raise ValueError(f"Unknown book: {value}. Valid books: {valid_books}") from exc
