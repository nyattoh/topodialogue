# Implementation status — 2026-08-14

Phase 1 and the arXiv-first-draft trajectory instrument are implemented. The
Python CLI and browser analyzer share the same deterministic operational model:
fixed-seed coordinates, explicit axis definitions, recurrence/progress-based
shape labels, and first-origin novelty provenance.

## Verified gates

- `python -m pytest -q` — 12 passed.
- `python -m topodialogue.cli validate-synthetic` — 6/6 expected cases passed.
- `node --test visualizer/trajectory-analysis.test.js` — 7/7 passed.
- `python scripts/check-paper.py` — British-English blacklist 0, six citation
  keys resolved, four figures present, and LaTeX environments balanced.
- `visualizer/e2e-smoke.js` — synthetic spiral, assistant loop, escape, Z-axis
  switch, six axis definitions, artifact report, and a 90-turn real JSON passed.

Three.js 0.170.0 is vendored for offline reproducibility. The current boundary
does not include Persistent Homology, body sensors, multi-agent orchestration,
cloud storage, diagnosis, or claims that rendered geometry is a topological or
psychological invariant.

The first-draft package now lives in `paper/`: a British-English LaTeX
manuscript, a Japanese counterpart, a six-source verified bibliography, four
captured figures, and a claim/fact-check audit. The current machine has no
`pdflatex`, `latexmk`, `bibtex`, or `chktex`, so PDF compilation remains an
environmental hand-over item. Author details, a public repository URL, and an
archival release identifier must be supplied before submission.
