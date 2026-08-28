from .models import OutcomeWindow, SemanticNode

def evaluate_outcome(decision_id: str, future_nodes: list[SemanticNode], baseline_keys: set[str], horizon: int, progress_score: float = 0.0) -> OutcomeWindow:
    user = [n for n in future_nodes if n.provenance == "user"]
    assistant = [n for n in future_nodes if n.provenance == "assistant"]
    new_user = [n for n in user if (n.normalized_key or n.label) not in baseline_keys]
    escaped = len(new_user) >= 3 and progress_score >= .2
    return OutcomeWindow(intervention_decision_id=decision_id, horizon_turns=horizon, new_user_node_ids=[n.node_id for n in new_user], new_assistant_node_ids=[n.node_id for n in assistant], user_originated_novelty=len(new_user)/max(1,len(user)), semantic_progress=min(1, progress_score), escaped=escaped, notes=["escape is an operational metric, not a psychological claim"])
