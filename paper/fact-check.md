# Fact-check and editorial audit

Audit date: 2026-08-14 (Asia/Tokyo)

## Scope decision

The supplied `Assistant  alphaXiv.md` and concept map are the design origin for
the paper. Their broad claims about topology, embodiment, culture, privacy, and
rendering sovereignty are not imported as established facts. The first draft
reports only the Phase-1 instrument and its synthetic validation. In particular,
the manuscript does **not** claim to infer mental state, measure human progress,
perform mathematical topological data analysis, improve dialogue outcomes, or
generalise from six authored fixtures to naturally occurring conversations.

## External claims

| Manuscript claim | Primary source checked | Status and wording constraint |
|---|---|---|
| Conversation dynamics can be studied separately from topical content, and dynamics summaries have been evaluated in a downstream forecasting task. | Hua et al. (2024), ACL Anthology, <https://aclanthology.org/2024.naacl-long.414/> | Verified. The manuscript does not transfer their forecasting result to TopoDialogue. |
| High-dimensional text representations have been used to trace conversational trajectories and quantify topical flow. | Fischer and Ram (2024), ACL Anthology, <https://aclanthology.org/2024.sicon-1.3/> | Verified. Their personality findings are not used to justify psychological inference here. |
| Semantic-space transition models have been used for multi-turn conversation planning. | Chen et al. (2025), arXiv v2 / ICLR 2025 Spotlight, <https://arxiv.org/abs/2503.11586> | Verified. Formal title uses “with Semantic Space”, not the older local “using” wording. Their planning method is not claimed as a component of TopoDialogue. |
| Successive paraphrasing can exhibit periodic attractor cycles. | Wang et al. (2025), arXiv v2, <https://arxiv.org/abs/2502.15208> | Verified for the paper's successive-paraphrasing setting. The manuscript explicitly says that this is not evidence that ordinary human--LLM dialogue has the same dynamics. |
| Multi-turn task decomposition can make tested LLMs less reliable than single-turn presentation. | Laban et al. (2025), arXiv, <https://arxiv.org/abs/2505.06120> | Verified for their simulations. The first draft uses the result only as motivation to inspect trajectories, not as evidence for TopoDialogue's classifier. |
| TDA has an established but still developing NLP literature. | Uchendu and Le (2026), arXiv v5, <https://arxiv.org/abs/2411.10298> | Verified. The v5 title and 137-paper survey supersede the older local title and 87-paper figure. TopoDialogue v1 does not compute TDA invariants. |

## Implementation claims

| Claim | Evidence | Status |
|---|---|---|
| Same input and seed give an identical report within the Python implementation. | `tests/test_trajectory_shapes.py::test_same_input_and_seed_produce_identical_report` | Tested. Cross-runtime byte identity is not claimed. |
| Changing the seed changes display geometry but preserves operational metrics, apart from the seed-stability diagnostic. | `tests/test_trajectory_shapes.py::test_projection_seed_changes_geometry_but_not_operational_metrics` | Tested on the spiral fixture. |
| Python and JavaScript classify all six declared fixtures as expected and identify the declared recurrence source. | Python fixture test, CLI validator, and `visualizer/trajectory-analysis.test.js` | Tested. This is specification conformance, not an estimate of population accuracy. |
| User- and assistant-originated novelty are separated by first feature occurrence. | `topodialogue/trajectory.py` and assistant-loop provenance test | Tested for the authored fixture. This is feature provenance, not causal attribution. |
| `LoopScore` equals mean revisit similarity multiplied by one minus mean progress on revisit, clipped to [0,1]. | `topodialogue/trajectory.py` | Code-verified. Escape is a higher-priority class, so an escape fixture can still have `LoopScore = 1.0` for its preceding recurrent region. |
| Time height is monotonic and must not be read as progress. | Axis definition and emitted `time_height_monotonicity` warning | Code-verified and stated in every relevant caption. |

## Synthetic measurements

The values below were regenerated from `trajectory-v1` with seed 1729 on the
audit date.

| Case | Class | Source | Revisit rate | Mean similarity | Mean progress | LoopScore | Escape@5 | Projection stability |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| exact-loop | closed loop | mixed | 0.666667 | 1.000000 | 0.000000 | 1.000000 | false | 1.000000 |
| spiral-revisit | spiral revisit | mixed | 0.666667 | 0.583333 | 0.243333 | 0.441389 | false | 0.939956 |
| open-trajectory | open trajectory | none | 0.000000 | 0.000000 | 0.000000 | 0.000000 | false | 0.442795 |
| assistant-induced-loop | closed loop | assistant | 0.333333 | 1.000000 | 0.000000 | 1.000000 | false | 0.434584 |
| spiral-escape | escape | mixed | 0.333333 | 1.000000 | 0.000000 | 1.000000 | true | 0.824146 |
| speaker-drift | closed loop | mixed | 0.666667 | 1.000000 | 0.000000 | 1.000000 | false | 1.000000 |

## Editorial checks

- English prose is intentionally British: `visualise`, `analyse`, `behaviour`,
  `normalise`, `artefact`, `centre`, and `modelling`.
- Original paper titles and software identifiers are preserved exactly even if
  their spelling differs.
- “Topology” is used as naming provenance or a future analytical direction;
  the implemented classifier is described as geometric and operational.
- “Escape” denotes a finite-window rule over feature recurrence; it does not
  denote recovery, wellbeing, insight, or psychological change.
- The author name and affiliation are set to Ryoko Sakakibara, Independent
  Researcher. Licence metadata and compiled-PDF inspection remain
  pre-submission tasks. The software has not yet been deposited in a public
  archive, and the manuscript states this explicitly rather than citing an
  unavailable repository or archival identifier.
