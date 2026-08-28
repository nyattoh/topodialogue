"""Privacy-preserving preparation of real dialogue cases.

Public derivatives contain no transcript text or evidence quotes.  They retain
only interaction structure and pseudonymous region identifiers required to
reproduce aggregate figures.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import re
from typing import Any

from pydantic import BaseModel, Field

from .interaction import InteractionEvent, extract_interaction_events
from .models import DialogueTurn


class PrivacyAudit(BaseModel):
    algorithm_version: str = "privacy-audit-v1"
    turn_count: int
    character_count: int
    maximum_turn_characters: int
    speaker_counts: dict[str, int]
    risk_pattern_counts: dict[str, int]
    raw_sha256: str
    release_mode: str = "content-withheld structural derivative"
    residual_raw_text_released: bool = False
    warnings: list[str] = Field(default_factory=list)


_RISK_PATTERNS = {
    "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    "url": re.compile(r"https?://\S+", re.IGNORECASE),
    "phone": re.compile(r"(?<!\d)(?:\+?81[- ]?)?0\d{1,4}[- ]?\d{1,4}[- ]?\d{3,4}(?!\d)"),
    "money": re.compile(r"(?:¥|￥|\$|€|£)\s?[\d,]+|\d[\d,]*\s?(?:円|万円|億円)"),
    "date_or_time": re.compile(r"\d{1,4}[年/-]\d{1,2}(?:[月/-]\d{1,2}日?)?|\d{1,2}:\d{2}"),
    "filesystem_path": re.compile(r"(?:[A-Za-z]:\\|/(?:Users|home)/)\S+"),
    "account_handle": re.compile(r"(?<!\w)@[A-Za-z0-9_]{2,}"),
}


def audit_dialogue(turns: list[DialogueTurn]) -> PrivacyAudit:
    raw = json.dumps(
        [{"speaker": turn.speaker, "text": turn.text} for turn in turns],
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )
    texts = [turn.text for turn in turns]
    counts = {
        name: sum(len(pattern.findall(text)) for text in texts)
        for name, pattern in _RISK_PATTERNS.items()
    }
    warnings = [
        "Automatic pattern checks cannot prove that a transcript contains no identifying context.",
        "The public derivative therefore withholds every original utterance rather than relying on span masking alone.",
        "Pseudonymous region identifiers preserve recurrence structure but are not semantic labels.",
    ]
    return PrivacyAudit(
        turn_count=len(turns), character_count=sum(map(len, texts)),
        maximum_turn_characters=max(map(len, texts), default=0),
        speaker_counts=dict(Counter(turn.speaker for turn in turns)),
        risk_pattern_counts=counts,
        raw_sha256=sha256(raw.encode("utf-8")).hexdigest(), warnings=warnings,
    )


def _features(text: str) -> set[str]:
    compact = "".join(text.casefold().split())
    return {
        compact[index:index + 3]
        for index in range(max(1, len(compact) - 2))
        if len(compact[index:index + 3]) == 3
    } or {"empty"}


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _length_bin(length: int) -> str:
    if length < 80:
        return "short"
    if length < 400:
        return "medium"
    if length < 1000:
        return "long"
    return "very_long"


def _region_ids(turns: list[DialogueTurn], threshold: float = 0.10) -> list[str]:
    rows = [_features(turn.text) for turn in turns]
    region_for_turn: list[str] = []
    representatives: list[int] = []
    for index, row in enumerate(rows):
        best_score, best_region = 0.0, None
        for region_index, representative in enumerate(representatives):
            score = _jaccard(row, rows[representative])
            if score > best_score:
                best_score, best_region = score, region_index
        if best_region is None or best_score < threshold:
            representatives.append(index)
            best_region = len(representatives) - 1
        region_for_turn.append(f"region:{best_region + 1:03d}")
    return region_for_turn


def public_derivative(
    turns: list[DialogueTurn],
    *,
    case_id: str,
    events: list[InteractionEvent] | None = None,
) -> dict[str, Any]:
    """Create a release-safe event/trajectory input with all text withheld."""
    events = events if events is not None else extract_interaction_events(turns)
    by_turn: dict[str, list[InteractionEvent]] = {}
    for event in events:
        by_turn.setdefault(event.turn_id, []).append(event)
    regions = _region_ids(turns)
    messages = []
    for index, (turn, region) in enumerate(zip(turns, regions), 1):
        turn_events = by_turn.get(turn.turn_id, [])
        # Only recurrence-bearing features enter the trajectory.  Length and
        # form remain descriptive metadata; otherwise common structural bins
        # manufacture false revisits in the released derivative.
        feature_keys = [region]
        if "?" in turn.text or "？" in turn.text:
            form = "question"
        else:
            form = "statement"
        feature_keys.extend(f"event:{event.event_type}" for event in turn_events)
        feature_keys = sorted(set(feature_keys))
        event_payloads = []
        for event in turn_events:
            payload = event.model_dump(mode="json")
            payload["evidence"] = []
            event_payloads.append(payload)
        messages.append({
            "role": turn.speaker,
            "text": f"[content withheld; {_length_bin(len(turn.text))} turn]",
            "annotations": {
                "nodes": [
                    {"key": key, "label": key, "type": "concept", "confidence": 0.8}
                    for key in feature_keys
                ],
                "interaction_events": event_payloads,
                "source_turn_index": index,
                "text_length_bin": _length_bin(len(turn.text)),
                "form": form,
                "content_withheld": True,
            },
        })
    return {
        "case_id": case_id,
        "release": {
            "format": "topodialogue-public-derivative-v2",
            "content_withheld": True,
            "region_similarity_threshold": 0.10,
            "event_revisit_similarity_threshold": 0.10,
            "description": (
                "Every utterance is withheld. Pseudonymous regions and observable "
                "interaction-event candidates reproduce the released analysis."
            ),
        },
        "messages": messages,
    }
