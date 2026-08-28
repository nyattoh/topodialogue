import json
from pathlib import Path

from topodialogue.adapters import load_dialogue
from topodialogue.trajectory import TrajectoryConfig, analyze_trajectory


MANIFEST = Path("examples/synthetic/manifest.json")


def test_all_synthetic_cases_match_declared_shape_and_source():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for case in manifest["cases"]:
        report = analyze_trajectory(load_dialogue(MANIFEST.parent / case["file"]))
        assert report.shape_class == case["expected_shape"], case["id"]
        assert report.recurrence_source == case["expected_recurrence_source"], case["id"]


def test_same_input_and_seed_produce_identical_report():
    turns = load_dialogue(MANIFEST.parent / "spiral-revisit.jsonl")
    first = analyze_trajectory(turns, TrajectoryConfig(projection_seed=11))
    second = analyze_trajectory(turns, TrajectoryConfig(projection_seed=11))
    assert first.model_dump() == second.model_dump()


def test_projection_seed_changes_geometry_but_not_operational_metrics():
    turns = load_dialogue(MANIFEST.parent / "spiral-revisit.jsonl")
    first = analyze_trajectory(turns, TrajectoryConfig(projection_seed=11))
    second = analyze_trajectory(turns, TrajectoryConfig(projection_seed=12))
    assert [(point.semantic_x, point.semantic_y) for point in first.points] != [
        (point.semantic_x, point.semantic_y) for point in second.points
    ]
    assert first.shape_class == second.shape_class
    assert first.metrics.model_dump(exclude={"projection_stability"}) == second.metrics.model_dump(exclude={"projection_stability"})


def test_assistant_hypothesis_is_not_user_originated_novelty():
    report = analyze_trajectory(load_dialogue(MANIFEST.parent / "assistant-induced-loop.jsonl"))
    assistant_point = next(point for point in report.points if "assistant_hypothesis_a" in point.features)
    assert assistant_point.assistant_originated_novelty == 1
    assert assistant_point.user_originated_novelty == 0
    assert report.metrics.assistant_induced_recurrence_count > report.metrics.user_recurrence_count


def test_unannotated_export_reports_lexical_artifact(tmp_path):
    path = tmp_path / "anonymous-export.json"
    path.write_text(json.dumps({"messages": [
        {"role": "user", "text": "alpha region"},
        {"role": "assistant", "text": "beta response"},
        {"role": "user", "text": "alpha region again"},
        {"role": "assistant", "text": "gamma response"},
        {"role": "user", "text": "delta region"},
        {"role": "assistant", "text": "epsilon response"},
    ]}), encoding="utf-8")
    report = analyze_trajectory(load_dialogue(path))
    assert report.metrics.turn_count > 4
    assert any(warning.code == "lexical_fallback" for warning in report.artifact_warnings)
