# Codex モデル／effort割当表 — TopoLoad v0.1

基準日: 2026-09-13 JST

## 1. 前提

現行のGPT-5.6系では、Solは複雑な専門作業向け、Terraは知能とcostの均衡、Lunaはcost-sensitiveなhigh-volume処理向けとして案内されている。各modelは `none / low / medium / high / xhigh / max` のreasoning effortを持つ。

公式資料:

- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://help.openai.com/ja-jp/articles/11369540-using-codex-with-your-chatgpt-plan

実際にCodexで選択可能なmodelはworkspace設定と提供状況に従う。推奨modelが表示されない場合は、**同等以上の能力階層**へ置き換え、run manifestへ実model名とeffortを記録する。

## 2. 能力別の使い分け

| Model／effort | 向く仕事 | 向かない仕事 |
|---|---|---|
| Sol max | 数式の最終固定、新規性・反証、claim gate、複数制約の統合 | lint、単純fixture、機械的転記 |
| Sol xhigh | 文献統合、実験設計、論文構成、adversarial review | 大量の反復的ファイル生成 |
| Sol high | 範囲が固定された技術レビュー、結果解釈、section改稿 | 単純整形 |
| Terra xhigh | 中規模以上の実装、architecture整合、cross-file refactor | noveltyの最終断定 |
| Terra high | baseline、metrics、runner、test、bounded analysis | claim-bearing独立査読の単独担当 |
| Terra medium | 小さなmodule、bug fix、data transform、図表script | 曖昧な研究問題の定式化 |
| Luna high | 大量fixture、schema準拠test、反復的case生成 | 数式・新規性・最終解釈 |
| Luna medium | docs index、metadata、reference normalisation、整形 | 主要設計判断 |
| Luna low／none | lint、リンク確認、命名統一、定型更新 | 研究判断全般 |

`max`は「常に良い」設定ではない。数式、claim、独立反証のように誤りの波及が大きい箇所へ限定する。

## 3. Task routing

| Task | Maker | Checker | 理由 |
|---|---|---|---|
| T00 文献・新規性地図 | Sol xhigh | Sol max、新規session | 分野横断の同一操作発見と過剰claim防止 |
| T01 数理定式化 | Sol max | Sol max、新規session | goal uncertainty、projection、state machineの整合 |
| T02 評価事前登録 | Sol xhigh | Sol max | benchmark leakageと都合の良いmetric選択を防ぐ |
| T03 参照実装 | Terra xhigh | Sol high | 実装力と研究仕様の照合を分担 |
| T04 合成fixture | Luna high | Terra high | 量産を低costで行い、schema／coverageを上位で確認 |
| T05 baseline・ablation | Terra high | Sol high | 比較の公平性と実装正確性を両方見る |
| T06 runner・解析 | Terra high | Sol high | 再現性と統計解釈を分離 |
| T07 独立反証 | Sol max | 別のSol max又は人間承認 | maker文脈から切り離して破壊的に検査 |
| T08 論文初稿 | Sol xhigh | Sol max | 複数成果物の統合とclaim-to-evidence監査 |
| T09 再現性・整備 | Luna medium | Terra high | 機械作業を安価に行い、実runで検証 |

## 4. 役割分離規則

- claim-bearing成果物のcheckerをmakerより弱い設定にしない。
- makerとcheckerは同じ会話contextを共有しない。checkerはrepositoryとmanifestから再構成する。
- checkerへ「正しいことを確認せよ」ではなく「反証、漏れ、不公平な比較を探せ」と依頼する。
- Lunaが文献候補を抽出しても、採否・新規性判定はSolが行う。
- 実験結果の解釈は、実装担当とは別sessionで行う。
- model名、snapshot、effort、tool access、date、commit SHAを`run-manifest.json`へ保存する。
- provider固有挙動を一般結論へ拡張しない。

## 5. Effort fallback

推奨effortが使えない場合:

```text
max -> xhigh + independent second pass
xhigh -> high + narrower scope + independent checker
high -> medium + smaller task unit + stronger tests
medium -> low only for deterministic mechanical work
```

modelを弱くする場合はtask範囲も狭める。単に長いpromptを与えて代替しない。

## 6. 並行実行

並行可能:

- T03 implementation scaffold と T04 fixture generation
- baselineごとの独立実装
- paper sectionの非重複draft

直列必須:

- T01の数式固定前にT03 controllerを確定しない。
- T02のtest split固定前にthreshold tuningを始めない。
- T06の結果前にT08 Results／Conclusionを書かない。
- T07の重大指摘解消前にpublication-readyとしない。

## 7. 予算を抑える順序

1. Lunaでschema、fixture、文書indexを整える。
2. Terraで実装とtestを完成させる。
3. Solは定式化、比較設計、反証、claimへ集中する。
4. Sol maxのrunはcheckpoint単位にし、入力を必要文書へ限定する。

安価なmodelへ研究判断を委譲するのではなく、高能力modelが読むべき材料を安価なmodelで構造化する。
