from topodialogue.outcomes import evaluate_outcome
from topodialogue.models import SemanticNode

def test_assistant_suggestion_is_not_user_novelty():
    nodes = [SemanticNode(node_id="a", type="desire", label="suggestion", normalized_key="suggestion", provenance="assistant", first_seen_turn="t2", last_seen_turn="t2")]
    outcome = evaluate_outcome("op:t1", nodes, set(), 3, .5)
    assert outcome.user_originated_novelty == 0
    assert not outcome.escaped
