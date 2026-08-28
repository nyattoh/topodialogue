"""Render deterministic Paper 5 figures from the checked agency report."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "examples" / "agency" / "synthetic-strategy-report.json"
OUTPUT = ROOT / "paper" / "figures" / "draft5"

def save(fig, name):
    OUTPUT.mkdir(parents=True, exist_ok=True); fig.tight_layout()
    fig.savefig(OUTPUT / name, dpi=220, bbox_inches="tight"); plt.close(fig)

def main():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.spines.top":False,"axes.spines.right":False})
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    labels = ["No history","Text RAG","Event RAG","Relation graph","Controlled\nadaptation"]
    matrix = np.array([[0,0,0,0],[1,0,0,0],[0,1,0,0],[0,1,1,0],[0,1,1,1]])
    fig, ax = plt.subplots(figsize=(8.8,4.0)); ax.imshow(matrix, cmap="Reds", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(4), ["Text retrieval","Event retrieval","Relation model","Strategy proposal"])
    ax.set_yticks(range(5), labels)
    for y in range(5):
        for x in range(4): ax.text(x,y,"Yes" if matrix[y,x] else "-",ha="center",va="center",color="white" if matrix[y,x] else "#5a6570",weight="bold")
    ax.set_title("Capability separation", weight="bold", color="#17324d"); save(fig,"condition-capabilities.png")

    summaries = report["condition_summaries"]
    novelty = [summaries[k]["mean_user_originated_novelty"] for k in summaries]
    recurrence = [summaries[k]["mean_assistant_induced_recurrence"] for k in summaries]
    burden = [summaries[k]["mean_interaction_burden"] for k in summaries]
    x = np.arange(5); fig, ax = plt.subplots(figsize=(9.2,4.4))
    ax.plot(x,novelty,"o-",label="User-originated novelty",color="#237a67",lw=2)
    ax.plot(x,recurrence,"o-",label="Assistant-induced recurrence",color="#b22542",lw=2)
    ax.plot(x,burden,"o-",label="Interaction burden",color="#516c91",lw=2)
    ax.set_ylim(0,1); ax.set_xticks(x,labels); ax.set_ylabel("Declared mean (0-1)"); ax.grid(axis="y",alpha=.22); ax.legend(frameon=False,ncols=3,loc="upper center")
    ax.set_title("Constructed outcomes: arithmetic test values, not human effects",weight="bold",color="#17324d"); save(fig,"constructed-outcomes.png")

    gate = report["topology_gate"]; fig, axes = plt.subplots(1,2,figsize=(9.2,4.0))
    axes[0].axis("off"); boxes=[(.5,.82,"Evidence + uncertainty"),(.5,.58,"Strategy proposal"),(.5,.34,"Explicit user decision"),(.5,.10,"Execute only if adopted")]
    for x0,y0,label in boxes: axes[0].text(x0,y0,label,ha="center",va="center",transform=axes[0].transAxes,bbox=dict(boxstyle="round,pad=.45",facecolor="#e8eef4",edgecolor="#6f8191"))
    for y1,y2 in ((.75,.65),(.51,.41),(.27,.17)): axes[0].annotate("",xy=(.5,y2),xytext=(.5,y1),xycoords=axes[0].transAxes,arrowprops=dict(arrowstyle="->",color="#b22542"))
    axes[0].set_title("Control gate",weight="bold",color="#17324d")
    axes[1].bar([0,1],[gate["baseline_explanatory_score"],gate["richer_topology_score"]],color=["#6f8191","#b22542"])
    axes[1].axhline(gate["baseline_explanatory_score"]+gate["minimum_gain"],ls="--",color="#237a67",label="Admission threshold")
    axes[1].set_xticks([0,1],["Baseline","Richer"]); axes[1].set_ylim(0,1); axes[1].set_ylabel("Declared explanatory score"); axes[1].legend(frameon=False); axes[1].set_title("Topology gate: not admitted",weight="bold",color="#17324d")
    save(fig,"control-and-topology-gates.png")
    print(f"Rendered 3 figures to {OUTPUT}")

if __name__ == "__main__": main()
