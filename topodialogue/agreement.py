"""Agreement measures for independently produced interaction annotations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Any


EVENT_TYPES = ("revisit", "repair", "rejection", "adoption", "handover", "reframing", "pause")


@dataclass(frozen=True)
class LabelAgreement:
    label: str
    observed_agreement: float
    cohen_kappa: float | None
    positive_f1: float | None
    positives_a: int
    positives_b: int


def _turn_labels(payload: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for row in payload.get("turns", []):
        turn_id = str(row["turn_id"])
        labels = {str(label) for label in row.get("labels", [])}
        unknown = labels - set(EVENT_TYPES)
        if unknown:
            raise ValueError(f"unknown event labels for {turn_id}: {sorted(unknown)}")
        result[turn_id] = labels
    return result


def compare_annotations(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare two annotators over the same turn universe.

    Kappa is null when chance agreement is one.  Positive-class F1 is null
    when neither annotator assigned the label.  Those degenerate cases must not
    be reported as perfect human agreement.
    """
    a, b = _turn_labels(left), _turn_labels(right)
    if set(a) != set(b):
        missing_left = sorted(set(b) - set(a))
        missing_right = sorted(set(a) - set(b))
        raise ValueError(
            f"turn universes differ; missing_left={missing_left}, missing_right={missing_right}"
        )
    turn_ids = sorted(a)
    rows: list[LabelAgreement] = []
    for label in EVENT_TYPES:
        pairs = [(label in a[turn_id], label in b[turn_id]) for turn_id in turn_ids]
        n = len(pairs)
        agree = sum(left_value == right_value for left_value, right_value in pairs)
        positives_a = sum(left_value for left_value, _ in pairs)
        positives_b = sum(right_value for _, right_value in pairs)
        observed = agree / n if n else 0.0
        p_a = positives_a / n if n else 0.0
        p_b = positives_b / n if n else 0.0
        expected = p_a * p_b + (1 - p_a) * (1 - p_b)
        kappa = None if expected == 1 else (observed - expected) / (1 - expected)
        true_positive = sum(x and y for x, y in pairs)
        denominator = positives_a + positives_b
        f1 = None if denominator == 0 else 2 * true_positive / denominator
        rows.append(LabelAgreement(label, observed, kappa, f1, positives_a, positives_b))
    return {
        "case_id": left.get("case_id") or right.get("case_id"),
        "annotator_a": left.get("annotator_id", "a"),
        "annotator_b": right.get("annotator_id", "b"),
        "turn_count": len(turn_ids),
        "labels": [asdict(row) for row in rows],
        "interpretation_note": (
            "These statistics describe the supplied independent annotations only; "
            "they do not validate the automatic candidate extractor."
        ),
    }


def aggregate_annotations(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate independent annotations without hiding disagreement.

    A strict majority creates an adjudicated label. A tied label is retained
    in ``unresolved_labels`` and is not silently treated as absent.
    """
    if len(payloads) < 2:
        raise ValueError("at least two independent annotation files are required")
    case_ids = {str(payload.get("case_id", "")) for payload in payloads}
    if len(case_ids) != 1 or not next(iter(case_ids)):
        raise ValueError("all annotation files must have the same non-empty case_id")
    annotator_ids = [str(payload.get("annotator_id", "")) for payload in payloads]
    if any(not value for value in annotator_ids) or len(set(annotator_ids)) != len(annotator_ids):
        raise ValueError("annotator_id values must be non-empty and unique")
    if any(payload.get("independent_before_adjudication") is not True for payload in payloads):
        raise ValueError("all annotations must declare independent_before_adjudication=true")

    mappings = [_turn_labels(payload) for payload in payloads]
    universe = set(mappings[0])
    if any(set(mapping) != universe for mapping in mappings[1:]):
        raise ValueError("turn universes differ across annotation files")

    turns = []
    for turn_id in sorted(universe):
        accepted: list[str] = []
        unresolved: list[str] = []
        votes: dict[str, int] = {}
        for label in EVENT_TYPES:
            positive = sum(label in mapping[turn_id] for mapping in mappings)
            votes[label] = positive
            if positive > len(mappings) / 2:
                accepted.append(label)
            elif positive * 2 == len(mappings):
                unresolved.append(label)
        turns.append({
            "turn_id": turn_id,
            "labels": accepted,
            "unresolved_labels": unresolved,
            "positive_votes": votes,
        })

    pairwise = [
        compare_annotations(payloads[left], payloads[right])
        for left, right in combinations(range(len(payloads)), 2)
    ]
    return {
        "schema_version": "topodialogue-adjudication-v1",
        "case_id": next(iter(case_ids)),
        "annotator_ids": annotator_ids,
        "annotator_count": len(payloads),
        "decision_rule": "strict majority; ties remain unresolved",
        "turns": turns,
        "pairwise_agreement": pairwise,
        "scope_note": (
            "This aggregation preserves tied labels for human adjudication. "
            "It does not establish the validity of the label ontology."
        ),
    }


def evaluate_event_predictions(
    reference: dict[str, Any], predicted_events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score event candidates against resolved reference labels by turn."""
    reference_map = _turn_labels(reference)
    predicted_map = {turn_id: set() for turn_id in reference_map}
    for event in predicted_events:
        turn_id = str(event.get("turn_id", ""))
        label = str(event.get("event_type", ""))
        if turn_id not in predicted_map:
            raise ValueError(f"prediction refers to unknown turn_id: {turn_id}")
        if label not in EVENT_TYPES:
            raise ValueError(f"prediction has unknown event_type: {label}")
        predicted_map[turn_id].add(label)

    label_rows: list[dict[str, Any]] = []
    totals = {"true_positive": 0, "false_positive": 0, "false_negative": 0}
    for label in EVENT_TYPES:
        tp = sum(label in reference_map[turn_id] and label in predicted_map[turn_id] for turn_id in reference_map)
        fp = sum(label not in reference_map[turn_id] and label in predicted_map[turn_id] for turn_id in reference_map)
        fn = sum(label in reference_map[turn_id] and label not in predicted_map[turn_id] for turn_id in reference_map)
        totals["true_positive"] += tp
        totals["false_positive"] += fp
        totals["false_negative"] += fn
        precision = None if tp + fp == 0 else tp / (tp + fp)
        recall = None if tp + fn == 0 else tp / (tp + fn)
        f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
        label_rows.append({
            "label": label, "true_positive": tp, "false_positive": fp,
            "false_negative": fn, "precision": precision, "recall": recall, "f1": f1,
        })

    micro_precision = None if totals["true_positive"] + totals["false_positive"] == 0 else totals["true_positive"] / (totals["true_positive"] + totals["false_positive"])
    micro_recall = None if totals["true_positive"] + totals["false_negative"] == 0 else totals["true_positive"] / (totals["true_positive"] + totals["false_negative"])
    micro_f1 = None if micro_precision is None or micro_recall is None or micro_precision + micro_recall == 0 else 2 * micro_precision * micro_recall / (micro_precision + micro_recall)
    defined_f1 = [row["f1"] for row in label_rows if row["f1"] is not None]
    return {
        "case_id": reference.get("case_id"),
        "turn_count": len(reference_map),
        "labels": label_rows,
        "micro": {**totals, "precision": micro_precision, "recall": micro_recall, "f1": micro_f1},
        "macro_f1_over_defined_labels": None if not defined_f1 else sum(defined_f1) / len(defined_f1),
        "scope_note": "Scores apply only to the supplied resolved reference labels.",
    }


def synthetic_annotation_dry_run() -> dict[str, Any]:
    """Exercise aggregation and extractor scoring with declared fake labels."""
    turns_a = [
        {"turn_id": "t1", "labels": ["handover"]},
        {"turn_id": "t2", "labels": ["repair"]},
        {"turn_id": "t3", "labels": ["revisit", "reframing"]},
        {"turn_id": "t4", "labels": ["adoption"]},
    ]
    turns_b = [
        {"turn_id": "t1", "labels": ["handover"]},
        {"turn_id": "t2", "labels": ["repair"]},
        {"turn_id": "t3", "labels": ["revisit"]},
        {"turn_id": "t4", "labels": ["adoption"]},
    ]
    payloads = [
        {
            "schema_version": "topodialogue-independent-annotation-v1",
            "case_id": "synthetic-annotation-case",
            "annotator_id": annotator_id,
            "independent_before_adjudication": True,
            "synthetic": True,
            "turns": turns,
        }
        for annotator_id, turns in (("synthetic-a", turns_a), ("synthetic-b", turns_b))
    ]
    adjudication = aggregate_annotations(payloads)
    predictions = [
        {"turn_id": "t1", "event_type": "handover"},
        {"turn_id": "t2", "event_type": "repair"},
        {"turn_id": "t3", "event_type": "revisit"},
        {"turn_id": "t4", "event_type": "rejection"},
    ]
    evaluation = evaluate_event_predictions(adjudication, predictions)
    return {
        "synthetic": True,
        "annotations": payloads,
        "adjudication": adjudication,
        "predictions": predictions,
        "evaluation": evaluation,
        "scope_note": "Pipeline dry run only; these are constructed labels, not human annotations.",
    }
