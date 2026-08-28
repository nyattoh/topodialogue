# 05 — Loop detection

## Goal
Detect **recurrent low-progress regions**, not repeated words and not merely repeated topics.

A discussion may productively revisit the same topic. Intervention should trigger only when recurrence co-occurs with low progress and structural repetition.

## Inputs
For each time t:
- dense state embedding `z_t`;
- active semantic nodes/edges in snapshot `x_t`;
- recent transition motifs;
- provenance-aware new-node counts;
- optional semantic-progress metric.

Use a sliding window W, excluding the most recent short neighborhood when searching for meaningful returns.

## Component 1 — semantic recurrence
One simple starting statistic:

`R_t = max_{i in [t-W, t-gap]} cosine(z_t, z_i)`

Better robust variant:

`R_t = mean(top_k similarities above epsilon)`

A recurrence plot can be defined as:

`Rec(i,j) = 1[d(z_i,z_j) < epsilon]`.

From this matrix, compute return rate, diagonal/vertical structure, or simpler revisitation counts. Start simple and preserve the matrix for later analysis.

## Component 2 — graph-state recurrence
Represent each snapshot by a weighted set of normalized active nodes/relations. Compute weighted Jaccard or graph-feature similarity against earlier snapshots.

`G_t = max similarity(snapshot_t, snapshot_i)`.

This catches recurrence missed by generic embeddings and allows interpretable evidence such as “same SelfClaim + same Constraint set returned.”

## Component 3 — user-originated novelty decay
Let `U_t` be the fraction/weighted mass of active semantic nodes newly introduced by the user within the current window.

A simple decay term:

`D_novelty = 1 - normalized(U_t)`.

Novelty is type-sensitive: a genuinely new Constraint or Counterfactual may matter more than a new named entity.

## Component 4 — semantic progress decay
Prefer an external or independently defined progress metric when possible. The 2026 “Semantic Progress via Information Gain” paper is a strong baseline/reference.

For Phase 1, implement both:
- `progress_simple`: distance / cluster coverage / novelty-based proxy;
- optional `progress_information_gain` adapter if reproduced faithfully.

Convert low progress to a loop component:

`D_progress = 1 - normalized(progress)`.

## Component 5 — repeated transition motif
Examples:
- `Desire -> Constraint -> Rejection -> GlobalSelfClaim`
- `Question(same frame) -> Uncertainty -> Question(same frame) -> Uncertainty`
- `OptionGeneration -> FeasibilityFilter -> OptionRemoval`

Phase 1 can encode motifs as short sequences of node-type/edge-type signatures and compute recurrence with n-grams or edit distance.

## Component 6 — constraint persistence
High persistence is not inherently bad. It matters when it repeatedly eliminates newly generated candidates.

Example metric:
- fraction of candidate Desire/Action nodes inhibited by the same Constraint categories within W;
- repeated `inhibits` edges from same normalized Constraint node.

## Composite LoopScore
Start with interpretable weighted combination, not a learned black box:

`raw_t = a*R_t + b*G_t + c*D_novelty + d*D_progress + e*M_t + f*C_t`

`LoopScore_t = sigmoid(raw_t - bias)`

where:
- `R_t`: embedding recurrence
- `G_t`: graph recurrence
- `D_novelty`: novelty decay
- `D_progress`: semantic-progress decay
- `M_t`: motif recurrence
- `C_t`: repeated constraint persistence

All components must be returned in `LoopDecision` for inspection.

## Trigger logic
Avoid noisy single-turn triggers.

Suggested initial logic:
- `LoopScore > high_threshold` for `n_confirm` turns, OR
- one very high score plus explicit self-recurrence language (“we are back at the same thing”) if annotated;
- after intervention, enter cooldown for N turns;
- use hysteresis: release only when `LoopScore < low_threshold`.

## Candidate defaults for tests only
Do not treat these as research conclusions:
- W = 12 turns
- gap = 3
- high_threshold = 0.72
- low_threshold = 0.48
- n_confirm = 2
- cooldown = 3 user turns

Expose every value in config.

## Evidence output
The detector should explain itself mechanically, e.g.:

```json
{
  "score": 0.81,
  "evidence": [
    "state similarity to turn 8 = 0.91",
    "same self_claim active in turns 8, 11, 14",
    "user-originated novelty below baseline for 4 turns",
    "same feasibility constraint inhibited 3 candidate nodes"
  ]
}
```

Do not ask an LLM to generate the loop score.

## Evaluation of detector itself
Human annotators label windows as:
- productive revisit;
- recurrent/stuck;
- ambiguous.

Report:
- precision/recall/F1;
- calibration of LoopScore;
- false-intervention rate;
- time-to-detection;
- component ablations.

## Later TDA extension
Only after the simpler detector is validated:
- build point clouds from `z_t` or graph embeddings;
- test Mapper for trajectory visualization;
- test persistent H1 features for recurrent geometry;
- compare incremental predictive value over recurrence features.

If TDA adds no predictive or explanatory value, omit it from the final system.