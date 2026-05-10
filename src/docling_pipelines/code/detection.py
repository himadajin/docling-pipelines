import html
import re

from ..text_utils import JAPANESE_TEXT_CHARS


CODE_PROMPT_RE = re.compile(r"^\s*(?:>>>|\.\.\.)")
ESCAPED_CODE_PROMPT_RE = re.compile(r"^\s*(?:&gt;&gt;&gt;|\.\.\.)")
CODE_START_RE = re.compile(
    r"^\s*(?:def|class|import|from|for|if|elif|else|while|return|print)\b"
)
COMMENT_CODE_START_RE = re.compile(r"^\s*#(?!#)")
JAPANESE_CHAR_RE = re.compile(f"[{JAPANESE_TEXT_CHARS}]")


def is_docling_code_label(label: object) -> bool:
    return getattr(label, "value", label) == "code"


def is_code_like_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    if ">>>" in stripped:
        return True

    return (
        CODE_START_RE.match(stripped) is not None
        or COMMENT_CODE_START_RE.match(stripped) is not None
    )


def is_code_line(line: str) -> bool:
    stripped = html.unescape(line).lstrip()
    return (
        CODE_PROMPT_RE.match(stripped) is not None
        or CODE_START_RE.match(stripped) is not None
        or COMMENT_CODE_START_RE.match(stripped) is not None
        or stripped.startswith(("$ ", "...", ">>>"))
    )


def starts_with_japanese_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    first_char = stripped[0]
    return JAPANESE_CHAR_RE.match(first_char) is not None


def normalize_python_prompt_indents(text: str) -> str:
    return re.sub(
        r"(?m)^(\s*\.\.\.) (?!else:|elif\b|except\b|finally:)(\S)",
        r"\1     \2",
        text,
    )


def is_markdown_code_like_block(block: list[str]) -> bool:
    if not block:
        return False

    first_nonempty = next((line for line in block if line.strip()), "")
    if ESCAPED_CODE_PROMPT_RE.match(first_nonempty) or CODE_PROMPT_RE.match(
        first_nonempty
    ):
        return True
    if any(
        ESCAPED_CODE_PROMPT_RE.match(line) or CODE_PROMPT_RE.match(line)
        for line in block
    ):
        return True

    if (
        len(block) == 1
        and (
            CODE_START_RE.match(first_nonempty)
            or COMMENT_CODE_START_RE.match(first_nonempty)
            or first_nonempty.lstrip().startswith("$ ")
        )
        and any(token in first_nonempty for token in ("(", "=", "[", "]", "."))
    ):
        return True

    if not (
        CODE_START_RE.match(first_nonempty)
        or COMMENT_CODE_START_RE.match(first_nonempty)
        or first_nonempty.lstrip().startswith("$ ")
    ):
        return False

    codeish_lines = sum(
        1
        for line in block
        if (
            is_code_line(line)
            or line.startswith(("    ", "\t"))
            or any(token in line for token in ("=", "(", ")", "[", "]", ".", ":"))
        )
    )
    return len(block) >= 2 and codeish_lines >= 2


def is_prose_line_inside_code(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    if is_code_line(line):
        return False

    return starts_with_japanese_text(stripped)
