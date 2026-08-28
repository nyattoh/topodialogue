"""Static, numerical, privacy, and British-English audit for Paper 4."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAPER = HERE / "topodialogue-en.tex"
BIB = HERE / "references.bib"
FIXTURE = ROOT / "examples" / "modality" / "synthetic-conversion-cases.json"
REPORT = ROOT / "examples" / "modality" / "synthetic-conversion-report.json"

AMERICAN_FORMS = {
    "analyze", "analyzed", "analyzes", "analyzing", "artifact", "artifacts",
    "behavior", "behavioral", "center", "centered", "centering", "centers",
    "characterize", "characterized", "color", "colors", "generalize",
    "generalized", "labeled", "labeling", "modeling", "normalization",
    "normalize", "normalized", "operationalize", "operationalized",
    "optimization", "optimize", "organization", "personalization",
    "visualization", "visualizations", "visualize",
}


def close(actual: float, expected: float) -> None:
    if abs(actual - expected) > 1e-6:
        raise SystemExit(f"metric drift: actual={actual}, expected={expected}")


def main() -> None:
    tex = PAPER.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    prose = re.sub(r"(?m)^%.*$|\\includegraphics(?:\[[^]]*\])?\{[^}]+\}|\\[A-Za-z@]+\*?", "", tex)
    found = sorted({m.group(0).casefold() for word in AMERICAN_FORMS for m in re.finditer(rf"\b{word}\b", prose, re.I)})
    if found:
        raise SystemExit(f"American English forms found: {', '.join(found)}")

    citation_groups = re.findall(r"\\cite[pt]?\{([^}]+)\}", tex)
    cited = {key.strip() for group in citation_groups for key in group.split(",")}
    available = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
    if cited != available:
        raise SystemExit(f"bibliography mismatch: missing={sorted(cited-available)}, unused={sorted(available-cited)}")

    figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    absent = [name for name in figures if not (ROOT / "paper" / "figures" / "draft4" / name).exists()]
    if absent:
        raise SystemExit(f"missing figures: {absent}")

    before, after = report["aggregate_before_correction"], report["aggregate_after_correction"]
    expected_counts = (5, 4, 3, 2, 1, 12, 5)
    actual_counts = tuple(before[key] for key in ("source_event_count", "converted_event_count", "preserved_event_count", "omitted_event_count", "false_generated_event_count", "source_feature_count", "preserved_feature_count"))
    if actual_counts != expected_counts:
        raise SystemExit(f"before-correction count drift: {actual_counts}")
    close(before["event_preservation_rate"], .6); close(before["event_omission_rate"], .4)
    close(before["false_generation_rate"], .25); close(before["feature_preservation_rate"], 5/12)
    close(after["event_preservation_rate"], .8); close(after["event_omission_rate"], .2)
    close(after["false_generation_rate"], 0); close(after["feature_preservation_rate"], 7/12)

    if len(fixture["cases"]) != 5 or fixture["cases"][0]["transcript"] != fixture["cases"][1]["transcript"]:
        raise SystemExit("same-transcript fixture drift")
    events = [event for case in fixture["cases"] for side in ("source_events", "converted_events") for event in case[side]]
    if any(event.get("raw_signal_retained") for event in events):
        raise SystemExit("raw signal retained in fixture")

    combined = re.sub(r"\s+", " ", tex + " " + (HERE / "fact-check.md").read_text(encoding="utf-8"))
    required = [
        "All five cases are constructed", "not an accuracy or causal result",
        "Independent human annotation has not yet been completed",
        "participatory review", "not a culturally universal model",
        "does not infer emotion, disability, truthfulness, personality, culture, or intention",
        "Group Draft Note rather than a normative standard", "neither RAG nor a graph-memory replacement",
    ]
    missing = [phrase for phrase in required if phrase not in combined]
    if missing:
        raise SystemExit(f"required scope language missing: {missing}")

    print(f"PASS draft4 audit | British-English blacklist=0 | citations={len(cited)} | figures={len(figures)} | cases=5 | raw_signal=false")


if __name__ == "__main__":
    main()
