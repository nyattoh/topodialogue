# 15 — Empirical validation status

## What was tested on 16 August 2026

The executable benchmark `synthetic-robustness-v1` evaluates all six declared
trajectory cases under:

- seven recurrence thresholds: 0.35 to 0.65 in steps of 0.05;
- three projection seeds: 11, 1729, and 104729;
- two feature conditions: declared semantic annotations and a text-only
  ablation in which those annotations are removed.

This produces 252 deterministic runs. The machine-readable result is
`output/empirical/synthetic-robustness-v1.json`.

## Result

| Feature condition | Runs | Shape match | Provenance match | Joint match |
|---|---:|---:|---:|---:|
| Declared annotations | 126 | 100.0% | 100.0% | 100.0% |
| Text-only ablation | 126 | 7.1% | 7.1% | 7.1% |

The operational outputs were invariant to projection seed in all tested
conditions. This supports the narrow claim that display rotation induced by a
seed change does not alter the operational classification.

The text-only failure is the more important result. Five of six cases had zero
joint matches across the tested grid. The open-trajectory case matched in 9 of
21 text-only runs. Thus the present lexical fallback is not an adequate
substitute for declared semantic/event features.

## What this establishes

1. Given the declared feature representation, the six known structures are
   reproduced across the tested threshold range.
2. Operational labels do not depend on the visual projection seed.
3. Removing the declared representation exposes a severe input-layer failure.

## What this does not establish

- accuracy on natural dialogue;
- agreement between independent human annotators;
- benefit for accessibility or personalisation;
- causal benefit of any display or intervention;
- a uniquely correct geometry of meaning.

The result is therefore a controlled computational experiment, not a completed
participant validation. The next gate is the independently annotated study in
`study/empirical-v1/`.

## Participant-study software gate

The repository also contains executable infrastructure for the next gate:

- strict-majority aggregation of two or more independent annotation files;
- explicit preservation of tied labels as unresolved;
- pairwise Cohen's kappa and positive-class F1;
- precision, recall, and F1 for automatic event candidates against resolved
  reference labels;
- deterministic cyclic Latin-square assignment across transcript-only, 2D,
  and layered-3D conditions;
- complete-response, range, assignment, exclusion, and answer-key validation;
- descriptive condition summaries with an explicit non-causal scope note.

`output/empirical/study-dry-run-v1.json` exercises these paths using constructed
data marked `synthetic: true`. It is software verification only. Human
annotation agreement and display effects remain unmeasured until consented,
independent observations are collected.

## Reproduction

```powershell
python -m topodialogue.cli benchmark-synthetic --output output/empirical/synthetic-robustness-v1.json
python -m topodialogue.cli study-dry-run --output output/empirical/study-dry-run-v1.json
python -m pytest -q
node --test visualizer/trajectory-analysis.test.js
```

The report contains SHA-256 hashes for the manifest and each case file, the
full run grid, confusion counts, threshold summaries, and the explicit scope
boundary.
