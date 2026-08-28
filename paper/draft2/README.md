# TopoDialogue second-draft package

This directory contains the second manuscript draft prepared from the
implementation and evidence already present in the project. The first-draft
files in `paper/` are deliberately unchanged by this package.

## Files

- `topodialogue-en.tex`: self-contained submission manuscript in British English.
- `topodialogue-ja.md`: Japanese counterpart with the same claim boundaries.
- `references.bib`: bibliography used by the English manuscript.
- `fact-check.md`: source, implementation, measurement, and editorial audit.
- `check.py`: local static audit for spelling, citations, figures, and scope language.

The second draft sharpens the paper around one falsifiable question: can a
return to a similar semantic feature region, and the amount of change during
that return, be represented reproducibly without treating a rendered curve as
evidence of psychological change? It keeps the Phase-1 boundary. It does not
claim persistent homology, body sensing, clinical interpretation, online
intervention effects, or accuracy on naturally occurring conversations.

## Build and audit

From the project root:

```powershell
python paper/draft2/check.py
```

With a conventional LaTeX installation, compile from this directory:

```powershell
pdflatex topodialogue-en.tex
bibtex topodialogue-en
pdflatex topodialogue-en.tex
pdflatex topodialogue-en.tex
```

The figures are reused from `paper/figures/`; the manuscript references them by
relative path. The current project audit and test commands remain the source
of truth for the implementation claims:

```powershell
python scripts/check-paper.py
python -m pytest -q
python -m topodialogue.cli validate-synthetic
node --test visualizer/trajectory-analysis.test.js
```
