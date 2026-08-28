# 10 — Tentative paper outline

## Working title
**TopoDialogue: Detecting and Escaping Recurrent Semantic Loops in Long-Horizon Human–LLM Dialogue**

Alternative:
**Beyond Local Follow-Up: State-Space Transformations for Escaping Recurrent Semantic Loops in Human–LLM Dialogue**

Use “topology-aware” in the title only if the final method actually uses defensible topological machinery.

## Abstract — target claims
1. Long-horizon exploratory dialogue can revisit semantically similar states while making little progress.
2. We define an operational recurrent semantic loop using dense recurrence, temporal semantic structure, novelty/progress decay, and repeated constraint motifs.
3. We introduce transformation operators that change the search frame instead of only generating another local follow-up.
4. We introduce provenance-aware metrics that distinguish user-originated novelty from assistant-suggested novelty.
5. Experiments compare ordinary follow-up, diverse-question prompting, random operators, and rule-based operator selection.
6. Report both gains and costs: escape, novelty, contamination, cognitive load, false interventions.

## 1. Introduction
- Problem: long conversations can be locally coherent yet globally recurrent.
- Multi-turn LLMs often fail to recover after early wrong assumptions.
- Motivating formative case: “no desires” remained stable under local search; constraint removal opened a large new semantic region.
- Research challenge: detect when to change the frame without imposing an answer.
- Contributions.

## 2. Related work
2.1 Multi-turn dialogue planning in semantic space — SCOPE  
2.2 Attractor-like LLM dynamics — successive paraphrasing; model–model conversation attractors  
2.3 Semantic progress / information gain  
2.4 Multi-turn unreliability and recovery  
2.5 Long-term and graph memory — MemGPT, A-MEM, SGMem, graph-memory survey  
2.6 Dynamic orchestration  
2.7 TDA in NLP — positioned as optional/future unless used experimentally

## 3. Problem formulation
- dialogue state trajectory
- structured DialogueTopo snapshot
- candidate loop definition
- escape definition
- provenance and user-originated novelty

## 4. Method
4.1 State extraction  
4.2 Dense and graph recurrence  
4.3 Novelty/progress decay  
4.4 Composite LoopScore + hysteresis  
4.5 Transformation operator taxonomy  
4.6 Rule-based selection policy  
4.7 Non-leading question rendering  
4.8 Outcome logging

## 5. Experimental setup
- synthetic controlled set
- anonymized natural dialogue set
- human annotation
- baselines
- embedding models
- metrics
- statistical model

## 6. Results
6.1 Loop detector performance  
6.2 Intervention outcomes  
6.3 User-originated novelty vs suggestion contamination  
6.4 Operator effectiveness by loop signature  
6.5 Ablations  
6.6 Error analysis

## 7. Discussion
- when repetition is productive rather than stuck
- semantic novelty is not well-being
- agency vs novelty tradeoff
- implications for long-horizon assistants
- relation to state-space planning and memory systems
- whether “topological” language survives empirical scrutiny

## 8. Limitations and ethics
- formative origin is N=1
- state extraction errors
- cultural/language dependence
- subjective loop annotation
- sensitive-dialogue privacy
- non-clinical scope
- risk of leading users

## 9. Future work
- Transition RAG
- learned operator policy
- graph memory evolution
- TDA increment
- rendering sovereignty / body gate as separate HCI research line

## Appendix
- annotation guide
- operator templates
- schema
- hyperparameters
- synthetic examples
- prompt/model configurations

## Contribution wording discipline
Prefer:
> We propose and evaluate an operational framework...

Avoid before evidence:
> We discovered the topology of human thought...

Prefer:
> attractor-like recurrent semantic region

Avoid unless formally established:
> attractor of the human cognitive dynamical system