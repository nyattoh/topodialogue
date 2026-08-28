"""Controlled robustness benchmarks for the operational trajectory classifier.

The benchmark uses declared synthetic cases.  It measures reproducibility and
sensitivity; it is not evidence of accuracy on natural human dialogue.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from .adapters import load_dialogue
from .models import DialogueTurn
from .trajectory import TrajectoryConfig, analyze_trajectory


DEFAULT_THRESHOLDS = (0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65)
DEFAULT_SEEDS = (11, 1729, 104729)


def _without_annotations(turns: Iterable[DialogueTurn]) -> list[DialogueTurn]:
    """Return a text-only copy without mutating the source records."""
    return [
        turn.model_copy(update={
            "metadata": {
                key: value for key, value in turn.metadata.items()
                if key != "annotations"
            }
        })
        for turn in turns
    ]


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def run_synthetic_robustness_benchmark(
    manifest_path: str | Path,
    *,
    thresholds: Iterable[float] = DEFAULT_THRESHOLDS,
    seeds: Iterable[int] = DEFAULT_SEEDS,
) -> dict[str, Any]:
    """Run a deterministic threshold, seed, and feature-source sensitivity grid."""
    path = Path(manifest_path)
    manifest_bytes = path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    threshold_values = tuple(float(value) for value in thresholds)
    seed_values = tuple(int(value) for value in seeds)
    if not threshold_values or not seed_values:
        raise ValueError("at least one threshold and one seed are required")
    if any(value < 0 or value > 1 for value in threshold_values):
        raise ValueError("thresholds must be between zero and one")

    runs: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {}
    for case in manifest["cases"]:
        case_path = path.parent / case["file"]
        input_hashes[case["id"]] = sha256(case_path.read_bytes()).hexdigest()
        annotated_turns = load_dialogue(case_path)
        modes = {
            "declared_annotations": annotated_turns,
            "text_only_ablation": _without_annotations(annotated_turns),
        }
        for feature_mode, turns in modes.items():
            for threshold in threshold_values:
                for seed in seed_values:
                    report = analyze_trajectory(
                        turns,
                        TrajectoryConfig(
                            projection_seed=seed,
                            recurrence_threshold=threshold,
                        ),
                    )
                    shape_match = report.shape_class == case["expected_shape"]
                    source_match = report.recurrence_source == case["expected_recurrence_source"]
                    runs.append({
                        "case_id": case["id"],
                        "feature_mode": feature_mode,
                        "threshold": threshold,
                        "seed": seed,
                        "expected_shape": case["expected_shape"],
                        "observed_shape": report.shape_class,
                        "expected_recurrence_source": case["expected_recurrence_source"],
                        "observed_recurrence_source": report.recurrence_source,
                        "shape_match": shape_match,
                        "source_match": source_match,
                        "joint_match": shape_match and source_match,
                        "revisit_count": report.metrics.revisit_count,
                        "loop_score": report.metrics.loop_score,
                        "projection_stability": report.metrics.projection_stability,
                    })

    def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(rows)
        shape_matches = sum(row["shape_match"] for row in rows)
        source_matches = sum(row["source_match"] for row in rows)
        joint_matches = sum(row["joint_match"] for row in rows)
        by_case: dict[str, dict[str, Any]] = {}
        for case_id in sorted({row["case_id"] for row in rows}):
            case_rows = [row for row in rows if row["case_id"] == case_id]
            by_case[case_id] = {
                "run_count": len(case_rows),
                "shape_match_rate": _rate(sum(row["shape_match"] for row in case_rows), len(case_rows)),
                "source_match_rate": _rate(sum(row["source_match"] for row in case_rows), len(case_rows)),
                "joint_match_rate": _rate(sum(row["joint_match"] for row in case_rows), len(case_rows)),
            }
        shape_confusion = Counter(
            f"{row['expected_shape']}->{row['observed_shape']}" for row in rows
        )
        source_confusion = Counter(
            f"{row['expected_recurrence_source']}->{row['observed_recurrence_source']}"
            for row in rows
        )
        return {
            "run_count": total,
            "shape_match_rate": _rate(shape_matches, total),
            "source_match_rate": _rate(source_matches, total),
            "joint_match_rate": _rate(joint_matches, total),
            "by_case": by_case,
            "shape_confusion": dict(sorted(shape_confusion.items())),
            "source_confusion": dict(sorted(source_confusion.items())),
        }

    summaries = {
        mode: summarise([row for row in runs if row["feature_mode"] == mode])
        for mode in ("declared_annotations", "text_only_ablation")
    }
    threshold_summary: dict[str, dict[str, Any]] = {}
    for mode in summaries:
        threshold_summary[mode] = {}
        for threshold in threshold_values:
            rows = [
                row for row in runs
                if row["feature_mode"] == mode and row["threshold"] == threshold
            ]
            threshold_summary[mode][f"{threshold:.2f}"] = {
                "shape_match_rate": _rate(sum(row["shape_match"] for row in rows), len(rows)),
                "source_match_rate": _rate(sum(row["source_match"] for row in rows), len(rows)),
                "joint_match_rate": _rate(sum(row["joint_match"] for row in rows), len(rows)),
            }

    grouped_without_seed: dict[tuple[Any, ...], set[tuple[Any, ...]]] = defaultdict(set)
    for row in runs:
        key = (row["case_id"], row["feature_mode"], row["threshold"])
        grouped_without_seed[key].add((
            row["observed_shape"], row["observed_recurrence_source"],
            row["revisit_count"], row["loop_score"],
        ))
    seed_invariance = all(len(outcomes) == 1 for outcomes in grouped_without_seed.values())

    return {
        "benchmark_version": "synthetic-robustness-v1",
        "manifest": str(path.as_posix()),
        "manifest_sha256": sha256(manifest_bytes).hexdigest(),
        "case_input_sha256": input_hashes,
        "case_count": len(manifest["cases"]),
        "thresholds": list(threshold_values),
        "seeds": list(seed_values),
        "total_run_count": len(runs),
        "seed_invariance_of_operational_outputs": seed_invariance,
        "summaries": summaries,
        "threshold_summary": threshold_summary,
        "runs": runs,
        "scope_note": (
            "This is a controlled benchmark over declared synthetic cases. It tests "
            "reproducibility and sensitivity, not field accuracy, participant benefit, "
            "accessibility, personalisation quality, or causal effect."
        ),
    }
