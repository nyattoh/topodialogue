from topodialogue.graph import TemporalSemanticGraph
from topodialogue.models import StateSnapshot

def test_graph_recurrence_ignores_turn_scoped_ids():
    graph = TemporalSemanticGraph()
    old = StateSnapshot(snapshot_id="s1", turn_id="t1", active_node_ids=["t1:no_desires"])
    current = StateSnapshot(snapshot_id="s2", turn_id="t2", active_node_ids=["t2:no_desires"])
    assert graph.recurrence(current, [old]) == (1.0, "t1")
