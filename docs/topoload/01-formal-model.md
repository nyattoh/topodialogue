# TopoLoad 最小数理モデル v0.1

## 1. 設計原則

v0.1は、状態空間上の移動を「目標へ沿う成分」と「目標から外れる成分」に分ける。目的は人間の意図や心理を推定することではなく、明示されたtask goalに対する計算経路の挙動を観測することである。

## 2. 記号

時刻又はstep `t` において:

- `z_t in R^d`: task／reasoning state
- `v_t = z_t - z_{t-1}`: state transition
- `G_t in R^{d x k}`: goal subspaceのbasis
- `P_t`: `G_t`へのprojection matrix
- `c_t in [0,1]`: goal subspace推定のconfidence
- `D_t`: task demand又は必要能力の推定量
- `R_t`: TopoDialogue型のrecurrence／low-progress score
- `J_t`: burst／queue impulse
- `K_t`: switching cost又は経路変更コスト

`G_t`はv0.1では、明示されたtask specification、rubric、expected state featureから決定する。暗黙の人間的欲求から推定しない。

正規直交basisなら:

```text
P_t = G_t G_t^T
```

一般basisなら:

```text
P_t = G_t (G_t^T G_t)^(-1) G_t^T
```

特異又は不安定な場合はpseudo-inverseを用い、condition numberとfallbackを記録する。

## 3. 方向付き成分

### 3.1 Aligned magnitude

```text
A_t = ||P_t v_t||_2
```

目標部分空間に沿ってどれだけ移動したかを示す。大きいこと自体は良否を意味しない。

### 3.2 Signed progress

1次元goal vector `g_t`を正規化した `g_hat_t` に対して:

```text
p_t = <v_t, g_hat_t>
```

複数次元の場合は、rubric-defined progress function `phi(z)`を使い:

```text
p_t = phi(z_t) - phi(z_{t-1})
```

とする。`phi`をembedding距離だけで定義しない。task-specific oracle又は独立graderを優先する。

### 3.3 Lateral magnitude

```text
L_t = ||(I - P_t) v_t||_2
```

目標部分空間では説明されない移動量である。探索、必要な準備、誤逸脱を同じ値だけで区別できないため、単独で遮断条件にしない。

### 3.4 Reverse drift

```text
B_t = max(0, -p_t)
```

明示された進捗関数に対して後退した成分を表す。

### 3.5 Lateral ratio

```text
rho_t = L_t / (A_t + epsilon)
```

scale差を吸収する補助量。`A_t`が小さいと不安定になるため、absolute thresholdと併用する。

## 4. Recurrenceとの統合

TopoDialogueから以下の機械的特徴を受け取る。

- semantic recurrence
- graph-state recurrence
- novelty decay
- progress decay
- repeated transition motif
- constraint persistence

v0.1では既存`LoopScore`を再計算せず、adapter経由で `R_t` とcomponent evidenceを受け取る。TopoLoadは「ループかどうか」の正本判定器にはならない。

## 5. Disclusion hazard

方向情報にconfidenceを掛け、低confidence時の誤遮断を防ぐ。

```text
H_t = c_t * (
    w_L * norm(L_t)
  + w_rho * norm(rho_t)
  + w_B * norm(B_t)
  + w_R * norm(R_t)
  + w_M * norm(M_t)
)
```

ここで `M_t` はtool-cycle、wrong-premise reinforcement、branch explosion等の構造的逸脱特徴である。

goal confidenceが低い場合はhard disclusionではなく、別の曖昧性scoreを使う。

```text
U_t = 1 - c_t
```

`U_t`が高い場合の既定actionは `HOLD` 又は `CLARIFY` であり、`DEEP`でも`DISCLUDE`でもない。

## 6. Burst／damping signal

queue又はrequest pressure `q_t` に対し、例えば:

```text
J_t = max(0, q_t - EWMA(q)_t)
```

context pressureは別量として保持する。

```text
X_t = used_context_t / context_budget_t
```

`J_t`又は`X_t`が閾値を超えた場合、canonical recordを変更せず、次のderived／scheduling actionのみ許可する。

- request queueing
- adaptive rate limiting
- batching
- derived context selection
- loss-declared summarisation
- retrieval narrowing
- lower-cost modelへの一時dispatch

禁止:

- canonical observationの要約置換
- contradiction又はprovenanceの黙示的削除
- stale derived viewを正本扱いすること
- dampingを理由にgoalを変更すること

## 7. Controller state

### 7.1 Modes

- `LOCAL`: bounded taskを軽量経路で処理
- `DEEP`: aligned high-demand taskを高能力経路で処理
- `DISCLUDE`: 現在経路を停止し、replan／operator changeへ移る
- `DAMP`: queue／working representationを緩衝する
- `HOLD`: goal confidence不足、evidence不足、又はconflicting control signalのため保留する

### 7.2 最小policy

```text
if c_t < theta_conf:
    action = HOLD
elif J_t > theta_burst or X_t > theta_context:
    action = DAMP
elif H_t > theta_enter for n_confirm steps:
    action = DISCLUDE
elif D_t > theta_deep and H_t < theta_safe:
    action = DEEP
else:
    action = LOCAL
```

優先順位は固定の研究対象である。例えばsecurity hard guardはこのpolicyの外側に置き、TopoLoadの効果へ混入させない。

### 7.3 Hysteresis

```text
enter DISCLUDE when H_t > theta_enter
leave DISCLUDE when H_t < theta_exit
where theta_exit < theta_enter
```

- `n_confirm`: 連続確認step数
- `cooldown`: 経路変更直後に再変更しないstep数
- hard guard以外は単一stepで切り替えない

## 8. Disclusion action contract

`DISCLUDE`は単なるエラー終了ではない。次の順を守る。

1. 現在のroute ID、reason codes、evidence、costを記録する。
2. canonical task specificationとsource evidenceを保持する。
3. current working planを無効化するが、削除しない。
4. TopoDialogue型operator又は明示的replan strategyを選ぶ。
5. 新routeを新しいIDで開始する。
6. recovery outcomeをK step後に評価する。

理由コード例:

- `lateral_drift_high`
- `reverse_progress`
- `recurrent_low_progress`
- `tool_cycle`
- `wrong_premise_reinforcement`
- `branch_explosion`
- `goal_ambiguous`
- `burst_pressure`

## 9. Optimisation objective

controller policy `pi` について、概念上は次を最小化する。

```text
min_pi E[
    lambda_C * compute_cost
  + lambda_F * task_failure
  + lambda_L * lateral_exposure
  + lambda_Q * queue_cost
  + lambda_S * switching_cost
  + lambda_D * false_disclusion
]
```

制約:

```text
task_quality(pi) >= baseline_quality - delta
canonical_fidelity(pi) = 1
false_disclusion_rate(pi) <= alpha
```

v0.1はpolicy learningを行わない。透明なrule-based policyで各項の測定可能性を確認する。

## 10. Identifiabilityと交絡

少なくとも次を分離して記録する。

- high demandとlong output
- lateral explorationとharmful deviation
- model failureとrouter failure
- goal estimator failureとcontroller failure
- context compression failureとcanonical-store failure
- provider latencyとpolicy latency
- cost reductionとenergy reduction

## 11. v0.1で固定しないもの

- embedding model
- goal basis dimension `k`
- component weight
- threshold
- model tier名
- provider
- energy conversion factor

これらをconfig化し、benchmark split又は評価結果を見てから都合よく変更しない。

## 12. 反証条件

次の結果なら主要仮説は支持されない。

- direction featureを加えてもscalar baselineを再現可能に上回らない。
- false disclusionがquality gainを相殺する。
- goal confidenceを導入してもambiguous-goal failureが改善しない。
- dampingがcanonical fidelity又はcontradiction retentionを損なう。
- switching cost込みでは常時高能力モデルより総costが増える。
- 結果が特定embedding、単一seed、単一providerだけに依存する。
