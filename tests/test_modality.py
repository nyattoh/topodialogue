import pytest
from pydantic import ValidationError

from topodialogue.modality import (
    CalibrationProfile,
    ModalityEvent,
    ModalityFixture,
    PathwayCase,
    UserCorrection,
    apply_user_corrections,
    audit_conversion,
    audit_fixture,
    compare_with_baseline,
)


def event(event_id, event_type, ref, *, modality="speech", observed=(), preserved=(), missing=None):
    return ModalityEvent(
        event_id=event_id, event_type=event_type, source_modality=modality,
        source_event_ref=ref, conversion_chain=[modality],
        observed_features=list(observed), preserved_features=list(preserved),
        missing_features=missing or {}, raw_signal_retained=False,
    )


def test_missingness_categories_are_explicit_and_disjoint():
    with pytest.raises(ValidationError):
        event("e1", "pause", "r1", observed=["pause"], preserved=["pause"],
              missing={"pause": "unobserved"})
    with pytest.raises(ValidationError):
        event("e1", "pause", "r1", missing={"pitch": "unknown"})


def test_conversion_audit_counts_preserved_omitted_and_false_events():
    case = PathwayCase(
        case_id="speech", transcript="same words", source_modality="speech",
        source_events=[
            event("s1", "adoption", "r1", observed=["words", "turn_order"]),
            event("s2", "handover", "r2", observed=["terminal_rise"]),
        ],
        converted_events=[
            event("c1", "adoption", "r1", observed=["words"], preserved=["words"],
                  missing={"turn_order": "conversion_failed"}),
            event("c2", "rejection", "invented", observed=["punctuation"]),
        ],
    )
    report = audit_conversion(case)
    assert report["event_preservation_rate"] == 0.5
    assert report["event_omission_rate"] == 0.5
    assert report["false_generation_rate"] == 0.5
    assert report["feature_preservation_rate"] == pytest.approx(1 / 3)
    assert report["source_feature_count"] == 3
    assert report["preserved_feature_count"] == 1
    assert report["unaccounted_missing_features"] == []


def test_user_correction_relabels_without_erasing_history():
    converted = [event("c1", "rejection", "r1")]
    corrected = apply_user_corrections(converted, [
        UserCorrection(correction_id="u1", target_event_id="c1", action="relabel",
                       replacement_event_type="handover")
    ])
    assert converted[0].event_type == "rejection"
    assert corrected[0].event_type == "handover"
    assert corrected[0].user_confirmed is True
    assert corrected[0].notes == ["relabeled by u1"]


def test_same_transcript_can_retain_distinct_observable_events():
    fixture = ModalityFixture(
        cases=[
            PathwayCase(case_id="fall", transcript="それでいい", source_modality="speech",
                        source_events=[event("s1", "adoption", "a")], converted_events=[]),
            PathwayCase(case_id="rise", transcript="それでいい", source_modality="speech",
                        source_events=[event("s2", "handover", "b")], converted_events=[]),
        ], scope_note="synthetic",
    )
    labels = [row.source_events[0].event_type for row in fixture.cases]
    assert fixture.cases[0].transcript == fixture.cases[1].transcript
    assert labels == ["adoption", "handover"]
    report = audit_fixture(fixture)
    assert report["case_count"] == 2
    assert report["aggregate_before_correction"]["event_omission_rate"] == 1.0


def test_baseline_comparison_keeps_calibration_level_explicit():
    profile = CalibrationProfile(
        profile_id="same-task-v1", baseline_level="situation",
        event_counts={"handover": 2, "pause": 2}, observation_count=4,
    )
    result = compare_with_baseline({"handover": 3, "pause": 1}, profile)
    assert result["baseline_level"] == "situation"
    assert result["rate_differences"]["handover"] == 0.25
    assert "demographic" in result["scope_note"]
