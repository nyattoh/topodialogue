from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

Speaker = Literal["user", "assistant", "system"]
Provenance = Literal["user", "assistant", "system", "extractor", "heuristic"]
NodeType = Literal["concept", "affect", "body", "context", "desire", "constraint", "value", "self_claim", "counterfactual", "action_pattern", "uncertainty"]

class DialogueTurn(BaseModel):
    model_config = ConfigDict(extra="allow")
    turn_id: str
    session_id: str = "default"
    speaker: Speaker
    text: str
    timestamp: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class EvidenceSpan(BaseModel):
    turn_id: str
    start_char: int | None = None
    end_char: int | None = None
    quote_hash: str | None = None

class SemanticNode(BaseModel):
    node_id: str
    type: NodeType
    label: str
    normalized_key: str | None = None
    confidence: float = Field(default=.95, ge=0, le=1)
    salience: float = Field(ge=0, le=1, default=1)
    provenance: Provenance
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    first_seen_turn: str
    last_seen_turn: str
    active: bool = True

class SemanticEdge(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    relation: Literal["supports", "conflicts_with", "inhibits", "enables", "co_occurs", "precedes", "same_theme_as", "changes_under", "derived_from"]
    confidence: float = Field(ge=0, le=1)
    provenance: Provenance
    evidence: list[EvidenceSpan] = Field(default_factory=list)

class StateSnapshot(BaseModel):
    snapshot_id: str
    turn_id: str
    active_node_ids: list[str]
    active_edge_ids: list[str] = Field(default_factory=list)
    state_embedding_ref: str | None = None
    user_token_count: int = 0
    assistant_token_count: int = 0

class LoopComponents(BaseModel):
    recurrence: float = Field(ge=0, le=1)
    graph_cycle: float = Field(ge=0, le=1)
    novelty_decay: float = Field(ge=0, le=1)
    semantic_progress_decay: float = Field(ge=0, le=1)
    motif_recurrence: float = Field(ge=0, le=1)
    constraint_persistence: float = Field(ge=0, le=1)

class LoopDecision(BaseModel):
    turn_id: str
    score: float = Field(ge=0, le=1)
    is_loop: bool
    components: LoopComponents
    evidence_turn_ids: list[str] = Field(default_factory=list)
    detector_version: str = "phase1-v1"
    threshold: float
    cooldown_active: bool = False
    reason: str = ""

class OperatorDecision(BaseModel):
    decision_id: str
    turn_id: str
    operator: str
    rule_ids: list[str] = Field(default_factory=list)
    alternatives: list[tuple[str, float]] = Field(default_factory=list)
    rendered_question: str | None = None
    introduced_candidate_answers: list[str] = Field(default_factory=list)

class OutcomeWindow(BaseModel):
    intervention_decision_id: str
    horizon_turns: int
    new_user_node_ids: list[str] = Field(default_factory=list)
    new_assistant_node_ids: list[str] = Field(default_factory=list)
    user_originated_novelty: float = Field(ge=0)
    semantic_progress: float = Field(ge=0, le=1)
    escaped: bool
    explicit_resonance: float | None = None
    cognitive_load: float | None = None
    notes: list[str] = Field(default_factory=list)
