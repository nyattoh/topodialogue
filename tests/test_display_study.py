import pytest

from topodialogue.display_study import (
    CONDITIONS,
    balanced_assignments,
    summarise_responses,
    synthetic_dry_run,
    validate_responses,
)


def _responses(assignments):
    return [
        {
            **row,
            "trajectory_answer": "closed_loop",
            "response_time_ms": 1000,
            "confidence_1_to_5": 3,
            "ease_1_to_5": 3,
            "disorientation_1_to_5": 2,
            "felt_led_1_to_5": 1,
            "stopped": False,
            "deletion_requested": False,
        }
        for row in assignments["assignments"]
    ]


def test_assignment_is_balanced_for_three_by_three_design():
    report = balanced_assignments(["p1", "p2", "p3"], ["c1", "c2", "c3"])
    assert report["condition_counts"] == {condition: 3 for condition in CONDITIONS}
    assert len(report["assignments"]) == 9
    p2_first = next(
        row for row in report["assignments"]
        if row["participant_id"] == "p2" and row["presentation_order"] == 1
    )
    assert p2_first["case_id"] == "c2"


def test_validation_rejects_condition_mismatch():
    assignments = balanced_assignments(["p1"], ["c1"])
    responses = _responses(assignments)
    responses[0]["condition"] = "layered_3d"
    with pytest.raises(ValueError, match="condition mismatch"):
        validate_responses(assignments, responses)


def test_summary_excludes_stopped_rows_and_is_descriptive():
    assignments = balanced_assignments(["p1", "p2", "p3"], ["c1"])
    responses = _responses(assignments)
    responses[0]["stopped"] = True
    report = summarise_responses(assignments, responses, {"c1": "closed_loop"})
    assert report["response_count"] == 3
    assert report["included_count"] == 2
    assert report["excluded_stopped_or_deleted"] == 1
    assert "Descriptive statistics only" in report["scope_note"]


def test_synthetic_dry_run_is_complete_and_balanced():
    report = synthetic_dry_run()
    assert report["synthetic"] is True
    assert report["summary"]["response_count"] == 27
    assert report["assignments"]["condition_counts"] == {condition: 9 for condition in CONDITIONS}
