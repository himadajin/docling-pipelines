import html
import re

from ..text_utils import MARKDOWN_FENCE_RE
from .detection import is_markdown_code_like_block, is_prose_line_inside_code

BARE_CODE_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(\s*)$")
SHELL_PROMPT_RE = re.compile(r"^\s*\$ ")
PYTHON_PROMPT_RE = re.compile(r"^\s*(?:>>>|\.\.\.)")
PYTHON_START_RE = re.compile(
    r"^\s*(?:def|class|import|from|for|if|elif|else|while|return|print|with|try|except)\b"
)
PYTHON_ASSIGNMENT_RE = re.compile(r"^\s*[A-Za-z_][\w.]*\s*=")
PYTHON_CALL_RE = re.compile(r"^\s*[A-Za-z_][\w.]*\(")
PYTHON_OBJECT_RE = re.compile(r"\b(?:np|plt|self)\.")


def render_code_like_markdown_block(block: list[str]) -> list[str]:
    return ["```", *[html.unescape(line) for line in block], "```"]


def fence_code_like_markdown_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    repaired: list[str] = []
    paragraph: list[str] = []
    inside_fenced_code = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if is_markdown_code_like_block(paragraph):
            repaired.extend(render_code_like_markdown_block(paragraph))
        else:
            repaired.extend(paragraph)
        paragraph = []

    for line in lines:
        if MARKDOWN_FENCE_RE.match(line):
            flush_paragraph()
            inside_fenced_code = not inside_fenced_code
            repaired.append(line)
            continue

        if inside_fenced_code:
            repaired.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            repaired.append(line)
            continue

        paragraph.append(line)

    flush_paragraph()
    trailing_newline = "\n" if markdown.endswith("\n") else ""
    return "\n".join(repaired) + trailing_newline


def remove_empty_fenced_code_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    repaired: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if not MARKDOWN_FENCE_RE.match(line):
            repaired.append(line)
            index += 1
            continue

        end_index = index + 1
        while end_index < len(lines) and not MARKDOWN_FENCE_RE.match(lines[end_index]):
            end_index += 1

        if end_index < len(lines):
            content = lines[index + 1 : end_index]
            if not any(content_line.strip() for content_line in content):
                index = end_index + 1
                continue

            repaired.extend(lines[index : end_index + 1])
            index = end_index + 1
            continue

        repaired.append(line)
        index += 1

    trailing_newline = "\n" if markdown.endswith("\n") else ""
    return "\n".join(repaired) + trailing_newline


def split_mixed_fenced_code_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    repaired: list[str] = []
    index = 0

    def append_code_run(run: list[str]) -> None:
        if not run:
            return
        repaired.append("```")
        repaired.extend(run)
        repaired.append("```")

    while index < len(lines):
        line = lines[index]
        if not MARKDOWN_FENCE_RE.match(line):
            repaired.append(line)
            index += 1
            continue

        end_index = index + 1
        while end_index < len(lines) and not MARKDOWN_FENCE_RE.match(lines[end_index]):
            end_index += 1

        if end_index >= len(lines):
            repaired.append(line)
            index += 1
            continue

        content = lines[index + 1 : end_index]
        if not content:
            index = end_index + 1
            continue

        if all(
            (not content_line.strip()) or is_prose_line_inside_code(content_line)
            for content_line in content
        ):
            repaired.extend(content)
            index = end_index + 1
            continue

        if not any(is_prose_line_inside_code(content_line) for content_line in content):
            repaired.extend(lines[index : end_index + 1])
            index = end_index + 1
            continue

        code_run: list[str] = []
        for content_line in content:
            if is_prose_line_inside_code(content_line):
                append_code_run(code_run)
                code_run = []
                repaired.append(content_line)
                continue

            if content_line.strip() or code_run:
                code_run.append(content_line)

        append_code_run(code_run)
        index = end_index + 1

    trailing_newline = "\n" if markdown.endswith("\n") else ""
    return "\n".join(repaired) + trailing_newline


def is_python_markdown_code_block(content: list[str]) -> bool:
    nonempty = [line for line in content if line.strip()]
    if not nonempty:
        return False

    first_nonempty = nonempty[0]
    if SHELL_PROMPT_RE.match(first_nonempty):
        return False

    if any(line.lstrip().startswith(">>>") for line in nonempty):
        return True

    pythonish_lines = 0
    for line in nonempty:
        unescaped = html.unescape(line)
        if (
            PYTHON_START_RE.match(unescaped)
            or PYTHON_ASSIGNMENT_RE.match(unescaped)
            or PYTHON_CALL_RE.match(unescaped)
            or PYTHON_OBJECT_RE.search(unescaped)
            or PYTHON_PROMPT_RE.match(unescaped)
        ):
            pythonish_lines += 1

    if PYTHON_START_RE.match(html.unescape(first_nonempty)):
        return True

    return pythonish_lines >= 2


def annotate_python_fenced_code_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    repaired: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        opening_match = BARE_CODE_FENCE_RE.match(line)
        if not opening_match:
            repaired.append(line)
            index += 1
            continue

        fence = opening_match.group(2)
        end_index = index + 1
        while end_index < len(lines):
            closing_match = BARE_CODE_FENCE_RE.match(lines[end_index])
            closing_fence = closing_match.group(2) if closing_match else ""
            if closing_fence.startswith(fence[0]) and len(closing_fence) >= len(fence):
                break
            end_index += 1

        if end_index >= len(lines):
            repaired.append(line)
            index += 1
            continue

        content = lines[index + 1 : end_index]
        if is_python_markdown_code_block(content):
            repaired.append(f"{opening_match.group(1)}{fence}python")
        else:
            repaired.append(line)
        repaired.extend(content)
        repaired.append(lines[end_index])
        index = end_index + 1

    trailing_newline = "\n" if markdown.endswith("\n") else ""
    return "\n".join(repaired) + trailing_newline
