import pytest
from pydantic import ValidationError

from topodialogue.agency import AgencyFixture, StrategyEpisode, audit_fixture


def load_fixture():
    return AgencyFixture.model_validate_json(
        open("examples/agency/synthetic-strategy-cases.json", encoding="utf-8").read()
    )


def test_fixture_separates_retrieval_representation_and_adaptation():
    report = audit_fixture(load_fixture())
    assert report["episode_count"] == 15
    assert list(report["condition_summaries"]) == [
        "no_history", "text_rag", "event_rag", "relation_graph",
        "user_controlled_adaptation",
    ]
    assert report["contract_violations"] == []


def test_user_controlled_adaptation_is_suggestion_only_and_complete():
    report = audit_fixture(load_fixture())
    assert report["suggestion_only"] is True
    assert set(report["adaptive_control_coverage"].values()) == {1.0}
    adaptive = report["condition_summaries"]["user_controlled_adaptation"]
    assert adaptive["decision_counts"] == {
        "adopt": 1, "reject": 0, "repair": 0, "correct": 1, "delete": 0, "stop": 1,
    }


def test_rejected_adaptive_proposal_cannot_execute():
    payload = load_fixture().episodes[-1].model_dump()
    payload.update(user_decision="reject", executed_strategy="reframe", intervention_stopped=False)
    with pytest.raises(ValidationError, match="cannot execute"):
        StrategyEpisode.model_validate(payload)


def test_rendering_request_is_authoritative():
    payload = load_fixture().episodes[-2].model_dump()
    payload.update(requested_rendering="timeline", final_rendering="spiral")
    with pytest.raises(ValidationError, match="final rendering"):
        StrategyEpisode.model_validate(payload)


def test_richer_topology_fails_the_declared_gain_gate():
    gate = audit_fixture(load_fixture())["topology_gate"]
    assert gate["observed_gain"] == pytest.approx(0.01)
    assert gate["richer_topology_justified"] is False
    assert gate["decision"] == "retain_operational_metrics"
