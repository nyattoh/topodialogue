# 09 — Safety, privacy, and research boundary

## 1. Local-first default
This project handles long-horizon dialogue, which may contain intimate life history, body state, relationships, health details, and unresolved thoughts. The prototype should work with local files and deterministic test data without sending raw conversation to external services.

If a remote LLM or embedding service is enabled, it must be opt-in and clearly configured.

## 2. Data minimization
Persist only what the experiment needs:
- normalized turn text or redacted text;
- evidence hashes/spans;
- structured nodes/edges;
- embeddings if required;
- experiment outcomes.

Support a mode where raw text is not retained after extraction.

## 3. Provenance and uncertainty
The system must distinguish:
- explicit user statement;
- assistant suggestion;
- extractor inference;
- heuristic classification.

Never display an inference as “you are X.” Prefer “one current hypothesis is X, based on turns …” when exposing it at all.

## 4. Non-clinical scope
The detector does **not** diagnose:
- depression;
- trauma;
- suicidality;
- dissociation;
- cognitive disorders.

A semantic loop is an interaction pattern, not a pathology.

For research prototypes, exclude crisis intervention from the experimental target. If the host application has a safety layer, its crisis/safety policy takes precedence over TopoDialogue exploration.

## 5. Avoid compulsive engagement
Do not reward:
- longer sessions;
- more messages;
- emotional dependence;
- deeper disclosure for its own sake.

The operator policy should be allowed to choose **no intervention**.

## 6. Intrusion guard
Do not repeatedly transform the frame when:
- the user says “stop / enough / not that”; 
- cognitive-load estimate is high;
- a recent operator was rejected;
- there is insufficient evidence that the dialogue is stuck.

Implement cooldown and a `no_operator` outcome.

## 7. Leadingness guard
Research evaluation requires separating user-generated novelty from assistant-seeded content.

The renderer should prefer open structural questions over candidate answers.

Bad for evaluation:
> Maybe you really want to travel, make art, or start a company?

Better:
> If feasibility were temporarily removed, what appears first?

## 8. Raw source handling
The `source/` files were supplied for conceptual context. Do not automatically ingest them into model-training datasets or publish them. Any personal or identifiable material used in a paper requires explicit review/anonymization.

## 9. Reproducibility vs privacy
Release synthetic examples, schemas, detector code, and aggregate statistics by default. Release raw natural dialogues only with appropriate consent and ethics/privacy review.

## 10. Audit trail
Log:
- why a loop was detected;
- which operator was selected;
- which rule selected it;
- exactly what question was rendered;
- what candidate content the assistant introduced;
- which later nodes were user-originated.

This auditability is part of the research contribution, not just debugging.