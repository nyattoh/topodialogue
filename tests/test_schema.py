from topodialogue.models import DialogueTurn, SemanticNode

def test_schema_validates_and_keeps_provenance():
    turn = DialogueTurn(turn_id="t1", speaker="user", text="hello")
    node = SemanticNode(node_id="n1", type="desire", label="walk", provenance="user", first_seen_turn=turn.turn_id, last_seen_turn=turn.turn_id)
    assert node.provenance == "user"
