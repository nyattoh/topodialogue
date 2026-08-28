# TopoDialogue III release preparation

This directory contains the British-English manuscript, Japanese companion,
fact-check ledger, bibliography, figure renderer, release audit, and Zenodo
metadata for Paper 3.

## Regenerate the public case and figures

The first command requires the author's local raw file. Do not copy that file
into a public package or Git commit.

```powershell
python -m topodialogue.cli prepare-case "グッド・オーメンズ3 感想と評価.json" --output-dir examples\real --case-id real-case-01
python paper\draft3\render_figures.py
python paper\draft3\check.py
```

The figures and released analysis use only `examples/real/real-case-01.public.json`,
`comparison.json`, and `analysis.json`. The audit contains aggregate pattern
counts and a raw-input fingerprint, but no utterance text.

## Human annotation gate

Create two independent files using `docs/14-interaction-events.md`, then run:

```powershell
python -m topodialogue.cli agreement annotator-a.json annotator-b.json -o agreement.json
```

No human agreement value is included in this pilot. Do not replace the gate
with automatic self-agreement.

## Upload set

Upload only the three files from `output/zenodo/draft3/`:

1. `topodialogue-draft3-en.pdf`
2. `topodialogue-draft3-ja.md`
3. `topodialogue-draft3-source.zip`

`zenodo-metadata.md` is a form-filling aid and is not an upload.
