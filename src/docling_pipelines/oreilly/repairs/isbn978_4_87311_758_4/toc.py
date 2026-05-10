from ....models import TocEntry


def repair_toc_entries(entries: list[TocEntry]) -> list[TocEntry]:
    expanded: list[TocEntry] = []

    for entry in entries:
        if entry.number is None and entry.title == "まえがき" and entry.page is None:
            expanded.append(TocEntry(number=None, title="まえがき", page="iii"))
            continue

        if entry.number == "3.7" and entry.title == "バッチ処理 まとめ":
            expanded.extend(
                [
                    TocEntry(number="3.6.3", title="バッチ処理", page="78"),
                    TocEntry(number="3.7", title="まとめ", page="81"),
                ]
            )
            continue

        if entry.number == "7.6.1" and entry.title == "1 層目の重みの可視化 階層構造による情報抽出":
            expanded.extend(
                [
                    TocEntry(number="7.6.1", title="1 層目の重みの可視化", page="234"),
                    TocEntry(number="7.6.2", title="階層構造による情報抽出", page="235"),
                ]
            )
            continue

        expanded.append(entry)

    return expanded
