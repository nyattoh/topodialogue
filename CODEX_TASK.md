# CODEX TASK — Implement Phase 1 only

## Objective
Create a runnable, testable Python research prototype for TopoDialogue as specified in `docs/`.

The first implementation must answer this engineering question:

> Can we ingest a dialogue trajectory, compute interpretable recurrence/novelty features, detect a candidate low-progress semantic loop, choose a transparent transformation operator, and measure whether subsequent **user** turns enter new semantic territory?

## Deliverables
Create a Python package, suggested name `topodialogue`, with:

```text
topodialogue/
  models.py
  adapters.py
  extraction.py
  embeddings.py
  store.py
  graph.py
  recurrence.py
  progress.py
  detector.py
  operators.py
  renderer.py
  outcomes.py
  cli.py

tests/
  test_schema.py
  test_recurrence.py
  test_graph_recurrence.py
  test_novelty.py
  test_detector.py
  test_operator_policy.py
  test_provenance.py
  test_formative_case.py

scripts/
  run_case.py
```

You may adjust names if architecture improves, but preserve module separation and explain changes.

## Required behavior
1. Read JSONL dialogue fixtures.
2. Support a deterministic `FakeEmbedder` used in tests.
3. Support an optional real embedder adapter without downloading models during tests.
4. Build `StateSnapshot` objects and provenance-aware nodes/edges.
5. Implement:
   - semantic recurrence;
   - snapshot/graph recurrence;
   - user-originated novelty;
   - simple semantic-progress proxy;
   - motif/constraint persistence hooks;
   - composite LoopScore;
   - hysteresis + cooldown.
6. Implement the Phase-1 rule-based operator policy.
7. Render a non-leading question using deterministic templates in tests.
8. Compute post-intervention outcomes including UON and Escape@K.
9. Run the formative case and print an interpretable event trace.

## Acceptance criteria
`pytest` passes offline.

The formative case test must show all of the following:
- at least one candidate loop before the intervention point;
- `constraint_removal` is selected or ranked first for the intended loop signature;
- after the intervention, user-originated novelty increases;
- new user concepts are not misattributed to assistant provenance;
- LoopScore eventually falls or escape condition becomes true;
- assistant suggestions are not required to produce the expected novelty.

## Determinism
- Seed all pseudo-random operations.
- Unit tests must not call network services.
- Golden fixture behavior must not depend on proprietary model output.

## Config
Provide a human-readable config (YAML/TOML/JSON) with:
- window size;
- recurrence threshold;
- LoopScore component weights;
- hysteresis thresholds;
- cooldown;
- novelty type weights;
- escape horizon K.

## CLI demo
Example target command:

```bash
python -m topodialogue.cli analyze examples/formative-case.jsonl
```

Output should show per relevant turn:
- top recurrence evidence;
- component scores;
- LoopScore;
- loop decision;
- selected operator;
- rendered question;
- post-intervention UON / escape event when available.

## State extraction in first pass
Do not build a complex automatic extractor before the detector works. The formative fixture may include annotated semantic nodes. Implement:
- `AnnotatedExtractor` for fixtures;
- optional `LLMStateExtractor` interface/stub.

A later task can add automatic extraction.

## Do not implement yet
- multi-agent system;
- GraphRAG / Transition RAG;
- persistent homology / Mapper;
- wearable sensor/body gate;
- web UI;
- authentication;
- cloud deployment;
- fine-tuning/RL.

## Documentation
At completion, update the root README with:
- installation;
- test command;
- demo command;
- architecture summary;
- known limitations;
- next research steps.

## Research honesty
If any acceptance criterion conflicts with a sound implementation, document the conflict rather than hard-code a fake success. The fixture can define expected annotations, but do not engineer the numeric score solely to force the desired result.