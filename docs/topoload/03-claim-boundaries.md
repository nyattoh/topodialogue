# TopoLoad 主張境界 v0.1

## 1. 現時点の位置付け

TopoLoadは、方向付き計算負荷に基づく動的dispatch／route disclusionの**設計仮説**である。現時点で実証済みの新規アーキテクチャではない。

## 2. 言ってよい表現

- 「我々は操作的枠組みを提案し、比較可能なprototypeで評価する」
- 「咬合力学は設計着想であり、対応関係は比喩的である」
- 「goal-aligned componentとlateral componentを区別する」
- 「方向情報のincremental valueをbaselineとablationで検証する」
- 「token、model call、latency、recovery、queueを測定した」
- 「energyは物理計測した範囲だけ報告する」
- 「negative resultは仮説の適用境界を示す」

## 3. 言ってはいけない表現

証拠がない限り、次を禁止する。

- 「咬合構造を直接AIへ転用した」
- 「生体が最適なのでAIでも最適である」
- 「犬歯誘導が人間の普遍的な唯一の咬合様式である」
- 「token削減により電力を同率で削減した」
- 「Flash Attentionはsparse attentionである」
- 「speculative decodingでは大型modelが不要になる」
- 「hallucination、injection、loopを根絶する」
- 「人間の思考方向又は心理状態を測定する」
- 「topological invariantを発見した」
- 「世界初」「唯一」「新規」と、体系的調査前に断定する

## 4. 咬合比喩の対応表

この表は説明用であり、実装仕様ではない。

| 着想 | TopoLoadで残す抽象原理 | 残さないもの |
|---|---|---|
| 小さな接触領域 | bounded local workへの選択的資源投入 | 応力式をtoken効率へそのまま適用 |
| 臼歯の荷重支持 | aligned high-demand workを安定した高能力経路へ送る | 特定咬合力の数字をmodel capacityへ換算 |
| 側方運動時の離開 | harmful lateral routeを増強せず切り替える | canine guidanceの普遍性又は筋活動機序の断定 |
| 歯周組織の緩衝 | burstを時間・queue・derived viewで平滑化する | 生体粘弾性式をそのままschedulerへ当てる |

## 5. TopoDialogueとの境界

TopoDialogueはrecurrent low-progress regionを検出し、変換演算子を選ぶ。TopoLoadはその特徴を一入力として、計算経路の継続、増強、離開、緩衝を決める。

- TopoLoadの成功をTopoDialogueの成功として報告しない。
- TopoDialogueのLoopScoreを、方向付き負荷のground truthとして扱わない。
- productive revisitとharmful lateral deviationを別ラベルにする。
- TopoDialogue codeを変更する場合は、既存golden testを壊さないadapter追加を優先する。

## 6. TopoPhaseとの境界

TopoPhaseのcanonical／derived分離を設計契約として参照する。

- v0.1はTopoPhaseのresource efficiencyを実証したことにしない。
- TypeScript engineを無理にPythonへ移植しない。
- canonical fidelityをfixture contractで検証し、cross-repository統合は後段へ送る。
- summary、vector、token、search indexを正本として扱わない。

## 7. Securityとの境界

TopoLoadはsecurity classifierではない。

- injection-like fixtureはgoal conflictのcontrol behaviourだけを測る。
- actual security enforcementは独立guardrailへ委ねる。
- security hard stopをTopoLoadの精度へ加算しない。
- benign explorationの誤遮断を必ず測る。

## 8. Energyとの境界

- token数、model tier、latency、GPU utilisationはenergyの代理になり得るが同一ではない。
- energy claimには、measurement boundary、hardware、idle subtraction、sampling、batch sizeが必要。
- simulatorでは`compute unit`と呼び、joule又はkWhへ換算しない。

## 9. 新規性判定の条件

新規性は次が完了するまで「novelty hypothesis」とする。

- model routing
- cascade／speculative inference
- circuit breaker／agent loop detection
- goal-conditioned planning
- state-space projection
- queueing／admission control
- context compression／memory provenance
- biologically inspired computing

各領域の一次資料を検索し、operation-level claim matrixを作る。名称が違っても同じ操作を行う先行研究を除外しない。

## 10. Kill criteria

次のいずれかなら「TopoLoad」という独立研究線を縮小又は終了する。

- directional featureが既存scalar routerへ一貫した予測価値を追加しない。
- goal specification costがresource savingを上回る。
- false disclusionが許容範囲を超え、confidence／hysteresisでも改善しない。
- canonical-preserving dampingが既存provenance-aware compressionと操作的に同一で、追加価値がない。
- biomechanical framingが方法理解を助けず、誤解だけを増やす。

終了時もbenchmark、negative result、再現scriptを保存する。
