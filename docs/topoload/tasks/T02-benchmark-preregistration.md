# T02 — Benchmarkと評価の事前登録

- 推奨maker: GPT-5.6 Sol / xhigh
- 推奨checker: GPT-5.6 Sol / max
- 種別: evaluation gate
- 依存: T00, T01
- 次task: T04, T05, T06

## Objective

結果を見てから成功条件を動かせないように、task family、split、baseline、primary metric、quality margin、threshold tuning手順を固定する。

## Read first

1. `docs/topoload/02-experiment-plan.md`
2. `docs/topoload/spec/model-v0.1.md`
3. `docs/topoload/spec/controller-v0.1.md`
4. `docs/topoload/spec/test-obligations-v0.1.md`
5. `docs/topoload/research/claim-matrix.md`
6. `docs/07-evaluation.md`

## Required deliverables

### A. `study/topoload/preregistration-v0.1.md`

- research questions
- hypotheses and nulls
- primary／secondary comparisons
- task family
- sampling unit
- split
- seed plan
- primary metric
- quality non-inferiority margin
- multiple comparison policy
- exclusion rule
- missing run policy
- sensitivity analysis
- stop rule

### B. `study/topoload/config.schema.json`

全configをmachine-readableにする。

### C. `study/topoload/config/preregistered-v0.1.json`

- thresholds
- weights
- normalisation
- task counts
- seed list
- cost profile
- latency profile
- split hash

### D. `study/topoload/benchmark-spec-v0.1.md`

各fixtureのobservable input、hidden truth、expected controller region、許容される複数actionを定義する。単一のdesired resultへscoreをhard-codeしない。

### E. `study/topoload/analysis-plan-v0.1.md`

- paired comparison
- interval estimation
- non-inferiority test
- task-family stratification
- ablation
- calibration
- failure analysis

## Required baselines

最低限:

- AlwaysLocal
- AlwaysDeep
- ScalarDifficultyRouter
- CostQualityCascade
- FixedBudgetBreaker
- RecurrenceOnlyBreaker
- DirectionOnlyRouter
- FullTopoLoad

全baselineへ同じ情報を与えない場合、その差を明記する。

## Leakage controls

- generator parameterをtest resultから調整しない。
- threshold tuningはcalibration splitだけで行う。
- final test splitはmanifest hashで封印する。
- policyごとに異なるtraceを使わない。
- expected actionをfeatureとしてpolicyへ渡さない。

## Acceptance criteria

- 成功／失敗が数値で判定できる。
- resource改善はquality非劣性を満たした場合だけ主張できる。
- false disclusionとmissed disclusionを両方測る。
- productive explorationとambiguous goalがnegative controlにある。
- direction featureの追加価値がablationで分離できる。
- energyをsimulated computeと混同していない。
- checkerが結果を知らずに計画を承認又は却下できる。

## Checker focus

- baseline unfairness
- circular ground truth
- test leakage
- metric cherry-picking
- hidden oracle information
- task familyの偏り
- quality marginの恣意性
- null resultを隠せる集計方法

## Hand over

approved configのhash、open issue、変更禁止項目を`study/topoload/T02-hand_over.md`へ記録する。
