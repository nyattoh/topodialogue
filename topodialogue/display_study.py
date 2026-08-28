"""Deterministic assignment and descriptive analysis for the display study."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


CONDITIONS = ("transcript_only", "timeline_2d", "layered_3d")
TRAJECTORY_LABELS = ("closed_loop", "spiral_revisit", "open_trajectory", "escape", "ambiguous")


def balanced_assignments(participant_ids: list[str], case_ids: list[str]) -> dict[str, Any]:
    """Create a deterministic cyclic Latin-square condition schedule."""
    if not participant_ids or not case_ids:
        raise ValueError("participant_ids and case_ids must be non-empty")
    if len(set(participant_ids)) != len(participant_ids) or len(set(case_ids)) != len(case_ids):
        raise ValueError("participant_ids and case_ids must be unique")
    rows = []
    for participant_index, participant_id in enumerate(participant_ids):
        rotated_cases = case_ids[participant_index % len(case_ids):] + case_ids[:participant_index % len(case_ids)]
        for order_index, case_id in enumerate(rotated_cases):
            case_index = case_ids.index(case_id)
            rows.append({
                "participant_id": participant_id,
                "case_id": case_id,
                "condition": CONDITIONS[(participant_index + case_index) % len(CONDITIONS)],
                "presentation_order": order_index + 1,
            })
    counts = {condition: sum(row["condition"] == condition for row in rows) for condition in CONDITIONS}
    return {
        "schema_version": "topodialogue-display-assignment-v1",
        "design": "deterministic cyclic Latin square",
        "conditions": list(CONDITIONS),
        "assignments": rows,
        "condition_counts": counts,
        "case_order_rule": "cyclic rotation by participant index",
    }


def validate_responses(assignments: dict[str, Any], responses: list[dict[str, Any]]) -> None:
    expected = {
        (str(row["participant_id"]), str(row["case_id"])): row
        for row in assignments.get("assignments", [])
    }
    seen: set[tuple[str, str]] = set()
    for response in responses:
        key = (str(response.get("participant_id", "")), str(response.get("case_id", "")))
        if key in seen:
            raise ValueError(f"duplicate response for participant/case: {key}")
        seen.add(key)
        if key not in expected:
            raise ValueError(f"response has no assignment: {key}")
        assignment = expected[key]
        if response.get("condition") != assignment["condition"]:
            raise ValueError(f"condition mismatch for {key}")
        if response.get("presentation_order") != assignment["presentation_order"]:
            raise ValueError(f"presentation_order mismatch for {key}")
        if response.get("trajectory_answer") not in TRAJECTORY_LABELS:
            raise ValueError(f"invalid trajectory_answer for {key}")
        response_time = response.get("response_time_ms")
        if not isinstance(response_time, int) or response_time <= 0:
            raise ValueError(f"response_time_ms must be a positive integer for {key}")
        for field in ("confidence_1_to_5", "ease_1_to_5", "disorientation_1_to_5", "felt_led_1_to_5"):
            value = response.get(field)
            if not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"{field} must be an integer from 1 to 5 for {key}")
    if seen != set(expected):
        raise ValueError(f"response set is incomplete; missing={sorted(set(expected) - seen)}")


def summarise_responses(
    assignments: dict[str, Any], responses: list[dict[str, Any]], answer_key: dict[str, str],
) -> dict[str, Any]:
    """Return descriptive condition summaries without causal inference."""
    validate_responses(assignments, responses)
    case_ids = {str(row["case_id"]) for row in assignments["assignments"]}
    if set(answer_key) != case_ids:
        raise ValueError("answer_key must cover exactly the assigned cases")
    if any(label not in TRAJECTORY_LABELS for label in answer_key.values()):
        raise ValueError("answer_key contains an invalid trajectory label")

    included = [row for row in responses if not row.get("stopped") and not row.get("deletion_requested")]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in included:
        grouped[str(row["condition"])].append(row)
    conditions = []
    for condition in CONDITIONS:
        rows = grouped[condition]
        conditions.append({
            "condition": condition,
            "included_count": len(rows),
            "accuracy": None if not rows else sum(row["trajectory_answer"] == answer_key[row["case_id"]] for row in rows) / len(rows),
            "mean_response_time_ms": None if not rows else mean(row["response_time_ms"] for row in rows),
            "mean_confidence": None if not rows else mean(row["confidence_1_to_5"] for row in rows),
            "mean_ease": None if not rows else mean(row["ease_1_to_5"] for row in rows),
            "mean_disorientation": None if not rows else mean(row["disorientation_1_to_5"] for row in rows),
            "mean_felt_led": None if not rows else mean(row["felt_led_1_to_5"] for row in rows),
        })
    return {
        "schema_version": "topodialogue-display-summary-v1",
        "response_count": len(responses),
        "included_count": len(included),
        "excluded_stopped_or_deleted": len(responses) - len(included),
        "conditions": conditions,
        "scope_note": (
            "Descriptive statistics only. A synthetic dry run demonstrates the pipeline "
            "but is not participant evidence and supports no interface-effect claim."
        ),
    }


def synthetic_dry_run() -> dict[str, Any]:
    """Exercise the complete display-study pipeline with explicit fake data."""
    participants = [f"synthetic-p{index:02d}" for index in range(1, 10)]
    answer_key = {
        "synthetic-loop": "closed_loop",
        "synthetic-spiral": "spiral_revisit",
        "synthetic-escape": "escape",
    }
    assignments = balanced_assignments(participants, list(answer_key))
    responses = []
    for index, assignment in enumerate(assignments["assignments"]):
        expected = answer_key[assignment["case_id"]]
        condition_index = CONDITIONS.index(assignment["condition"])
        correct = (index + condition_index) % 5 != 0
        responses.append({
            **assignment,
            "trajectory_answer": expected if correct else "ambiguous",
            "response_time_ms": 28000 - condition_index * 2500 + (index % 4) * 700,
            "confidence_1_to_5": 3 + min(condition_index, 1),
            "ease_1_to_5": 3 + min(condition_index, 1),
            "disorientation_1_to_5": 3 - min(condition_index, 1),
            "felt_led_1_to_5": 2,
            "stopped": False,
            "deletion_requested": False,
            "synthetic": True,
        })
    return {
        "synthetic": True,
        "assignments": assignments,
        "responses": responses,
        "answer_key": answer_key,
        "summary": summarise_responses(assignments, responses, answer_key),
    }
