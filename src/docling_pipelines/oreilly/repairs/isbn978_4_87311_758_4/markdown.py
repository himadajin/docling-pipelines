import re


def repair_class_template_markdown(markdown: str) -> str:
    pattern = re.compile(
        r"## class クラス名：\n"
        r"    def init\(self引数\): # コンストラクタ\n\n"
        r"```\n"
        r"def \\_\\_init\\_\\_\(self, 引数, …\): # コンストラクタ\n"
        r"```\n\n"
        r"```\n"
        r"def メソッド名 1\(self, 引数, …\): # メソッド 1\n"
        r"```\n\n"
        r"```\n"
        r"def メソッド名 2\(self, 引数, …\): # メソッド 2\n"
        r"```"
    )
    replacement = (
        "```\n"
        "class クラス名：\n"
        "    def __init__(self, 引数, …): # コンストラクタ\n"
        "        ...\n"
        "    def メソッド名 1(self, 引数, …): # メソッド 1\n"
        "        ...\n"
        "    def メソッド名 2(self, 引数, …): # メソッド 2\n"
        "        ...\n"
        "```"
    )
    return pattern.sub(replacement, markdown)


def apply_markdown_repairs(markdown: str) -> str:
    markdown = repair_class_template_markdown(markdown)
    return markdown.replace(
        "また、各変数に関する微分は、で求めることができます。",
        "また、各変数に関する微分は、backward() で求めることができます。",
    )
