import networkx as nx
from .models import SemanticNode, SemanticEdge, StateSnapshot

def weighted_jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0

class TemporalSemanticGraph:
    def __init__(self): self.graph = nx.DiGraph(); self.snapshots: list[StateSnapshot] = []
    def add(self, snapshot: StateSnapshot, nodes: list[SemanticNode], edges: list[SemanticEdge]):
        self.snapshots.append(snapshot)
        for node in nodes: self.graph.add_node(node.node_id, type=node.type, key=node.normalized_key, provenance=node.provenance, turn_id=snapshot.turn_id)
        for edge in edges: self.graph.add_edge(edge.source_id, edge.target_id, relation=edge.relation, edge_id=edge.edge_id)
    def recurrence(self, current: StateSnapshot, previous: list[StateSnapshot]) -> tuple[float, list[str]]:
        # Node ids are turn-scoped; recurrence must compare normalized state keys,
        # not incidental ids such as ``t9:no_desires``.
        def keys(snapshot):
            return {item.split(":", 1)[-1] for item in snapshot.active_node_ids}
        scores = [(weighted_jaccard(keys(current), keys(s)), s.turn_id) for s in previous]
        return max(scores, default=(0.0, ""))
    def cycle_signal(self, snapshot: StateSnapshot) -> float:
        active = set(snapshot.active_node_ids)
        return 1.0 if any(a in active and b in active for a,b in self.graph.edges) else 0.0
