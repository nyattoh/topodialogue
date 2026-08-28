# 第2稿の事実確認・文字校・出典監査

監査日：2026-08-16（Asia/Tokyo）

## 監査方針

第1稿の設計由来である `Assistant  alphaXiv.md` と概念図は、着想の出典として扱う。
それらに含まれる「トポロジー」「身体性」「文化」「表示の主権」などの広い提案を、
確立した学術的事実として本文へ移していない。第2稿は実装、合成fixture、テスト、
既存の一次文献で確認できる範囲だけを主張する。

## 外部文献の確認

| 本文での位置づけ | 確認した一次情報 | 判定・制約 |
|---|---|---|
| 会話の相互作用ダイナミクスを要約し、後続予測で評価できる | Hua et al. (2024), ACL Anthology, <https://aclanthology.org/2024.naacl-long.414/> | 書誌と要旨を確認。TopoDialogueの性能へ一般化しない。 |
| 高次元表現で会話の話題流を軌跡として扱える | Fischer and Ram (2024), ACL Anthology, <https://aclanthology.org/2024.sicon-1.3/> | 書誌と要旨を確認。性格や感情の推定をTopoDialogueへ移さない。 |
| 意味空間によるマルチターン対話計画がある | Chen et al. (2025), arXiv v2, <https://arxiv.org/abs/2503.11586> | タイトル、著者、v2を確認。計画法を本実装の機能とは言わない。 |
| 連続的な言い換えで周期的アトラクターが報告されている | Wang et al. (2025), arXiv v2, <https://arxiv.org/abs/2502.15208> | 言い換え実験の範囲で確認。自然な人間‐AI対話へ一般化しない。 |
| マルチターン課題で信頼性低下を調べたシミュレーションがある | Laban et al. (2025), arXiv, <https://arxiv.org/abs/2505.06120> | シミュレーションの結果としてのみ記載。分類器の妥当性の証拠にはしない。 |
| NLPにおけるTDA研究が発展している | Uchendu and Le (2026), arXiv v5, <https://arxiv.org/abs/2411.10298> | v5のタイトル・著者・更新日を確認。本実装はTDA不変量を計算しない。 |
| 先行するTopoDialogue設計論文 | Sakakibara (2026), Zenodo record 21962837, <https://doi.org/10.5281/zenodo.21962837> | 公開レコードのタイトル、著者、公開日、DOIをZenodo APIで確認。第2稿の実装結果を先行論文へ遡及して帰属しない。 |

## 実装上の主張と証拠

| 第2稿の主張 | 証拠 | 状態 |
|---|---|---|
| 同じ入力とseedでPythonのレポートが一致する | `tests/test_trajectory_shapes.py::test_same_input_and_seed_produce_identical_report` | テスト済み |
| seedを変えると表示幾何は変わり得るが、運用指標は保たれる | `tests/test_trajectory_shapes.py::test_projection_seed_changes_geometry_but_not_operational_metrics` | 螺旋fixtureでテスト済み |
| PythonとJavaScriptが6ケースのクラス・再帰由来を一致させる | fixture test、CLI validator、`visualizer/trajectory-analysis.test.js` | テスト済み。自然データ精度ではない |
| 新規性を最初の特徴出現の話者で分ける | `topodialogue/trajectory.py` と assistant-loop provenance test | fixtureでテスト済み。因果帰属ではない |
| LoopScoreは平均類似度×（1−平均進展）を[0,1]にclipする | `topodialogue/trajectory.py` | コード確認済み |
| Time高さは単調で、上昇を進展と読んではならない | 軸定義と `time_height_monotonicity` 警告 | コード確認済み |
| エクスポートファイルが全会話を含む | 本稿の証拠にはない | 主張しない。取得完全性は別試験 |

## 合成測定値

`trajectory-v1`、seed 1729で再生成した値である。

| Case | Class | Source | Revisit rate | Mean similarity | Mean progress | LoopScore | Escape@5 | Projection stability |
|---|---|---|---:|---:|---:|---:|---|---:|
| exact-loop | closed loop | mixed | 0.666667 | 1.000000 | 0.000000 | 1.000000 | false | 1.000000 |
| spiral-revisit | spiral revisit | mixed | 0.666667 | 0.583333 | 0.243333 | 0.441389 | false | 0.939956 |
| open-trajectory | open trajectory | none | 0.000000 | 0.000000 | 0.000000 | 0.000000 | false | 0.442795 |
| assistant-induced-loop | closed loop | assistant | 0.333333 | 1.000000 | 0.000000 | 1.000000 | false | 0.434584 |
| spiral-escape | escape | mixed | 0.333333 | 1.000000 | 0.000000 | 1.000000 | true | 0.824146 |
| speaker-drift | closed loop | mixed | 0.666667 | 1.000000 | 0.000000 | 1.000000 | false | 1.000000 |

## 英語校正

- `visualise`, `analyse`, `behaviour`, `normalise`, `artefact`, `centre`,
  `modelling`, `labelled`, `favour` など British English を使用した。
- LaTeXコマンド名（例：`\centering`）と論文タイトルの固有表記は、本文の英米綴り監査から除外する。
- “topology” は実装済みの数学的結果ではなく、名称の由来または将来方向として使う。
- “escape” は有限窓の再帰規則であり、回復・洞察・健康・心理的変化を意味しない。

## 未完了項目

- LaTeXをコンパイルできる環境でPDFを生成し、全ページを目視確認する。
- 専用の公開ソフトウェアアーカイブを実際に公開した場合だけ、そのURLと永続識別子を追加する。
- 自然会話の評価、取得完全性、ヒューマンアノテーションは次の研究で行う。
