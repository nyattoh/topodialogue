# 00 — Research scope

## Working title
**TopoDialogue: Escaping Recurrent Semantic Loops in Long-Horizon Human–LLM Dialogue via State-Space Transformation**

Japanese working name: **対話位相検索アルゴリズム**.

## Research problem
In long-horizon exploratory dialogue, wording can change while the interaction repeatedly returns to the same semantic self-model, constraint set, or explanatory frame. A conventional assistant often responds by asking a more specific question inside the same frame. This can deepen the loop rather than reveal a new region of the user's meaning space.

The proposed system asks a different question: **when should the dialogue stop searching locally and change its coordinate system?**

## Primary research question
Can a dialogue agent detect low-progress recurrent semantic regions and improve subsequent **user-originated semantic progress** by selecting a transformation operator rather than continuing ordinary local follow-up?

## Secondary research questions
RQ2. Which features best predict a practically harmful loop: embedding recurrence, graph-cycle recurrence, novelty decay, semantic-progress decay, repeated constraints, or combinations?

RQ3. Which transformation operators are effective for which loop signatures?

RQ4. Can operator selection improve novelty without increasing assistant-led suggestion, coercion, or user cognitive load?

RQ5. Does structured memory of prior loop→operator→outcome transitions improve future operator selection compared with ordinary vector RAG?

## Phase-1 hypotheses
H1. A combined recurrence score detects human-annotated “same place again” segments better than lexical repetition or embedding similarity alone.

H2. After a detected loop, coordinate-changing operators produce higher user-originated semantic novelty within K turns than ordinary follow-up questions.

H3. The effect remains after controlling for assistant token count and explicit suggestion count.

H4. Provenance-aware novelty distinguishes genuine user expansion from novelty injected by the assistant.

## Contribution hypothesis — not yet a novelty claim
Existing work separately studies:
- LLM attractor/cycle dynamics,
- semantic-space conversation planning,
- long-term graph memory,
- dynamic multi-agent orchestration,
- multi-turn reliability degradation.

The candidate contribution is to combine these ideas around a different target: **human-side recurrent semantic regions in exploratory human–LLM dialogue**, with explicit loop detection, coordinate-transforming conversational operators, and evaluation of **user-originated** escape.

A systematic literature review is required before any claim of novelty.

## What this paper should NOT claim
- That human cognition is literally a topological manifold.
- That a graph cycle is a topological invariant.
- That the system diagnoses depression, trauma, or any clinical state.
- That semantic novelty is equivalent to psychological improvement.
- That every repeated topic is a bad loop; revisiting can be useful.
- That a single formative conversation generalizes to users broadly.

## Operational definition of a dialogue loop
A time window is a candidate recurrent loop when:
1. the current semantic state repeatedly returns near earlier states;
2. the set of active semantic nodes/constraints changes little;
3. semantic progress or user-originated novelty is low;
4. the trajectory remains in the same local explanatory frame despite multiple turns.

This is a functional definition for experimentation, not a psychological diagnosis.

## Escape definition
A loop is considered escaped if, after an intervention, the subsequent user turns show one or more of:
- entry into a previously unvisited semantic cluster;
- appearance of new user-originated Desire/Value/Constraint/Counterfactual nodes;
- a material change in active constraints or self-claims;
- sustained semantic progress for at least N turns;
- explicit user annotation such as “that is a different angle / that helped me see something new.”

Escape does not require positivity or agreement.