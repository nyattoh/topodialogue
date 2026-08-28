# 要件定義HTML 敵対検証結果

検証担当: codex#7  
対象: `docs/tasks/54df411b/requirements-definition.html`  
検証日: 2026-08-28  
判定: **条件付き不合格（1件の文書整合性指摘）**

## 実行した検査

リポジトリルートで次を実行する。

```bash
python3 scripts/verify_requirements.py --negative
```

結果は `11 passed, 1 failed`、終了コード `1` だった。検査器は標準ライブラリだけで動き、元HTMLは変更しない。`--negative` は対象HTMLの一時コピーに次の変異を一つずつ適用し、必須検査が失敗することを確認してから一時ファイルを削除する。

| 変異 | 期待した失敗 | 結果 |
| --- | --- | --- |
| `data-kamui-architecture-proposal="true"` を削除 | architecture proposal attribute | 期待どおり失敗 |
| 中央命題の `物理配置` を削除 | central thesis | 期待どおり失敗 |
| metrics の `HBM occupancy` を削除 | metrics | 期待どおり失敗 |
| draft5 READMEリンクを不存在パスへ変更 | draft5/docs alignment | 期待どおり失敗 |
| `</html>` を削除 | complete HTML parse | 期待どおり失敗 |

## 通過した反証レンズ

- 完全HTML: `<!doctype html>`、`html/head/body/main` の一意性、タグバランス、UTF-8、`lang="ja"`、title、重複IDなしを確認した。IDは21件すべて一意、目次の15 fragment linkは全て解決した。
- 単独表示性: 外部stylesheet、script、画像、iframe、font/import、外部CSS URLを要求しない。SVGの `url(#...)` は自己完結したmarker/filter参照として許容した。ローカルHTTP配信でも `200 text/html`、本文55882 bytesを取得した。
- 構成図: `section#architecture` に `data-kamui-architecture-proposal="true"` がちょうど1件あり、inline SVGをXMLとして解析でき、アクセシブルな `title` と `desc` がある。
- 内容: 中央命題（representation form / precision / physical placementの同一phase化）、vapor/liquid/ice、evaporate/condense/freeze/melt、6要素のtopology skeleton、電力4項、指定指標、FPGA提案実験、未実施境界、novelty hypothesisと非数学的topology境界を確認した。
- 成果物と受入条件: 指定7成果物、主要AC項目、TopoDialogue conceptual modelとdraft5 READMEへの相対リンクを確認した。
- 引用URL: HTML内の5つのarXiv URLは `curl -L` で全てHTTP 200だった。一次ページの `citation_title` は、HTML記載の5題名（R³Memは数式表記差を除く）と一致した。HTTP 200は書誌・主張の完全な正しさを保証しない。

## 指摘事項

### REQ-ALIGN-001 — 重要度: Low〜Medium

**反証:** HTML 410行は、リンク先 `paper/draft5/README.md` が「EN/JA・references・fact-check・静的監査・PDF builder」の包装を採ると記述する。しかし実際のdraft5 README 3行目は paper source、Japanese companion、references、PDF builder、static auditを列挙するだけで、`fact-check` を列挙しない。`paper/draft5/fact-check.md` 自体は存在するため、成果物欠落ではなく、リンク先説明とHTMLの証拠付けの不一致である。

**再現:**

```bash
rg -n "draft5は|fact-check" docs/tasks/54df411b/requirements-definition.html
nl -ba paper/draft5/README.md
test -f paper/draft5/fact-check.md
```

**修正対象:** `paper/draft5/README.md` に `fact-check.md` を包装一覧として追記する、またはHTML 410行の出所リンクを `paper/draft5/fact-check.md` まで分けて、READMEが直接裏付ける主張と実在ファイルの主張を分離する。後続担当はどちらか一方を選び、検証器を再実行すること。

## 環境制約

- ホスト管理の会話経路を確認したが、`peers` は空で、実サブエージェントの割り当ては利用できなかった。そのため構文・要件・整合・負のテストを独立プロセスで並列実行した。
- この環境では通常の `playwright-core` 解決と実行可能Chromiumが利用できず、ブラウザレンダリングの新規スクリーンショットは撮影していない。前段コミット `b8aea22` にある `achievement-report-assets/playwright/requirements-definition.png` を目視確認し、全体のスタイル、表、構成図、15節の縦長表示を確認した。今回の担当はHTMLを編集していないため、新たなUI変更の証跡は不要と判断した。
- 回帰確認として `python3 -m pytest -q` も試したが、この環境には `pytest` がなく `No module named pytest` で起動できなかった。HTML専用の標準ライブラリ検証器は独立して実行できている。
- リポジトリ内に `gate.sh` は存在しなかった。したがって上記検証器の終了コードをこの担当の検証ゲートとした。終了コードは指摘が残るため `1` であり、無条件の合格とは扱わない。

## 変更範囲

- 追加: `scripts/verify_requirements.py`
- 追加: 本報告書
- 未変更: `docs/tasks/54df411b/requirements-definition.html`
- 一時変異ファイルと一時ディレクトリは検証後に残っていない。
