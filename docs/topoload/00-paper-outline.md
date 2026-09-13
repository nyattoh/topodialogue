# TopoLoad 論文骨子 v0.1

## 仮題

第一候補:

**TopoLoad: Direction-Aware Dynamic Dispatch and Route Disclusion for Efficient LLM Systems**

説明性を優先する代替案:

**Directional Computational Load: Separating Aligned Difficulty from Lateral Deviation in Dynamic LLM Routing**

咬合を前面に出す題名は、実験で対応関係の有用性が示されるまで採用しない。

## 一文要約

既存の動的routingが主としてtask difficultyをスカラー量として扱うのに対し、TopoLoadは推論状態の移動を目標部分空間への成分と直交成分へ分解し、aligned hard workは高能力経路へ、lateral deviationはroute disclusionへ、burst loadはcanonical dataを保つdampingへ振り分ける。

## Abstractで許される目標主張

1. LLM／agent taskの計算負荷には、量だけでなく目標に対する方向があるという操作的定義を提案する。
2. state transitionをaligned componentとlateral componentへ分解する最小モデルを示す。
3. difficulty escalationとroute disclusionを分離した透明なcontrollerを実装する。
4. TopoDialogue由来のrecurrence／progress特徴が、direction-only又はdifficulty-only routingへ追加価値を持つか検証する。
5. canonical observationを保持し、derived working representationだけを変形するdamping contractを評価する。
6. task quality、heavy-model usage、token、latency、false disclusion、recovery、queue pressureを同時に報告する。

Abstractで禁止する主張:

- 電力削減を、token又はmodel-call削減から推定して断定する。
- 咬合系の生体力学がそのままAIの最適設計であると述べる。
- 数学的topologyを使っていない段階でtopological invariantを主張する。
- hallucination、prompt injection、agent loopを一般に根絶すると述べる。
- 新規性調査完了前に「初の方式」と書く。

## Research questions

### RQ1 — Directional value

状態遷移の方向情報は、scalar difficultyだけを使うrouterに比べて、品質を維持しながら高コスト経路の不要な利用を減らすか。

### RQ2 — Disclusion value

lateral deviationとrecurrenceを用いるroute disclusionは、recurrence-only breaker又は固定budget breakerに比べて、false interruptionを増やさずloop継続長とrecovery stepsを減らすか。

### RQ3 — Damping value

canonical recordを不変に保ち、derived working view、queue、rateのみを調整するdampingは、burst load下でhard failure又はpeak queueを減らしつつ、矛盾・provenance・task qualityを保持するか。

### RQ4 — Incremental value of the Topo series

TopoDialogueのrecurrence／progress特徴とTopoPhase型のcanonical／derived分離は、単純なdirection routerに対して測定可能な追加価値を持つか。

### RQ5 — Failure boundary

goal directionの推定誤差、複数目的、正当な探索、productive revisitのどの条件でTopoLoadは誤って離開するか。

## 仮説

- **H1:** Full TopoLoadは、scalar difficulty routerに対してtask qualityの事前定義した非劣性範囲を満たしつつ、heavy-model calls又はtotal tokensを減らす。
- **H2:** Direction + recurrenceによるdisclusionは、recurrence-only breakerより短いtime-to-recoveryを示す。
- **H3:** goal confidenceを使わないcontrollerは、ambiguous-goal controlでfalse disclusionが増える。
- **H4:** canonical-preserving dampingは、destructive summarisation baselineよりcontradiction／provenance retentionが高い。
- **H5:** 一部taskでは方向分解の追加価値がなく、scalar routerで十分である。このnull regionを特定できる。

## 想定貢献

1. **Directional load formulation**  
   difficultyとは別に、goal-aligned progress、lateral deviation、reverse drift、recurrence、burst pressureを定義する。

2. **Transparent control policy**  
   `LOCAL / DEEP / DISCLUDE / DAMP / HOLD`の状態遷移を、閾値、hysteresis、cooldown、reason code付きで示す。

3. **Canonical-preserving damping contract**  
   正本を要約で置換せず、派生表現だけを圧縮・遅延・batchingする契約を明示する。

4. **Falsifiable benchmark**  
   aligned-hard、lateral-drift、cyclic plan、wrong-premise deepening、burst、ambiguous-goalを含む合成benchmarkとablationを提供する。

5. **Negative-result discipline**  
   direction情報が不要な条件、goal推定誤差に弱い条件、switching costが利益を上回る条件を報告する。

## 論文構成

### 1. Introduction

- 高負荷taskと逸脱taskは、ともに長い推論を生むが制御上は異なる。
- 単純な難易度routerは、難しい正攻法と、誤った前提を深掘りする高コスト逸脱を区別しにくい。
- 研究課題は「もっと強いモデルへ送るか」だけではなく「現在経路を離開すべきか」である。
- 研究質問、貢献、主張境界を提示する。

### 2. Design inspiration and non-equivalence

- 尖頭接触、垂直荷重支持、側方離開、粘弾性緩衝を、設計着想として簡潔に整理する。
- canine guidanceが唯一又は普遍的な咬合様式ではないことを明記する。
- 生体機構とAI control planeの一対一同一視を否定する。
- 比喩に依存せず、以降は数学的・操作的定義だけで議論できるようにする。

### 3. Related work

3.1 Cost／quality-aware model routing  
3.2 Cascades and speculative execution  
3.3 Agent loop detection and circuit breakers  
3.4 Semantic progress, recurrence, and long-horizon recovery  
3.5 Queueing, admission control, rate limiting, and burst smoothing  
3.6 Context compression and memory provenance  
3.7 Directional control／projection methods in state spaces  
3.8 Biomechanical inspiration in computing, used only as positioning

体系的調査前はgapを仮説として書く。

### 4. Problem formulation

- task state `z_t`
- explicit goal specification and goal subspace `G_t`
- goal confidence `c_t`
- transition `v_t = z_t - z_{t-1}`
- aligned magnitude、signed progress、lateral magnitude、reverse drift
- recurrence、burst、resource demand
- controller action set and switching cost
- quality and fidelity constraints

### 5. Method

5.1 State and goal representation  
5.2 Directional load decomposition  
5.3 Recurrence and progress adapter from TopoDialogue  
5.4 Disclusion hazard  
5.5 Hysteresis, confirmation, cooldown  
5.6 Local／deep model dispatch  
5.7 Canonical-preserving damping  
5.8 Reason codes and auditable event trace  
5.9 Safe behaviour under low goal confidence

### 6. Experimental setup

- deterministic simulator first
- optional real-model run second
- task families and split
- model-tier cost／quality profiles
- baselines
- metrics
- paired seeds and confidence intervals
- threshold preregistration
- quality non-inferiority margin

### 7. Results

7.1 Quality–resource frontier  
7.2 Heavy-model call and token reduction  
7.3 False／missed disclusion  
7.4 Recovery time and loop length  
7.5 Burst and queue behaviour  
7.6 Canonical fidelity and contradiction retention  
7.7 Ablation results  
7.8 Sensitivity to goal error and threshold drift  
7.9 Negative results

### 8. Discussion

- 難しい処理と逸脱処理を分ける価値
- productive explorationを横方向逸脱と誤認する危険
- goal specificationがcontrollerへ与える権力
- cost savingsとquality／agencyのtrade-off
- TopoDialogue、TopoPhaseとの関係
- 咬合比喩を残すべきか、方法名から外すべきか

### 9. Limitations and ethics

- state embeddingとgoal subspaceの構成依存
- 複数目的と目的変更
- 合成benchmarkから実運用への外的妥当性
- provider token accountingの違い
- energy未実測
- security detectorとの混同
- 人間の意図・感情を推定しない境界
- controllerによる過剰遮断、探索の抑制

### 10. Conclusion

方向付き負荷がscalar routingに対して追加価値を持つ条件と、持たない条件を簡潔にまとめる。咬合比喩ではなく、再現可能なcontroller、benchmark、否定可能な結果を結論の中心にする。

## Appendix

- 数式と記号表
- controller pseudocode
- task generator specification
- config and thresholds
- model／effort設定
- full ablation table
- event trace examples
- canonical／derived fidelity checks
- literature search protocol
