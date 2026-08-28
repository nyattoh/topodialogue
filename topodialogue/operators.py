from .models import OperatorDecision

OPERATORS = ("constraint_removal", "abstraction_shift_down", "perspective_shift", "temporal_shift", "ordinary_follow_up")

def select_operator(*, constraint_persistence: float, recurrence: float, user_uncertainty: bool = False, turn_id: str = "") -> OperatorDecision:
    ranked = [("constraint_removal", .92 if constraint_persistence >= .35 else .35), ("abstraction_shift_down", .78 if user_uncertainty else .45), ("perspective_shift", .35), ("temporal_shift", .25), ("ordinary_follow_up", .1)]
    ranked.sort(key=lambda x: x[1], reverse=True)
    selected = ranked[0][0]
    return OperatorDecision(decision_id=f"op:{turn_id}", turn_id=turn_id, operator=selected, rule_ids=["R-CONSTRAINT-01"] if selected == "constraint_removal" else ["R-GENERAL-01"], alternatives=ranked[1:])

def render_question(decision: OperatorDecision) -> OperatorDecision:
    templates = {"constraint_removal":"条件をいったん外します。お金・身体・年齢・失敗の影響を考えず、最初に何が浮かびますか？", "abstraction_shift_down":"その方向に進む最初の一週間を、具体的な場面として描くと何をしていますか？", "perspective_shift":"あなたではなく、少し距離のある観察者なら何に気づきますか？", "temporal_shift":"今ではなく、少し先の時点から振り返ると何が変わっていますか？", "ordinary_follow_up":"もう少し具体的にすると、どの部分が重要ですか？"}
    return decision.model_copy(update={"rendered_question": templates[decision.operator], "introduced_candidate_answers": []})
