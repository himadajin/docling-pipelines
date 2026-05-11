import re

from ...code.markdown_blocks import (
    annotate_python_fenced_code_blocks,
    fence_code_like_markdown_blocks,
    remove_empty_fenced_code_blocks,
    split_mixed_fenced_code_blocks,
)
from ...models import ConversionConfig, MarkdownRepair
from ...text_utils import repair_japanese_markdown_spacing


def polish_markdown(
    markdown: str,
    config: ConversionConfig,
    markdown_repairs: tuple[MarkdownRepair, ...] = (),
) -> str:
    if config.apply_markdown_spacing:
        markdown = repair_japanese_markdown_spacing(markdown)
    markdown = repair_markdown_heading_spacing(markdown)
    markdown = trim_markdown_table_cell_padding(markdown)
    markdown = fence_code_like_markdown_blocks(markdown)
    markdown = split_mixed_fenced_code_blocks(markdown)
    for repair in markdown_repairs:
        markdown = repair(markdown)
    markdown = remove_empty_fenced_code_blocks(markdown)
    return annotate_python_fenced_code_blocks(markdown)


def repair_markdown_heading_spacing(markdown: str) -> str:
    return re.sub(r"(?m)^(#{1,6}) +([）】』」])$", r"\1\2", markdown)


def trim_markdown_table_cell_padding(markdown: str) -> str:
    lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        content = line.removesuffix("\n")
        line_ending = "\n" if line.endswith("\n") else ""
        if content.startswith("|"):
            content = re.sub(r"([。、，．！？：；）】』」]) +\|", r"\1|", content)
        lines.append(content + line_ending)

    return "".join(lines)
