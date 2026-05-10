from ...models import IndexEntry


def replace_index_entry(
    entries: list[IndexEntry],
    term: str,
    replacement: list[IndexEntry],
) -> list[IndexEntry]:
    replaced: list[IndexEntry] = []
    for entry in entries:
        if entry.term == term:
            replaced.extend(replacement)
        else:
            replaced.append(entry)

    return replaced


def insert_index_heading_before(
    entries: list[IndexEntry],
    heading: str,
    term: str,
) -> list[IndexEntry]:
    inserted: list[IndexEntry] = []
    done = False

    for entry in entries:
        if not done and entry.term == term:
            inserted.append(IndexEntry(heading=heading, term=None, pages=None))
            done = True
        inserted.append(entry)

    return inserted


def insert_index_entry_after(
    entries: list[IndexEntry],
    anchor_term: str,
    entry_to_insert: IndexEntry,
) -> list[IndexEntry]:
    inserted: list[IndexEntry] = []
    done = False

    for entry in entries:
        inserted.append(entry)
        if not done and entry.term == anchor_term:
            inserted.append(entry_to_insert)
            done = True

    return inserted


def remove_index_terms(entries: list[IndexEntry], terms: set[str]) -> list[IndexEntry]:
    return [entry for entry in entries if entry.term not in terms]


def remove_duplicate_index_headings(entries: list[IndexEntry]) -> list[IndexEntry]:
    deduped: list[IndexEntry] = []
    previous_heading: str | None = None

    for entry in entries:
        if entry.heading:
            if entry.heading == previous_heading:
                continue
            previous_heading = entry.heading
        elif entry.term:
            previous_heading = None
        deduped.append(entry)

    return deduped
