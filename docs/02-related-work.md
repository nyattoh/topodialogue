# 02 — Related work and gap hypothesis

Access date for this seed review: 2026-08-13.

This is a **seed map**, not a systematic review. Before publication, expand searches across arXiv, ACL Anthology, Semantic Scholar/OpenAlex, and relevant HCI/CSCW venues; add explicit inclusion/exclusion criteria.

## A. Multi-turn dialogue as semantic state / planning

### SCOPE — Chen et al., 2025
**Broaden your SCOPE! Efficient Multi-turn Conversation Planning for LLMs using Semantic Space**  
arXiv:2503.11586  
https://arxiv.org/abs/2503.11586

Key relevance: models stochastic conversation transitions and rewards in dense semantic space to plan responses efficiently. This supports treating conversation as a semantic state transition process rather than only a token sequence.

Difference: SCOPE optimizes expected conversation reward; TopoDialogue focuses on recurrent low-progress regions and coordinate-changing interventions, with provenance-aware user-originated novelty as an outcome.

## B. Attractors and recurrent dynamics

### Wang et al., 2025
**Unveiling Attractor Cycles in Large Language Models: A Dynamical Systems View of Successive Paraphrasing**  
arXiv:2502.15208  
https://arxiv.org/abs/2502.15208

Key relevance: iterative LLM paraphrasing can converge to stable periodic states such as two-period cycles; offers dynamical-systems language for repetitive model transformations.

Difference: model self-transformation rather than human–assistant semantic self-model loops.

### Ko & Geiping, 2026
**Attractor States Emerge in Multi-Turn LLM Conversations**  
arXiv:2606.30571  
https://arxiv.org/abs/2606.30571

Key relevance: open-ended model–model multi-turn conversations exhibit model-specific attractor-like behavior in representation/discourse space.

Difference: focuses on model–model partner influence, not intervention policies for recurrent human-side semantic regions.

## C. Measuring semantic progress

### He, Kasiviswanathan & Janzing, 2026
**Measuring Semantic Progress in Multi-turn Dialogue via Information Gain**  
arXiv:2606.12332  
https://arxiv.org/abs/2606.12332

Key relevance: formalizes semantic progress as question-conditioned uncertainty reduction; proposes an embedding-space information-gain metric with diminishing returns for redundancy.

Use in TopoDialogue: strong candidate metric/baseline for progress decay and post-intervention progress. Do not copy the method blindly; test whether it behaves sensibly in exploratory self-reflective dialogue where “relevance to a fixed question” may be unstable.

## D. Multi-turn unreliability

### Laban et al., 2025
**LLMs Get Lost In Multi-Turn Conversation**  
arXiv:2505.06120  
https://arxiv.org/abs/2505.06120

Key relevance: large-scale simulations show substantial performance degradation in multi-turn settings; models often make early assumptions and fail to recover after a wrong turn.

Connection: motivates recovery mechanisms and explicit detection of unproductive trajectories.

### MultiChallenge — Sirdeshmukh et al., 2025
**A Realistic Multi-Turn Conversation Evaluation Benchmark Challenging to Frontier LLMs**  
arXiv:2501.17399  
https://arxiv.org/abs/2501.17399

Key relevance: multi-turn instruction-following and context allocation remain difficult even for frontier models.

## E. Long-term and graph memory

### MemGPT — Packer et al., 2023
**MemGPT: Towards LLMs as Operating Systems**  
arXiv:2310.08560  
https://arxiv.org/abs/2310.08560

Key relevance: hierarchical/virtual context management for long-running conversation and memory.

### LoCoMo — Maharana et al., 2024
**Evaluating Very Long-Term Conversational Memory of LLM Agents**  
arXiv:2402.17753  
https://arxiv.org/abs/2402.17753

Key relevance: benchmark for long-term conversational memory; long context/RAG still lag human performance on long-range temporal/causal dynamics.

### A-MEM — Xu et al., 2025
**A-MEM: Agentic Memory for LLM Agents**  
arXiv:2502.12110  
https://arxiv.org/abs/2502.12110

Key relevance: dynamically creates and evolves interconnected memory networks rather than fixed memory records.

Use in TopoDialogue Phase 2: inspiration for evolving transition memory.

### SGMem — Wu et al., 2025
**SGMem: Sentence Graph Memory for Long-Term Conversational Agents**  
arXiv:2509.21212  
https://arxiv.org/abs/2509.21212

Key relevance: graph-organized dialogue memory across turn/round/session granularities.

### Graph-based Agent Memory survey — Yang et al., 2026
**Graph-based Agent Memory: Taxonomy, Techniques, and Applications**  
arXiv:2602.05665  
https://arxiv.org/abs/2602.05665

Key relevance: current survey of extraction, storage, retrieval, and evolution in graph-based agent memory.

## F. Dynamic orchestration

### Dang et al., 2025
**Multi-Agent Collaboration via Evolving Orchestration**  
arXiv:2505.19591  
https://arxiv.org/abs/2505.19591

Key relevance: centralized orchestrator dynamically chooses/sequences agents based on evolving task state.

Use in later TopoDialogue: operator modules could eventually be internally orchestrated. Phase 1 should remain single-orchestrator to avoid unnecessary coordination complexity.

## G. Reflection / iterative self-correction

### Reflexion — Shinn et al., 2023
arXiv:2303.11366  
https://arxiv.org/abs/2303.11366

Key relevance: agents preserve verbal reflection in episodic memory and use it to improve later decisions.

### Self-Refine — Madaan et al., 2023
arXiv:2303.17651  
https://arxiv.org/abs/2303.17651

Key relevance: iterative feedback/refinement without weight updates.

Difference: these primarily improve the agent's own outputs. TopoDialogue measures whether intervention opens new semantic territory for the **user**, while minimizing assistant-imposed content.

## H. Topological Data Analysis in NLP

### Uchendu & Le, 2024/2025 survey
**Unveiling Topological Structures in Text: A Comprehensive Survey of Topological Data Analysis Applications in NLP**  
arXiv:2411.10298  
https://arxiv.org/abs/2411.10298

Key relevance: surveys 87 TDA/NLP papers and supports TDA as a legitimate later analytical layer.

Caution: TDA is not needed to justify the MVP. If persistent homology is added, specify exactly what point cloud/filtration represents, how time order is treated, and what predictive value H0/H1 provides beyond simpler recurrence features.

## Gap hypothesis
The literature above provides close components, but the seed search did not identify the exact combination below:

1. long-horizon **human–LLM exploratory dialogue** as a semantic trajectory;
2. explicit detection of recurrent, low-progress semantic regions;
3. a policy choosing **coordinate-changing transformation operators** rather than only response content;
4. graph provenance that separates user-generated semantic novelty from assistant-suggested novelty;
5. evaluation of loop escape and agency preservation;
6. later transition-memory retrieval of prior `loop signature -> operator -> outcome` episodes.

This is a hypothesis for systematic review, not a publishable novelty claim yet.