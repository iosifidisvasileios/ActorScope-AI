from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def write_trace_jsonl(trace_events: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for event in trace_events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


def write_final_output_json(final_output: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(final_output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _format_list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]


def _group_trace_events_by_round(trace_events: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for event in trace_events:
        round_id = int(event.get("round_id", 0))
        grouped[round_id].append(event)
    return dict(sorted(grouped.items(), key=lambda x: x[0]))


def _find_first_event(events: list[dict], node_name: str) -> dict[str, Any] | None:
    for event in events:
        if event.get("node_name") == node_name:
            return event
    return None


def _render_round_section(round_id: int, events: list[dict]) -> list[str]:
    lines: list[str] = [f"## Round {round_id}", ""]

    interpret_event = _find_first_event(events, "interpret_actors")
    select_event = _find_first_event(events, "select_actions")
    update_event = _find_first_event(events, "apply_updates")
    evaluate_event = _find_first_event(events, "evaluate_scenario")
    stop_event = _find_first_event(events, "check_stop_conditions")

    lines.append("### Interpretations")
    if interpret_event:
        lines.append(interpret_event.get("summary", "No interpretation summary available."))
        postures = interpret_event.get("state_diff_summary", {}).get("postures", {})
        if postures:
            lines.append("")
            lines.append("Postures:")
            for actor_id, posture in postures.items():
                lines.append(f"- {actor_id}: {posture}")
    else:
        lines.append("No interpretation event recorded.")
    lines.append("")

    lines.append("### Action selection")
    if select_event:
        lines.append(select_event.get("summary", "No action-selection summary available."))
        selected = select_event.get("state_diff_summary", {}).get("selected_action", {})
        if selected:
            lines.append("")
            lines.append("Selected action details:")
            lines.append(f"- action_type: {selected.get('action_type')}")
            lines.append(f"- targets: {selected.get('targets', [])}")
            lines.append(f"- assertiveness_level: {selected.get('assertiveness_level')}")
        top_salience = select_event.get("state_diff_summary", {}).get("top_salience_scores", [])
        if top_salience:
            lines.append("")
            lines.append("Top salience scores:")
            for actor_id, score in top_salience:
                lines.append(f"- {actor_id}: {score}")
    else:
        lines.append("No action-selection event recorded.")
    lines.append("")

    lines.append("### Applied updates")
    if update_event:
        lines.append(update_event.get("summary", "No update summary available."))
    else:
        lines.append("No update event recorded.")
    lines.append("")

    lines.append("### Evaluation")
    if evaluate_event:
        lines.append(evaluate_event.get("summary", "No evaluation summary available."))
        diff = evaluate_event.get("state_diff_summary", {})
        lines.append("")
        lines.append("Evaluation details:")
        lines.append(f"- key_tensions: {diff.get('key_tensions', [])}")
        lines.append(f"- conflict_hotspots: {diff.get('conflict_hotspots', [])}")
        lines.append(f"- coalitions: {diff.get('coalitions', [])}")
        lines.append(f"- likely_outcomes: {diff.get('likely_outcomes', [])}")
        lines.append(f"- recommended_interventions: {diff.get('recommended_interventions', [])}")
    else:
        lines.append("No evaluation event recorded.")
    lines.append("")

    lines.append("### Stop check")
    if stop_event:
        lines.append(stop_event.get("summary", "No stop-check summary available."))
        diff = stop_event.get("state_diff_summary", {})
        lines.append("")
        lines.append("Stop details:")
        lines.append(f"- stop_condition_met: {diff.get('stop_condition_met')}")
        lines.append(f"- stop_reason: {diff.get('stop_reason')}")
        lines.append(f"- consecutive_low_change_rounds: {diff.get('consecutive_low_change_rounds')}")
        lines.append(f"- repeated_conflict_pattern_rounds: {diff.get('repeated_conflict_pattern_rounds')}")
    else:
        lines.append("No stop-check event recorded.")
    lines.append("")

    return lines


def write_summary_markdown(
    final_output: dict,
    trace_events: list[dict],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    grouped_events = _group_trace_events_by_round(trace_events)

    lines = [
        "# Simulation Summary",
        "",
        f"**Scenario:** {final_output['scenario_title']}",
        f"**Rounds:** {final_output['round_count']}",
        f"**Stop reason:** {final_output['stop_reason']}",
        "",
        "## Final key tensions",
    ]
    lines.extend(_format_list(final_output.get("key_tensions", [])))
    lines.extend(["", "## Final likely outcomes"])
    lines.extend(_format_list(final_output.get("likely_outcomes", [])))
    lines.extend(["", "## Final recommended interventions"])
    lines.extend(_format_list(final_output.get("recommended_interventions", [])))
    lines.extend(
        [
            "",
            "## Final scores",
            f"- Stability: {final_output.get('stability_score')}",
            f"- Escalation risk: {final_output.get('escalation_risk')}",
            f"- Cooperation probability: {final_output.get('cooperation_probability')}",
            f"- Resolution probability: {final_output.get('resolution_probability')}",
            "",
            "# Round-by-round breakdown",
            "",
        ]
    )

    if not grouped_events:
        lines.append("No trace events recorded.")
    else:
        for round_id, round_events in grouped_events.items():
            if round_id <= 0:
                continue
            lines.extend(_render_round_section(round_id, round_events))

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_run_artifacts(
    final_state: dict,
    final_output: dict,
    artifacts_dir: str = "artifacts",
) -> None:
    base = Path(artifacts_dir)
    trace_events = final_state.get("trace_events", [])

    write_trace_jsonl(trace_events, base / "trace.jsonl")
    write_final_output_json(final_output, base / "final_output.json")
    write_summary_markdown(final_output, trace_events, base / "summary.md")