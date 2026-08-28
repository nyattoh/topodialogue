# TopoDialogue first-draft paper package

This directory contains the implementation-grounded first draft requested for
arXiv preparation.

- `topodialogue-en.tex`: English submission draft, written in British English.
- `topodialogue-ja.md`: Japanese counterpart with the same claim boundaries.
- `references.bib`: primary-source-checked bibliography used by the draft.
- `fact-check.md`: claim, evidence, citation, and wording audit.
- `figures/`: reproducible browser captures from the synthetic fixtures.

The formative `Assistant  alphaXiv.md` clipping and its concept map were used as
design provenance. They are not treated as scholarly evidence. The paper narrows
that broader programme to what the Phase-1 software currently implements and
tests: deterministic co-ordinates, operational recurrence classes, speaker-aware
provenance, six synthetic fixtures, and explicit display warnings.

## Build

From this directory, on a machine with a conventional LaTeX installation:

```powershell
pdflatex topodialogue-en.tex
bibtex topodialogue-en
pdflatex topodialogue-en.tex
pdflatex topodialogue-en.tex
```

The present development machine does not have `pdflatex`, `latexmk`, `bibtex`,
or `chktex` installed. Repository tests and the paper-specific static audit can
still be run from the project root:

```powershell
python scripts/check-paper.py
python -m pytest -q
python -m topodialogue.cli validate-synthetic
node --test visualizer/trajectory-analysis.test.js
```

## Before submission

Compile and inspect every page before the final arXiv action. Add a public
repository URL and archival software identifier in a later revision when the
software archive is released. The current result is a research-software first
draft, not a completed human-subject evaluation and not a clinical or
psychological instrument.
