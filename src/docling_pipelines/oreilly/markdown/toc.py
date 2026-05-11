import re
import unicodedata

from ...models import TocEntry
PAGE_TOKEN_RE = re.compile(r"(?:[ivxlcdm]+|\d+)", re.IGNORECASE)
SECTION_NUMBER_RE = re.compile(r"(?:\d+(?:\.\d+)+|[A-Z](?:\.\d+)?)")
CHAPTER_NUMBER_RE = re.compile(r"(\d+)\s*章")
APPENDIX_NUMBER_RE = re.compile(r"付録\s+[A-Z]")


def normalize_toc_text(text: object) -> str:
    normalized = unicodedata.normalize("NFKC", str(text))
    normalized = re.sub(r"[·・･.]{3,}", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def strip_trailing_page(text: str, page: str | None) -> str:
    if page is None:
        return text

    return re.sub(rf"\s+{re.escape(page)}$", "", text).strip()


def page_from_cell(cell: str) -> str | None:
    if PAGE_TOKEN_RE.fullmatch(cell):
        return cell

    match = re.search(r"\s+([ivxlcdm]+|\d+)$", cell, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def find_toc_page(cells: list[str]) -> str | None:
    for cell in reversed(cells):
        page = page_from_cell(cell)
        if page:
            return page

    return None


def split_toc_number(cell: str) -> tuple[str | None, str]:
    chapter_match = re.fullmatch(r"(\d+)\s*章", cell)
    if chapter_match:
        return f"{chapter_match.group(1)}章", ""

    if SECTION_NUMBER_RE.fullmatch(cell):
        return cell, ""

    appendix_match = re.match(r"^(付録\s+[A-Z])\s*(.*)$", cell)
    if appendix_match:
        return appendix_match.group(1), appendix_match.group(2)

    chapter_with_title = re.match(r"^(\d+)\s*章\s+(.+)$", cell)
    if chapter_with_title:
        return f"{chapter_with_title.group(1)}章", chapter_with_title.group(2)

    section_with_title = re.match(rf"^({SECTION_NUMBER_RE.pattern})\s+(.+)$", cell)
    if section_with_title:
        return section_with_title.group(1), section_with_title.group(2)

    return None, cell


def is_toc_page_header(cells: list[str]) -> bool:
    return len(cells) == 1 and PAGE_TOKEN_RE.fullmatch(cells[0]) is not None


def clean_toc_title_candidate(
    cell: str,
    number: str | None,
    page: str | None,
) -> str:
    title = strip_trailing_page(cell, page)

    if number:
        loose_number = re.escape(number).replace("章", r"\s*章")
        title = re.sub(rf"^{loose_number}\s+", "", title).strip()

    _, remainder = split_toc_number(title)
    return remainder.strip()


def build_toc_entry(
    raw_cells: list[object],
    next_chapter_number: int,
) -> tuple[TocEntry | None, int]:
    cells = [normalize_toc_text(cell) for cell in raw_cells]
    cells = [cell for cell in cells if cell and cell.lower() != "nan"]

    if not cells or is_toc_page_header(cells):
        return None, next_chapter_number

    page = find_toc_page(cells)
    number: str | None = None
    title_from_number = ""
    number_cell_index: int | None = None

    for index, cell in enumerate(cells):
        if cell == "章":
            number = f"{next_chapter_number}章"
            number_cell_index = index
            break

        cell_number, remainder = split_toc_number(strip_trailing_page(cell, page))
        if cell_number:
            number = cell_number
            title_from_number = remainder
            number_cell_index = index
            break

    title_candidates: list[str] = []
    if title_from_number:
        title_candidates.append(strip_trailing_page(title_from_number, page))

    for index, cell in enumerate(cells):
        if index == number_cell_index:
            continue
        if page and cell == page:
            continue

        title = clean_toc_title_candidate(cell, number, page)
        if title:
            title_candidates.append(title)

    if not number and not title_candidates:
        return None, next_chapter_number

    unique_titles = list(dict.fromkeys(title_candidates))
    title = min(unique_titles, key=len) if unique_titles else ""
    title = strip_trailing_page(title, page)

    if not title:
        return None, next_chapter_number

    if number and CHAPTER_NUMBER_RE.fullmatch(number):
        next_chapter_number = int(number.removesuffix("章")) + 1

    return TocEntry(number=number, title=title, page=page), next_chapter_number


def toc_entry_indent(entry: TocEntry, inside_references: bool) -> int:
    if entry.number:
        if CHAPTER_NUMBER_RE.fullmatch(entry.number) or APPENDIX_NUMBER_RE.fullmatch(
            entry.number
        ):
            return 0
        return min(entry.number.count("."), 2)

    if entry.title in {"まえがき", "参考文献", "索引"}:
        return 0
    if inside_references:
        return 1
    return 0


def render_toc_markdown(entries: list[TocEntry]) -> str:
    lines = ["## 目次", ""]
    inside_references = False

    for entry in entries:
        indent = toc_entry_indent(entry, inside_references)
        text = f"{entry.number} {entry.title}" if entry.number else entry.title

        if indent == 0:
            text = f"**{text}**"

        if entry.page:
            text = f"{text} {entry.page}"

        lines.append(f"{'  ' * indent}- {text}")

        if entry.title == "参考文献":
            inside_references = True
        elif entry.title == "索引" or entry.number:
            inside_references = False

    return "\n".join(lines) + "\n"


def extract_toc_entries(document: object) -> list[TocEntry]:
    entries: list[TocEntry] = []
    next_chapter_number = 1

    for table in getattr(document, "tables", []):
        dataframe = table.export_to_dataframe(doc=document)
        for row in dataframe.itertuples(index=False, name=None):
            entry, next_chapter_number = build_toc_entry(
                list(row),
                next_chapter_number,
            )
            if entry:
                entries.append(entry)

    return entries


def format_toc_markdown(document: object, fallback_markdown: str) -> str:
    entries = extract_toc_entries(document)
    if not entries:
        return fallback_markdown
    return render_toc_markdown(entries)
