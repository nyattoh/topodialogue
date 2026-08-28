TopoDialogue III source and reproducibility bundle
=================================================

Canonical paper source
----------------------
main.tex is the British-English submission source. references.bib and the
three PNG files in figures/ are required to compile it with a standard LaTeX
installation containing geometry, amsmath, booktabs, graphicx, microtype,
natbib, and hyperref.

An installation-independent review PDF can also be built from the same source:

  python build_pdf.py topodialogue-draft3-en.pdf

Reproduce the released public analysis
--------------------------------------
The public/ directory contains no utterance content. From this bundle root:

  python -m topodialogue.cli trajectory public/real-case-01.public.json -o reproduced-analysis.json
  python paper/render_figures.py
  python paper/check.py
  python -m pytest -q
  node --test visualizer/trajectory-analysis.test.js

The original conversation is intentionally excluded. The released figures can
be regenerated from the content-withheld public derivative and aggregate
reports. Automatic interaction labels are candidates, not human gold labels.
The two-annotator gate is documented in docs/14-interaction-events.md.

Release boundary
----------------
Do not add a raw transcript to this archive. The project makes no inference
about hidden mental states and no clinical or diagnostic claim.
