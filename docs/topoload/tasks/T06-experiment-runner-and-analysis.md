# T06 — Experiment runner・集計・結果生成

- 推奨maker: GPT-5.6 Terra / high
- 推奨checker: GPT-5.6 Sol / high
- 種別: reproducible evaluation
- 依存: T02–T05
- 次task: T07, T08

## Objective

事前登録configから全policy × split × seedを再現可能に実行し、raw eventから表・図・claim候補までを一方向に生成する。

## Read first

1. `study/topoload/preregistration-v0.1.md`
2. `study/topoload/analysis-plan-v0.1.md`
3. `study/topoload/config/preregistered-v0.1.json`
4. `docs/topoload/03-claim-boundaries.md`
5. T03–T05 hand over documents

## Required pipeline

```text
validated config
  -> immutable run manifest
  -> policy runs
  -> raw JSONL events
  -> validated tidy metrics
  -> statistical summaries
  -> tables／figures
  -> machine-readable claim evidence table
```

raw resultを手修正しない。

## Required outputs

```text
scripts/run_topoload_study.py
scripts/analyse_topoload_study.py
output/topoload/<run-id>/
  run-manifest.json
  raw/
  metrics/
  tables/
  figures/
  logs/
  claim-evidence.json
```

## Run manifest

- date／timezone
- repository commit SHA
- dirty status
- config hash
- fixture manifest hash
- model profile version
- actual model／effort, real-model stageのみ
- seed
- commands
- environment／dependency version
- excluded runs and reason

## Required tables

1. quality–resource frontier
2. task-family quality
3. heavy-model calls／compute units
4. false／missed disclusion
5. time-to-recovery／loop length
6. queue／burst metrics
7. canonical fidelity
8. ablations
9. sensitivity
10. negative results／failed hypotheses

## Figure rules

- raw point又はdistributionを可能な範囲で示す。
- error barの定義を書く。
- dual axisで効果を誇張しない。
- task familyを全体平均だけで隠さない。
- resultがないcellをゼロにしない。

## Statistical requirements

- paired comparison
- confidence intervals
- non-inferiority evaluation
- effect size
- calibration curve, applicableの場合
- multiple comparison policy
- sensitivity analysis

## Acceptance criteria

- clean checkoutから一つのdocumented commandで再生成できる。
- same config／seedでraw resultが一致する、又はreal provider差がmanifestに残る。
- test splitのthreshold再調整がない。
- quality非劣性を満たさないresource reductionは「成功」と表示されない。
- energy列はinstrumented run以外で生成されない。
- claim-evidence tableが論文の各result sentence候補をspecific table／metricへ結ぶ。

## Verification

- small smoke run
- full offline run
- malformed result rejection
- interrupted run resume／refusal policy
- second clean regeneration
- generated-file idempotence

## Hand over

run ID、主要結果、失敗仮説、data caveat、未実行stageを`output/topoload/<run-id>/T06-hand_over.md`へ記録する。
