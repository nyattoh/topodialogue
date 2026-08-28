# 06 — Transformation operators

## Principle
An operator changes the **frame of search**, not merely the wording of the next question.

Phase 1 uses a small transparent taxonomy. The question renderer should ask one question at a time and avoid injecting content whenever possible.

## Operator set

### O1 — `constraint_removal`
Temporarily remove feasibility filters.

Use when:
- many Desire/Action candidates are immediately inhibited;
- self-claim says “nothing comes to mind” while constraints are highly active.

Question template:
> If money/body/age/failure cost were temporarily removed, what appears first?

Do not imply a specific answer.

### O2 — `constraint_isolation`
Remove only one constraint dimension at a time.

Use when global constraint removal produces too many changes and causal interpretation is unclear.

Examples:
- money unchanged, body free;
- body unchanged, no social evaluation;
- success not required, all else unchanged.

### O3 — `valence_inversion`
Switch positive search to negative/aversive search, or vice versa.

Use when “what do you want/like?” yields no structure but strong rejection or anger signals exist.

Question:
> What kind of system or situation makes you immediately think “I do not want this”?

### O4 — `counterexample_search`
Test a global self-claim by looking for exceptions.

Use when:
- repeated `SelfClaim` is absolute: “I never choose,” “I have no interests,” etc.

Question:
> Can you remember even one case that does not fit that statement?

Important: the goal is not to disprove the user. Store both claim and counterexample.

### O5 — `identity_to_pattern`
Move from identity label to recurring behavior/operation.

Use when labels remain unsatisfying.

Question:
> Instead of naming what kind of person you are, what do you repeatedly end up doing when nobody asked you to?

### O6 — `object_to_operation`
Move from “what object/topic do you like?” to “what transformation do you like performing?”

Examples:
- mix / repair / compare / translate / discover / connect / reshape.

Use when topics vary but action patterns recur.

### O7 — `abstraction_shift_down`
Move from life-purpose/global identity to a bounded scene.

Question:
> Not your whole life—imagine only the first week. What are you doing?

### O8 — `abstraction_shift_up`
Move from isolated examples to shared pattern.

Question:
> These examples look different; what operation is common across them?

### O9 — `time_shift`
Move time horizon or viewpoint.

Variants:
- “before it became a job, what was happening?”
- “if this only had to matter for one month?”
- “what changed exactly when interest disappeared?”

### O10 — `perspective_shift`
Change agent/observer perspective without assigning a fixed identity.

Examples:
- younger-self / older-self / outsider / collaborator view.

Avoid anthropomorphic authority such as “your future self knows the answer.”

### O11 — `body_channel`
Move from explanation to felt/behavioral signal.

Question:
> Before you can explain why, what happens first—tension, blankness, irritation, urge to leave, something else?

This is not clinical sensing. It is user-reported phenomenology only in Phase 1.

### O12 — `assumption_negation`
Identify and negate a hidden premise.

Example premise: “a meaningful activity must become a career.”

Question:
> If it did not have to become a career or even be completed, would the answer change?

## Operator selection policy — Phase 1
Use transparent rules based on loop signature. Example:

```text
IF high constraint_persistence AND low desire novelty
  -> constraint_removal
ELIF repeated global self_claim
  -> counterexample_search
ELIF many topic nodes but stable action motifs
  -> object_to_operation
ELIF repeated abstract life-purpose language
  -> abstraction_shift_down
ELIF positive-search failure AND strong rejection/value conflict
  -> valence_inversion
ELIF repeated labels rejected by user
  -> identity_to_pattern
ELSE
  -> assumption_negation OR time_shift
```

Return ranked alternatives and rule IDs.

## Operator failure
An operator can fail when:
- user says the premise is wrong;
- no new semantic region appears;
- cognitive load increases;
- it repeats a recently failed operator;
- the question feels leading.

Store failure as data. Do not immediately chain more operators.

## Cooldown and consent
After a transformation operator:
- wait for user response;
- avoid stacking multiple transformations in the same turn;
- if user signals fatigue or asks to stop, switch to ordinary supportive conversation / pause research behavior;
- record explicit rejection as a policy signal.

## Phase-2 policy learning
Learn `pi(operator | loop_signature)` with a contextual bandit or offline policy, using rewards defined in `07-evaluation.md`.

Do not use raw “user engagement” as the primary reward; it can reward dependency or endless conversation.