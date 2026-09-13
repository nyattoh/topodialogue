# T04 — 合成fixtureとcounterexample生成

- 推奨maker: GPT-5.6 Luna / high
- 推奨checker: GPT-5.6 Terra / high
- 種別: bounded high-volume generation
- 依存: T01, T02
- 次task: T05, T06

## Objective

事前登録したtask familyについて、個人会話を使わず、deterministicで多様な合成trajectory、expected event、negative controlを生成する。

## Read first

1. `study/topoload/benchmark-spec-v0.1.md`
2. `study/topoload/config.schema.json`
3. `docs/topoload/spec/model-v0.1.md`
4. `docs/topoload/spec/controller-v0.1.md`
5. `docs/topoload/spec/test-obligations-v0.1.md`
6. `docs/topoload/03-claim-boundaries.md`

## Required families

- aligned local
- aligned hard
- wrong-premise deepening
- cyclic tool plan
- branch explosion
- prompt conflict
- productive exploration
- ambiguous／changing goal
- burst pressure
- mixed load

## Required outputs

```text
examples/topoload/
  train/
  calibration/
  test/
  stress/
  manifests/
```

各caseは最低限:

- case ID
- family
- seed
- visible observation
- hidden generator truth
- explicit goal specification
- goal confidence source
- transition series
- demand／pressure series
- allowed controller actions
- forbidden assumption
- expected invariants

を持つ。

## Generator requirements

- seedで再生成可能
- train／calibration／testのparameter rangeを分離
- single-template paraphrase量産にしない
- easy lexical cueだけでfamily判定できないcaseを含む
- productive explorationを十分含める
- ambiguous goalをlateral deviationのpositive caseにしない
- hidden truthをcontroller inputへ混入させない

## Counterexamples

最低限、次を作る。

1. lateral magnitudeは高いが必要な探索
2. recurrenceは高いがproductive refinement
3. demandは高いが完全にaligned
4. demandは低いが危険なroute cycle
5. goal confidenceが低く、どの方向判定も不安定
6. burst中にcontradiction evidenceが圧縮対象になりやすいcase
7. threshold付近を往復するoscillation case
8. route switch自体がcostを悪化させるcase

## Non-goals

- claim判断
- threshold tuning
- test resultに合わせたcase修正
- real personal dialogue使用
- LLM APIによるruntime生成

## Acceptance criteria

- schema validationを全caseが通る。
- 同一seedでbyte-stable又はsemantic-stableに再生成できる。
- split間重複検査がある。
- hidden fieldsがpolicy inputへ出ないtestがある。
- checkerがfamily labelを見ずにcaseを読み、少なくとも主要control distinctionを確認できる。
- positive／negative case数と難易度分布がmanifestにある。

## Verification

fixture generatorを二回実行し、hash又はcanonicalised outputが一致することを確認する。0件、1件、複数件のcollection boundaryもtestする。

## Hand over

case count、coverage、generator version、known biasを`examples/topoload/manifests/T04-hand_over.md`へ記録する。
