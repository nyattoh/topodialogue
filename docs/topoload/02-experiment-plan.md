# TopoLoad 実験計画 v0.1

## 1. 方針

最初の実験は、LLM providerの変動に左右されないdeterministic simulatorで行う。方向付きcontrollerの追加価値が確認できた後に、実モデルによる小規模追試を行う。

実験開始前にconfig、threshold、primary metric、quality non-inferiority marginを固定する。

## 2. 実験段階

### Stage A — Deterministic control simulator

- model tierを固定cost／latency／success profileとして模擬する。
- task trajectory、goal、deviation eventをseed付きで生成する。
- routing policyだけを比較する。
- network、paid API、LLM出力へ依存しない。

### Stage B — Replay benchmark

- 保存済みの匿名化／合成event traceを全policyへ同一順序で再生する。
- policy間で入力系列を変えない。
- counterfactual outcome modelの仮定を明記する。

### Stage C — Optional real-model study

- 小規模な固定task setで実モデルを比較する。
- model snapshot、reasoning effort、prompt、tool version、dateを記録する。
- Stage A/Bの結果と混ぜず、外的妥当性の補助結果として報告する。

### Stage D — Energy instrumentation, optional

- GPU／host電力を物理測定できる場合だけ実施する。
- token、latency、model callsからenergyを換算しない。
- measurement boundary、idle baseline、sampling interval、hardware、batchingを記録する。

## 3. Task families

### F1. Aligned local

- 小さく局所的な変換、lookup、形式チェック。
- expected action: `LOCAL`
- failure例: 不必要な`DEEP`

### F2. Aligned hard

- 長いが仕様とrubricが明確な証明、コード変更、文書整合。
- expected action: `DEEP`
- failure例: high demandをlateral deviationと誤認して遮断

### F3. Wrong-premise deepening

- 初期仮定が証拠と衝突しているのに、その仮定を守るため推論が肥大化する。
- expected action: evidence蓄積後に`DISCLUDE`

### F4. Cyclic tool plan

- `search -> plan -> search`等が成果なしで反復する。
- expected action: recurrence確認後に`DISCLUDE`

### F5. Branch explosion

- goalへ寄与しない候補分岐が指数的に増える。
- expected action: branch evidenceに応じて`DISCLUDE`又は`HOLD`

### F6. Prompt conflict／injection-like deviation

- task specificationと競合する後続命令が入る。
- security benchmarkとは分離し、goal conflictとroute behaviourだけを測る。
- expected action: `HOLD`又は`DISCLUDE`

### F7. Productive exploration negative control

- 一時的にgoal subspace外へ出るが、後で成果へ必要な情報を持ち帰る。
- expected action: 誤って早期遮断しない。

### F8. Ambiguous／changing goal

- goalが不足、複数、途中変更される。
- expected action: `HOLD`／goal update protocol
- hard disclusionを既定にしない。

### F9. Burst request pressure

- arrival rate又はcontext pressureが急増する。
- expected action: `DAMP`
- canonical recordとcontradiction evidenceを保持する。

### F10. Mixed load

- high demand、lateral deviation、burstが時間差又は同時に発生する。
- controller priorityとswitching costを評価する。

## 4. Baselines

- `B0 AlwaysLocal`
- `B1 AlwaysDeep`
- `B2 ScalarDifficultyRouter`
- `B3 CostQualityCascade`
- `B4 FixedBudgetBreaker`
- `B5 RecurrenceOnlyBreaker`
- `B6 DirectionOnlyRouter` — recurrenceなし
- `B7 FullTopoLoad` — direction + recurrence + confidence + damping
- `B8 Oracle` — simulator内の真のeventを知る上限参考値。主要比較には使わない。

## 5. Ablations

- `-direction`
- `-recurrence`
- `-goal_confidence`
- `-reverse_drift`
- `-hysteresis`
- `-cooldown`
- `-switching_cost`
- `-damping`
- `-canonical_contract`
- `direction_scalar_only`
- `single_goal_vector` vs `goal_subspace`

## 6. Primary outcomes

### Quality

- task success
- exact／rubric score
- constraint satisfaction
- contradiction preservation
- provenance preservation

### Resource

- heavy-model calls
- local-model calls
- input／output tokens, real-model studyのみ
- simulated compute units
- p50／p95 latency
- switching overhead

### Control

- false disclusion rate
- missed disclusion rate
- precision／recall／F1
- time-to-disclusion
- time-to-recovery
- loop continuation length
- mode oscillation count

### Load／queue

- peak queue depth
- queue area under curve
- hard-limit failures
- dropped／deferred requests
- context pressure

### Fidelity

- canonical records retained
- stale derived views rejected
- contradictions retained
- provenance retained
- representation loss declared

EnergyはStage Dでのみprimary又はsecondary outcomeにする。

## 7. 統計計画

- 全policyへ同一seed／同一traceを使うpaired design。
- primary comparisonとprimary metricを先に固定する。
- bootstrap confidence interval又はtask-family階層を考慮したmodelを使う。
- effect sizeとuncertaintyを報告し、p値だけに依存しない。
- qualityは事前定義したnon-inferiority margin `delta`で評価する。
- resource改善はquality非劣性を満たしたpolicyだけで主張する。
- task family別結果を必ず示し、全体平均でfailure regionを隠さない。
- threshold tuning splitとfinal evaluation splitを分ける。

## 8. Dataset split

- `train/dev`: ruleとthresholdの初期化
- `calibration`: confidenceとthreshold調整
- `test`: 最終比較、一度だけ開封
- `stress`: distribution shift、goal noise、burst極端値

合成generatorのparameter rangeもsplitごとに固定する。

## 9. Sensitivity tests

- goal vector角度誤差
- goal subspace dimension
- recurrence noise
- model cost ratio
- switching cost
- burst rate
- context budget
- task length
- threshold drift
- productive exploration比率

## 10. Acceptance gates

### Gate A — Instrument validity

- 同一traceで全policyを再生できる。
- event traceにreason codeとcomponent valueがある。
- offline testがdeterministicに通る。

### Gate B — Controller validity

- F1/F2で基本dispatchを満たす。
- F7/F8で過剰遮断を測定できる。
- hysteresis testでmode oscillationが抑制される。

### Gate C — Comparative evidence

- primary comparisonのquality非劣性を評価できる。
- directionのincremental valueをablationで分離できる。
- negative resultを同じ形式で保存できる。

### Gate D — Paper readiness

- 全表が生成scriptから再構成できる。
- run manifest、seed、config、commit SHAが残る。
- claim tableの各文が結果又は一次資料へ対応する。

## 11. Stop conditions

- goalのground truthを作れずdirection評価が循環論法になる。
- baseline実装が不公平である。
- thresholdをtest setへ適合させてしまった。
- provider変動で再現性が取れず、simulator結果と区別できない。
- canonical fidelityの検査なしにcompression benefitだけを報告している。

停止時は失敗理由と次の反証可能な修正案を記録する。
