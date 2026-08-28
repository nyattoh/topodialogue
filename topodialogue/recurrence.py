import numpy as np
from .embeddings import cosine
from .models import SemanticNode
from .graph import weighted_jaccard

def semantic_recurrence(current: np.ndarray, history: list[np.ndarray], threshold: float) -> tuple[float, int | None]:
    if not history: return 0.0, None
    scores = [cosine(current, old) for old in history]
    best = max(enumerate(scores), key=lambda x: x[1])
    return max(0.0, best[1]), best[0] if best[1] >= threshold else None

def user_novelty(nodes: list[SemanticNode], known_keys: set[str]) -> tuple[float, list[str]]:
    user_nodes = [n for n in nodes if n.provenance == "user"]
    new = [n for n in user_nodes if (n.normalized_key or n.label) not in known_keys]
    mass = sum(n.salience for n in new) / max(1.0, sum(n.salience for n in user_nodes))
    return mass, [n.node_id for n in new]

def progress(previous: list[str], current: list[str]) -> float:
    return 1 - weighted_jaccard(set(previous), set(current))
