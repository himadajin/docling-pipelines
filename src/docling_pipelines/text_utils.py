import re


MARKDOWN_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
JAPANESE_TEXT_CHARS = (
    r"\u3040-\u30ff"
    r"\u3400-\u4dbf"
    r"\u4e00-\u9fff"
    r"\uf900-\ufaff"
    r"\u2e80-\u2fdf"
    r"々〆〤"
)
JAPANESE_INTERNAL_SPACE_RE = re.compile(
    rf"([{JAPANESE_TEXT_CHARS}]) +([{JAPANESE_TEXT_CHARS}])"
)
SPACE_BEFORE_JAPANESE_PUNCT_RE = re.compile(
    rf"([{JAPANESE_TEXT_CHARS}A-Za-z0-9）】』」]) +([。、，．！？：；）】』」])"
)
SPACE_AFTER_JAPANESE_PUNCT_RE = re.compile(r"([。、，．！？：；]) +(\S)")
SPACE_AFTER_JAPANESE_OPEN_BRACKET_RE = re.compile(r"([（「『【]) +")
SPACE_BEFORE_JAPANESE_CLOSE_BRACKET_RE = re.compile(r" +([）】』」])")


def repair_japanese_spacing_in_line(line: str) -> str:
    while True:
        repaired = JAPANESE_INTERNAL_SPACE_RE.sub(r"\1\2", line)
        repaired = SPACE_BEFORE_JAPANESE_PUNCT_RE.sub(r"\1\2", repaired)
        repaired = SPACE_AFTER_JAPANESE_PUNCT_RE.sub(r"\1\2", repaired)
        repaired = SPACE_AFTER_JAPANESE_OPEN_BRACKET_RE.sub(r"\1", repaired)
        repaired = SPACE_BEFORE_JAPANESE_CLOSE_BRACKET_RE.sub(r"\1", repaired)

        if repaired == line:
            return repaired
        line = repaired


def repair_japanese_markdown_spacing(markdown: str) -> str:
    lines: list[str] = []
    inside_fenced_code = False

    for line in markdown.splitlines(keepends=True):
        content = line.removesuffix("\n")
        line_ending = "\n" if line.endswith("\n") else ""

        if MARKDOWN_FENCE_RE.match(content):
            inside_fenced_code = not inside_fenced_code
            lines.append(line)
            continue

        if inside_fenced_code:
            lines.append(line)
            continue

        lines.append(repair_japanese_spacing_in_line(content) + line_ending)

    return "".join(lines)
