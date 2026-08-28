"""Render deterministic figures for Paper 4 from the checked JSON report."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "examples" / "modality" / "synthetic-conversion-report.json"
OUTPUT = ROOT / "paper" / "figures" / "draft4"


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
    })


def save(fig: plt.Figure, name: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT / name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def conversion_rates(report: dict) -> None:
    labels = ["Preservation", "Omission", "False generation", "Feature preservation"]
    keys = ["event_preservation_rate", "event_omission_rate", "false_generation_rate", "feature_preservation_rate"]
    before = [report["aggregate_before_correction"][key] for key in keys]
    after = [report["aggregate_after_correction"][key] for key in keys]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.2, 4.3))
    ax.bar(x - 0.18, before, 0.36, label="Before correction", color="#9aa8b5")
    ax.bar(x + 0.18, after, 0.36, label="After correction", color="#b22542")
    ax.set_ylim(0, 1.04)
    ax.set_ylabel("Rate")
    ax.set_xticks(x, labels, rotation=12, ha="right")
    ax.legend(frameon=False, ncols=2, loc="upper center")
    ax.grid(axis="y", alpha=.22)
    save(fig, "conversion-rates.png")


def pathway_preservation(report: dict) -> None:
    labels = [row["before_correction"]["case_id"].replace("-", "\n") for row in report["cases"]]
    before = [row["before_correction"]["event_preservation_rate"] for row in report["cases"]]
    after = [row["after_correction"]["event_preservation_rate"] for row in report["cases"]]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9.2, 4.3))
    ax.bar(x - 0.18, before, 0.36, label="Before correction", color="#6f8191")
    ax.bar(x + 0.18, after, 0.36, label="After correction", color="#b22542")
    ax.set_ylim(0, 1.04)
    ax.set_ylabel("Event preservation rate")
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, ncols=2, loc="upper center")
    ax.grid(axis="y", alpha=.22)
    save(fig, "pathway-preservation.png")


def same_transcript() -> None:
    fig, ax = plt.subplots(figsize=(9.2, 3.7))
    ax.axis("off")
    boxes = {
        "fall": (.06, .66, "Speech fixture A\nterminal fall\nsource: adoption"),
        "rise": (.06, .18, "Speech fixture B\nterminal rise\nsource: handover"),
        "text1": (.40, .66, "Same Japanese transcript\nsore de ii"),
        "text2": (.40, .18, "Same Japanese transcript\nsore de ii"),
        "flat": (.73, .66, "Converted event\nadoption"),
        "wrong": (.73, .18, "Converted event\nadoption\nthen user relabels: handover"),
    }
    for key, (x, y, label) in boxes.items():
        colour = "#f4dce2" if key == "wrong" else "#e9eef2"
        ax.text(x, y, label, transform=ax.transAxes, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=.55", facecolor=colour, edgecolor="#708090"))
    for y in (.66, .18):
        ax.annotate("", xy=(.33, y), xytext=(.19, y), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="->", color="#8a3046", lw=1.5))
        ax.annotate("", xy=(.66, y), xytext=(.52, y), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="->", color="#8a3046", lw=1.5))
    ax.text(.5, .96, "Identical text does not prove identical source evidence",
            transform=ax.transAxes, ha="center", va="top", fontsize=13, weight="bold", color="#17324d")
    ax.text(.5, .01, "Constructed conditions only: no universal prosody-to-intent rule is asserted.",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#596773")
    save(fig, "same-transcript.png")


def main() -> None:
    style()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    conversion_rates(report)
    pathway_preservation(report)
    same_transcript()
    print(f"Rendered 3 figures to {OUTPUT}")


if __name__ == "__main__":
    main()
