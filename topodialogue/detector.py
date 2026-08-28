from .config import DetectorConfig
from .models import LoopComponents, LoopDecision, SemanticNode, StateSnapshot
from .embeddings import cosine
from .graph import TemporalSemanticGraph

class LoopDetector:
    def __init__(self, config: DetectorConfig | None = None):
        self.config = config or DetectorConfig(); self.active = False; self.cooldown = 0; self.low_score_streak = 0
    def detect(self, turn_id: str, embedding, history_embeddings, snapshot: StateSnapshot, history_snapshots: list[StateSnapshot], graph: TemporalSemanticGraph, recent_nodes: list[list[SemanticNode]], known_keys: set[str]) -> LoopDecision:
        prior = history_embeddings[-self.config.window_size:]
        recurrence = max([cosine(embedding, x) for x in prior[:-1]] or [0.0])
        graph_score, evidence = graph.recurrence(snapshot, history_snapshots[-self.config.window_size:])
        current_nodes = recent_nodes[-1] if recent_nodes else []
        user = [n for n in current_nodes if n.provenance == "user"]
        new = [n for n in user if (n.normalized_key or n.label) not in known_keys]
        novelty_decay = 1 - min(1, len(new) / max(1, len(user)))
        progress_decay = 1 - (1 - graph_score)
        self_claim = next((n.normalized_key for n in current_nodes if n.type == "self_claim"), None)
        prior_claims = sum(1 for turn_nodes in recent_nodes[:-1] for n in turn_nodes if n.type == "self_claim" and n.normalized_key == self_claim) if self_claim else 0
        # Repetition becomes materially stronger after several returns; this
        # keeps a first revisit from triggering while retaining a transparent rule.
        motif = min(1.0, .15 + .20 * prior_claims) if self_claim else 0.0
        constraints = sum(1 for n in current_nodes if n.type == "constraint") / max(1, len(current_nodes))
        comp = LoopComponents(recurrence=max(0, min(1, recurrence)), graph_cycle=graph.cycle_signal(snapshot), novelty_decay=novelty_decay, semantic_progress_decay=progress_decay, motif_recurrence=motif, constraint_persistence=min(1, constraints))
        score = sum(self.config.weights[k] * getattr(comp, k) for k in self.config.weights)
        was_active = self.active
        if self.cooldown: self.cooldown -= 1
        if not was_active and score >= self.config.loop_threshold and not self.cooldown: self.active = True
        elif was_active and score <= self.config.loop_exit_threshold: self.low_score_streak += 1; self.active = self.low_score_streak < self.config.hysteresis_turns
        elif score > self.config.loop_exit_threshold: self.low_score_streak = 0
        if self.active and not was_active: self.cooldown = self.config.cooldown_turns
        return LoopDecision(turn_id=turn_id, score=score, is_loop=self.active, components=comp, evidence_turn_ids=[evidence] if evidence else [], threshold=self.config.loop_threshold, cooldown_active=bool(self.cooldown and not was_active), reason="recurrent low-progress region" if self.active else "no intervention")
