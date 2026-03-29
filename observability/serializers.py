from __future__ import annotations

from typing import Any


def summarize_interpret_actors(state: dict, result: dict) -> str:
    round_context = result.get("round_context", {})
    interpretations = round_context.get("actor_interpretations", {})

    if not interpretations:
        return "No actor interpretations produced."

    parts = []
    for actor_id, interpretation in interpretations.items():
        posture = interpretation.get("strategic_posture", "unknown")
        objectives = interpretation.get("current_objectives", [])[:2]
        parts.append(
            f"{actor_id}: posture={posture}, objectives={objectives}"
        )

    return "Actor interpretations generated: " + " | ".join(parts)


def diff_interpret_actors(state: dict, result: dict) -> dict[str, Any]:
    round_context = result.get("round_context", {})
    interpretations = round_context.get("actor_interpretations", {})

    return {
        "interpreted_actor_ids": list(interpretations.keys()),
        "postures": {
            actor_id: interpretation.get("strategic_posture")
            for actor_id, interpretation in interpretations.items()
        },
    }


def summarize_select_actions(state: dict, result: dict) -> str:
    round_context = result.get("round_context", {})
    primary = round_context.get("selected_primary_actor")
    reactive = round_context.get("selected_reactive_actor")
    proposals = round_context.get("action_proposals", {})

    if not primary:
        return "No primary actor selected."

    proposal = proposals.get(primary, {})
    action_type = proposal.get("action_type", "unknown")
    targets = proposal.get("target_actor_ids", [])

    return (
        f"Selected primary actor={primary}, reactive actor={reactive}, "
        f"action={action_type}, targets={targets}"
    )


def diff_select_actions(state: dict, result: dict) -> dict[str, Any]:
    round_context = result.get("round_context", {})
    salience_scores = round_context.get("salience_scores", {})
    proposals = round_context.get("action_proposals", {})
    primary = round_context.get("selected_primary_actor")

    top_salience = sorted(
        salience_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    selected_action = proposals.get(primary, {}) if primary else {}

    return {
        "selected_primary_actor": primary,
        "selected_reactive_actor": round_context.get("selected_reactive_actor"),
        "top_salience_scores": top_salience,
        "selected_action": {
            "action_type": selected_action.get("action_type"),
            "targets": selected_action.get("target_actor_ids", []),
            "assertiveness_level": selected_action.get("assertiveness_level"),
        },
    }


def summarize_apply_updates(state: dict, result: dict) -> str:
    round_context = result.get("round_context", {})
    impact_estimates = round_context.get("impact_estimates", {})
    events = result.get("events", [])

    actor_summaries = []
    for actor_id, impact in impact_estimates.items():
        actor_summaries.append(
            f"{actor_id}: action={impact.get('action_type')}, "
            f"targets={impact.get('target_actor_ids', [])}"
        )

    return (
        f"Applied updates for {len(impact_estimates)} actor action(s); "
        f"total events now={len(events)}. "
        + " | ".join(actor_summaries)
    )


def diff_apply_updates(state: dict, result: dict) -> dict[str, Any]:
    old_events = state.get("events", [])
    new_events = result.get("events", [])
    round_context = result.get("round_context", {})
    impact_estimates = round_context.get("impact_estimates", {})

    return {
        "new_event_count": len(new_events) - len(old_events),
        "impact_estimates": impact_estimates,
    }


def summarize_evaluate_scenario(state: dict, result: dict) -> str:
    evaluation = result.get("evaluation", {})
    metadata = evaluation.get("metadata", {})

    return (
        f"Evaluation completed: stability={evaluation.get('stability_score')}, "
        f"escalation_risk={evaluation.get('escalation_risk')}, "
        f"cooperation_probability={evaluation.get('cooperation_probability')}, "
        f"resolution_probability={metadata.get('resolution_probability')}"
    )


def diff_evaluate_scenario(state: dict, result: dict) -> dict[str, Any]:
    evaluation = result.get("evaluation", {})
    metadata = evaluation.get("metadata", {})

    return {
        "key_tensions": evaluation.get("key_tensions", []),
        "conflict_hotspots": evaluation.get("conflict_hotspots", []),
        "coalitions": evaluation.get("coalitions", []),
        "stability_score": evaluation.get("stability_score"),
        "escalation_risk": evaluation.get("escalation_risk"),
        "cooperation_probability": evaluation.get("cooperation_probability"),
        "resolution_probability": metadata.get("resolution_probability"),
        "likely_outcomes": evaluation.get("likely_outcomes", []),
        "recommended_interventions": evaluation.get("recommended_interventions", []),
    }


def summarize_stop_check(state: dict, result: dict) -> str:
    run_control = result.get("run_control", {})

    return (
        f"Stop check completed: stop_condition_met={run_control.get('stop_condition_met')}, "
        f"stop_reason={run_control.get('stop_reason')}, "
        f"current_round={run_control.get('current_round')}"
    )


def diff_stop_check(state: dict, result: dict) -> dict[str, Any]:
    run_control = result.get("run_control", {})

    return {
        "stop_condition_met": run_control.get("stop_condition_met"),
        "stop_reason": run_control.get("stop_reason"),
        "current_round": run_control.get("current_round"),
        "consecutive_low_change_rounds": run_control.get("consecutive_low_change_rounds"),
        "last_conflict_pattern_signature": run_control.get("last_conflict_pattern_signature"),
        "repeated_conflict_pattern_rounds": run_control.get("repeated_conflict_pattern_rounds"),
    }