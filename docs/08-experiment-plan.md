# 08 — Experiment plan

## Study 0 — formative case replay
Purpose: engineering sanity check only; not generalization evidence.

Use `examples/formative-case.jsonl` and verify:
- repeated semantic region is detected before the intervention;
- `constraint_removal` ranks highly;
- user-originated novelty rises after the intervention;
- the new concepts are not counted as assistant-originated.

## Study 1 — synthetic controlled dialogues
Generate/author small scenarios with known structures:
- exact lexical repetition;
- paraphrased semantic loop;
- productive revisit with genuine new evidence;
- repeated global self-claim plus counterexample;
- constraint-filter loop;
- topic repetition without stuckness;
- assistant-induced novelty contamination.

The executable six-case geometry gate is `examples/synthetic/manifest.json`:
exact closed recurrence, productive spiral-like revisit, open trajectory,
assistant-induced recurrence, user-originated escape, and speaker drift. Run
`python -m topodialogue.cli validate-synthetic`. This gate validates operational
labels and provenance; it does not validate a unique geometric embedding.

The robustness and feature-source ablation grid is executable as:

`python -m topodialogue.cli benchmark-synthetic --output output/empirical/synthetic-robustness-v1.json`

Its current 252-run result is documented in `docs/15-empirical-validation.md`.
The severe text-only ablation failure is a blocking result for natural-dialogue
accuracy claims, not a cosmetic implementation issue.

Target: 100–500 sequences for fast iteration.

Evaluate detector components and false positives.

## Study 2 — human-annotated natural dialogues
After privacy/ethics review, create an anonymized set of long exploratory dialogues. Do not begin with clinical or crisis conversations.

Annotate loop windows and intervention opportunities.

Software readiness: annotation aggregation, unresolved-tie preservation,
pairwise agreement, automatic-event scoring, display-condition assignment, and
descriptive response summaries are implemented. Run `study-dry-run` to verify
these paths using constructed data. No human observation has yet been
collected, so Study 2 remains pending rather than complete.

Compare:
- lexical baseline;
- embedding recurrence only;
- graph recurrence only;
- recurrence + novelty/progress;
- full Phase-1 LoopScore.

## Study 3 — intervention comparison
At matched detected-loop states, compare response policies:

A. `VanillaFollowUp`: ordinary LLM follow-up inside current frame  
B. `DiversePrompt`: ask LLM to produce a “different question” without explicit operator  
C. `RandomOperator`: choose an operator randomly  
D. `RuleTopoDialogue`: rule-based operator selection

Primary outcomes:
- UON@3
- Escape@3
- ASC
- intrusion/load

Secondary:
- semantic progress
- explicit resonance

## Study 4 — Transition RAG (Phase 2)
Add memory of prior intervention episodes.

Baselines:
- no memory;
- vector retrieval of similar text;
- vector retrieval of similar state signature;
- structured transition retrieval.

Question: does retrieving previous `loop -> operator -> outcome` improve operator choice?

## Study 5 — learned operator policy (Phase 2)
Use offline contextual bandit / supervised ranking before RL.

Features:
- LoopComponents
- active node-type distribution
- dominant constraint categories
- recent failed operators
- user load indicators

Labels/reward from Study 3/4.

## Study 6 — TDA increment (Phase 3)
Only run after a reliable baseline exists.

Compare:
- recurrence features alone;
- recurrence + Mapper summaries;
- recurrence + persistent homology features.

Report incremental predictive value and computational cost.

## Robustness checks
- at least two embedding models;
- Japanese and English subsets if data permits;
- paraphrase perturbation;
- varying window sizes / thresholds;
- removing assistant turns from embeddings;
- user-only vs joint-state embeddings;
- short vs long conversations.

## Ablations
- remove graph recurrence;
- remove novelty decay;
- remove progress decay;
- remove constraint persistence;
- remove provenance correction;
- remove cooldown;
- replace rule policy with random.

## Statistical plan — preliminary
For intervention experiments, prefer mixed-effects models or paired comparisons because multiple windows may come from the same participant/conversation.

Pre-register primary metrics and exclusion criteria before the main user study.

Do not choose thresholds on the final test set.
