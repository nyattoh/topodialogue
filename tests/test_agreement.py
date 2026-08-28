import pytest

from topodialogue.agreement import (
    aggregate_annotations,
    compare_annotations,
    evaluate_event_predictions,
    synthetic_annotation_dry_run,
)


def _payload(annotator, rows):
    return {
        "case_id": "case-1", "annotator_id": annotator,
        "turns": [{"turn_id": turn_id, "labels": labels} for turn_id, labels in rows],
    }


def test_agreement_reports_label_kappa_and_degenerate_nulls():
    left = _payload("a", [("t1", ["repair"]), ("t2", []), ("t3", ["repair"])])
    right = _payload("b", [("t1", ["repair"]), ("t2", []), ("t3", [])])
    report = compare_annotations(left, right)
    repair = next(row for row in report["labels"] if row["label"] == "repair")
    pause = next(row for row in report["labels"] if row["label"] == "pause")
    assert repair["observed_agreement"] == pytest.approx(2 / 3)
    assert repair["positive_f1"] == pytest.approx(2 / 3)
    assert pause["cohen_kappa"] is None
    assert pause["positive_f1"] is None


def test_agreement_requires_matching_turn_universes():
    with pytest.raises(ValueError, match="turn universes differ"):
        compare_annotations(_payload("a", [("t1", [])]), _payload("b", [("t2", [])]))


def test_aggregation_uses_strict_majority_and_preserves_ties():
    left = _payload("a", [("t1", ["repair"]), ("t2", ["pause"])])
    right = _payload("b", [("t1", ["repair"]), ("t2", [])])
    left["independent_before_adjudication"] = True
    right["independent_before_adjudication"] = True
    report = aggregate_annotations([left, right])
    assert report["turns"][0]["labels"] == ["repair"]
    assert report["turns"][1]["labels"] == []
    assert report["turns"][1]["unresolved_labels"] == ["pause"]
    assert len(report["pairwise_agreement"]) == 1


def test_aggregation_rejects_non_independent_input():
    left = _payload("a", [("t1", [])])
    right = _payload("b", [("t1", [])])
    with pytest.raises(ValueError, match="independent_before_adjudication"):
        aggregate_annotations([left, right])


def test_event_prediction_evaluation_reports_micro_counts():
    reference = _payload("resolved", [("t1", ["repair"]), ("t2", ["pause"])])
    events = [
        {"turn_id": "t1", "event_type": "repair"},
        {"turn_id": "t2", "event_type": "rejection"},
    ]
    report = evaluate_event_predictions(reference, events)
    assert report["micro"]["true_positive"] == 1
    assert report["micro"]["false_positive"] == 1
    assert report["micro"]["false_negative"] == 1
    assert report["micro"]["f1"] == pytest.approx(0.5)


def test_synthetic_annotation_dry_run_exposes_unresolved_vote():
    report = synthetic_annotation_dry_run()
    t3 = next(row for row in report["adjudication"]["turns"] if row["turn_id"] == "t3")
    assert report["synthetic"] is True
    assert t3["labels"] == ["revisit"]
    assert t3["unresolved_labels"] == ["reframing"]
    assert report["evaluation"]["micro"]["true_positive"] == 3
