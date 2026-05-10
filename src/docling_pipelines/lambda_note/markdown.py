import re
import unicodedata


MARKDOWN_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
WATERMARK_RE = re.compile(r"^\s*★(?:\s|$).*$")
RUNNING_CHAPTER_HEADER_RE = re.compile(r"^##\s+\d+\s+第\s*\d+\s*章\b.*$")


def is_cjk_radical_or_kangxi(char: str) -> bool:
    codepoint = ord(char)
    return 0x2E80 <= codepoint <= 0x2FFF


def normalize_cjk_radicals(text: str) -> str:
    return "".join(
        unicodedata.normalize("NFKC", char)
        if is_cjk_radical_or_kangxi(char)
        else char
        for char in text
    )


def polish_markdown(markdown: str) -> str:
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

        if WATERMARK_RE.match(content):
            continue

        if RUNNING_CHAPTER_HEADER_RE.match(content):
            continue

        lines.append(normalize_cjk_radicals(content) + line_ending)

    return "".join(lines)
