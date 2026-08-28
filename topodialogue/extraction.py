import hashlib
from typing import Protocol
from .models import DialogueTurn, SemanticNode, SemanticEdge, EvidenceSpan

class StateExtractor(Protocol):
    def extract(self, turn: DialogueTurn) -> tuple[list[SemanticNode], list[SemanticEdge]]: ...

class AnnotatedExtractor:
    def extract(self, turn: DialogueTurn) -> tuple[list[SemanticNode], list[SemanticEdge]]:
        annotations = turn.metadata.get("annotations", {})
        nodes, edges = [], []
        for item in annotations.get("nodes", []):
            key = item["key"]
            node_id = f"{turn.turn_id}:{key}"
            nodes.append(SemanticNode(node_id=node_id, type=item["type"], label=key.replace("_", " "), normalized_key=key, confidence=float(item.get("confidence", .95)), salience=float(item.get("salience", 1)), provenance=turn.speaker, evidence=[EvidenceSpan(turn_id=turn.turn_id)], first_seen_turn=turn.turn_id, last_seen_turn=turn.turn_id))
        for index, item in enumerate(annotations.get("relations", [])):
            edges.append(SemanticEdge(edge_id=f"{turn.turn_id}:e{index}", source_id=f"{turn.turn_id}:{item['source']}", target_id=f"{turn.turn_id}:{item['target']}", relation=item["relation"], confidence=.95, provenance=turn.speaker, evidence=[EvidenceSpan(turn_id=turn.turn_id)]))
        return nodes, edges

class LLMStateExtractor:
    """Interface placeholder: production adapters must return strict validated models."""
    def extract(self, turn: DialogueTurn):
        raise NotImplementedError("Configure an explicit local/remote provider; no implicit network call is made")

def stable_node_key(node: SemanticNode) -> str:
    return node.normalized_key or hashlib.sha1(node.label.casefold().encode()).hexdigest()[:12]
