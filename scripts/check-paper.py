"""Static editorial checks for the TopoDialogue first draft."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "topodialogue-en.tex"
BIB = ROOT / "paper" / "references.bib"

AMERICAN_FORMS = {
    "analyze", "analyzed", "analyzes", "analyzing",
    "artifact", "artifacts",
    "behavior", "behaviors", "behavioral",
    "center", "centered", "centering", "centers",
    "characterize", "characterized", "characterizes", "characterizing",
    "color", "colored", "colors",
    "generalize", "generalized", "generalizes", "generalizing",
    "labeled", "labeling",
    "modeling",
    "normalization", "normalize", "normalized", "normalizes", "normalizing",
    "operationalize", "operationalized", "operationalizes", "operationalizing",
    "optimization", "optimize", "optimized", "optimizes", "optimizing",
    "organization", "organizations",
    "visualization", "visualizations", "visualize", "visualized", "visualizes", "visualizing",
}


def main() -> None:
    tex = PAPER.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")

    prose = re.sub(r"(?m)^%.*$", "", tex)
    prose = re.sub(r"\\includegraphics(?:\[[^]]*\])?\{[^}]+\}", "", prose)
    # LaTeX's language-neutral layout command is named ``\\centering``.
    # Remove command names so they cannot be mistaken for manuscript prose.
    prose = re.sub(r"\\[A-Za-z@]+\*?", "", prose)
    found = sorted({
        match.group(0).casefold()
        for word in AMERICAN_FORMS
        for match in re.finditer(rf"\b{re.escape(word)}\b", prose, flags=re.IGNORECASE)
    })
    if found:
        raise SystemExit(f"American English forms found in manuscript: {', '.join(found)}")

    citation_groups = re.findall(r"\\cite[pt]?\{([^}]+)\}", tex)
    cited = {key.strip() for group in citation_groups for key in group.split(",")}
    available = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
    missing = cited - available
    unused = available - cited
    if missing:
        raise SystemExit(f"Missing bibliography keys: {', '.join(sorted(missing))}")
    if unused:
        raise SystemExit(f"Unused bibliography keys: {', '.join(sorted(unused))}")

    figure_paths = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    absent = [path for path in figure_paths if not (ROOT / "paper" / path).exists()]
    if absent:
        raise SystemExit(f"Missing figures: {', '.join(absent)}")

    required_phrases = [
        "not a calibrated measure of psychological state",
        "specification-conformance tests",
        "British English",
    ]
    normalised_tex = re.sub(r"\s+", " ", tex)
    absent_phrases = [phrase for phrase in required_phrases if phrase not in normalised_tex]
    if absent_phrases:
        raise SystemExit(f"Required scope language missing: {', '.join(absent_phrases)}")

    environments = re.findall(r"\\(begin|end)\{([^}]+)\}", tex)
    stack: list[str] = []
    for action, environment in environments:
        if action == "begin":
            stack.append(environment)
        elif not stack or stack.pop() != environment:
            raise SystemExit(f"Unbalanced LaTeX environment near: {action}{{{environment}}}")
    if stack:
        raise SystemExit(f"Unclosed LaTeX environments: {', '.join(stack)}")

    print(
        "PASS paper audit | British-English blacklist=0 | "
        f"citations={len(cited)} | figures={len(figure_paths)}"
    )


if __name__ == "__main__":
    main()
