import json
from pathlib import Path

import pytest

from topodialogue.benchmark import run_synthetic_robustness_benchmark


MANIFEST = Path("examples/synthetic/manifest.json")


def test_benchmark_runs_full_grid_and_is_reproducible():
    first = run_synthetic_robustness_benchmark(
        MANIFEST, thresholds=(0.45, 0.50), seeds=(11, 1729),
    )
    second = run_synthetic_robustness_benchmark(
        MANIFEST, thresholds=(0.45, 0.50), seeds=(11, 1729),
    )
    assert first == second
    assert first["case_count"] == 6
    assert first["total_run_count"] == 6 * 2 * 2 * 2
    assert first["seed_invariance_of_operational_outputs"] is True
    assert first["scope_note"].startswith("This is a controlled benchmark")


def test_default_declared_cases_match_at_declared_threshold():
    report = run_synthetic_robustness_benchmark(
        MANIFEST, thresholds=(0.50,), seeds=(1729,),
    )
    declared = report["summaries"]["declared_annotations"]
    assert declared["shape_match_rate"] == 1.0
    assert declared["source_match_rate"] == 1.0
    assert declared["joint_match_rate"] == 1.0


def test_benchmark_rejects_invalid_threshold():
    with pytest.raises(ValueError, match="between zero and one"):
        run_synthetic_robustness_benchmark(MANIFEST, thresholds=(1.1,))
