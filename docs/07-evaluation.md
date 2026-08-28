# 07 — Evaluation

## Core requirement
The system should not receive credit merely because the **assistant** introduced an interesting new topic. The key outcome is whether the **user** generates new semantic structure after an intervention.

## 1. Loop detection metrics
- Window-level precision / recall / F1 against human labels
- AUROC / AUPRC for candidate loops
- calibration error of `LoopScore`
- time-to-detection
- false intervention rate during productive revisiting

## 2. User-Originated Novelty (UON)
Define semantic nodes first introduced in user turns after intervention.

A simple weighted form:

`UON_K = sum(weight(type_i) * novelty_i for new user nodes within K turns) / normalization`

Suggested initial type weights are configurable, not normative:
- Desire 1.2
- Value 1.2
- Counterfactual 1.1
- Constraint 1.0
- ActionPattern 1.1
- Concept 0.7
- named entity 0.3

Novelty can combine:
- graph-new node/key;
- embedding distance from prior user nodes;
- new relation pattern;
- new cluster membership.

Assistant-introduced concepts do not count as full UON.

## 3. Assistant Suggestion Contamination (ASC)
Estimate how much post-intervention content was seeded by assistant candidates.

`ASC = semantic overlap(new_user_nodes, assistant_introduced_candidate_nodes)`

Report UON both raw and contamination-adjusted.

A deliberately non-leading operator should have low ASC.

## 4. Semantic Progress (SP)
Implement at least two variants:
1. a simple reproducible proxy;
2. a reproduction/adapter inspired by He et al. 2026 information-gain formulation if feasible.

Because exploratory dialogue may change the effective question, also report cluster coverage / new relation growth rather than relying on a single fixed-goal metric.

## 5. Escape@K
Binary or graded outcome after detected loop:

`Escape@K = 1` if within K user turns:
- LoopScore falls below release threshold;
- UON exceeds threshold;
- and recurrence remains lower for at least N turns.

Report K = 1, 3, 5.

## 6. Resonance / self-recognition
Human rating, e.g. 1–5:
- “This question opened a different angle.”
- “The assistant put words in my mouth.” (reverse)
- “I could recognize the new idea as mine.”

Do not equate resonance with objective truth.

## 7. Agency Preservation Score (APS)
Composite research metric, initially exploratory:

Positive:
- UON
- explicit ownership (“that came from me / that fits”)
- low suggestion contamination

Negative:
- leading questions
- assistant-first candidate concepts later adopted unchanged
- repeated intervention despite rejection

Keep component scores visible; do not publish only a single composite.

## 8. Cognitive Load / Intrusion
Self-report after intervention:
- effort required to answer;
- felt pressure to produce an answer;
- felt intrusiveness;
- desire to continue.

Important: “desire to continue” is a safety/UX signal, not a reward for maximizing session length.

## 9. Operator reward for Phase 2
Candidate reward:

`r = l1*UON + l2*SP + l3*Escape + l4*Resonance - l5*ASC - l6*Intrusion - l7*Load`

All terms normalized. Publish ablations and sensitivity to weights.

## 10. Human annotation scheme
Annotators label:
- `loop_state`: productive_revisit / stuck_recurrence / ambiguous
- `frame`: current explanatory/search frame
- `operator_applicable`: none / one-or-more
- `assistant_leading`: none / mild / strong
- `user_new_region`: no / weak / clear

Use at least two annotators and report agreement. Develop annotation guidance using synthetic examples before exposing annotators to sensitive real dialogue.

## 11. Negative results that matter
The research is still valuable if:
- embedding recurrence is too noisy;
- human loop labels have low agreement;
- operators increase novelty but also leadingness;
- simple ordinary follow-up performs equally well;
- TDA adds no value;
- learned policy does not beat rules.

Design the code to make these findings visible rather than hiding them.