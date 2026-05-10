from pathlib import Path
import re
import statistics
import unicodedata

import pypdfium2 as pdfium

from ....code.detection import (
    is_code_like_text,
    is_docling_code_label,
    normalize_python_prompt_indents,
)
from ....models import CodeRepair


PDF_CODE_X_PADDING = 1.0
PDF_CODE_Y_PADDING = 1.0
PDF_TEXT_CODE_Y_PADDING = 5.0
PDF_CODE_RIGHT_MARGIN = 35.0
PDF_LINE_Y_TOLERANCE = 3.0
PDF_MIN_CHAR_WIDTH = 2.0
PDF_MAX_CHAR_WIDTH = 8.0


def normalize_pdf_code_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip() for line in normalized.splitlines())
    return normalized.strip()


def text_bounds_overlap(
    left: float,
    bottom: float,
    right: float,
    top: float,
    bounds: tuple[float, float, float, float],
) -> bool:
    bound_left, bound_bottom, bound_right, bound_top = bounds
    return (
        right >= bound_left
        and left <= bound_right
        and top >= bound_bottom
        and bottom <= bound_top
    )


def group_pdf_chars_by_line(chars: list[dict[str, object]]) -> list[list[dict[str, object]]]:
    lines: list[dict[str, object]] = []

    for char in sorted(chars, key=lambda c: (-float(c["y"]), float(c["left"]))):
        for line in lines:
            if abs(float(line["y"]) - float(char["y"])) < PDF_LINE_Y_TOLERANCE:
                line_chars = line["chars"]
                assert isinstance(line_chars, list)
                line_chars.append(char)
                line["y"] = (
                    float(line["y"]) * (len(line_chars) - 1) + float(char["y"])
                ) / len(line_chars)
                break
        else:
            lines.append({"y": char["y"], "chars": [char]})

    lines.sort(key=lambda line: -float(line["y"]))
    return [
        sorted(line["chars"], key=lambda c: (float(c["left"]), int(c["index"])))
        for line in lines
    ]


def infer_pdf_code_char_width(lines: list[list[dict[str, object]]]) -> float | None:
    deltas: list[float] = []

    for line in lines:
        for left, right in zip(line, line[1:], strict=False):
            delta = float(right["left"]) - float(left["left"])
            if PDF_MIN_CHAR_WIDTH < delta < PDF_MAX_CHAR_WIDTH:
                deltas.append(delta)

    if not deltas:
        return None

    return statistics.median(deltas)


def pdf_code_line_indents(
    text_page: object,
    bounds: tuple[float, float, float, float],
) -> list[int]:
    chars: list[dict[str, object]] = []

    for index in range(text_page.count_chars()):
        char = text_page.get_text_range(index, 1)
        if not char or char in "\r\n" or char == " ":
            continue

        left, bottom, right, top = text_page.get_charbox(index)
        if not text_bounds_overlap(left, bottom, right, top, bounds):
            continue

        chars.append(
            {
                "index": index,
                "left": left,
                "y": (bottom + top) / 2,
            }
        )

    if not chars:
        return []

    lines = group_pdf_chars_by_line(chars)
    char_width = infer_pdf_code_char_width(lines)
    if char_width is None:
        return [0 for _ in lines]

    base_left = min(float(char["left"]) for line in lines for char in line)
    return [
        max(0, round((float(line[0]["left"]) - base_left) / char_width))
        for line in lines
        if line
    ]


def apply_pdf_code_indents(text: str, indents: list[int]) -> str:
    if not indents:
        return text

    lines = text.splitlines()
    nonempty_count = sum(1 for line in lines if line.strip())
    if nonempty_count > len(indents):
        return text

    repaired: list[str] = []
    indent_index = 0
    for line in lines:
        if not line.strip():
            repaired.append("")
            continue

        repaired.append(" " * indents[indent_index] + line.lstrip())
        indent_index += 1

    return "\n".join(repaired)


def normalized_fragment_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", "", normalized)


def item_page_and_bbox(item: object) -> tuple[int, object] | None:
    provenance = getattr(item, "prov", None)
    if not provenance:
        return None

    first_provenance = provenance[0]
    page_no = getattr(first_provenance, "page_no", None)
    bbox = getattr(first_provenance, "bbox", None)
    if page_no is None or bbox is None:
        return None

    return page_no, bbox


def extract_pdf_text_for_item(
    pdf_document: object,
    item: object,
) -> str | None:
    page_and_bbox = item_page_and_bbox(item)
    if page_and_bbox is None:
        return None

    page_no, bbox = page_and_bbox
    page = pdf_document[page_no - 1]
    text_page = page.get_textpage()
    try:
        page_width, _ = page.get_size()
        y_bottom_padding = (
            PDF_CODE_Y_PADDING
            if is_docling_code_label(getattr(item, "label", None))
            else PDF_TEXT_CODE_Y_PADDING
        )
        text = text_page.get_text_bounded(
            max(0.0, bbox.l - PDF_CODE_X_PADDING),
            max(0.0, bbox.b - y_bottom_padding),
            max(bbox.r + PDF_CODE_X_PADDING, page_width - PDF_CODE_RIGHT_MARGIN),
            bbox.t + PDF_CODE_Y_PADDING,
        )
        bounds = (
            max(0.0, bbox.l - PDF_CODE_X_PADDING),
            max(0.0, bbox.b - y_bottom_padding),
            max(bbox.r + PDF_CODE_X_PADDING, page_width - PDF_CODE_RIGHT_MARGIN),
            bbox.t + PDF_CODE_Y_PADDING,
        )
        text = apply_pdf_code_indents(text, pdf_code_line_indents(text_page, bounds))
    finally:
        text_page.close()
        page.close()

    normalized = normalize_pdf_code_text(text)
    if not normalized:
        return None

    return normalize_python_prompt_indents(normalized)


def bboxes_overlap_vertically(left: object, right: object) -> bool:
    return min(left.t, right.t) - max(left.b, right.b) >= -PDF_CODE_Y_PADDING


def is_redundant_code_fragment(item: object, repair: CodeRepair) -> bool:
    if getattr(item, "self_ref", None) == repair.item_ref:
        return False

    page_and_bbox = item_page_and_bbox(item)
    if page_and_bbox is None:
        return False

    page_no, bbox = page_and_bbox
    if page_no != repair.page_no:
        return False

    fragment = normalized_fragment_text(str(getattr(item, "text", "")))
    if not fragment:
        return False

    repaired_text = normalized_fragment_text(repair.text)
    if fragment not in repaired_text:
        return False

    if bboxes_overlap_vertically(bbox, repair.bbox):
        return bbox.l >= repair.bbox.l - PDF_CODE_X_PADDING

    return len(fragment) <= 80 and "。" not in fragment


def remove_redundant_code_fragments(document: object, repairs: list[CodeRepair]) -> None:
    if not repairs:
        return

    for item in getattr(document, "texts", []):
        current_text = str(getattr(item, "text", ""))
        if not current_text.strip():
            continue
        if is_code_like_text(current_text):
            continue

        if any(is_redundant_code_fragment(item, repair) for repair in repairs):
            item.text = ""


def apply_document_repairs(document: object, input_pdf: Path) -> None:
    pdf_document = pdfium.PdfDocument(str(input_pdf))
    repairs: list[CodeRepair] = []

    try:
        for item in getattr(document, "texts", []):
            current_text = str(getattr(item, "text", ""))
            if not (
                is_docling_code_label(getattr(item, "label", None))
                or is_code_like_text(current_text)
            ):
                continue

            pdf_text = extract_pdf_text_for_item(pdf_document, item)
            page_and_bbox = item_page_and_bbox(item)
            if pdf_text and page_and_bbox:
                item.text = pdf_text
                page_no, bbox = page_and_bbox
                repairs.append(
                    CodeRepair(
                        item_ref=getattr(item, "self_ref", None),
                        page_no=page_no,
                        bbox=bbox,
                        text=pdf_text,
                    )
                )

        remove_redundant_code_fragments(document, repairs)
    finally:
        pdf_document.close()
