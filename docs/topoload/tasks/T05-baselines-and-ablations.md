# T05 — Baselineとablation実装

- 推奨maker: GPT-5.6 Terra / high
- 推奨checker: GPT-5.6 Sol / high
- 種別: comparative implementation
- 依存: T02, T03, T04
- 次task: T06

## Objective

TopoLoadに有利な不公平を避け、同じtrace、同じcost profile、同じobservable informationで比較できるbaselineとablationを実装する。

## Read first

1. `study/topoload/preregistration-v0.1.md`
2. `study/topoload/benchmark-spec-v0.1.md`
3. `docs/topoload/spec/controller-v0.1.md`
4. `topoload/` implementation
5. `examples/topoload/manifests/`

## Required baselines

- AlwaysLocal
- AlwaysDeep
- ScalarDifficultyRouter
- CostQualityCascade
- FixedBudgetBreaker
- RecurrenceOnlyBreaker
- DirectionOnlyRouter
- FullTopoLoad
- Oracle, reference only

## Required ablations

- no direction
- no recurrence
- no confidence
- no reverse drift
- no hysteresis
- no cooldown
- no switching cost
- no damping
- destructive derived-view replacement baseline
- goal vector only vs subspace

## Fairness requirements

- 共通`Policy` interfaceを使う。
- 全policyへ渡すfieldをmanifestへ出す。
- baselineが本来必要としない情報を与えてもよいが、TopoLoadだけにhidden truthを与えない。
- cost、latency、success profileを共有する。
- threshold tuning budgetを揃える。
- Oracleを主要比較に使わない。
- baselineの弱い実装を意図的に採用しない。

## Required tests

- same input trace
- same random draws
- same model profiles
- policy isolation
- no state leakage between runs
- baseline expected behaviour
- ablation actually disables component
- deterministic output

## Required outputs

- `topoload/policies/`
- `tests/topoload/test_baseline_fairness.py`
- `tests/topoload/test_ablations.py`
- `docs/topoload/implementation/baseline-contract.md`

## Acceptance criteria

- checkerが任意caseを一つ選び、全policyへ同一observable sequenceが渡ることをtraceで確認できる。
- ScalarDifficultyRouterが合理的なstrong baselineである。
- RecurrenceOnlyBreakerがTopoDialogue signalを公平に使う。
- destructive compression baselineの情報損失が明示的に記録される。
- ablation結果からcomponent contributionを分離できる。

## Checker focus

- straw baseline
- hidden information asymmetry
- unequal tuning
- policy-specific random seed
- baselineだけ遅くする実装
- FullTopoLoadだけに例外処理がある箇所

## Hand over

公平性上の判断、baselineの既知制約、checker指摘を`docs/topoload/implementation/T05-hand_over.md`へ記録する。
