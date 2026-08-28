import json

from topodialogue.interaction import extract_interaction_events
from topodialogue.models import DialogueTurn
from topodialogue.privacy import audit_dialogue, public_derivative
from topodialogue.trajectory import analyze_trajectory


def _turn(index: int, speaker: str, text: str) -> DialogueTurn:
    return DialogueTurn(turn_id=f"t{index}", speaker=speaker, text=text)


def test_surface_events_are_deterministic_and_evidence_grounded():
    turns = [
        _turn(1, "assistant", "この案で進めますか？"),
        _turn(2, "user", "というか、それは違う。別の視点に変えたい。"),
        _turn(3, "assistant", "別の視点なら、制約を外しますか？"),
        _turn(4, "user", "それでいい。そうしよう。"),
    ]
    first = extract_interaction_events(turns)
    second = extract_interaction_events(turns)
    assert first == second
    labels = {event.event_type for event in first}
    assert {"repair", "rejection", "reframing", "adoption", "handover"} <= labels
    assert all(event.evidence or event.event_type == "revisit" for event in first)


def test_ellipsis_does_not_infer_pause():
    turns = [_turn(1, "user", "ええっと……どうしようかな。")]
    assert "pause" not in {event.event_type for event in extract_interaction_events(turns)}


def test_explanatory_negation_is_not_a_rejection():
    turns = [_turn(1, "assistant", "これは心理状態の推定ではなく、表面上の指標です。")]
    labels = {event.event_type for event in extract_interaction_events(turns)}
    assert "rejection" not in labels


def test_public_derivative_releases_no_transcript_text():
    secret = "Contact me at private@example.com and see https://private.invalid/path"
    turns = [
        _turn(1, "user", secret),
        _turn(2, "assistant", "No, not that. Another perspective?"),
        _turn(3, "user", secret),
    ]
    derivative = public_derivative(turns, case_id="case-safe")
    serialised = json.dumps(derivative, ensure_ascii=False)
    assert secret not in serialised
    assert "private@example.com" not in serialised
    assert "private.invalid" not in serialised
    assert all(item["annotations"]["content_withheld"] for item in derivative["messages"])
    assert all("evidence_hash" not in json.dumps(item) for item in derivative["messages"])
    assert audit_dialogue(turns).residual_raw_text_released is False


def test_public_derivative_reproduces_event_enriched_trajectory():
    turns = [
        _turn(1, "assistant", "A proposal about one constraint?"),
        _turn(2, "user", "No, not that constraint."),
        _turn(3, "assistant", "Another perspective on the same constraint?"),
        _turn(4, "user", "Yes, let us do that."),
    ]
    derivative = public_derivative(turns, case_id="case-safe")
    rebuilt = [
        DialogueTurn(
            turn_id=f"t{index}", speaker=item["role"], text=item["text"],
            metadata={"annotations": item["annotations"]},
        )
        for index, item in enumerate(derivative["messages"], 1)
    ]
    assert analyze_trajectory(rebuilt) == analyze_trajectory(rebuilt)
