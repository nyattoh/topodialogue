# 04 — Data schema

The schema must distinguish **observed text**, **extracted structure**, **inference**, and **evaluation outcome**.

## Core models

```python
class DialogueTurn(BaseModel):
    turn_id: str
    session_id: str
    speaker: Literal["user", "assistant"]
    text: str
    timestamp: datetime | None = None
    metadata: dict[str, Any] = {}

class EvidenceSpan(BaseModel):
    turn_id: str
    start_char: int | None = None
    end_char: int | None = None
    quote_hash: str | None = None

class SemanticNode(BaseModel):
    node_id: str
    type: Literal[
        "concept", "affect", "body", "context", "desire", "constraint",
        "value", "self_claim", "counterfactual", "action_pattern", "uncertainty"
    ]
    label: str
    normalized_key: str | None = None
    confidence: float
    salience: float
    provenance: Literal["user", "assistant", "extractor", "heuristic"]
    evidence: list[EvidenceSpan]
    first_seen_turn: str
    last_seen_turn: str
    active: bool = True

class SemanticEdge(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    relation: Literal[
        "supports", "conflicts_with", "inhibits", "enables", "co_occurs",
        "precedes", "same_theme_as", "changes_under", "derived_from"
    ]
    confidence: float
    provenance: Literal["user", "assistant", "extractor", "heuristic"]
    evidence: list[EvidenceSpan]

class StateSnapshot(BaseModel):
    snapshot_id: str
    turn_id: str
    active_node_ids: list[str]
    active_edge_ids: list[str]
    state_embedding_ref: str | None
    user_token_count: int
    assistant_token_count: int
```

## Loop data

```python
class LoopComponents(BaseModel):
    recurrence: float
    graph_cycle: float
    novelty_decay: float
    semantic_progress_decay: float
    motif_recurrence: float
    constraint_persistence: float

class LoopDecision(BaseModel):
    turn_id: str
    score: float
    is_loop: bool
    components: LoopComponents
    evidence_turn_ids: list[str]
    detector_version: str
    threshold: float
    cooldown_active: bool
```

## Operator data

```python
class OperatorDecision(BaseModel):
    decision_id: str
    turn_id: str
    operator: str
    rule_ids: list[str]
    alternatives: list[tuple[str, float]]
    rendered_question: str | None
    introduced_candidate_answers: list[str] = []
```

The `introduced_candidate_answers` field is critical for agency evaluation. A question such as “Would you like to travel to Wales?” injects a candidate. A question such as “If money and body constraints disappeared, what appears first?” does not specify content.

## Outcome data

```python
class OutcomeWindow(BaseModel):
    intervention_decision_id: str
    horizon_turns: int
    new_user_node_ids: list[str]
    new_assistant_node_ids: list[str]
    user_originated_novelty: float
    semantic_progress: float
    escaped: bool
    explicit_resonance: float | None
    cognitive_load: float | None
    notes: list[str] = []
```

## Provenance rules
1. If a concept first appears in assistant text and the user later repeats it, it remains **assistant-introduced** unless the user independently reformulates it beyond a configured semantic-distance threshold.
2. If the user rejects an assistant suggestion, store the rejection; do not create a positive Desire node.
3. Inferred affect/body states must never have `provenance=user` unless explicitly stated.
4. Global self-claims and later counterexamples coexist; do not overwrite history.
5. Every model-produced node must have confidence < 1.0 and evidence.

## Storage
Phase 1 SQLite tables:
- `turns`
- `nodes`
- `edges`
- `node_evidence`
- `snapshots`
- `embeddings`
- `loop_decisions`
- `operator_decisions`
- `outcomes`

NetworkX is a derived analytical view, not the authoritative persistence layer.