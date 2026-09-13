# T01 — 数理定式化とcontroller specification

- 推奨maker: GPT-5.6 Sol / max
- 推奨checker: GPT-5.6 Sol / max、新規session
- 種別: formal specification gate
- 依存: T00
- 次task: T02, T03

## Objective

TopoLoadを咬合比喩なしでも再現可能な数理modelと有限状態controllerとして固定する。実装者が判断を補わずにcodeへ落とせる粒度にする。

## Read first

1. `AGENTS.md`
2. `docs/topoload/01-formal-model.md`
3. `docs/topoload/03-claim-boundaries.md`
4. `docs/topoload/research/claim-matrix.md`
5. `docs/05-loop-detection.md`
6. `docs/03-architecture.md`
7. `docs/topoload/research/T00-hand_over.md`

## Required decisions

1. state `z_t`の最小interface
2. explicit goal vector／subspaceの構成方法
3. goal confidenceと更新規則
4. aligned、signed progress、lateral、reverse driftの定義
5. scale normalisation
6. TopoDialogue recurrence adapter
7. disclusion hazard
8. burst／context pressure
9. controller modeと優先順位
10. hysteresis、confirmation、cooldown
11. switching cost
12. canonical／derived fidelity contract
13. reason codes
14. missing／invalid measurement時のfail-safe

## Required deliverables

### A. `docs/topoload/spec/model-v0.1.md`

- notation table
- assumptions
- equations
- domain／range
- undefined case
- normalisation
- counterexample

### B. `docs/topoload/spec/controller-v0.1.md`

- state transition table
- pseudocode
- precedence rule
- enter／exit condition
- reason code
- event schema

### C. `docs/topoload/spec/invariants-v0.1.md`

最低限:

- canonical record is never replaced by a derived summary
- low goal confidence cannot directly cause `DEEP`
- low goal confidence cannot directly cause hard `DISCLUDE`, except external hard guard
- `theta_exit < theta_enter`
- every route switch has evidence and reason codes
- failed transition does not partially mutate state
- cooldown is observable and testable

### D. `docs/topoload/spec/open-decisions-v0.1.md`

決められない点を曖昧な文章で埋めず、選択肢、影響、必要なexperimentを記録する。

## Required proofs／checks

厳密な定理でなくてもよいが、次を検査する。

- projectionがbasis表現に依存しない条件
- zero movement時のratio安定性
- threshold境界でのoscillation
- confidence zero／one
- multiple goals
- goal change
- contradictory control signals
- missing recurrence
- non-finite input

## Non-goals

- learned policy
- reinforcement learning
- persistent homology
- human intention estimation
- production scheduler
- energy model

## Acceptance criteria

- 全変数に観測又は計算方法がある。
- controllerの同一入力が一意のactionを返す。
- ambiguous goalが`HOLD`へ行く。
- aligned hard taskがlateral magnitudeだけで遮断されない。
- productive explorationを誤遮断し得る反例が明記され、T02のnegative controlへ送られている。
- claim matrixと矛盾しない。
- checkerが少なくとも三つのcounterexampleを作り、仕様が処理方法を持つ。

## Verification

仕様からproperty-based test一覧を導出し、`docs/topoload/spec/test-obligations-v0.1.md`へ記録する。codeはまだ書かない。

## Hand over

T02／T03へ、固定済みequation、未固定config、必須test、禁止解釈を`docs/topoload/spec/T01-hand_over.md`へ記録する。
