# TopoDialogue / 対話位相検索 — Phase 1 executable prototype

This repository contains an offline, reproducible implementation of the Phase-1
research loop. It reads annotated JSONL dialogue, detects recurrent low-progress
semantic regions, selects a transparent coordinate-changing operator, renders a
non-leading question, and measures user-originated novelty after the intervention.

It is a research instrument, not a therapy, diagnosis, or production chat service.

## Quick start

Requires Python 3.11+. Install the package and test dependencies in a virtual
environment, then run:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m topodialogue.cli analyze examples/formative-case.jsonl
```

The demo uses `FakeEmbedder`, so it does not download a model or call a network
service. It prints per-turn recurrence, novelty decay, LoopScore, the selected
operator/question, and the post-intervention UON/Escape@5 outcome.

## 3D dialogue explorer

ブラウザで会話ファイルを投入し、再現可能な意味特徴projection、発話軌跡、再訪、
由来別新規性、`closed loop / spiral revisit / escape / open trajectory` の操作的分類を
Three.jsで確認できます。時間・再訪回数・抽象度・代替成分の4つの高さを切り替え、
表示artifactも同じ画面で報告します。

```powershell
python -m http.server 4173 -d visualizer
```

`http://localhost:4173`を開き、`examples/formative-case.jsonl`をドロップするか、
ファイル選択で読み込んでください。ChatGPT書き出し（`messages`配列）と、
llm-rallyの`seed`/`turn`ログにも対応しています。データはブラウザ内で処理されます。
Three.js 0.170.0とOrbitControlsは`visualizer/vendor/three/`へ固定版を同梱しており、
表示・解析ともネットワーク接続を必要としません。

研究用の再現可能な解析JSONはCLIからも生成できます。

```powershell
python -m topodialogue.cli trajectory examples/synthetic/spiral-revisit.jsonl -o report.json
python -m topodialogue.cli validate-synthetic
python -m topodialogue.cli benchmark-synthetic --output output/empirical/synthetic-robustness-v1.json
python -m topodialogue.cli study-dry-run --output output/empirical/study-dry-run-v1.json
node --test visualizer/trajectory-analysis.test.js
```

実会話を研究用に扱う場合は、選択的な伏字ではなく全文を非公開にした派生JSONを
生成できます。元の会話ファイルはローカルに残り、公開JSONには話者順、粗い記述
メタデータ、仮名化した再訪領域、観測可能なinteraction event候補だけが入ります。

```powershell
python -m topodialogue.cli prepare-case "path\to\conversation.json" --output-dir examples\real --case-id real-case-01
python -m topodialogue.cli agreement annotator-a.json annotator-b.json -o agreement.json
```

ブラウザの右パネルでは `revisit / repair / rejection / adoption / handover /
reframing / pause` を個別に表示・非表示にできます。これらは表面的な手掛かりから
抽出した候補であり、意図・感情・心理状態の推定ではありません。ラベル定義と
人手検証手順は [`docs/14-interaction-events.md`](docs/14-interaction-events.md) にあります。

Chromium E2Eは`visualizer/e2e-smoke.js`で、合成螺旋、AI誘発ループ、脱出、
任意の実会話ファイルの読込を検査できます。`PLAYWRIGHT_CORE_ENTRY`と
`BROWSER_EXECUTABLE`を環境に合わせて指定してください。

軸、判定式、合成期待値、失敗表示の定義は
[`docs/13-trajectory-validation.md`](docs/13-trajectory-validation.md)に固定しています。

## Architecture

`adapters` loads and normalizes JSONL; `extraction` preserves annotated semantic
nodes and evidence; `embeddings` supplies deterministic test vectors plus an
explicit optional Sentence Transformers adapter; `graph` and `recurrence` compute
interpretable state recurrence; `detector` applies weighted LoopScore,
hysteresis, and cooldown; `operators` applies the rule policy; `outcomes` keeps
novelty user/assistant provenance separate; `store` provides a local SQLite
source of truth. The CLI composes these modules without requiring an LLM.

## Configuration and extension

`DetectorConfig` exposes window, thresholds, component weights, hysteresis,
cooldown, and Escape horizon. The default fixture extractor is deliberately
simple. A future extractor must return validated Pydantic models with evidence
spans and confidence; it must not silently make an external call. The optional
`SentenceTransformerEmbedder` is only instantiated explicitly by a caller.

## Known limitations

- Phase 1 uses annotated nodes and a hashed character-ngram fake embedding; it is
  not a claim of embedding quality or mathematical topological invariance.
- The 3D X/Y coordinates are fixed-seed display projections. Visual curvature or
  upward motion is not itself evidence of progress; the report keeps operational
  recurrence/progress metrics separate from rendering.
- Graph recurrence is currently weighted set recurrence, with graph-cycle hooks
  retained for later temporal-graph experiments.
- Escape is an operational metric (new user nodes plus progress), not a claim
  about a person's mental state.
- SQLite persistence is available as a library component; the local web UI and
  CLI are analysis/export surfaces only and do not expose authentication, cloud
  storage, or multi-agent orchestration.

## Next research steps

Compare against ordinary follow-up and embedding-only baselines, add anonymized
human annotations, measure false-positive intervention cost, and only then test
multiple embedding models or a learned operator policy. Any later topology or
multimodal work must earn its place through an ablation result.

## One-sentence idea
Long conversations can repeatedly return to the same semantic region even when the wording changes. TopoDialogue models the dialogue as a trajectory through a structured semantic state space, detects low-progress recurrent regions, and switches from “deeper questioning in the same frame” to a **transformation operator** that changes assumptions, viewpoint, abstraction level, or constraints.

## Why this bundle exists
The core insight arose from a formative human–AI conversation: repeated attempts to answer “what do you want?” stayed near the same self-description (“I do not know / I have no desire”). When the assistant removed feasibility constraints—money, body, age, failure cost—the user immediately generated many concrete desires. The research question is whether that kind of escape can be detected and operationalized without the assistant simply inventing the answer.

## Important distinction
The first prototype is **not** a theorem about mathematical topology. It is a state-space / temporal-graph / recurrence prototype. Topological Data Analysis is reserved for a later phase if it adds explanatory or predictive value.

## Bundle map
- `AGENTS.md` — instructions for Codex
- `CODEX_TASK.md` — concrete first implementation task
- `docs/00-research-scope.md` — questions, hypotheses, contribution boundary
- `docs/01-conceptual-model.md` — conceptual bridge from Topo to dialogue dynamics
- `docs/02-related-work.md` — current literature map and gap hypothesis
- `docs/03-architecture.md` — MVP architecture
- `docs/04-data-schema.md` — structured state/graph schema
- `docs/05-loop-detection.md` — detection algorithm
- `docs/06-transformation-operators.md` — operator taxonomy and policy
- `docs/07-evaluation.md` — metrics, especially user-originated novelty
- `docs/08-experiment-plan.md` — baselines, datasets, ablations
- `docs/09-safety-privacy.md` — local-first, provenance, non-clinical boundary
- `docs/10-paper-outline.md` — paper structure
- `docs/11-open-questions.md` — unresolved research decisions
- `docs/12-source-synthesis.md` — synthesis of the two supplied source texts plus the formative dialogue
- `examples/formative-case.jsonl` — anonymized synthetic case derived from the formative pattern
- `examples/expected-events.json` — expected detector/operator events
- `references.bib` — seed bibliography
- `source/` — original supplied conceptual source files

## Recommended implementation order
1. Parse dialogue turns into `DialogueTurn`.
2. Generate deterministic embeddings in tests; optional real embedding adapter.
3. Create per-turn `StateSnapshot` and provenance-aware semantic nodes.
4. Maintain a temporal semantic graph.
5. Compute recurrence, novelty, semantic-progress proxy, and motif recurrence.
6. Produce `LoopDecision` with cooldown/hysteresis.
7. Select a transformation operator from rules.
8. Generate a question through a provider interface.
9. Log whether later **user turns** introduce new semantic regions.
10. Run the synthetic evaluation harness.

## Phase boundaries
### Phase 1 — implement now
Single orchestrator, local state store, recurrence detector, rule-based operator policy, evaluation harness.

### Phase 2 — after Phase 1 evidence
Transition RAG over prior loop→operator→outcome episodes; learned/bandit operator policy; multiple embedding models; human annotation tooling.

### Phase 3 — only if justified
Persistent homology / Mapper, dynamic internal multi-agent decomposition, body gate, rendering sovereignty UI, sensor integration.

## Research discipline
A successful demo is not evidence that the theory is correct. The implementation should make the main claims falsifiable: loop detection must be compared against baselines; operator intervention must be compared against ordinary follow-up questions; novelty must be attributed to the user rather than assistant suggestions; and false-positive intervention cost must be measured.
