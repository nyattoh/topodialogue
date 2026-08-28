# 12 — Source synthesis

This document records how the supplied source texts and the formative dialogue map into the research prototype. It is a design synthesis, not an empirical result.

## Source A — `source/線形言語の終焉――意味のインターフェースへ.md`

### Core source claims used here
1. Human experience is described as simultaneous and multidimensional, while language serializes it into a one-dimensional sequence.
2. Serialization can impose false order/causality on simultaneous or contradictory experience.
3. The proposed Topo representation treats language as a rendered view rather than the primary data.
4. Topo is defined as a heterogeneous graph-like structure with node types including affect/body/concept/context, relation edges, strength/confidence, time/simultaneity, masking/granularity, and context curvature.
5. A future “Body Gate” changes granularity/latency/masking rather than forcing complete disclosure.
6. “Rendering sovereignty” separates underlying structure from the AI's presentation of it.

### What enters the first paper
- structured state representation;
- simultaneous/contradictory relations;
- provenance and confidence;
- separation between state and rendered question.

### What stays out of Phase 1
- claims about civilization/language as a whole;
- haptics/multimodal rendering;
- Body Gate sensor implementation;
- context curvature as a mathematical object;
- cultural infrastructure claims.

These can motivate future HCI work, but would make the first empirical paper too broad.

## Source B — `source/枝分かれ · AIプロンプト診断.md`

### Core source claims used here
1. There is a meaningful distinction between integrating many signals toward one goal and supervising multiple independent streams.
2. A multi-agent UI can externalize one original goal into many substreams that the human must remember and reintegrate.
3. The conversation connects this burden to the Topo idea: the user's natural “whole” may be broken into linear subparts and then reconstructed manually.
4. A prior phenomenological model describes fear/reality/control as a positive feedback loop, suggesting that recurrent dynamics can be a useful descriptive lens.
5. The source explicitly notes that the earlier equations were a thinking aid, not a clinical diagnostic model, and that some displayed formulas contained transcription/formatting errors.
6. The source proposes that AI can either further compress a user's multidimensional meaning or help re-expand it.

### What enters the first paper
- interaction burden from forcing humans to supervise/reconstruct multiple serialized states;
- feedback-loop language as motivation for recurrent state modeling;
- non-clinical caution;
- state representation should preserve multiple coexisting factors rather than choose one explanation.

### What stays out of Phase 1
- direct clinical interpretation of fear/reality;
- KAMUI-specific UI claims;
- any corrected differential-equation model unless independently rebuilt and validated.

## Formative dialogue in the present research branch
The later dialogue produced a new algorithmic insight.

### Observed pattern
Repeated local questions around “what do you want / what would make life meaningful?” returned to uncertainty and a global self-description that little or nothing was genuinely desired.

### Frame changes that produced new information
Several non-local questions produced qualitatively different material:
- asking what social structures feel intolerable revealed values about labels, conformity, middlemen, money as a dominant measure, and environmental control;
- asking for counterexamples revealed many unsolicited “I tried this because I wondered what would happen” episodes;
- shifting from object/identity to action pattern suggested experimentation as a recurring operation;
- most decisively, removing money/body/age/failure constraints immediately generated many concrete desired activities, travel, craft, research, making, meeting people, publishing, trade, and large physical construction.

### Research inference
The statement “I have no desires” and the later large desire set can coexist if the graph records a conditional relation such as:

`Desire generation -> feasibility/identity/social constraints -> early rejection -> accessible report = no desire`

This is not asserted as the person's true psychology. It is a better **dialogue hypothesis** because it explains a state transition triggered by changing the constraint frame.

### Algorithmic consequence
The system should search for:
- recurrent self-claims;
- persistent constraints;
- repeated candidate inhibition;
- low user-originated novelty;
- interventions that change one of those structural conditions.

The key outcome is not “the assistant found the right answer.” It is “the user generated new semantic structure after the search frame changed.”

## Unifying design principle
The two source documents and the formative dialogue converge on one engineering principle:

> Keep the multidimensional state separate from the linear response, monitor the trajectory rather than only the latest sentence, and change the rendering/search frame when local questioning repeatedly returns to the same low-progress region.

This principle is the bridge from the broader Topo theory to the narrow, falsifiable TopoDialogue prototype.