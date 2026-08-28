# 03 — Phase-1 architecture

## Design goal
A single-orchestrator prototype that can be tested offline. The architecture should make each research hypothesis independently measurable.

## Pipeline

```text
Dialogue turns
    |
    v
Turn normalizer
    |
    +----------------------------+
    |                            |
    v                            v
Embedding adapter          State extractor
    |                            |
    v                            v
Dense state z_t          typed StateSnapshot
    |                            |
    +-------------+--------------+
                  v
        Temporal Semantic Store
        (SQLite + graph view)
                  |
                  v
             Loop Detector
    recurrence / novelty / progress /
    repeated motifs / constraint persistence
                  |
         +--------+--------+
         |                 |
     no loop           candidate loop
         |                 |
 ordinary follow-up        v
                    Operator Selector
                         |
                         v
                    Question Renderer
                         |
                         v
                       user
                         |
                         v
                    Outcome Logger
             user-originated novelty,
             escape, resonance, load
```

## Components

### 1. `DialogueAdapter`
Input: JSONL or streaming turns.  
Output: normalized `DialogueTurn` with timestamp, speaker, text, session id.

### 2. `Embedder`
Interface:

```python
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...
```

Tests use deterministic fake embeddings. A real local multilingual embedder is optional and configured outside tests.

### 3. `StateExtractor`
Produces typed semantic nodes from each turn. Phase 1 should support two modes:
- deterministic fixture/rule extractor for tests;
- optional LLM extractor returning strict JSON/Pydantic schema.

Never discard the evidence span or provenance.

### 4. `TemporalSemanticStore`
SQLite as source of truth. NetworkX can construct an in-memory graph for analysis.

Store:
- raw/anonymized turn reference;
- state snapshots;
- semantic nodes;
- typed edges;
- embedding vectors or references;
- loop decisions;
- operator decisions;
- outcomes.

### 5. `LoopDetector`
Pure-ish numerical module. No LLM calls required.

Inputs: recent `z_t`, graph/snapshots, config.  
Output: `LoopDecision(score, is_loop, components, evidence_turns)`.

### 6. `OperatorSelector`
Phase 1: transparent rule-based policy.  
Phase 2: contextual bandit or learned policy.

Input: loop signature.  
Output: ranked operators + reason codes.

### 7. `QuestionRenderer`
Turns an operator plus current graph context into **one** concise question. Provider interface supports:
- fixture renderer for tests;
- local model;
- remote model.

The renderer must not smuggle candidate answers into the question when evaluating user-originated novelty.

### 8. `OutcomeEvaluator`
Computes short-horizon post-intervention metrics at K = 1, 3, 5 turns, including provenance-aware novelty and semantic progress.

## Why not multi-agent yet?
The supplied conceptual material distinguishes “integrating many signals toward one goal” from “supervising many independent streams.” The system should not reproduce the cognitive burden it aims to reduce. Internally splitting modules later is fine, but the user-facing interaction remains one coherent conversational process.

## Future Phase-2 extension: Transition RAG
Retrieve structured episodes:

`loop_signature -> operator -> observed outcome`

not merely similar past utterances.

Possible retrieval keys:
- active node types;
- repeated SelfClaim;
- dominant Constraint categories;
- recurrence component profile;
- user load/state;
- previous operator failures.

## Future Phase-3 extension
- Persistent homology / Mapper visualization
- learned orchestration across specialized internal agents
- Body Gate / rendering granularity
- multimodal/body signals
- user-controlled renderings

Each requires separate evidence and should not contaminate Phase-1 conclusions.