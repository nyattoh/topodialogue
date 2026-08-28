# TopoDialogue empirical study pack v1

This pack is the next evidence gate after the controlled synthetic robustness
benchmark. It is ready for ethical/privacy review and pilot recruitment; it
does not represent completed participant evidence.

## Two studies, kept separate

1. **Independent annotation study** — tests whether two people can apply the
   event and trajectory labels consistently to the same consented dialogues.
2. **Display comparison study** — tests whether transcript-only, flat timeline,
   and layered 3D views change participants' ability to identify declared
   recurrence, progress, and escape.

Do not combine the studies into a single success score. Annotation agreement is
an input-validity question; display comparison is a user-interface question.

## Required sequence

1. Review `participant-information-ja.md` and `consent-ja.md`.
2. Run a small training pilot using synthetic examples only.
3. Freeze the codebook and write its version into every annotation file.
4. Collect two independent annotations per dialogue. Annotators must not see
   each other's labels before submission.
5. Run `python -m topodialogue.cli agreement LEFT RIGHT` for each matched pair.
6. Record exclusions before looking at condition differences.
7. Run the display comparison only after the annotation gate is interpretable.

## Software dry run

Before collecting any participant response, run:

```powershell
python -m topodialogue.cli study-dry-run --output output/empirical/study-dry-run-v1.json
```

The output deliberately uses identifiers beginning with `synthetic-` and has
`synthetic: true` at every study boundary. It verifies annotation aggregation,
unresolved-tie preservation, automatic-event scoring, balanced condition
assignment, response validation, exclusions, and descriptive summaries. It is
not evidence about people, natural dialogue, accessibility, or display effects.

After real independent annotations exist, use:

```powershell
python -m topodialogue.cli adjudicate ANNOTATOR_A.json ANNOTATOR_B.json -o adjudicated.json
python -m topodialogue.cli evaluate-events adjudicated.json predicted-events.json -o event-evaluation.json
```

For the display study, create and analyse a frozen assignment with:

```powershell
python -m topodialogue.cli display-assign participant-ids.json case-ids.json -o assignments.json
python -m topodialogue.cli display-analyze assignments.json responses.json answer-key.json -o display-summary.json
```

The display summary is descriptive. Any inferential analysis, exclusion rule,
or stopping rule must be pre-specified before opening condition results.

## Stop conditions

- Stop natural-dialogue collection if consent or deletion handling is unclear.
- Revise, merge, or drop labels that annotators cannot distinguish reliably.
- Do not tune thresholds on the held-out evaluation set.
- Do not claim accessibility benefit without review by users of the relevant
  access pathways.
- Treat low agreement and null condition differences as publishable findings.

## Files

- `protocol-ja.md` — study design and analysis boundary.
- `annotation-codebook-ja.md` — observable labels and decision rules.
- `participant-information-ja.md` — Japanese participant information.
- `consent-ja.md` — Japanese consent checklist.
- `templates/annotation.json` — one independent annotation file.
- `templates/display-response.json` — one display-study response.
- `templates/annotation-table.csv` — non-programmer-friendly annotation table.
- `outreach/` — ready-to-copy recruitment, information, consent, instruction,
  reminder, form, and coordinator materials in Japanese.
- `output/empirical/study-dry-run-v1.json` — generated synthetic software-path
  verification (outside this directory).
