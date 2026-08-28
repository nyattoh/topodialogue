# TopoDialogue Paper 4 package

This directory contains the British-English source, Japanese companion version, references, reproducible figure renderer, PDF builder, and static audit for Paper 4.

## Reproduce

From the repository root:

```powershell
python -m topodialogue.cli modality-audit examples/modality/synthetic-conversion-cases.json --output examples/modality/synthetic-conversion-report.json
python paper/draft4/render_figures.py
python paper/draft4/check.py
python paper/draft4/build_pdf.py output/zenodo/draft4/TopoDialogue-IV-What-Transcription-Leaves-Behind-EN.pdf
```

The validation is synthetic and checks accounting, provenance, correction, and packaging. It does not measure field accuracy or accessibility outcomes.
