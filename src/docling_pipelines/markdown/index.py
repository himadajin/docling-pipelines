import re
import shutil
import subprocess
import unicodedata
from dataclasses import dataclass
from html import unescape
from pathlib import Path

from ..models import IndexEntry, PendingIndexTermSplitter
from ..text_utils import repair_japanese_markdown_spacing, repair_japanese_spacing_in_line
INDEX_PAGE_TOKEN = r"(?:[ivxlcdm]+|\d+)"
INDEX_PAGE_RE = re.compile(rf"{INDEX_PAGE_TOKEN}(?:,\s*{INDEX_PAGE_TOKEN})*")
INDEX_HEADING_RE = re.compile(r"^(?:記号(?:・数字)?|[A-Z]|[あかさたなはまやらわ]行)$")
INDEX_ENTRY_RE = re.compile(
    rf"(.+?)\s+({INDEX_PAGE_TOKEN}(?:,\s*{INDEX_PAGE_TOKEN})*)(?=\s+(?!系\b)\S|$)",
    re.IGNORECASE,
)
INDEX_LEADER_RE = re.compile(r"[·・･.]{2,}")


@dataclass(frozen=True)
class IndexExtractionOptions:
    pending_term_splitter: PendingIndexTermSplitter | None = None


def normalize_index_text(text: object) -> str:
    normalized = unescape(str(text))
    normalized = re.sub(r"\\([_*])", r"\1", normalized)
    normalized = unicodedata.normalize("NFKC", normalized)
    normalized = INDEX_LEADER_RE.sub(" ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = repair_japanese_spacing_in_line(normalized)
    normalized = re.sub(r"（\s*class\s*）", "（class）", normalized)
    return normalized.strip()


def is_index_heading(text: str) -> bool:
    return INDEX_HEADING_RE.fullmatch(text) is not None


def normalize_index_heading(text: str) -> str:
    if text == "記号・数字":
        return "記号"
    return text


def index_column_groups(column_count: int) -> list[list[int]]:
    if column_count <= 2:
        return [[column] for column in range(column_count)]
    if column_count == 3:
        return [[0], [1, 2]]
    if column_count == 4:
        return [[0, 1], [2, 3]]

    return [[column] for column in range(column_count)]


def index_table_grid(table: object) -> list[list[str]]:
    data = getattr(table, "data", None)
    grid = getattr(data, "grid", None)
    if not grid:
        return []

    return [[getattr(cell, "text", "") for cell in row] for row in grid]


def split_index_entries(text: str) -> tuple[list[tuple[str, str]], str]:
    entries: list[tuple[str, str]] = []
    consumed_until = 0

    for match in INDEX_ENTRY_RE.finditer(text):
        term = match.group(1).strip()
        pages = match.group(2).strip()
        if term:
            entries.append((term, pages))
        consumed_until = match.end(2)

    remainder = text[consumed_until:].strip()
    return entries, remainder


def split_repeated_index_heading(text: str) -> str | None:
    parts = text.split()
    if len(parts) == 2 and parts[0] == parts[1] and is_index_heading(parts[0]):
        return parts[0]

    return None


def split_pending_index_terms(
    text: str,
    page_count: int,
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> list[str]:
    if page_count <= 1:
        return [text]

    if options.pending_term_splitter:
        known_terms = options.pending_term_splitter(text)
        if known_terms:
            return known_terms

    return [text]


def append_index_text_entries(
    rendered: list[IndexEntry],
    text: str,
    pending_terms: list[str],
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> list[str]:
    normalized = normalize_index_text(text)
    if not normalized:
        return pending_terms

    if is_index_heading(normalized):
        rendered.append(
            IndexEntry(heading=normalize_index_heading(normalized), term=None, pages=None)
        )
        return []

    repeated_heading = split_repeated_index_heading(normalized)
    if repeated_heading:
        rendered.append(IndexEntry(heading=repeated_heading, term=None, pages=None))
        return []

    heading_with_entry = re.match(
        r"^([あかさたなはまやらわ]行)\s+(.+)$",
        normalized,
    )
    if heading_with_entry:
        rendered.append(
            IndexEntry(heading=heading_with_entry.group(1), term=None, pages=None)
        )
        normalized = heading_with_entry.group(2)

    if INDEX_PAGE_RE.fullmatch(normalized):
        pages = [page.strip() for page in re.split(r"\s+", normalized) if page.strip()]
        terms = pending_terms
        if len(terms) == 1 and len(pages) > 1:
            terms = split_pending_index_terms(terms[0], len(pages), options)
        for term, page in zip(terms, pages, strict=False):
            rendered.append(IndexEntry(heading=None, term=term, pages=page))
        return terms[len(pages) :]

    entries, remainder = split_index_entries(normalized)
    for term, pages in entries:
        rendered.append(IndexEntry(heading=None, term=term, pages=pages))

    if remainder and not INDEX_PAGE_RE.fullmatch(remainder):
        return [*pending_terms, remainder]

    return pending_terms


def extract_index_entries_from_docling_tables(
    document: object,
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> list[IndexEntry]:
    rendered: list[IndexEntry] = []

    for table in getattr(document, "tables", []):
        grid = index_table_grid(table)
        if not grid:
            continue

        column_count = max((len(row) for row in grid), default=0)
        pending_terms: list[str] = []
        for group in index_column_groups(column_count):
            pending_terms = []
            for row in grid:
                text = " ".join(
                    row[column]
                    for column in group
                    if column < len(row) and row[column]
                )
                pending_terms = append_index_text_entries(
                    rendered,
                    text,
                    pending_terms,
                    options,
                )

    return rendered


def markdown_table_cells(line: str) -> list[str]:
    if not line.startswith("|"):
        return []

    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
        return []
    return cells


def markdown_index_column_groups(column_count: int) -> list[list[int]]:
    if column_count == 2:
        return [[0, 1]]
    if column_count == 3:
        return [[0], [1], [2]]
    if column_count == 4:
        return [[0, 1], [2, 3]]
    return [[column] for column in range(column_count)]


def append_index_table_rows(
    rendered: list[IndexEntry],
    rows: list[list[str]],
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> None:
    column_count = max((len(row) for row in rows), default=0)
    for group in markdown_index_column_groups(column_count):
        pending_terms: list[str] = []
        for row in rows:
            text = " ".join(
                row[column]
                for column in group
                if column < len(row) and row[column]
            )
            pending_terms = append_index_text_entries(
                rendered,
                text,
                pending_terms,
                options,
            )


def extract_index_entries_from_markdown(
    markdown: str,
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> list[IndexEntry]:
    rendered: list[IndexEntry] = []
    pending_terms: list[str] = []
    table_rows: list[list[str]] = []

    def flush_table() -> None:
        nonlocal pending_terms, table_rows
        if table_rows:
            append_index_table_rows(rendered, table_rows, options)
            table_rows = []
            pending_terms = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("## ● 著者紹介") or line.startswith("## Printed in Japan"):
            break

        cells = markdown_table_cells(line)
        if cells:
            table_rows.append(cells)
            continue

        flush_table()
        if not line or line.startswith("![Image]"):
            pending_terms = []
            continue
        if line.startswith("|") or re.fullmatch(r"[·・･.]+", line):
            continue

        line = line.removeprefix("##").strip()
        pending_terms = append_index_text_entries(
            rendered,
            line,
            pending_terms,
            options,
        )

    flush_table()
    return rendered


def extract_pdf_layout_text(
    pdf_path: Path,
    page_range: tuple[int, int],
) -> str | None:
    if shutil.which("pdftotext") is None:
        return None

    start, end = page_range
    result = subprocess.run(
        [
            "pdftotext",
            "-layout",
            "-f",
            str(start),
            "-l",
            str(end),
            str(pdf_path),
            "-",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    return result.stdout


def split_layout_columns(lines: list[str]) -> list[str]:
    entries: list[str] = []
    left: list[str] = []
    right: list[str] = []

    def flush_page() -> None:
        entries.extend(left)
        entries.extend(right)
        left.clear()
        right.clear()

    for line in lines:
        if "\f" in line:
            line = line.replace("\f", "")
            if line.strip():
                left.append(line)
            flush_page()
            continue

        if line.strip() and len(line) - len(line.lstrip(" ")) >= 35:
            right.append(line)
            continue

        split_at = layout_column_split_index(line)
        if split_at and line[:split_at].strip() and line[split_at:].strip():
            left.append(line[:split_at])
            right.append(line[split_at:])
        else:
            left.append(line)

    flush_page()
    return entries


def layout_column_split_index(line: str) -> int | None:
    candidates: list[tuple[int, int]] = []
    for match in re.finditer(r" {3,}", line.rstrip()):
        start, end = match.span()
        if 20 <= start <= 75:
            candidates.append((start, end))

    if not candidates:
        return None

    start, end = max(candidates, key=lambda span: span[1] - span[0])
    return (start + end) // 2


def append_layout_index_text_entries(
    rendered: list[IndexEntry],
    text: str,
    pending_terms: list[str],
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> list[str]:
    normalized = normalize_index_text(text)
    if pending_terms:
        entries, remainder = split_index_entries(normalized)
        if entries:
            term, pages = entries[0]
            rendered.append(
                IndexEntry(
                    heading=None,
                    term=f"{pending_terms[-1]} {term}",
                    pages=pages,
                )
            )
            for extra_term, extra_pages in entries[1:]:
                rendered.append(IndexEntry(heading=None, term=extra_term, pages=extra_pages))
            return append_index_text_entries(rendered, remainder, [], options)

    return append_index_text_entries(rendered, normalized, pending_terms, options)


def extract_index_entries_from_pdf_layout(
    pdf_path: Path,
    page_range: tuple[int, int],
    options: IndexExtractionOptions = IndexExtractionOptions(),
) -> list[IndexEntry]:
    layout_text = extract_pdf_layout_text(pdf_path, page_range)
    if not layout_text:
        return []

    rendered: list[IndexEntry] = []
    pending_terms: list[str] = []
    for page_text in layout_text.split("\f"):
        for raw_line in split_layout_columns(page_text.splitlines()):
            text = raw_line.strip()
            if not text:
                pending_terms = []
                continue
            if re.fullmatch(r"(?:\d+\s+)?索引(?:\s+\d+)?|\d+", text):
                continue

            pending_terms = append_layout_index_text_entries(
                rendered,
                text,
                pending_terms,
                options,
            )

    return rendered


def render_index_entries(entries: list[IndexEntry], fallback_markdown: str) -> str:
    lines = ["## 索引", ""]
    leading_images = re.findall(
        r"(?m)^!\[Image\]\([^)]+\)$",
        fallback_markdown.split("|", maxsplit=1)[0],
    )
    if leading_images:
        lines.extend(leading_images)
        lines.append("")

    for entry in entries:
        if entry.heading:
            lines.append(f"- **{entry.heading}**")
            continue

        if entry.term and entry.pages:
            lines.append(f"  - {entry.term} {entry.pages}")

    tail = ""
    tail_match = re.search(r"\n## ● 著者紹介\b.*", fallback_markdown, re.DOTALL)
    if tail_match:
        tail = "\n\n" + repair_japanese_markdown_spacing(tail_match.group(0).strip())

    return "\n".join(lines) + "\n" + tail


def format_index_markdown(
    entries: list[IndexEntry],
    fallback_markdown: str,
) -> str:
    if not entries:
        return fallback_markdown
    return render_index_entries(entries, fallback_markdown)
