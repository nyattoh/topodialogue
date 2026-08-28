# 13 — 再現可能な軌跡表示と形状検証

## 目的

本実装は、対話の立体表示を「印象的な図」ではなく、反証可能な測定器として扱う。
Phase 1で扱うのは意味特徴の再訪、再訪時の進展、由来別新規性、および操作的な
Escapeである。数学的な位相不変量、心理状態、身体状態は測定していない。

## 軸の操作的定義

| 軸 | 定義 | 解釈上の制約 |
|---|---|---|
| X | 固定seedによるsigned feature projection第1成分 | 固有の心理軸・意味軸ではない |
| Y | 同じprojectionの第2成分 | 回転・反転・seed変更で見た目が変わり得る |
| Z: Time | 発話順を `[-50, 50]` へ線形変換 | 上昇は進展の証拠ではない |
| Z: Revisit count | 同一特徴signatureへの累積再訪回数 | 注釈粒度に依存する |
| Z: Abstraction | 明示注釈、なければnode typeから得る操作的抽象度 | 心理的な「深さ」ではない |
| Z: Alternative | 固定projectionの第3成分 | 形状の頑健性比較用であり実在軸ではない |

線は発話順、点の色は発話者、点の大きさは当該発話の新規特徴数、透明度は抽出の
confidence、破線は再訪点と最類似の過去点を表す。同じ正規化入力とseedからは同じ
解析レポートと座標が得られる。

## 操作的な形状分類

- `open_trajectory`: recurrence thresholdを超える再訪がない。
- `closed_loop`: 再訪はあるが、新規特徴または抽象度増分による進展が閾値未満。
- `spiral_revisit`: 再訪しながら新規特徴または抽象度増分が閾値以上。
- `escape`: 再訪後、K発話以内のユーザー発話が再帰領域から離れ、ユーザー由来の
  新規特徴を導入し、その後の観測範囲で再訪が復活しない。

これは表示形状の画像分類ではない。特徴集合の再訪と進展から得る操作的ラベルで、
見た目の円や螺旋を直接判定しない。`recurrence_source` は形状と分けて
`user / assistant / mixed / none` を報告する。

## 由来別新規性

特徴keyを最初に導入した発話者を記録する。AIが先に提示したkeyをユーザーが後から
使っても、user-originated noveltyには数えない。この方式は厳格で再現可能だが、
ユーザーが独立に再発見した概念を過小評価し得るため、その限界も報告対象とする。

## 合成検証ケース

`examples/synthetic/manifest.json` が期待値の正本である。

1. exact loop → `closed_loop / mixed`
2. same topic with cumulative detail → `spiral_revisit / mixed`
3. unrelated topic sequence → `open_trajectory / none`
4. assistant repeatedly restores its hypothesis → `closed_loop / assistant`
5. recurrent constraint followed by user-owned region → `escape / mixed`
6. speaker-specific semantic drift → `closed_loop / mixed`（二枝表示のfailure probe）

検証コマンド:

```powershell
python -m topodialogue.cli validate-synthetic
node --test visualizer/trajectory-analysis.test.js
```

ブラウザE2Eは`visualizer/e2e-smoke.js [conversation.json]`で実行し、合成3条件、
Z軸切替、6軸定義、artifact表示、実ファイル読込を検査する。Three.jsは固定版を
リポジトリ内に同梱し、外部CDNの可用性を再現条件から除外している。

## Artifact / failure report

各解析は少なくとも次を検査する。

- `time_height_monotonicity`: 時間軸が上昇形状を強制する。
- `lexical_fallback`: 注釈なし文字n-gram近似は意味的言い換えを落とす。
- `mixed_feature_sources`: 注釈特徴と文字特徴の距離は直接比較しにくい。
- `projection_seed_sensitivity`: 代替seedとの距離相関が低い。
- `small_sample`: 形状判定に発話数が足りない。
- `speaker_imbalance`: provenance比較に必要な発話者バランスが弱い。

第一稿では成功図だけでなく、speaker drift、seed感度、注釈なし入力、時間高さによる
見かけの螺旋をfailure/artifact例として併記する。

## 第一稿で主張できる範囲

「同じ意味領域への再訪と、再訪時の進展を、階層を持つ再現可能な軌跡として観測する
ためのPhase-1測定器を実装し、既知の合成ケースで操作的区別を検証した」と述べられる。
真の対話位相を復元した、心理状態を測った、螺旋が人の進歩を証明した、とは述べない。
