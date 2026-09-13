# TopoLoad v0.1 — 研究・実装計画

TopoLoad は、LLM／エージェント処理の負荷を単一の「難易度」ではなく、**目標へ沿う負荷**と**目標から横へ逸れる負荷**へ分解し、処理経路を動的に切り替える研究仮説である。

咬合力学は着想源にとどめる。歯の各部位をAI部品へ一対一対応させることや、生体としての最適性をAIへ直接移植できることは主張しない。

## 中心仮説

> 状態軌跡の目標方向成分と側方成分を分離し、側方逸脱時には高コスト経路を増強せず離開し、突発負荷時には正本を保持したまま作業表現を緩衝することで、品質を維持しながら無駄な大規模推論、ループ継続、復帰遅延を削減できるか。

## Topoシリーズ内の位置

```text
TopoDialogue
  対話・推論の状態軌跡、再訪、低進捗、変換演算子
        |
        v
TopoLoad
  方向付き負荷、動的dispatch、route disclusion、damping
        |
        v
TopoPhase contract
  canonical observationを保ち、derived working viewだけを変形
```

### 境界

- **TopoDialogue**からは、状態軌跡、再帰／進捗特徴、`LoopDecision`相当の観測量を受け取る。
- **TopoLoad**は、どの計算経路を使うか、離開するか、緩衝するかを決める。
- **TopoPhase**の原則は、正本と派生表現を混同しないための契約として参照する。v0.1でTypeScript実装へ直接依存しない。
- TopoLoadは新しいattention機構、foundation model、数学的位相不変量、一般的安全保証を主張しない。

## 文書

1. [`00-paper-outline.md`](00-paper-outline.md) — 論文骨子
2. [`01-formal-model.md`](01-formal-model.md) — 最小数理モデル
3. [`02-experiment-plan.md`](02-experiment-plan.md) — 比較実験と評価指標
4. [`03-claim-boundaries.md`](03-claim-boundaries.md) — 主張・非主張・停止条件
5. [`04-model-effort-matrix.md`](04-model-effort-matrix.md) — Codexのモデル／effort割当
6. [`tasks/`](tasks/) — そのままCodexへ渡せる実行タスク

## 実行順

```text
T00 文献・新規性地図
  |
  v
T01 数理定式化
  |
  v
T02 事前登録可能な評価設計
  |
  +---------------------+
  |                     |
  v                     v
T03 参照実装         T04 合成fixture
  |                     |
  +----------+----------+
             v
T05 baseline・ablation
             |
             v
T06 experiment runner・解析
             |
             v
T07 独立反証レビュー
             |
             v
T08 論文初稿
             |
             v
T09 再現性・整備
```

T03とT04は、T01・T02が固定された後なら並行実行できる。T07はmakerと異なる新規セッションで行う。

## v0.1の成功条件

v0.1は「歯を模したAIができた」ことを示すものではない。次のいずれかを再現可能に示せれば前進とする。

- scalar difficulty routerより少ない高能力モデル呼出しで、非劣性範囲のtask successを維持する。
- recurrence-only breakerより、誤遮断を増やさず早く横方向逸脱から復帰する。
- dampingにより、正本と矛盾証拠を保持したまま、ピークqueue／context failureを減らす。
- 反対に、方向情報が予測力を追加しない、離開コストが利益を上回る、goal推定誤差に耐えないことを明確に示す。

否定結果も研究成果として保存する。
