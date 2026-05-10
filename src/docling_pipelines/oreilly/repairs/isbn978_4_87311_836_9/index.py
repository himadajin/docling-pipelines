from ....models import IndexEntry
from ..index_common import remove_duplicate_index_headings


def apply_known_index_repairs(entries: list[IndexEntry]) -> list[IndexEntry]:
    return remove_duplicate_index_headings(entries)
