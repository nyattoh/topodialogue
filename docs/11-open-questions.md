# 11 — Open questions

These are deliberate unknowns. Codex should not silently decide them as if settled research facts.

## State representation
1. Should `z_t` embed only the latest user turn, the last user+assistant pair, a structured state serialization, or a learned graph embedding?
2. Should loop detection be user-only to avoid measuring assistant stylistic recurrence?
3. How should Japanese ellipsis, repetition, and speech-recognition noise affect extraction?

## Graph extraction
4. Which node types are reliable enough for automatic extraction?
5. Should relation extraction be LLM-based, rule-based, or hybrid?
6. How should contradictory nodes be merged/linked without collapsing them?

## Loop definition
7. How many returns constitute a loop?
8. How to distinguish productive revisiting from stuck recurrence?
9. Is low semantic progress necessary for all loops, or are some high-novelty loops still unproductive?
10. Does loop detection need a participant-specific baseline?

## Semantic progress
11. Can the 2026 information-gain metric be adapted when the implicit question itself changes during exploration?
12. Should progress be goal-conditioned, user-conditioned, or frame-conditioned?

## Operator policy
13. Is a fixed operator taxonomy sufficient?
14. Should the system ask permission before a strong frame shift?
15. How long should cooldown be?
16. Can an operator be selected by expected information gain while respecting agency constraints?

## Evaluation
17. Can annotators reliably agree on “same semantic region”?
18. What is the best contamination metric for assistant-seeded content?
19. How to quantify ownership: “this idea feels like mine”?
20. Which outcome matters more: immediate escape, sustained progress, or reduced load?

## TDA
21. What point cloud should persistent homology operate on?
22. How should temporal order enter the construction?
23. Does H1 persistence add anything beyond recurrence plots / temporal graphs?
24. Can Mapper provide useful interpretable maps for human annotation?

## Memory / RAG
25. What exactly is stored in a transition episode?
26. How to retrieve an old successful intervention without overfitting one user's history?
27. How to handle a previously successful operator that later becomes annoying or invalid?

## Local models
28. Can a small local multilingual model extract nodes reliably enough?
29. Is local embedding + remote renderer a useful privacy/quality compromise?
30. Can extraction be distilled into non-LLM classifiers after annotation data exists?

## Publication
31. Is the strongest first paper primarily cs.CL, cs.AI, or HCI/CSCW?
32. Should the Topo source theory appear as motivation only, with the empirical paper using conservative state-space terminology?
33. Is a second HCI paper on rendering sovereignty/body gate cleaner than combining it into the algorithm paper?

## Recommended stance now
For the first implementation and paper, answer only the questions necessary to test H1–H4. Keep everything else modular.