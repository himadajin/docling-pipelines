from ....models import TocEntry


def repair_toc_entries(entries: list[TocEntry]) -> list[TocEntry]:
    repaired: list[TocEntry] = []

    for entry in entries:
        if entry.number == "2.5" and entry.title == "PTB データセットでの評価 まとめ":
            repaired.extend(
                [
                    TocEntry(number="2.5", title="PTB データセットでの評価", page="86"),
                    TocEntry(number="2.6", title="まとめ", page="90"),
                ]
            )
            continue

        if entry.number is None and entry.title == "推論ベースの手法とニューラルネットワーク":
            repaired.append(
                TocEntry(
                    number="3.1",
                    title="推論ベースの手法とニューラルネットワーク",
                    page=entry.page,
                )
            )
            continue

        if entry.number == "3.1.2" and entry.title == "95":
            repaired.append(
                TocEntry(
                    number="3.1.2",
                    title="ニューラルネットワークにおける単語の処理",
                    page="95",
                )
            )
            continue

        if (
            entry.number == "4.2.6"
            and entry.title == "Negative Sampling のサンプリング手法 の実装"
        ):
            repaired.append(
                TocEntry(
                    number="4.2.6",
                    title="Negative Sampling のサンプリング手法",
                    page="154",
                )
            )
            repaired.append(
                TocEntry(
                    number="4.2.7",
                    title="Negative Sampling の実装",
                    page="155",
                )
            )
            continue

        if entry.number == "付録 B" and not entry.title:
            repaired.append(
                TocEntry(number="付録 B", title="WordNet を動かす", page=entry.page)
            )
            continue

        if entry.number == "付録 C" and entry.title == "GRU":
            repaired.append(entry)
            continue

        repaired.append(entry)

    return repaired
