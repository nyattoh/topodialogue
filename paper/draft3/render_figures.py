"""Render the third-paper figures from released, content-withheld artefacts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "examples" / "real"
OUTPUT = ROOT / "paper" / "figures" / "draft3"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(fig, name: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def event_counts(comparison: dict) -> None:
    order = ["handover", "reframing", "repair", "rejection", "revisit", "adoption", "pause"]
    values = [comparison["event_type_counts"].get(label, 0) for label in order]
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    bars = ax.bar(order, values, color="#9f233d")
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_ylabel("Candidate events")
    ax.set_ylim(0, max(values) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", rotation=22)
    fig.tight_layout()
    save(fig, "event-counts.png")


def trajectory(analysis: dict) -> None:
    points = analysis["points"]
    x = np.array([row["semantic_x"] for row in points])
    y = np.array([row["semantic_y"] for row in points])
    turn = np.array([row["turn_index"] for row in points])
    revisit = np.array([row["is_revisit"] for row in points])
    fig, ax = plt.subplots(figsize=(7.6, 6.0))
    ax.plot(x, y, color="#9ba0a8", linewidth=0.9, alpha=0.7, zorder=1)
    scatter = ax.scatter(x, y, c=turn, cmap="viridis", s=20, alpha=0.86, zorder=2)
    ax.scatter(x[revisit], y[revisit], facecolors="none", edgecolors="#b01536", s=74,
               linewidths=1.25, label="Operational revisit", zorder=3)
    ax.set_xlabel("Deterministic semantic projection X")
    ax.set_ylabel("Deterministic semantic projection Y")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    colour = fig.colorbar(scatter, ax=ax, pad=0.02)
    colour.set_label("Turn index")
    fig.tight_layout()
    save(fig, "public-trajectory.png")


def comparison(comparison: dict) -> None:
    base = comparison["text_only_baseline"]
    enriched = comparison["event_enriched_public_derivative"]
    labels = ["Revisit rate", "LoopScore", "Projection\nstability"]
    base_values = [base["revisit_rate"], base["loop_score"], base["projection_stability"]]
    event_values = [enriched["revisit_rate"], enriched["loop_score"], enriched["projection_stability"]]
    positions = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    left = ax.bar(positions - width / 2, base_values, width, label="Text-only fallback", color="#708090")
    right = ax.bar(positions + width / 2, event_values, width, label="Public event derivative", color="#9f233d")
    ax.bar_label(left, fmt="%.3f", padding=3, fontsize=8)
    ax.bar_label(right, fmt="%.3f", padding=3, fontsize=8)
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 0.62)
    ax.set_ylabel("Operational value")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, "baseline-comparison.png")


def main() -> None:
    comparison_payload = load("real-case-01.comparison.json")
    event_counts(comparison_payload)
    trajectory(load("real-case-01.analysis.json"))
    comparison(comparison_payload)
    print(f"wrote 3 figures to {OUTPUT}")


if __name__ == "__main__":
    main()
