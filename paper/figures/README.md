# Paper figure captures

All captures use projection seed `1729`. They are generated from synthetic,
non-personal dialogue fixtures so the screenshots can be shared safely.

- `fig01-spiral-revisit.png`: repeated semantic region with measurable progress.
- `fig02-assistant-induced-loop.png`: closed recurrence driven by assistant turns.
- `fig03-user-originated-escape.png`: recurrence followed by user-originated novelty.
- `fig04-speaker-drift-artifact.png`: speaker-conditioned projection collapse used
  as a visual stress case. This condition is visible in the trajectory but is not
  currently emitted as a dedicated automatic warning.

Regenerate from the project root while the local visualizer is running:

```powershell
node scripts/capture-paper-figures.cjs
```
