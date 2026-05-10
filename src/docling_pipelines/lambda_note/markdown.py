import re
import unicodedata


MARKDOWN_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
WATERMARK_RE = re.compile(r"^\s*★(?:\s|$).*$")
RUNNING_CHAPTER_HEADER_RE = re.compile(r"^##\s+\d+\s+第\s*\d+\s*章\b.*$")
LEADING_GLYPH_LIST_RE = re.compile(
    r"^(?P<indent>\s*)-\s+glyph\[(?P<glyph>a114|a113)\]\s*(?P<rest>.*)$"
)
HEADING_GLYPH_LIST_RE = re.compile(
    r"^##\s+glyph\[(?P<glyph>a114|a113)\]\s*(?P<rest>.*)$"
)
INLINE_GLYPH_MARKER_RE = re.compile(r"\s+glyph\[(a114|a113)\]\s+")
COMMAND_FRAME_RE = re.compile(
    r"^(?:##\s+)?(?P<command>\$\s+.*?)\s*"
    r"✂\s*(?:✁\s*)?✄\s*(?:glyph\[a0\]\s*)?✛\s*(?P<output>.*)$"
)
CODE_LISTING_HEADING_RE = re.compile(r"^##\s+(リスト\s+\d+(?:\.\d+)?\s*[：:].*)$")
COMMAND_FRAME_MARKER_RE = re.compile(r"^(?:glyph\[a0\]|✁|✂\s*✁\s*✄\s*glyph\[a0\]\s*✛)$")


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


def glyph_list_prefix(glyph: str) -> str:
    return "  - " if glyph == "a113" else "- "


def split_inline_glyph_list_markers(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return "\n" + glyph_list_prefix(match.group(1))

    return INLINE_GLYPH_MARKER_RE.sub(replace, text)


def repair_glyph_list_markers(line: str) -> str:
    match = LEADING_GLYPH_LIST_RE.match(line)
    if match:
        prefix = match.group("indent") + glyph_list_prefix(match.group("glyph"))
        return prefix + split_inline_glyph_list_markers(match.group("rest"))

    match = HEADING_GLYPH_LIST_RE.match(line)
    if match:
        return glyph_list_prefix(match.group("glyph")) + split_inline_glyph_list_markers(
            match.group("rest")
        )

    return line


def unescape_markdown_code_text(text: str) -> str:
    return text.replace(r"\_", "_")


def render_console_block(command: str, output: str) -> str:
    lines = ["```console", unescape_markdown_code_text(command.strip())]
    if output:
        lines.append(unescape_markdown_code_text(output.strip()))
    lines.append("```")
    return "\n".join(lines)


def repair_command_frame(line: str) -> str | None:
    if COMMAND_FRAME_MARKER_RE.match(line.strip()):
        return None

    match = COMMAND_FRAME_RE.match(line)
    if match:
        return render_console_block(match.group("command"), match.group("output"))

    return line


def repair_code_listing_heading(line: str) -> str:
    match = CODE_LISTING_HEADING_RE.match(line)
    if match:
        return f"**{match.group(1)}**"
    return line


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

        content = repair_glyph_list_markers(content)
        content = repair_command_frame(content)
        if content is None:
            continue
        content = repair_code_listing_heading(content)
        content = normalize_cjk_radicals(content)
        lines.append(content + line_ending)

    return "".join(lines)
