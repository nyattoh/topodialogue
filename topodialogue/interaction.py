"""Observable interaction events for dialogue research.

The extractor labels surface evidence only.  It does not infer intention,
emotion, hesitation, or any other unobserved psychological state.
"""

from __future__ import annotations

from hashlib import sha256
import re
from typing import Literal

from pydantic import BaseModel, Field

from .models import DialogueTurn


InteractionEventType = Literal[
    "revisit", "repair", "rejection", "adoption", "handover",
    "reframing", "pause",
]


class InteractionEvidence(BaseModel):
    turn_id: str
    start_char: int | None = None
    end_char: int | None = None
    evidence_hash: str | None = None


class InteractionEvent(BaseModel):
    event_id: str
    turn_id: str
    event_type: InteractionEventType
    confidence: float = Field(ge=0, le=1)
    basis: Literal["surface_marker", "turn_structure", "lexical_recurrence"]
    evidence: list[InteractionEvidence] = Field(default_factory=list)
    anchor_turn_id: str | None = None
    notes: list[str] = Field(default_factory=list)


_MARKERS: dict[InteractionEventType, tuple[str, ...]] = {
    "repair": (
        r"(?:というか|言い換えると|訂正(?:すると)?|正確には)",
        r"\b(?:rather|I mean|more precisely|correction)\b",
    ),
    "rejection": (
        r"(?:それは|これは)(?:違う|違います)", r"(?:そうでは|そうじゃ)ない",
        r"(?:無理|却下|やめよう)",
        r"\b(?:no[,;:]?|not that|that is wrong|reject)\b",
    ),
    "adoption": (
        r"(?:それで|これで)(?:いい|行こう|お願い)", r"(?:採用|やってみる|そうしよう|いいね|賛成)",
        r"\b(?:yes|let us do that|sounds good|adopt)\b",
    ),
    "reframing": (
        r"(?:では|じゃ)なく", r"(?:別の|違う)(?:視点|観点|枠|角度)", r"(?:むしろ|前提を|見方を変)",
        r"\b(?:instead|another perspective|reframe|change the assumption)\b",
    ),
    "pause": (
        r"\[(?:pause|silence|中断|休止)\]", r"<(?:pause|silence)\s*/?>",
    ),
}


def _surface_features(text: str) -> set[str]:
    compact = "".join(text.casefold().split())
    if not compact:
        return {"empty"}
    return {
        compact[index:index + 3]
        for index in range(max(1, len(compact) - 2))
        if len(compact[index:index + 3]) == 3
    } or {compact}


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _evidence(turn_id: str, text: str, match: re.Match[str]) -> InteractionEvidence:
    value = match.group(0)
    return InteractionEvidence(
        turn_id=turn_id,
        start_char=match.start(),
        end_char=match.end(),
        evidence_hash=sha256(value.encode("utf-8")).hexdigest()[:16],
    )


def extract_interaction_events(
    turns: list[DialogueTurn],
    *,
    revisit_threshold: float = 0.10,
    minimum_turn_gap: int = 2,
) -> list[InteractionEvent]:
    """Return deterministic event candidates grounded in visible log evidence."""
    events: list[InteractionEvent] = []
    features = [_surface_features(turn.text) for turn in turns]
    serial = 0

    def add(
        turn: DialogueTurn,
        event_type: InteractionEventType,
        confidence: float,
        basis: Literal["surface_marker", "turn_structure", "lexical_recurrence"],
        evidence: list[InteractionEvidence] | None = None,
        anchor_turn_id: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        nonlocal serial
        serial += 1
        events.append(InteractionEvent(
            event_id=f"ie{serial:04d}", turn_id=turn.turn_id,
            event_type=event_type, confidence=confidence, basis=basis,
            evidence=evidence or [], anchor_turn_id=anchor_turn_id,
            notes=notes or [],
        ))

    for index, turn in enumerate(turns):
        for event_type, patterns in _MARKERS.items():
            matches = [
                match
                for pattern in patterns
                for match in re.finditer(pattern, turn.text, flags=re.IGNORECASE)
            ]
            if matches:
                add(
                    turn, event_type, 0.88, "surface_marker",
                    [_evidence(turn.turn_id, turn.text, match) for match in matches[:3]],
                    notes=["Label denotes an observed marker, not an inferred mental state."],
                )

        question_matches = list(re.finditer(r"[?？]", turn.text))
        if question_matches and index + 1 < len(turns) and turns[index + 1].speaker != turn.speaker:
            add(
                turn, "handover", 0.82, "turn_structure",
                [_evidence(turn.turn_id, turn.text, question_matches[-1])],
                notes=["Question punctuation followed by a speaker change."],
            )

        best_similarity = 0.0
        best_index: int | None = None
        for prior in range(index):
            if index - prior < minimum_turn_gap:
                continue
            similarity = _jaccard(features[index], features[prior])
            if similarity > best_similarity:
                best_similarity, best_index = similarity, prior
        if best_index is not None and best_similarity >= revisit_threshold:
            add(
                turn, "revisit", min(0.95, best_similarity), "lexical_recurrence",
                anchor_turn_id=turns[best_index].turn_id,
                notes=[f"Character-trigram Jaccard similarity={best_similarity:.3f}."],
            )

    return events
