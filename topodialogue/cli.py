import argparse
import json
from pathlib import Path
from .adapters import load_dialogue, load_jsonl, normalize_turns
from .config import DetectorConfig
from .embeddings import FakeEmbedder
from .extraction import AnnotatedExtractor
from .graph import TemporalSemanticGraph
from .detector import LoopDetector
from .operators import select_operator, render_question
from .outcomes import evaluate_outcome
from .models import StateSnapshot
from .trajectory import TrajectoryConfig, analyze_trajectory, report_to_json
from .interaction import extract_interaction_events
from .privacy import audit_dialogue, public_derivative
from .agreement import (
    aggregate_annotations,
    compare_annotations,
    evaluate_event_predictions,
    synthetic_annotation_dry_run,
)
from .display_study import balanced_assignments, summarise_responses, synthetic_dry_run
from .modality import ModalityFixture, audit_fixture
from .agency import AgencyFixture, audit_fixture as audit_agency_fixture
from .benchmark import run_synthetic_robustness_benchmark

def analyze(path: str):
    turns = normalize_turns(load_jsonl(path)); extractor, embedder = AnnotatedExtractor(), FakeEmbedder(); graph, detector = TemporalSemanticGraph(), LoopDetector(DetectorConfig())
    embeddings, snapshots, all_nodes, node_history, known = [], [], [], [], set(); intervention = None
    print(f"TopoDialogue Phase 1 | turns={len(turns)} | offline deterministic mode")
    for turn_index, turn in enumerate(turns):
        nodes, edges = extractor.extract(turn); snapshot = StateSnapshot(snapshot_id=f"s:{turn.turn_id}", turn_id=turn.turn_id, active_node_ids=[n.node_id for n in nodes], active_edge_ids=[e.edge_id for e in edges], user_token_count=len(turn.text.split()) if turn.speaker == "user" else 0, assistant_token_count=len(turn.text.split()) if turn.speaker == "assistant" else 0)
        vector = embedder.embed([turn.text])[0]; decision = detector.detect(turn.turn_id, vector, embeddings, snapshot, snapshots, graph, node_history + [nodes], known); graph.add(snapshot, nodes, edges)
        if turn.speaker == "user": known.update(n.normalized_key or n.label for n in nodes)
        embeddings.append(vector); snapshots.append(snapshot); all_nodes.extend(nodes); node_history.append(nodes)
        print(f"{turn.turn_id} {turn.speaker:9} recurrence={decision.components.recurrence:.2f} novelty_decay={decision.components.novelty_decay:.2f} LoopScore={decision.score:.2f} loop={decision.is_loop}")
        if decision.is_loop and intervention is None:
            op = render_question(select_operator(constraint_persistence=decision.components.constraint_persistence, recurrence=decision.components.recurrence, user_uncertainty=any(n.type == "uncertainty" for n in nodes), turn_id=turn.turn_id)); intervention = op
            print(f"  operator={op.operator} question={op.rendered_question}")
    if intervention:
        intervention_index = next((i for i, t in enumerate(turns) if t.turn_id == intervention.turn_id), 0)
        after_turn_ids = {t.turn_id for t in turns[intervention_index + 1:]}
        after = [n for n in all_nodes if n.first_seen_turn in after_turn_ids and n.provenance == "user"]
        outcome = evaluate_outcome(intervention.decision_id, after, set(), 5, .5)
        print(f"outcome UON={outcome.user_originated_novelty:.2f} Escape@5={outcome.escaped} new_user_nodes={len(outcome.new_user_node_ids)}")
    return intervention

def main():
    parser = argparse.ArgumentParser(description="Analyze a dialogue trajectory offline")
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("analyze"); cmd.add_argument("path")
    trajectory = sub.add_parser("trajectory", help="write a deterministic trajectory research report")
    trajectory.add_argument("path")
    trajectory.add_argument("--output", "-o")
    trajectory.add_argument("--seed", type=int, default=1729)
    validate = sub.add_parser("validate-synthetic", help="validate known synthetic shape cases")
    validate.add_argument("--manifest", default="examples/synthetic/manifest.json")
    prepare = sub.add_parser(
        "prepare-case",
        help="create a content-withheld public derivative of a real dialogue",
    )
    prepare.add_argument("path")
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--case-id", default="real-case-01")
    agreement = sub.add_parser("agreement", help="compare two independent event annotation files")
    agreement.add_argument("left")
    agreement.add_argument("right")
    agreement.add_argument("--output", "-o")
    adjudicate = sub.add_parser("adjudicate", help="aggregate independent annotations and preserve ties")
    adjudicate.add_argument("annotations", nargs="+")
    adjudicate.add_argument("--output", "-o")
    evaluate_events = sub.add_parser("evaluate-events", help="score event candidates against resolved labels")
    evaluate_events.add_argument("reference")
    evaluate_events.add_argument("predictions")
    evaluate_events.add_argument("--output", "-o")
    display_assign = sub.add_parser("display-assign", help="create a balanced display-study assignment")
    display_assign.add_argument("participants", help="JSON array of pseudonymous participant IDs")
    display_assign.add_argument("cases", help="JSON array of case IDs")
    display_assign.add_argument("--output", "-o")
    display_analyze = sub.add_parser("display-analyze", help="validate and summarise display-study responses")
    display_analyze.add_argument("assignments")
    display_analyze.add_argument("responses")
    display_analyze.add_argument("answer_key")
    display_analyze.add_argument("--output", "-o")
    study_dry_run = sub.add_parser("study-dry-run", help="run the explicitly synthetic study pipeline")
    study_dry_run.add_argument("--output", "-o")
    modality = sub.add_parser("modality-audit", help="audit synthetic modality conversion loss")
    modality.add_argument("path")
    modality.add_argument("--output", "-o")
    agency = sub.add_parser("strategy-audit", help="audit constructed strategy and user-control episodes")
    agency.add_argument("path")
    agency.add_argument("--output", "-o")
    benchmark = sub.add_parser(
        "benchmark-synthetic",
        help="run the controlled synthetic robustness and ablation benchmark",
    )
    benchmark.add_argument("--manifest", default="examples/synthetic/manifest.json")
    benchmark.add_argument("--output", "-o")
    args = parser.parse_args()
    if args.command == "analyze":
        analyze(args.path)
    elif args.command == "trajectory":
        report = analyze_trajectory(normalize_turns(load_dialogue(args.path)), TrajectoryConfig(projection_seed=args.seed))
        payload = report_to_json(report)
        if args.output:
            Path(args.output).write_text(payload + "\n", encoding="utf-8")
            print(f"wrote {args.output} | shape={report.shape_class} | hash={report.input_hash[:12]}")
        else:
            print(payload)
    elif args.command == "validate-synthetic":
        manifest_path = Path(args.manifest)
        manifest = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
        failures = []
        for case in manifest["cases"]:
            report = analyze_trajectory(load_dialogue(manifest_path.parent / case["file"]))
            ok = report.shape_class == case["expected_shape"] and report.recurrence_source == case["expected_recurrence_source"]
            print(f"{'PASS' if ok else 'FAIL'} {case['id']}: shape={report.shape_class}, source={report.recurrence_source}")
            if not ok:
                failures.append(case["id"])
        if failures:
            raise SystemExit(f"synthetic validation failed: {', '.join(failures)}")
    elif args.command == "agreement":
        left = json.loads(Path(args.left).read_text(encoding="utf-8"))
        right = json.loads(Path(args.right).read_text(encoding="utf-8"))
        payload = json.dumps(compare_annotations(left, right), ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(payload + "\n", encoding="utf-8")
            print(f"wrote {args.output}")
        else:
            print(payload)
    elif args.command == "adjudicate":
        annotations = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args.annotations]
        payload = json.dumps(aggregate_annotations(annotations), ensure_ascii=False, indent=2)
        _write_or_print(payload, args.output)
    elif args.command == "evaluate-events":
        reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
        predictions_payload = json.loads(Path(args.predictions).read_text(encoding="utf-8"))
        predictions = predictions_payload.get("events", predictions_payload) if isinstance(predictions_payload, dict) else predictions_payload
        payload = json.dumps(evaluate_event_predictions(reference, predictions), ensure_ascii=False, indent=2)
        _write_or_print(payload, args.output)
    elif args.command == "display-assign":
        participants = json.loads(Path(args.participants).read_text(encoding="utf-8"))
        cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
        payload = json.dumps(balanced_assignments(participants, cases), ensure_ascii=False, indent=2)
        _write_or_print(payload, args.output)
    elif args.command == "display-analyze":
        assignments = json.loads(Path(args.assignments).read_text(encoding="utf-8"))
        responses_payload = json.loads(Path(args.responses).read_text(encoding="utf-8"))
        responses = responses_payload.get("responses", responses_payload) if isinstance(responses_payload, dict) else responses_payload
        answer_key = json.loads(Path(args.answer_key).read_text(encoding="utf-8"))
        payload = json.dumps(summarise_responses(assignments, responses, answer_key), ensure_ascii=False, indent=2)
        _write_or_print(payload, args.output)
    elif args.command == "study-dry-run":
        payload = json.dumps({
            "schema_version": "topodialogue-study-dry-run-v1",
            "synthetic": True,
            "annotation_study": synthetic_annotation_dry_run(),
            "display_study": synthetic_dry_run(),
            "claim_boundary": (
                "This output verifies study software paths only. It contains no participant "
                "observations and supports no claim about natural dialogue or interface effects."
            ),
        }, ensure_ascii=False, indent=2)
        _write_or_print(payload, args.output)
    elif args.command == "modality-audit":
        fixture = ModalityFixture.model_validate_json(Path(args.path).read_text(encoding="utf-8"))
        payload = json.dumps(audit_fixture(fixture), ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(payload + "\n", encoding="utf-8")
            print(f"wrote {args.output} | cases={len(fixture.cases)}")
        else:
            print(payload)
    elif args.command == "strategy-audit":
        fixture = AgencyFixture.model_validate_json(Path(args.path).read_text(encoding="utf-8"))
        payload = json.dumps(audit_agency_fixture(fixture), ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(payload + "\n", encoding="utf-8")
            print(f"wrote {args.output} | episodes={len(fixture.episodes)}")
        else:
            print(payload)
    elif args.command == "benchmark-synthetic":
        report = run_synthetic_robustness_benchmark(args.manifest)
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(payload + "\n", encoding="utf-8")
            annotated = report["summaries"]["declared_annotations"]["joint_match_rate"]
            ablated = report["summaries"]["text_only_ablation"]["joint_match_rate"]
            print(
                f"wrote {args.output} | runs={report['total_run_count']} | "
                f"annotated_joint={annotated:.3f} | text_only_joint={ablated:.3f}"
            )
        else:
            print(payload)
    else:
        turns = normalize_turns(load_dialogue(args.path))
        events = extract_interaction_events(turns)
        derivative = public_derivative(turns, case_id=args.case_id, events=events)
        audit = audit_dialogue(turns)
        baseline = analyze_trajectory(turns)
        released = analyze_trajectory(normalize_turns([
            turn for turn in load_dialogue_payload(derivative)
        ]))
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / f"{args.case_id}.public.json").write_text(
            json.dumps(derivative, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        (output_dir / f"{args.case_id}.audit.json").write_text(
            audit.model_dump_json(indent=2) + "\n", encoding="utf-8",
        )
        comparison = {
            "case_id": args.case_id,
            "raw_text_released": False,
            "event_count": len(events),
            "event_type_counts": dict(__import__("collections").Counter(event.event_type for event in events)),
            "text_only_baseline": baseline.metrics.model_dump(mode="json"),
            "event_enriched_public_derivative": released.metrics.model_dump(mode="json"),
            "scope_note": "The comparison is descriptive for one case; it is not an accuracy or causal estimate.",
        }
        (output_dir / f"{args.case_id}.comparison.json").write_text(
            json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        (output_dir / f"{args.case_id}.analysis.json").write_text(
            report_to_json(released) + "\n", encoding="utf-8",
        )
        print(
            f"wrote public case | turns={len(turns)} | events={len(events)} | "
            f"raw_text_released=false | output={output_dir}"
        )


def load_dialogue_payload(payload: dict) -> list:
    """Normalise an in-memory payload through the same adapter semantics."""
    from .models import DialogueTurn
    result = []
    for index, message in enumerate(payload.get("messages", []), 1):
        result.append(DialogueTurn(
            turn_id=f"t{index}", session_id=str(payload.get("case_id", "default")),
            speaker=message["role"], text=message["text"],
            metadata={"annotations": message.get("annotations", {})},
        ))
    return result


def _write_or_print(payload: str, output: str | None) -> None:
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
        print(f"wrote {target}")
    else:
        print(payload)


if __name__ == "__main__": main()
