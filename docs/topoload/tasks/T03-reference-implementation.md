# T03 — Offline参照実装

- 推奨maker: GPT-5.6 Terra / xhigh
- 推奨checker: GPT-5.6 Sol / high
- 種別: implementation
- 依存: T01、可能ならT02承認済みconfig
- 次task: T05, T06

## Objective

TopoDialogue本体を壊さず、方向付き負荷controllerを独立packageとしてoffline、deterministic、inspectableに実装する。

## Read first

1. `AGENTS.md`
2. `CODEX_TASK.md`
3. `docs/topoload/spec/model-v0.1.md`
4. `docs/topoload/spec/controller-v0.1.md`
5. `docs/topoload/spec/invariants-v0.1.md`
6. `docs/topoload/spec/test-obligations-v0.1.md`
7. `study/topoload/config.schema.json`
8. 既存`topodialogue/` modulesとtests

## Suggested package

```text
topoload/
  models.py
  projection.py
  signals.py
  adapters.py
  controller.py
  damping.py
  simulator.py
  events.py
  metrics.py
  config.py
  cli.py
```

名前は変更可能だが、projection、signals、policy、damping、metricsを分離する。

## Required interfaces

- `StateObservation`
- `GoalSpecification`
- `DirectionalLoad`
- `RecurrenceSignalAdapter`
- `PressureObservation`
- `ControllerDecision`
- `RouteEvent`
- `CanonicalViewContract`
- `ModelTierProfile`

## Required behaviour

1. aligned／lateral／reverse componentを計算する。
2. invalid／non-finite inputを拒否する。
3. goal confidence不足時に`HOLD`を返す。
4. rule-based mode selectionを行う。
5. hysteresis、confirmation、cooldownを実装する。
6. 全decisionへcomponent values、threshold、reason codesを付ける。
7. `DISCLUDE`で旧routeを消さず、新route IDを発行する。
8. dampingはderived view／queueだけを変え、canonical fixtureを不変にする。
9. TopoDialogue adapterはoptionalで、既存detectorを再実装しない。
10. network／paid APIなしでtestsが通る。

## Required tests

- projection
- zero vector
- singular basis
- confidence boundary
- aligned hard routing
- lateral recurrence routing
- productive exploration negative control
- hysteresis
- cooldown
- conflicting signals
- burst damping
- canonical immutability
- contradiction preservation
- failed transaction no partial mutation
- deterministic replay

property-based testを可能な範囲で使う。

## CLI target

```bash
python -m topoload.cli simulate --config study/topoload/config/preregistered-v0.1.json
python -m topoload.cli replay examples/topoload/aligned-hard.jsonl
```

outputはJSONL event traceとhuman-readable summaryを分離する。

## Non-goals

- actual provider routing
- cloud deployment
- multi-agent orchestration
- learned policy
- cross-repository TopoPhase runtime dependency
- dashboard
- energy estimation

## Acceptance criteria

- existing TopoDialogue testsが回帰しない。
- TopoLoad testsがofflineでdeterministicに通る。
- config validation errorが明確である。
- controller decisionをLLMに生成させない。
- all state transitions are auditable。
- canonical fixture hashがdamping前後で一致する。
- READMEにexact run commandとknown limitationsがある。

## Verification

project既存gateがあればそれを正本にする。少なくとも:

```bash
python -m pytest -q
python -m topoload.cli --help
python -m topoload.cli simulate --config study/topoload/config/preregistered-v0.1.json
```

実際のcommandとexit codeを記録する。未実行の成功を報告しない。

## Hand over

実装commit、test結果、仕様からの逸脱、未実装事項を`docs/topoload/implementation/T03-hand_over.md`へ記録する。
