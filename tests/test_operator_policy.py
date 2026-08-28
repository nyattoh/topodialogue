from topodialogue.operators import select_operator, render_question

def test_constraint_policy_and_nonleading_render():
    decision = render_question(select_operator(constraint_persistence=.8, recurrence=.9, turn_id="t9"))
    assert decision.operator == "constraint_removal"
    assert decision.introduced_candidate_answers == []
    assert "旅行" not in decision.rendered_question
