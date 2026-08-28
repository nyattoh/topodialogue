"""Auditable strategy proposals and user-controlled rendering decisions.

This module evaluates declared, constructed interaction records. It does not
infer a person's stable preferences, culture, disability, emotion, or intent.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Literal

from pydantic import BaseModel, Field, model_validator


HistoryCondition = Literal[
    "no_history", "text_rag", "event_rag", "relation_graph",
    "user_controlled_adaptation",
]
Strategy = Literal[
    "ordinary_follow_up", "reframe", "constraint_change", "wait", "revisit",
    "return_choice",
]
UserDecision = Literal["adopt", "reject", "repair", "correct", "delete", "stop"]


class ConditionCapabilities(BaseModel):
    condition: HistoryCondition
    retrieves_text: bool = False
    retrieves_events: bool = False
    represents_relations: bool = False
    proposes_strategy: bool = False
    requires_acceptance: bool = False


class UserControls(BaseModel):
    can_inspect: bool = False
    can_correct: bool = False
    can_delete: bool = False
    can_stop: bool = False
    can_change_rendering: bool = False
    acceptance_before_execution: bool = False


class StrategyEpisode(BaseModel):
    episode_id: str
    condition: HistoryCondition
    proposed_strategy: Strategy
    executed_strategy: Strategy | None = None
    user_decision: UserDecision
    evidence_refs: list[str] = Field(default_factory=list)
    proposal_uncertainty: float = Field(ge=0, le=1)
    user_controls: UserControls
    requested_rendering: str | None = None
    final_rendering: str | None = None
    history_deleted: bool = False
    intervention_stopped: bool = False
    user_originated_novelty: float = Field(ge=0, le=1)
    assistant_induced_recurrence: float = Field(ge=0, le=1)
    interaction_burden: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_control_contract(self) -> "StrategyEpisode":
        if self.condition == "user_controlled_adaptation":
            if not self.user_controls.acceptance_before_execution:
                raise ValueError("adaptive proposals require acceptance before execution")
            if self.user_decision == "adopt" and self.executed_strategy is None:
                raise ValueError("an adopted proposal must declare the executed strategy")
            if self.user_decision != "adopt" and self.executed_strategy is not None:
                raise ValueError("a rejected, corrected, deleted, or stopped proposal cannot execute")
        if self.user_decision == "delete" and not self.history_deleted:
            raise ValueError("delete decisions must be reflected in history_deleted")
        if self.user_decision == "stop" and not self.intervention_stopped:
            raise ValueError("stop decisions must be reflected in intervention_stopped")
        if self.requested_rendering and self.final_rendering != self.requested_rendering:
            raise ValueError("the final rendering must follow the user's explicit request")
        return self


class TopologyGate(BaseModel):
    baseline_explanatory_score: float = Field(ge=0, le=1)
    richer_topology_score: float = Field(ge=0, le=1)
    minimum_gain: float = Field(gt=0, le=1)


class AgencyFixture(BaseModel):
    schema_version: str = "topodialogue-agency-v1"
    capabilities: list[ConditionCapabilities]
    episodes: list[StrategyEpisode]
    topology_gate: TopologyGate
    scope_note: str


def audit_fixture(fixture: AgencyFixture) -> dict:
    """Aggregate declared outcomes without turning adoption into a sole target."""
    capability_map = {row.condition: row for row in fixture.capabilities}
    if len(capability_map) != 5:
        raise ValueError("all five distinct history conditions are required")
    expected = {
        "no_history": (False, False, False, False),
        "text_rag": (True, False, False, False),
        "event_rag": (False, True, False, False),
        "relation_graph": (False, True, True, False),
        "user_controlled_adaptation": (False, True, True, True),
    }
    for condition, signature in expected.items():
        row = capability_map[condition]
        actual = (row.retrieves_text, row.retrieves_events,
                  row.represents_relations, row.proposes_strategy)
        if actual != signature:
            raise ValueError(f"capability confound for {condition}: {actual}")

    grouped: dict[str, list[StrategyEpisode]] = defaultdict(list)
    for episode in fixture.episodes:
        grouped[episode.condition].append(episode)

    summaries = {}
    for condition in expected:
        rows = grouped[condition]
        if not rows:
            raise ValueError(f"no episodes for {condition}")
        count = len(rows)
        decisions = {name: sum(row.user_decision == name for row in rows)
                     for name in ("adopt", "reject", "repair", "correct", "delete", "stop")}
        summaries[condition] = {
            "episode_count": count,
            "decision_counts": decisions,
            "adoption_rate": decisions["adopt"] / count,
            "mean_user_originated_novelty": sum(row.user_originated_novelty for row in rows) / count,
            "mean_assistant_induced_recurrence": sum(row.assistant_induced_recurrence for row in rows) / count,
            "mean_interaction_burden": sum(row.interaction_burden for row in rows) / count,
        }

    adaptive = grouped["user_controlled_adaptation"]
    controls = (
        "can_inspect", "can_correct", "can_delete", "can_stop",
        "can_change_rendering", "acceptance_before_execution",
    )
    control_coverage = {
        name: sum(getattr(row.user_controls, name) for row in adaptive) / len(adaptive)
        for name in controls
    }
    contract_violations = []
    for row in adaptive:
        if row.user_decision != "adopt" and row.executed_strategy is not None:
            contract_violations.append(f"{row.episode_id}:executed_without_adoption")
        if row.requested_rendering and row.final_rendering != row.requested_rendering:
            contract_violations.append(f"{row.episode_id}:rendering_override_ignored")

    gate = fixture.topology_gate
    gain = gate.richer_topology_score - gate.baseline_explanatory_score
    richer_topology_justified = gain >= gate.minimum_gain
    return {
        "schema_version": fixture.schema_version,
        "episode_count": len(fixture.episodes),
        "condition_summaries": summaries,
        "adaptive_control_coverage": control_coverage,
        "contract_violations": contract_violations,
        "suggestion_only": True,
        "topology_gate": {
            **gate.model_dump(),
            "observed_gain": gain,
            "richer_topology_justified": richer_topology_justified,
            "decision": "retain_operational_metrics" if not richer_topology_justified else "evaluate_richer_topology",
        },
        "scope_note": fixture.scope_note,
        "interpretation_note": (
            "Constructed outcomes validate accounting and control semantics only; "
            "they do not establish benefit, personalisation quality, or causal effect."
        ),
    }
