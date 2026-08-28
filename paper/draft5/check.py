"""Static, numerical, scope, citation, and British-English audit for Paper 5."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
TEX=HERE/"topodialogue-en.tex"; BIB=HERE/"references.bib"; REPORT=ROOT/"examples"/"agency"/"synthetic-strategy-report.json"
AMERICAN={"analyze","analyzed","behavior","behavioral","centered","color","labeled","modeling","normalization","normalize","normalized","operationalize","operationalized","personalization","visualization","visualize","artifact","artifacts"}

def main():
    tex=TEX.read_text(encoding="utf-8"); bib=BIB.read_text(encoding="utf-8"); report=json.loads(REPORT.read_text(encoding="utf-8"))
    prose=re.sub(r"(?m)^%.*$|\\includegraphics(?:\[[^]]*\])?\{[^}]+\}|\\[A-Za-z@]+\*?","",tex)
    found=sorted({m.group(0).casefold() for word in AMERICAN for m in re.finditer(rf"\b{word}\b",prose,re.I)})
    if found: raise SystemExit(f"American English forms found: {found}")
    cited={k.strip() for g in re.findall(r"\\cite[pt]?\{([^}]+)\}",tex) for k in g.split(",")}; available=set(re.findall(r"@[A-Za-z]+\{([^,]+),",bib))
    if cited != available: raise SystemExit(f"bibliography mismatch: missing={sorted(cited-available)}, unused={sorted(available-cited)}")
    figures=re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}",tex); absent=[f for f in figures if not (ROOT/"paper"/"figures"/"draft5"/f).exists()]
    if absent: raise SystemExit(f"missing figures: {absent}")
    if report["episode_count"] != 15 or report["contract_violations"]: raise SystemExit("agency fixture drift")
    if set(report["adaptive_control_coverage"].values()) != {1.0}: raise SystemExit("adaptive control coverage drift")
    adaptive=report["condition_summaries"]["user_controlled_adaptation"]
    if adaptive["decision_counts"] != {"adopt":1,"reject":0,"repair":0,"correct":1,"delete":0,"stop":1}: raise SystemExit("decision count drift")
    gate=report["topology_gate"]
    if abs(gate["observed_gain"]-.01)>1e-8 or gate["richer_topology_justified"]: raise SystemExit("topology gate drift")
    combined=tex+(HERE/"fact-check.md").read_text(encoding="utf-8")
    required=["All episodes are constructed","not the sole objective","does not infer a stable personality, culture, disability, emotion, or intention","future participatory study","suggestion-only","not evidence that adaptation outperforms RAG or graphs"]
    missing=[p for p in required if p not in combined]
    if missing: raise SystemExit(f"required scope language missing: {missing}")
    print(f"PASS draft5 audit | British-English blacklist=0 | citations={len(cited)} | figures={len(figures)} | episodes=15 | violations=0")

if __name__ == "__main__": main()
