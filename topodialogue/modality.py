"""Modality provenance and conversion-loss audits.

The module records observable interaction events across input pathways.  It
does not infer emotion, disability, truthfulness, personality, or intention
from speech, gaze, timing, or assistive-technology use.
"""

from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .interaction import InteractionEventType


SourceModality = Literal[
    "direct_text", "speech", "sign", "symbol_aac", "switch_aac",
    "gaze_aac", "tactile", "ui_action",
]
MissingReason = Literal[
    "unobserved", "not_applicable", "consent_withheld", "conversion_failed",
]
CorrectionAction = Literal["confirm", "reject", "relabel"]
BaselineLevel = Literal["individual", "relationship", "situation"]


class ModalityEvent(BaseModel):
    """One event before or after a modality conversion."""

    event_id: str
    event_type: InteractionEventType
    source_modality: SourceModality
    source_event_ref: str
    conversion_chain: list[str] = Field(min_length=1)
    observed_features: list[str] = Field(default_factory=list)
    preserved_features: list[str] = Field(default_factory=list)
    missing_features: dict[str, MissingReason] = Field(default_factory=dict)
    alignment_uncertainty_ms: float | None = Field(default=None, ge=0)
    user_confirmed: bool | None = None
    raw_signal_retained: bool = False
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_feature_accounting(self) -> "ModalityEvent":
        observed = set(self.observed_features)
        preserved = set(self.preserved_features)
        missing = set(self.missing_features)
        if preserved & missing:
            raise ValueError("a feature cannot be both preserved and missing")
        if len(observed) != len(self.observed_features):
            raise ValueError("observed_features must be unique")
        if len(preserved) != len(self.preserved_features):
            raise ValueError("preserved_features must be unique")
        return self


class UserCorrection(BaseModel):
    correction_id: str
    target_event_id: str
    action: CorrectionAction
    replacement_event_type: InteractionEventType | None = None

    @model_validator(mode="after")
    def validate_replacement(self) -> "UserCorrection":
        if (self.action == "relabel") != (self.replacement_event_type is not None):
            raise ValueError("replacement_event_type is required only for relabel")
        return self


class PathwayCase(BaseModel):
    case_id: str
    transcript: str
    source_modality: SourceModality
    source_events: list[ModalityEvent]
    converted_events: list[ModalityEvent]
    corrections: list[UserCorrection] = Field(default_factory=list)


class ModalityFixture(BaseModel):
    schema_version: str = "topodialogue-modality-v1"
    cases: list[PathwayCase]
    scope_note: str


class CalibrationProfile(BaseModel):
    profile_id: str
    baseline_level: BaselineLevel
    event_counts: dict[InteractionEventType, int]
    observation_count: int = Field(gt=0)


def apply_user_corrections(
    events: list[ModalityEvent], corrections: list[UserCorrection]
) -> list[ModalityEvent]:
    """Apply explicit user decisions without silently overwriting evidence."""
    by_id = {event.event_id: event.model_copy(deep=True) for event in events}
    for correction in corrections:
        if correction.target_event_id not in by_id:
            raise ValueError(f"unknown correction target: {correction.target_event_id}")
        event = by_id[correction.target_event_id]
        if correction.action == "reject":
            del by_id[correction.target_event_id]
        elif correction.action == "confirm":
            event.user_confirmed = True
            event.notes.append(f"confirmed by {correction.correction_id}")
        else:
            event.event_type = correction.replacement_event_type  # type: ignore[assignment]
            event.user_confirmed = True
            event.notes.append(f"relabeled by {correction.correction_id}")
    return [by_id[event.event_id] for event in events if event.event_id in by_id]


def audit_conversion(case: PathwayCase, *, apply_corrections: bool = False) -> dict:
    """Measure event and feature loss against declared source events.

    A relabelled event is counted as one omitted source event and one falsely
    generated converted event.  This keeps the denominators auditable.
    """
    converted = (
        apply_user_corrections(case.converted_events, case.corrections)
        if apply_corrections else case.converted_events
    )
    source_by_ref = {event.source_event_ref: event for event in case.source_events}
    converted_by_ref = {event.source_event_ref: event for event in converted}
    if len(source_by_ref) != len(case.source_events):
        raise ValueError(f"duplicate source_event_ref in {case.case_id}")
    if len(converted_by_ref) != len(converted):
        raise ValueError(f"duplicate converted source_event_ref in {case.case_id}")

    preserved_refs: list[str] = []
    omitted_refs: list[str] = []
    false_event_ids: list[str] = []
    feature_total = 0
    feature_preserved = 0
    feature_missing = Counter()
    unaccounted: list[str] = []

    for ref, source in source_by_ref.items():
        target = converted_by_ref.get(ref)
        source_features = set(source.observed_features)
        feature_total += len(source_features)
        if target is None or target.event_type != source.event_type:
            omitted_refs.append(ref)
            if target is not None:
                false_event_ids.append(target.event_id)
            continue
        preserved_refs.append(ref)
        preserved = source_features & set(target.preserved_features)
        feature_preserved += len(preserved)
        missing = source_features - preserved
        for feature in missing:
            reason = target.missing_features.get(feature)
            if reason is None:
                unaccounted.append(f"{target.event_id}:{feature}")
            else:
                feature_missing[reason] += 1

    for target in converted:
        if target.source_event_ref not in source_by_ref:
            false_event_ids.append(target.event_id)

    source_count = len(case.source_events)
    converted_count = len(converted)
    return {
        "case_id": case.case_id,
        "source_modality": case.source_modality,
        "transcript": case.transcript,
        "source_event_count": source_count,
        "converted_event_count": converted_count,
        "preserved_event_count": len(preserved_refs),
        "omitted_event_count": len(omitted_refs),
        "false_generated_event_count": len(false_event_ids),
        "source_feature_count": feature_total,
        "preserved_feature_count": feature_preserved,
        "event_preservation_rate": len(preserved_refs) / source_count if source_count else None,
        "event_omission_rate": len(omitted_refs) / source_count if source_count else None,
        "false_generation_rate": len(false_event_ids) / converted_count if converted_count else None,
        "feature_preservation_rate": feature_preserved / feature_total if feature_total else None,
        "missing_feature_reasons": dict(sorted(feature_missing.items())),
        "unaccounted_missing_features": sorted(unaccounted),
        "preserved_source_refs": sorted(preserved_refs),
        "omitted_source_refs": sorted(omitted_refs),
        "false_generated_event_ids": sorted(set(false_event_ids)),
        "corrections_applied": apply_corrections,
    }


def audit_fixture(fixture: ModalityFixture) -> dict:
    """Return deterministic before/after-correction reports for all pathways."""
    rows = []
    for case in fixture.cases:
        rows.append({
            "before_correction": audit_conversion(case),
            "after_correction": audit_conversion(case, apply_corrections=True),
        })
    def aggregate(key: str) -> dict:
        reports = [row[key] for row in rows]
        source = sum(report["source_event_count"] for report in reports)
        converted = sum(report["converted_event_count"] for report in reports)
        preserved = sum(report["preserved_event_count"] for report in reports)
        omitted = sum(report["omitted_event_count"] for report in reports)
        false_generated = sum(report["false_generated_event_count"] for report in reports)
        source_features = sum(report["source_feature_count"] for report in reports)
        preserved_features = sum(report["preserved_feature_count"] for report in reports)
        return {
            "source_event_count": source,
            "converted_event_count": converted,
            "preserved_event_count": preserved,
            "omitted_event_count": omitted,
            "false_generated_event_count": false_generated,
            "source_feature_count": source_features,
            "preserved_feature_count": preserved_features,
            "event_preservation_rate": preserved / source if source else None,
            "event_omission_rate": omitted / source if source else None,
            "false_generation_rate": false_generated / converted if converted else None,
            "feature_preservation_rate": preserved_features / source_features if source_features else None,
        }

    return {
        "schema_version": fixture.schema_version,
        "case_count": len(rows),
        "cases": rows,
        "aggregate_before_correction": aggregate("before_correction"),
        "aggregate_after_correction": aggregate("after_correction"),
        "scope_note": fixture.scope_note,
        "interpretation_note": (
            "Rates describe declared synthetic events and conversions only. "
            "They are not estimates of user intent, disability, emotion, or field accuracy."
        ),
    }


def compare_with_baseline(current_counts: dict[str, int], profile: CalibrationProfile) -> dict:
    """Compare rates only within an explicitly chosen calibration level."""
    labels = sorted(set(current_counts) | set(profile.event_counts))
    current_total = sum(current_counts.values()) or 1
    return {
        "profile_id": profile.profile_id,
        "baseline_level": profile.baseline_level,
        "rate_differences": {
            label: current_counts.get(label, 0) / current_total
            - profile.event_counts.get(label, 0) / profile.observation_count
            for label in labels
        },
        "scope_note": "No demographic, diagnostic, cultural, or personality inference is performed.",
    }
