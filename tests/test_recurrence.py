import numpy as np
from topodialogue.recurrence import semantic_recurrence, user_novelty
from topodialogue.models import SemanticNode

def test_semantic_recurrence_and_novelty():
    score, index = semantic_recurrence(np.array([1., 0.]), [np.array([1., 0.])], .8)
    assert score == 1 and index == 0
    node = SemanticNode(node_id="n", type="desire", label="new", normalized_key="new", provenance="user", first_seen_turn="t", last_seen_turn="t")
    assert user_novelty([node], set())[0] == 1
