from topodialogue.adapters import load_jsonl
from topodialogue.cli import analyze

def test_formative_case_has_intervention():
    decision = analyze("examples/formative-case.jsonl")
    assert decision is not None
    assert decision.operator == "constraint_removal"
    assert decision.introduced_candidate_answers == []
