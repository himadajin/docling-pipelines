import re
import unicodedata


MARKDOWN_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
WATERMARK_RE = re.compile(r"^\s*★(?:\s|$).*$")
RUNNING_CHAPTER_HEADER_RE = re.compile(r"^##\s+\d+\s+第\s*\d+\s*章\b.*$")
JAPANESE_TEXT_CHARS = (
    r"\u3040-\u30ff"
    r"\u3400-\u4dbf"
    r"\u4e00-\u9fff"
    r"\uf900-\ufaff"
    r"\u2e80-\u2fff"
    r"々〆〤"
)
JAPANESE_INTERNAL_SPACE_RE = re.compile(
    rf"([{JAPANESE_TEXT_CHARS}]) +([{JAPANESE_TEXT_CHARS}])"
)
SPACE_BEFORE_JAPANESE_PUNCT_RE = re.compile(
    rf"([{JAPANESE_TEXT_CHARS}A-Za-z0-9）】』」]) +([。、，．！？；）】』」])"
)
SPACE_AFTER_JAPANESE_PUNCT_RE = re.compile(r"([。、，．！？；]) +(\S)")
SPACE_AFTER_JAPANESE_OPEN_BRACKET_RE = re.compile(r"([（「『【]) +")
SPACE_BEFORE_JAPANESE_CLOSE_BRACKET_RE = re.compile(r" +([）】』」])")
URL_RE = re.compile(r"https?://|www\.")
INLINE_MATH_RE = re.compile(r"(?:\$\S.*\S\$|\\\(|\\\[|<!--\s*formula-not-decoded\s*-->)")
MATH_SYMBOL_RE = re.compile(r"[φγπ⌊⌋]|; *: *: *: *;")
INDENTED_CODE_RE = re.compile(r"^(?: {4,}|\t)")
COMMAND_LINE_RE = re.compile(r"^\s*(?:\$|#)\s+\S")
MARKDOWN_TABLE_RE = re.compile(r"^\s*\|")
MARKDOWN_IMAGE_RE = re.compile(r"^\s*!\[[^]]*]\(")
CODE_LIKE_LINE_RE = re.compile(
    r"^\s*(?:"
    r"[A-Za-z_][A-Za-z0-9_]*\s*[({=;]"
    r"|[{};]"
    r"|//"
    r"|/\*"
    r"|\*/"
    r")"
)
LEADING_GLYPH_LIST_RE = re.compile(
    r"^(?P<indent>\s*)-\s+glyph\[(?P<glyph>a114|a113)\]\s*(?P<rest>.*)$"
)
HEADING_GLYPH_LIST_RE = re.compile(
    r"^##\s+glyph\[(?P<glyph>a114|a113)\]\s*(?P<rest>.*)$"
)
INLINE_GLYPH_MARKER_RE = re.compile(r"\s+glyph\[(a114|a113)\]\s+")
TRAILING_GLYPH_MARKER_RE = re.compile(r"\s*(?:[、,]\s*)?glyph\[(?:a114|a113)\]\s*$")
BARE_GLYPH_LIST_RE = re.compile(r"^glyph\[(?P<glyph>a114|a113)\]\s*(?P<rest>.*)$")
SHORT_LABEL_GLYPH_LIST_RE = re.compile(
    r"^(?P<label>[A-Za-z0-9][A-Za-z0-9 +./-]{0,40})\s+"
    r"glyph\[(?P<glyph>a114|a113)\]\s+(?P<rest>.+)$"
)
COMMAND_FRAME_RE = re.compile(
    r"^(?:##\s+)?(?P<command>\$\s+.*?)\s*"
    r"✂\s*(?:✁\s*)?✄\s*(?:glyph\[a0\]\s*)?✛\s*(?P<output>.*)$"
)
CODE_LISTING_HEADING_RE = re.compile(r"^##\s+(リスト\s+\d+(?:\.\d+)?\s*[：:].*)$")
COMMAND_FRAME_MARKER_RE = re.compile(r"^(?:glyph\[a0\]|✁|✂\s*✁\s*✄\s*glyph\[a0\]\s*✛)$")
FORMULA_NOT_DECODED = "<!-- formula-not-decoded -->"
CJK_RADICAL_COMPATIBILITY_MAP = {
    "⻑": "長",
    "⻄": "西",
    "⻫": "斉",
    "⻩": "黄",
}

CHAPTER_01_FORMULA_REPAIRS = (
    "$$\n"
    "\\begin{aligned}\n"
    "\\operatorname{addFirst}(x) &\\Rightarrow \\operatorname{add}(0,x) \\\\\n"
    "\\operatorname{removeFirst}() &\\Rightarrow \\operatorname{remove}(0) \\\\\n"
    "\\operatorname{addLast}(x) &\\Rightarrow \\operatorname{add}(\\operatorname{size}(),x) \\\\\n"
    "\\operatorname{removeLast}() &\\Rightarrow \\operatorname{remove}(\\operatorname{size}()-1)\n"
    "\\end{aligned}\n"
    "$$",
    "$$\n"
    "\\operatorname{compare}(x,y)=\n"
    "\\begin{cases}\n"
    "<0 & \\text{if } x<y \\\\\n"
    ">0 & \\text{if } x>y \\\\\n"
    "=0 & \\text{if } x=y\n"
    "\\end{cases}\n"
    "$$",
    "$$\n"
    "b^x = \\underbrace{b \\times b \\times \\cdots \\times b}_{x}\n"
    "$$",
    "$$\n"
    "b^x = k\n"
    "$$",
    "$$\n"
    "e = \\lim_{n\\to\\infty}\\left(1+\\frac{1}{n}\\right)^n \\approx 2.71828\n"
    "$$",
    "$$\n"
    "\\int_1^k \\frac{1}{x}\\,dx = \\ln k\n"
    "$$",
    "$$\n"
    "b^{\\log_b k}=k\n"
    "$$",
    "$$\n"
    "\\log_b k = \\frac{\\log_a k}{\\log_a b}\n"
    "$$",
    "$$\n"
    "\\ln k = \\frac{\\log k}{\\log e} = \\frac{\\log k}{(\\ln e)/(\\ln 2)} = (\\ln 2)(\\log k) \\approx 0.693147\\log k\n"
    "$$",
    "$$\n"
    "n! = 1 \\cdot 2 \\cdot 3 \\cdot \\cdots \\cdot n\n"
    "$$",
    "$$\n"
    "n! = \\sqrt{2\\pi n}\\left(\\frac{n}{e}\\right)^n e^{\\alpha(n)}\n"
    "$$",
    "$$\n"
    "\\frac{1}{12n+1} < \\alpha(n) < \\frac{1}{12n}\n"
    "$$",
    "$$\n"
    "\\ln(n!) = n\\ln n - n + \\frac{1}{2}\\ln(2\\pi n) + \\alpha(n)\n"
    "$$",
    "$$\n"
    "\\binom{n}{k}=\\frac{n!}{k!(n-k)!}\n"
    "$$",
    "$$\n"
    "O(f(n)) = \\{g(n): \\text{ある } c>0 \\text{ と } n_0 \\text{ が存在し、任意の } n\\ge n_0 \\text{ について } g(n)\\le c\\cdot f(n) \\text{ を満たす}\\}\n"
    "$$",
    "$$\n"
    "\\begin{aligned}\n"
    "5n\\log n+8n-200 &\\le 5n\\log n+8n\\log n && (n\\ge2) \\\\\n"
    "&\\le 13n\\log n\n"
    "\\end{aligned}\n"
    "$$",
    "$$\n"
    "O(n^{c_1}) \\subset O(n^{c_2})\n"
    "$$",
    "$$\n"
    "O(a) \\subset O(\\log n) \\subset O(n^b) \\subset O(c^n)\n"
    "$$",
    "$$\n"
    "O(n) \\subset O(n\\log n) \\subset O(n^{1+b}) \\subset O(nc^n)\n"
    "$$",
    "",
    "$$\n"
    "T(n)=2\\log n+O(1)\n"
    "$$",
    "$$\n"
    "T(n)=a+b(n+1)+cn+dn+en\n"
    "$$",
    "$$\n"
    "T(n)=O(n)\n"
    "$$",
    "$$\n"
    "O(f(n_1,\\ldots,n_k)) = \\{g(n_1,\\ldots,n_k): \\text{ある } c>0 \\text{ と } z \\text{ が存在し、} g(n_1,\\ldots,n_k)\\ge z \\text{ を満たす任意の } n_1,\\ldots,n_k \\text{ について } g(n_1,\\ldots,n_k)\\le c\\cdot f(n_1,\\ldots,n_k) \\text{ が成り立つ}\\}\n"
    "$$",
    "$$\n"
    "E[X] = \\sum_{x\\in U} x\\cdot \\Pr\\{X=x\\}\n"
    "$$",
    "$$\n"
    "E[X+Y]=E[X]+E[Y]\n"
    "$$",
    "$$\n"
    "E\\left[\\sum_{i=1}^{k}X_i\\right]=\\sum_{i=1}^{k}E[X_i]\n"
    "$$",
    "$$\n"
    "\\begin{aligned}\n"
    "E[X] &= \\sum_{i=0}^{k} i\\cdot \\Pr\\{X=i\\} \\\\\n"
    "&= \\sum_{i=0}^{k} i\\cdot \\binom{k}{i}/2^k \\\\\n"
    "&= k\\cdot \\sum_{i=0}^{k-1}\\binom{k-1}{i}/2^k \\\\\n"
    "&= k/2\n"
    "\\end{aligned}\n"
    "$$",
    "$$\n"
    "I_i = \\begin{cases}1 & i\\text{番めのコイントスの結果が表のとき} \\\\ 0 & \\text{そうでないとき}\\end{cases}\n"
    "$$",
    "$$\n"
    "E[I_i]=(1/2)1+(1/2)0=1/2\n"
    "$$",
    "$$\n"
    "\\begin{aligned}\n"
    "E[X] &= E\\left[\\sum_{i=1}^{k}I_i\\right] \\\\\n"
    "&= \\sum_{i=1}^{k}E[I_i] \\\\\n"
    "&= \\sum_{i=1}^{k}1/2 \\\\\n"
    "&= k/2\n"
    "\\end{aligned}\n"
    "$$",
)


def is_cjk_radical_or_kangxi(char: str) -> bool:
    codepoint = ord(char)
    return 0x2E80 <= codepoint <= 0x2FFF


def normalize_cjk_radicals(text: str) -> str:
    return "".join(
        CJK_RADICAL_COMPATIBILITY_MAP.get(char, unicodedata.normalize("NFKC", char))
        if is_cjk_radical_or_kangxi(char)
        else char
        for char in text
    )


def should_repair_japanese_spacing_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return not (
        URL_RE.search(line)
        or "$" in line
        or INLINE_MATH_RE.search(line)
        or MATH_SYMBOL_RE.search(line)
        or INDENTED_CODE_RE.match(line)
        or COMMAND_LINE_RE.match(line)
        or MARKDOWN_TABLE_RE.match(line)
        or MARKDOWN_IMAGE_RE.match(line)
        or CODE_LIKE_LINE_RE.match(line)
    )


def repair_japanese_spacing_in_line(line: str) -> str:
    if not should_repair_japanese_spacing_line(line):
        return line

    while True:
        repaired = JAPANESE_INTERNAL_SPACE_RE.sub(r"\1\2", line)
        repaired = SPACE_BEFORE_JAPANESE_PUNCT_RE.sub(r"\1\2", repaired)
        repaired = SPACE_AFTER_JAPANESE_PUNCT_RE.sub(r"\1\2", repaired)
        repaired = SPACE_AFTER_JAPANESE_OPEN_BRACKET_RE.sub(r"\1", repaired)
        repaired = SPACE_BEFORE_JAPANESE_CLOSE_BRACKET_RE.sub(r"\1", repaired)

        if repaired == line:
            return repaired
        line = repaired


def glyph_list_prefix(glyph: str) -> str:
    return "  - " if glyph == "a113" else "- "


def split_inline_glyph_list_markers(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return "\n" + glyph_list_prefix(match.group(1))

    return INLINE_GLYPH_MARKER_RE.sub(replace, text)


def repair_glyph_markers_in_list_line(line: str) -> str:
    repaired = split_inline_glyph_list_markers(line)
    return TRAILING_GLYPH_MARKER_RE.sub("", repaired)


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

    match = BARE_GLYPH_LIST_RE.match(line)
    if match:
        return glyph_list_prefix(match.group("glyph")) + split_inline_glyph_list_markers(
            match.group("rest")
        )

    if line.lstrip().startswith("- "):
        return repair_glyph_markers_in_list_line(line)

    match = SHORT_LABEL_GLYPH_LIST_RE.match(line)
    if match:
        first_item = glyph_list_prefix(match.group("glyph")) + match.group("label")
        second_item = glyph_list_prefix(match.group("glyph")) + split_inline_glyph_list_markers(
            match.group("rest")
        )
        return first_item + "\n" + second_item

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


def is_glyph_only_code_block(content: list[str]) -> bool:
    non_empty = [line.strip() for line in content if line.strip()]
    return bool(non_empty) and all(
        re.fullmatch(r"(?:glyph\[(?:a114|a113)\]\s*)+", line) for line in non_empty
    )


def remove_glyph_only_code_blocks(markdown: str) -> str:
    lines = markdown.splitlines(keepends=True)
    repaired: list[str] = []
    index = 0

    while index < len(lines):
        content = lines[index].removesuffix("\n")
        if not MARKDOWN_FENCE_RE.match(content):
            repaired.append(lines[index])
            index += 1
            continue

        end_index = index + 1
        while end_index < len(lines):
            end_content = lines[end_index].removesuffix("\n")
            if MARKDOWN_FENCE_RE.match(end_content):
                break
            end_index += 1

        if end_index < len(lines) and is_glyph_only_code_block(lines[index + 1 : end_index]):
            index = end_index + 1
            continue

        repaired.extend(lines[index : end_index + 1])
        index = end_index + 1

    return "".join(repaired)


def repair_known_split_list_fragments(markdown: str) -> str:
    return re.sub(
        r"(?m)^MergeSort QuickSort\n\n"
        r"- 第 12 章：幅優先探索、深さ優先探索\n\n"
        r"- 第 11 章：$",
        "- 第 11 章：MergeSort、QuickSort\n\n"
        "- 第 12 章：幅優先探索、深さ優先探索",
        markdown,
    )


def repair_chapter_01_formula_placeholders(markdown: str) -> str:
    if (
        "## 1.2.2 List インターフェース" not in markdown
        or "## 1.3.4 ランダム性と確率" not in markdown
    ):
        return markdown

    repaired = markdown
    for formula in CHAPTER_01_FORMULA_REPAIRS:
        if FORMULA_NOT_DECODED not in repaired:
            break
        replacement = formula
        if not replacement:
            replacement = ""
        repaired = repaired.replace(FORMULA_NOT_DECODED, replacement, 1)
    return re.sub(r"\n{4,}", "\n\n\n", repaired)


def repair_chapter_01_formula_order(markdown: str) -> str:
    euler_formula = (
        "$$\n"
        "e = \\lim_{n\\to\\infty}\\left(1+\\frac{1}{n}\\right)^n \\approx 2.71828\n"
        "$$"
    )
    euler_intro = (
        "次のように定義されるオイラーの定数（Euler's constant） e を底とする対数も"
        "よく使う ψ 6。そこで、log e k のことを ln k と書き、自然対数"
        "（natural logarithm） と呼ぶ。"
    )
    return markdown.replace(
        euler_formula + "\n\n" + euler_intro,
        euler_intro + "\n\n" + euler_formula,
    )


def repair_visible_glyph_markers(markdown: str) -> str:
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
            lines.append(normalize_cjk_radicals(content) + line_ending)
            continue

        lines.append(repair_glyph_list_markers(content) + line_ending)

    return "".join(lines)


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
        content = repair_japanese_spacing_in_line(content)
        lines.append(content + line_ending)

    markdown = remove_glyph_only_code_blocks("".join(lines))
    markdown = repair_visible_glyph_markers(markdown)
    markdown = repair_known_split_list_fragments(markdown)
    markdown = repair_chapter_01_formula_placeholders(markdown)
    return repair_chapter_01_formula_order(markdown)
