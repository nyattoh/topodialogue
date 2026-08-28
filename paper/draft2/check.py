"""Static audit for the TopoDialogue second-draft manuscript."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAPER = HERE / "topodialogue-en.tex"
BIB = HERE / "references.bib"

AMERICAN_FORMS = {
    "analyze", "analyzed", "analyzes", "analyzing",
    "artifact", "artifacts", "behavior", "behaviours", "behavioral",
    "center", "centered", "centering", "centers", "characterize",
    "characterized", "characterizes", "characterizing", "color", "colored",
    "colors", "generalize", "generalized", "generalizes", "generalizing",
    "labeled", "labeling", "modeling", "normalization", "normalize",
    "normalized", "normalizes", "normalizing", "operationalize",
    "operationalized", "operationalizes", "operationalizing", "optimization",
    "optimize", "optimized", "optimizes", "optimizing", "organization",
    "organizations", "visualization", "visualizations", "visualize",
    "visualized", "visualizes", "visualizing",
}


def main() -> None:
    tex = PAPER.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")

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
    missing = cited - available
    unused = available - cited
    if missing:
        raise SystemExit(f"Missing bibliography keys: {', '.join(sorted(missing))}")
    if unused:
        raise SystemExit(f"Unused bibliography keys: {', '.join(sorted(unused))}")

    figure_names = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    figure_root = ROOT / "paper" / "figures"
    absent = [name for name in figure_names if not (figure_root / name).exists()]
    if absent:
        raise SystemExit(f"Missing figures: {', '.join(absent)}")

    required = [
        "not a calibrated measure of psychological state",
        "specification conformance",
        "British English",
        "persistent homology",
        "export completeness",
    ]
    normalised = re.sub(r"\s+", " ", tex)
    absent_phrases = [phrase for phrase in required if phrase not in normalised]
    if absent_phrases:
        raise SystemExit(f"Required scope language missing: {', '.join(absent_phrases)}")

    environments = re.findall(r"\\(begin|end)\{([^}]+)\}", tex)
    stack: list[str] = []
    for action, environment in environments:
        if action == "begin":
            stack.append(environment)
        elif not stack or stack.pop() != environment:
            raise SystemExit(f"Unbalanced LaTeX environment: {action}{{{environment}}}")
    if stack:
        raise SystemExit(f"Unclosed LaTeX environments: {', '.join(stack)}")

    print(
        "PASS draft2 audit | British-English blacklist=0 | "
        f"citations={len(cited)} | figures={len(figure_names)}"
    )


if __name__ == "__main__":
    main()
