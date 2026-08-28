"""Static, numerical, privacy, and British-English audit for Paper 3."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAPER = HERE / "topodialogue-en.tex"
BIB = HERE / "references.bib"
DATA = ROOT / "examples" / "real"

AMERICAN_FORMS = {
    "analyze", "analyzed", "analyzes", "analyzing", "artifact", "artifacts",
    "behavior", "behavioral", "center", "centered", "centering", "centers",
    "characterize", "characterized", "characterizes", "characterizing",
    "color", "colored", "colors", "generalize", "generalized", "labeled",
    "labeling", "modeling", "normalization", "normalize", "normalized",
    "operationalize", "operationalized", "optimization", "optimize",
    "organization", "visualization", "visualizations", "visualize",
}


def close(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(actual - expected) > tolerance:
        raise SystemExit(f"metric drift: actual={actual}, expected={expected}")


def main() -> None:
    tex = PAPER.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    comparison = json.loads((DATA / "real-case-01.comparison.json").read_text(encoding="utf-8"))
    public = json.loads((DATA / "real-case-01.public.json").read_text(encoding="utf-8"))
    audit = json.loads((DATA / "real-case-01.audit.json").read_text(encoding="utf-8"))

    prose = re.sub(r"(?m)^%.*$", "", tex)
    prose = re.sub(r"\\includegraphics(?:\[[^]]*\])?\{[^}]+\}", "", prose)
    prose = re.sub(r"\\[A-Za-z@]+\*?", "", prose)
    found = sorted({
        match.group(0).casefold()
        for word in AMERICAN_FORMS
        for match in re.finditer(rf"\b{re.escape(word)}\b", prose, flags=re.IGNORECASE)
    })
    if found:
        raise SystemExit(f"American English forms found: {', '.join(found)}")

    citation_groups = re.findall(r"\\cite[pt]?\{([^}]+)\}", tex)
    cited = {key.strip() for group in citation_groups for key in group.split(",")}
    available = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
    if cited - available:
        raise SystemExit(f"missing bibliography keys: {sorted(cited - available)}")
    if available - cited:
        raise SystemExit(f"unused bibliography keys: {sorted(available - cited)}")

    figure_names = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    figure_root = ROOT / "paper" / "figures" / "draft3"
    absent = [name for name in figure_names if not (figure_root / name).exists()]
    if absent:
        raise SystemExit(f"missing figures: {absent}")

    counts = comparison["event_type_counts"]
    if comparison["event_count"] != 137 or sum(counts.values()) != 137:
        raise SystemExit("event-count drift")
    if audit["turn_count"] != 114 or audit["character_count"] != 69030:
        raise SystemExit("audit-count drift")
    close(comparison["event_enriched_public_derivative"]["revisit_rate"], 0.280702)
    close(comparison["event_enriched_public_derivative"]["loop_score"], 0.498714)
    close(comparison["event_enriched_public_derivative"]["projection_stability"], 0.206696)

    messages = public["messages"]
    if len(messages) != 114 or not public["release"]["content_withheld"]:
        raise SystemExit("public derivative shape drift")
    for message in messages:
        if not re.fullmatch(r"\[content withheld; (?:short|medium|long|very_long) turn\]", message["text"]):
            raise SystemExit("unexpected public text payload")
        annotations = message["annotations"]
        if not annotations.get("content_withheld"):
            raise SystemExit("withholding flag missing")
        if any(event.get("evidence") for event in annotations.get("interaction_events", [])):
            raise SystemExit("public event evidence was not removed")
        node_keys = {node["key"] for node in annotations.get("nodes", [])}
        if any(key.startswith(("length:", "form:")) for key in node_keys):
            raise SystemExit("structural metadata leaked into recurrence features")

    required = [
        "not an accuracy or causal result",
        "Independent human annotation has not yet been completed",
        "not a psychological reading",
        "persistent homology",
        "British English",
        "individual, relationship, and context baselines",
        "not a culturally universal model",
    ]
    combined = re.sub(r"\s+", " ", tex + " " + (HERE / "fact-check.md").read_text(encoding="utf-8"))
    missing = [phrase for phrase in required if phrase not in combined]
    if missing:
        raise SystemExit(f"required scope language missing: {missing}")

    print(
        "PASS draft3 audit | British-English blacklist=0 | citations="
        f"{len(cited)} | figures={len(figure_names)} | turns=114 | events=137 | raw_text=false"
    )


if __name__ == "__main__":
    main()
