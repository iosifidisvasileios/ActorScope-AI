from __future__ import annotations

import argparse
import json
from pathlib import Path
from pprint import pprint
from typing import Callable

from graph.builder import build_graph
from observability.artifacts import write_run_artifacts
from usecases.demo_organization import build_demo_organization_input


UsecaseFactory = Callable[[], dict]

USECASE_REGISTRY: dict[str, UsecaseFactory] = {
    "demo_organization": build_demo_organization_input,
}


def extract_final_output(final_state: dict) -> dict:
    scenario = final_state["scenario"]
    evaluation = final_state["evaluation"]
    run_control = final_state["run_control"]
    round_context = final_state.get("round_context", {})
    actor_interpretations = round_context.get("actor_interpretations", {})

    per_actor = {}
    for actor_id, interpretation in actor_interpretations.items():
        per_actor[actor_id] = {
            "viewpoint_summary": interpretation.get("viewpoint_summary"),
            "strategic_posture": interpretation.get("strategic_posture"),
            "current_objectives": interpretation.get("current_objectives", []),
            "perceived_risks": interpretation.get("perceived_risks", []),
        }

    return {
        "scenario_id": scenario["scenario_id"],
        "scenario_title": scenario["title"],
        "round_count": run_control["current_round"],
        "stop_condition_met": run_control["stop_condition_met"],
        "stop_reason": run_control["stop_reason"],
        "per_actor_standpoints": per_actor,
        "key_tensions": evaluation.get("key_tensions", []),
        "conflict_hotspots": evaluation.get("conflict_hotspots", []),
        "likely_outcomes": evaluation.get("likely_outcomes", []),
        "recommended_interventions": evaluation.get("recommended_interventions", []),
        "stability_score": evaluation.get("stability_score"),
        "escalation_risk": evaluation.get("escalation_risk"),
        "cooperation_probability": evaluation.get("cooperation_probability"),
        "resolution_probability": evaluation.get("metadata", {}).get("resolution_probability"),
        "evaluation_summary": evaluation.get("metadata", {}).get("evaluation_summary"),
    }


def load_input_from_json(path: str | Path) -> dict:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_usecase_payload(
    usecase_name: str | None = None,
    input_json: str | None = None,
) -> dict:
    if input_json:
        return load_input_from_json(input_json)

    selected = usecase_name or "demo_organization"
    try:
        return USECASE_REGISTRY[selected]()
    except KeyError as exc:
        available = ", ".join(sorted(USECASE_REGISTRY))
        raise ValueError(
            f"Unknown use case '{selected}'. Available use cases: {available}"
        ) from exc


def run_usecase(
    raw_input: dict,
    *,
    artifacts_dir: str = "artifacts",
    print_final_output: bool = True,
) -> tuple[dict, dict]:
    app = build_graph()
    final_state = app.invoke({"raw_input": raw_input})
    final_output = extract_final_output(final_state)

    write_run_artifacts(
        final_state=final_state,
        final_output=final_output,
        artifacts_dir=artifacts_dir,
    )

    if print_final_output:
        print("\n=== FINAL OUTPUT ===\n")
        pprint(final_output)
        print(f"\nArtifacts written to ./{artifacts_dir}/")

    return final_state, final_output


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an ActorScope-AI use case or custom scenario input."
    )
    parser.add_argument(
        "--usecase",
        default="demo_organization",
        choices=sorted(USECASE_REGISTRY.keys()),
        help="Named built-in use case to run.",
    )
    parser.add_argument(
        "--input-json",
        default=None,
        help="Path to a custom JSON scenario input. Overrides --usecase when provided.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts",
        help="Directory where trace and output artifacts will be written.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress printing the final output to stdout.",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    payload = resolve_usecase_payload(
        usecase_name=args.usecase,
        input_json=args.input_json,
    )

    run_usecase(
        raw_input=payload,
        artifacts_dir=args.artifacts_dir,
        print_final_output=not args.quiet,
    )


if __name__ == "__main__":
    main()

