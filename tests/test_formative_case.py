import json
from pathlib import Path
from topodialogue.adapters import load_jsonl
from topodialogue.extraction import AnnotatedExtractor

def test_fixture_contains_post_intervention_user_nodes():
    turns = load_jsonl(Path("examples/formative-case.jsonl"))
    nodes = [n for t in turns for n in AnnotatedExtractor().extract(t)[0]]
    assert len([n for n in nodes if n.provenance == "user" and n.first_seen_turn in {"t11", "t13", "t14"}]) >= 3
