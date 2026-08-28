# Paper 4 fact-check and claim audit

Checked on 16 August 2026.

## Reproducible claims

- The fixture has five constructed cases and four converted events before correction.
- Before correction: 3/5 events preserved, 2/5 omitted, 1/4 falsely generated, and 5/12 declared source features preserved.
- After one relabelling: 4/5 events preserved, 1/5 omitted, 0/4 falsely generated, and 7/12 features preserved.
- The first two cases have exactly the same transcript.
- Every distributed event has `raw_signal_retained: false`.
- `python -m topodialogue.cli modality-audit ...` regenerates the report.
- `check.py` fails if metrics, sources, figures, privacy flags, or required scope statements drift.

## Source verification

- W3C NAUR is correctly described as a **Group Draft Note**, not a W3C Recommendation: <https://www.w3.org/TR/naur/>.
- WCAG 2.2 is cited for error identification, review, and correction principles: <https://www.w3.org/TR/WCAG22/>.
- Müller et al. (2023) is an ACL publication on the losses and limitations of gloss-based sign-language translation: DOI 10.18653/v1/2023.acl-short.60.
- Stolcke et al. (2000) studies lexical, prosodic, and contextual evidence for dialogue-act modelling: ACL Anthology J00-3003.
- Kafle et al. (2019) studies acoustic-prosodic cues beyond text-only measures: DOI 10.18653/v1/W19-1702.
- TopoDialogue I, II, and III DOI records were checked against Zenodo: 10.5281/zenodo.21962837, 10.5281/zenodo.21963131, and 10.5281/zenodo.21964573.

## Claims deliberately not made

- This is not an accuracy or causal result.
- Independent human annotation has not yet been completed.
- Participatory review with speech, sign-language, or AAC users has not yet been completed.
- Event labels in the fixtures are stipulated and do not infer emotion, disability, truthfulness, personality, culture, or intention.
- The framework is not a culturally universal model.
- A terminal contour is not asserted to determine intention.
- Synthetic improvement after correction is not evidence of model learning.
- NAUR is not presented as a normative standard.
- TopoDialogue is neither RAG nor a graph-memory replacement.

## Remaining empirical gates

1. Freeze pathway-specific annotation guidance before observing evaluation results.
2. Measure independent human agreement and adjudication effects.
3. Conduct participatory review with people familiar with each represented pathway.
4. Evaluate speech, sign-language, and AAC pathways separately.
5. Reassess privacy risks from timing and rare interaction patterns before any real-data release.
