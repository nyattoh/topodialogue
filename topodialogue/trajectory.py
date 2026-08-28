"""Deterministic Phase-1 dialogue trajectory analysis.

The geometry is a reproducible visualization coordinate system, not a claim
that language has a unique physical or topological embedding.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
import re
from typing import Any, Literal

from pydantic import BaseModel, Field

from .models import DialogueTurn

ShapeClass = Literal["closed_loop", "spiral_revisit", "escape", "open_trajectory", "insufficient_data"]
RecurrenceSource = Literal["user", "assistant", "mixed", "none"]


class TrajectoryConfig(BaseModel):
    algorithm_version: str = "trajectory-v1"
    projection_seed: int = 1729
    recurrence_threshold: float = Field(default=0.5, ge=0, le=1)
    minimum_turn_gap: int = Field(default=2, ge=1)
    spiral_progress_threshold: float = Field(default=0.2, ge=0, le=1)
    escape_similarity_ratio: float = Field(default=0.55, ge=0, le=1)
    escape_horizon: int = Field(default=5, ge=1)


class AxisDefinition(BaseModel):
    key: str
    label: str
    definition: str
    caveat: str


class TrajectoryPoint(BaseModel):
    turn_id: str
    turn_index: int
    speaker: str
    text: str
    features: list[str]
    feature_source: Literal["annotated", "structured", "lexical"]
    semantic_x: float
    semantic_y: float
    alternative_z: float
    time_height: float
    revisit_height: float
    abstraction_height: float
    confidence: float
    novelty_count: int
    user_originated_novelty: int
    assistant_originated_novelty: int
    recurrence_similarity: float
    recurrence_anchor_turn_id: str | None = None
    is_revisit: bool = False
    progress_on_revisit: float = 0.0


class TrajectoryMetrics(BaseModel):
    turn_count: int
    revisit_count: int
    revisit_rate: float
    mean_revisit_similarity: float
    mean_progress_on_revisit: float
    abstraction_gain_on_revisit: float
    loop_score: float
    user_originated_novelty_count: int
    assistant_originated_novelty_count: int
    system_originated_novelty_count: int
    assistant_induced_recurrence_count: int
    user_recurrence_count: int
    escape_at_5: bool
    projection_stability: float


class ArtifactWarning(BaseModel):
    code: str
    severity: Literal["info", "warning"]
    message: str


class TrajectoryReport(BaseModel):
    algorithm_version: str
    input_hash: str
    projection_seed: int
    axis_definitions: list[AxisDefinition]
    shape_class: ShapeClass
    recurrence_source: RecurrenceSource
    shape_confidence: float
    metrics: TrajectoryMetrics
    points: list[TrajectoryPoint]
    artifact_warnings: list[ArtifactWarning]
    interpretation: list[str]


_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def _lexical_features(text: str) -> set[str]:
    normalized = "".join(text.casefold().split())
    words = {f"w:{word}" for word in _TOKEN_RE.findall(text.casefold()) if len(word) > 1}
    grams = {f"g:{normalized[index:index + 3]}" for index in range(max(0, len(normalized) - 2))}
    return words | grams or {"empty"}


def _turn_features(turn: DialogueTurn) -> tuple[set[str], str, float, float]:
    annotations = turn.metadata.get("annotations", {})
    if not isinstance(annotations, dict):
        annotations = {}
    nodes = annotations.get("nodes", [])
    if isinstance(nodes, list) and nodes:
        keys = {
            str(node.get("key", node.get("label", ""))).strip().casefold()
            for node in nodes if isinstance(node, dict)
        } - {""}
        confidence_values = [float(node.get("confidence", 0.95)) for node in nodes if isinstance(node, dict)]
        confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.95
        abstraction = annotations.get("abstraction")
        if abstraction is None:
            levels = {
                "action_pattern": 0.2, "desire": 0.3, "context": 0.35,
                "concept": 0.5, "constraint": 0.6, "uncertainty": 0.65,
                "self_claim": 0.75, "value": 0.8, "counterfactual": 0.55,
                "affect": 0.55, "body": 0.25,
            }
            node_levels = [levels.get(str(node.get("type", "concept")), 0.5) for node in nodes if isinstance(node, dict)]
            abstraction = sum(node_levels) / len(node_levels) if node_levels else 0.5
        return keys or _lexical_features(turn.text), "annotated", float(abstraction), confidence

    structured = []
    for key in ("frame", "operator", "state", "topic"):
        value = annotations.get(key)
        if value:
            structured.append(f"{key}:{str(value).casefold()}")
    if structured:
        return set(structured), "structured", float(annotations.get("abstraction", 0.5)), 0.75
    return _lexical_features(turn.text), "lexical", 0.5, 0.45


def _fnv1a(text: str) -> int:
    value = 2166136261
    for character in text:
        value ^= ord(character)
        value = (value * 16777619) & 0xFFFFFFFF
    return value


def _feature_projection(features: set[str], seed: int) -> tuple[float, float, float]:
    values = []
    for axis in range(3):
        axis_values = [((_fnv1a(f"{seed}:{axis}:{feature}") / 0xFFFFFFFF) * 2.0 - 1.0) for feature in sorted(features)]
        values.append(sum(axis_values) / max(1, len(axis_values)))
    return values[0], values[1], values[2]


def _scale(values: list[float], radius: float = 52.0) -> list[float]:
    if not values:
        return []
    center = sum(values) / len(values)
    shifted = [value - center for value in values]
    maximum = max((abs(value) for value in shifted), default=0.0)
    return [round((value / maximum) * radius, 6) if maximum else 0.0 for value in shifted]


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _pairwise_distances(rows: list[tuple[float, float]]) -> list[float]:
    return [math.dist(rows[i], rows[j]) for i in range(len(rows)) for j in range(i)]


def _correlation(left: list[float], right: list[float]) -> float:
    if len(left) < 2 or len(left) != len(right):
        return 1.0
    left_mean, right_mean = sum(left) / len(left), sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_norm = math.sqrt(sum((a - left_mean) ** 2 for a in left))
    right_norm = math.sqrt(sum((b - right_mean) ** 2 for b in right))
    return max(0.0, min(1.0, numerator / (left_norm * right_norm))) if left_norm and right_norm else 1.0


def analyze_trajectory(turns: list[DialogueTurn], config: TrajectoryConfig | None = None) -> TrajectoryReport:
    config = config or TrajectoryConfig()
    extracted = [_turn_features(turn) for turn in turns]
    feature_sets = [item[0] for item in extracted]
    abstractions = [item[2] for item in extracted]
    projections = [_feature_projection(features, config.projection_seed) for features in feature_sets]
    alternative = [_feature_projection(features, config.projection_seed + 104729) for features in feature_sets]
    xs, ys, zs = _scale([row[0] for row in projections]), _scale([row[1] for row in projections]), _scale([row[2] for row in projections])

    stability = _correlation(
        _pairwise_distances([(row[0], row[1]) for row in projections]),
        _pairwise_distances([(row[0], row[1]) for row in alternative]),
    )
    first_origin: dict[str, str] = {}
    seen: set[str] = set()
    visit_counts: Counter[str] = Counter()
    point_data: list[dict[str, Any]] = []
    revisits: list[dict[str, Any]] = []

    for index, turn in enumerate(turns):
        features = feature_sets[index]
        best_similarity, best_index = 0.0, None
        for prior in range(max(0, index - 200), index):
            if index - prior < config.minimum_turn_gap:
                continue
            similarity = _jaccard(features, feature_sets[prior])
            if similarity > best_similarity:
                best_similarity, best_index = similarity, prior
        is_revisit = best_similarity >= config.recurrence_threshold and best_index is not None
        new_features = features - seen
        for feature in sorted(new_features):
            first_origin[feature] = turn.speaker
        seen.update(features)
        user_novelty = sum(first_origin.get(feature) == "user" for feature in new_features)
        assistant_novelty = sum(first_origin.get(feature) == "assistant" for feature in new_features)
        abstraction_delta = abstractions[index] - abstractions[best_index] if best_index is not None else 0.0
        novelty_ratio = len(new_features) / max(1, len(features))
        progress = min(1.0, 0.7 * novelty_ratio + 0.3 * max(0.0, abstraction_delta)) if is_revisit else 0.0
        signature = "|".join(sorted(features))
        visit_counts[signature] += 1
        item = {
            "best_index": best_index,
            "best_similarity": best_similarity,
            "is_revisit": is_revisit,
            "new_features": new_features,
            "user_novelty": user_novelty,
            "assistant_novelty": assistant_novelty,
            "progress": progress,
            "abstraction_delta": abstraction_delta,
            "revisit_height": float(visit_counts[signature] - 1),
        }
        point_data.append(item)
        if is_revisit:
            revisits.append({"index": index, **item})

    escaped = False
    for revisit in revisits:
        end = min(len(turns), revisit["index"] + config.escape_horizon + 1)
        for index in range(revisit["index"] + 1, end):
            if turns[index].speaker != "user":
                continue
            recurrence_stays_lower = not any(point_data[later]["is_revisit"] for later in range(index + 1, end))
            if (
                point_data[index]["best_similarity"] < config.recurrence_threshold * config.escape_similarity_ratio
                and point_data[index]["new_features"]
                and recurrence_stays_lower
            ):
                escaped = True
                break
        if escaped:
            break

    mean_similarity = sum(item["best_similarity"] for item in revisits) / len(revisits) if revisits else 0.0
    mean_progress = sum(item["progress"] for item in revisits) / len(revisits) if revisits else 0.0
    abstraction_gain = sum(max(0.0, item["abstraction_delta"]) for item in revisits) / len(revisits) if revisits else 0.0
    loop_score = max(0.0, min(1.0, mean_similarity * (1.0 - mean_progress)))
    if len(turns) < 3:
        shape: ShapeClass = "insufficient_data"
    elif not revisits:
        shape = "open_trajectory"
    elif escaped:
        shape = "escape"
    elif mean_progress >= config.spiral_progress_threshold or abstraction_gain >= config.spiral_progress_threshold:
        shape = "spiral_revisit"
    else:
        shape = "closed_loop"

    recurrence_counts = Counter(turns[item["index"]].speaker for item in revisits)
    user_recurrence = recurrence_counts["user"]
    assistant_recurrence = recurrence_counts["assistant"]
    if not revisits:
        recurrence_source: RecurrenceSource = "none"
    elif user_recurrence == assistant_recurrence:
        recurrence_source = "mixed"
    elif assistant_recurrence > user_recurrence:
        recurrence_source = "assistant"
    else:
        recurrence_source = "user"

    max_revisit = max((item["revisit_height"] for item in point_data), default=0.0)
    points = [
        TrajectoryPoint(
            turn_id=turn.turn_id,
            turn_index=index + 1,
            speaker=turn.speaker,
            text=turn.text,
            features=sorted(feature_sets[index]),
            feature_source=extracted[index][1],
            semantic_x=xs[index], semantic_y=ys[index], alternative_z=zs[index],
            time_height=round(index / max(1, len(turns) - 1) * 100.0 - 50.0, 6),
            revisit_height=round((point_data[index]["revisit_height"] / max(1.0, max_revisit)) * 100.0 - 50.0, 6),
            abstraction_height=round(abstractions[index] * 100.0 - 50.0, 6),
            confidence=round(extracted[index][3], 6),
            novelty_count=len(point_data[index]["new_features"]),
            user_originated_novelty=point_data[index]["user_novelty"],
            assistant_originated_novelty=point_data[index]["assistant_novelty"],
            recurrence_similarity=round(point_data[index]["best_similarity"], 6),
            recurrence_anchor_turn_id=turns[point_data[index]["best_index"]].turn_id if point_data[index]["best_index"] is not None else None,
            is_revisit=point_data[index]["is_revisit"],
            progress_on_revisit=round(point_data[index]["progress"], 6),
        )
        for index, turn in enumerate(turns)
    ]

    origins = Counter(first_origin.values())
    warnings = [ArtifactWarning(
        code="time_height_monotonicity", severity="info",
        message="時間を高さにすると全軌跡が必ず上昇するため、上昇だけを進展の証拠にしないでください。",
    )]
    sources = Counter(item[1] for item in extracted)
    if sources["lexical"]:
        warnings.append(ArtifactWarning(
            code="lexical_fallback", severity="warning",
            message=f"{sources['lexical']}発話は注釈なしの文字n-gram近似です。意味的な言い換えを見落とす可能性があります。",
        ))
    if 0 < sources["annotated"] < len(turns):
        warnings.append(ArtifactWarning(
            code="mixed_feature_sources", severity="warning",
            message="注釈特徴と文字特徴が混在しています。距離の比較可能性は限定的です。",
        ))
    if len(turns) < 6:
        warnings.append(ArtifactWarning(code="small_sample", severity="warning", message="6発話未満では形状分類の信頼度が低いです。"))
    if stability < 0.65:
        warnings.append(ArtifactWarning(
            code="projection_seed_sensitivity", severity="warning",
            message=f"代替seedとの距離相関は{stability:.2f}です。画面上の向きや曲率を実在構造として解釈しないでください。",
        ))
    role_counts = Counter(turn.speaker for turn in turns)
    if turns and max(role_counts.values()) / len(turns) > 0.8:
        warnings.append(ArtifactWarning(code="speaker_imbalance", severity="warning", message="発話者の偏りが80%を超えています。由来別指標を比較するときに注意してください。"))

    confidence = 0.25 if shape == "insufficient_data" else min(0.95, 0.5 + 0.08 * len(revisits) + 0.2 * abs(mean_progress - config.spiral_progress_threshold))
    canonical = [{"speaker": turn.speaker, "text": turn.text, "metadata": turn.metadata} for turn in turns]
    metrics = TrajectoryMetrics(
        turn_count=len(turns), revisit_count=len(revisits), revisit_rate=round(len(revisits) / max(1, len(turns)), 6),
        mean_revisit_similarity=round(mean_similarity, 6), mean_progress_on_revisit=round(mean_progress, 6),
        abstraction_gain_on_revisit=round(abstraction_gain, 6), loop_score=round(loop_score, 6),
        user_originated_novelty_count=origins["user"], assistant_originated_novelty_count=origins["assistant"],
        system_originated_novelty_count=origins["system"], assistant_induced_recurrence_count=assistant_recurrence,
        user_recurrence_count=user_recurrence, escape_at_5=escaped, projection_stability=round(stability, 6),
    )
    interpretation = [
        f"Recurrence: {len(revisits)} revisits at threshold {config.recurrence_threshold:.2f}.",
        f"Progress on revisit: {mean_progress:.2f}; operational shape: {shape}.",
        f"Novelty origin: user={origins['user']}, assistant={origins['assistant']}, system={origins['system']}.",
        f"Escape@{config.escape_horizon}: {escaped}.",
    ]
    return TrajectoryReport(
        algorithm_version=config.algorithm_version,
        input_hash=sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest(),
        projection_seed=config.projection_seed,
        axis_definitions=[
            AxisDefinition(key="x", label="Semantic projection X", definition="固定seedのsigned feature projection第1成分。共有特徴を近く配置する。", caveat="固有の心理軸・意味軸ではない。"),
            AxisDefinition(key="y", label="Semantic projection Y", definition="固定seedのsigned feature projection第2成分。Xと独立な表示成分。", caveat="回転・反転・seed変更で見た目は変わり得る。"),
            AxisDefinition(key="z_time", label="Time", definition="発話順を[-50, 50]へ線形変換。", caveat="上昇は進展を意味しない。"),
            AxisDefinition(key="z_revisit", label="Revisit count", definition="同一特徴signatureへの累積再訪回数。", caveat="注釈粒度に依存する。"),
            AxisDefinition(key="z_abstraction", label="Abstraction", definition="明示注釈またはnode typeから得る操作的抽象度。", caveat="心理的な深さではない。"),
            AxisDefinition(key="z_alternative", label="Alternative semantic component", definition="同じ特徴集合の第3表示成分。", caveat="形状の頑健性比較用であり実在軸ではない。"),
        ],
        shape_class=shape, recurrence_source=recurrence_source, shape_confidence=round(confidence, 6),
        metrics=metrics, points=points, artifact_warnings=warnings, interpretation=interpretation,
    )


def report_to_json(report: TrajectoryReport) -> str:
    return json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
