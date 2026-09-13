# T07 — 独立反証レビュー

- 推奨maker: GPT-5.6 Sol / max、新規session
- 推奨second checker: 別のSol / max又は人間承認
- 種別: adversarial research review
- 依存: T00–T06
- 次task: T08又は研究停止

## Objective

TopoLoadを成立させるのではなく、最も短い反例、不公平な比較、循環定義、既存研究との重複、再現不能性を探し、claimを縮小又は研究を停止できる材料を作る。

## Independence rules

- maker sessionの会話summaryを読まない。
- repository、manifest、raw result、一次資料だけから再構成する。
-「正しいことを確認する」というpromptを使わない。
- 修正実装を先に作らず、failureを再現する。

## Read first

1. `docs/topoload/00-paper-outline.md`
2. `docs/topoload/03-claim-boundaries.md`
3. `docs/topoload/research/claim-matrix.md`
4. `study/topoload/preregistration-v0.1.md`
5. `docs/topoload/spec/`
6. implementation and tests
7. latest `output/topoload/<run-id>/run-manifest.json`
8. raw result and generated tables

## Attack surface

### Conceptual

- directionがdifficultyの変換に過ぎない可能性
- goal subspaceが答えを事前に符号化している可能性
- lateral deviation labelの循環性
- occlusion比喩が方法へ不要又は誤誘導

### Experimental

- synthetic generatorとcontrollerの共通仮定
- baseline unfairness
- threshold leakage
- task distribution bias
- hidden oracle feature
- underpowered comparison
- quality marginの恣意性

### Implementation

- state leakage
- random seed leakage
- ablationが実際には無効化されていない
- failed transitionのpartial mutation
- stale derived view
- canonical hashだけでは検出できない意味的損失

### Claims

- tokenからenergyへの飛躍
- task family平均によるfailure隠蔽
- correlationをcontrol benefitと解釈
- simulator結果をproductionへ一般化
- related workの見落とし

## Required deliverables

### A. `reviews/topoload/falsification-v0.1.md`

各finding:

- severity
- claim affected
- reproduction steps
- observed evidence
- expected evidence
- whether fix changes preregistration
- recommendation: fix／narrow／remove／stop

### B. `reviews/topoload/counterexamples/`

再現可能な最小case。

### C. `reviews/topoload/claim-verdict-v0.1.md`

各主要claimを:

- supported within scope
- inconclusive
- contradicted
- not tested
- duplicate／not novel

へ分類する。

### D. `reviews/topoload/publication-gate-v0.1.md`

- proceed
- proceed with narrowed claims
- rerun required
- stop

のいずれかを、未解決finding付きで示す。

## Minimum attack requirements

- goal angle noise sweep
- productive exploration adversarial set
- scalar router strong retuning
- switching cost increase
- recurrence noise
- burst without information loss
- cross-seed regeneration
- one alternative embedding／state representation, feasibleの場合

## Acceptance criteria

- 少なくとも一つは主要仮説を棄却し得るtestを実行する。
- 「問題なし」だけのreviewを禁止する。
-重大findingを再現command付きで示す。
- preregistration変更が必要な修正を、単なるbug fixとして扱わない。
- publication gateが未解決severityへ整合する。

## Hand over

人間が判断すべき項目を日本語で明示し、open findingを隠さない。
