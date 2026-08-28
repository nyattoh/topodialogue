# TopoDialogue Paper 5 package

This directory contains the British-English paper source, Japanese companion, references, deterministic figures, PDF builder, and static audit.

## Reproduce

```powershell
python -m topodialogue.cli strategy-audit examples/agency/synthetic-strategy-cases.json --output examples/agency/synthetic-strategy-report.json
python paper/draft5/render_figures.py
python paper/draft5/check.py
python paper/draft5/build_pdf.py output/zenodo/draft5/TopoDialogue-V-Agency-Rendering-Sovereignty-EN.pdf
```

The fixture validates arithmetic and user-control contracts only. It does not measure human benefit.
