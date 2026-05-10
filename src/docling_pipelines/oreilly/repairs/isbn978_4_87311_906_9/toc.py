from ....models import TocEntry


def repair_toc_entries(entries: list[TocEntry]) -> list[TocEntry]:
    repaired: list[TocEntry] = []

    for entry in entries:
        if entry.number is None and entry.title == "累乗":
            continue

        if entry.number == "7.3" and entry.title == "backward メソッドの追加":
            repaired.append(
                TocEntry(number="7.3", title="backward メソッドの追加", page="43")
            )
            continue

        if entry.number == "16.4" and entry.title == "動作確認":
            repaired.append(entry)
            repaired.append(TocEntry(number=None, title="ステップ 17 メモリ管理と循環参照", page="111"))
            continue

        if entry.number == "22.3" and entry.title == "割り算":
            repaired.append(entry)
            repaired.append(TocEntry(number="22.4", title="累乗", page="154"))
            continue

        if entry.number == "27.4" and entry.title == "計算グラフの可視化":
            repaired.append(entry)
            repaired.append(TocEntry(number=None, title="ステップ 28 関数の最適化", page="203"))
            continue

        if entry.number == "34.3" and entry.title == "sin 関数の高階微分":
            repaired.append(entry)
            repaired.append(TocEntry(number=None, title="ステップ 35 高階微分の計算グラフ", page="247"))
            continue

        if entry.number == "40.3" and entry.title == "ブロードキャストへの対応":
            repaired.append(entry)
            repaired.append(TocEntry(number=None, title="ステップ 41 行列の積", page="307"))
            continue

        if entry.number == "46.4" and entry.title == "SGD 以外の最適化手法":
            repaired.append(entry)
            repaired.append(
                TocEntry(
                    number=None,
                    title="ステップ 47 ソフトマックス関数と交差エントロピー誤差",
                    page="361",
                )
            )
            continue

        repaired.append(entry)

    return repaired
