from __future__ import annotations

from copy import deepcopy

from config.settings import settings
from state_structures.graph_state import GraphState
from observability.logger import traced_node
from observability.serializers import (
    summarize_stop_check,
    diff_stop_check,
)
def _average_change_magnitude(impact_estimates: dict) -> float:
    values: list[float] = []

    for estimate in impact_estimates.values():
        for delta_map_name in (
            "trust_delta_by_target",
            "alignment_delta_by_target",
            "conflict_delta_by_target",
            "defensiveness_delta_by_actor",
            "urgency_delta_by_actor",
            "cooperation_delta_by_actor",
        ):
            for value in estimate.get(delta_map_name, {}).values():
                values.append(abs(float(value)))

    if not values:
        return 0.0

    return sum(values) / len(values)

@traced_node(
    "check_stop_conditions",
    "stop_checked",
    summary_fn=summarize_stop_check,
    state_diff_fn=diff_stop_check,
)
def check_stop_conditions(state: GraphState) -> dict:
    """
    Apply layered stop logic using configured thresholds.
    """
    run_control = deepcopy(state["run_control"])
    evaluation = state["evaluation"]
    round_context = state["round_context"]

    current_round = run_control["current_round"]
    max_rounds = run_control["max_rounds"]
    escalation_risk = float(evaluation.get("escalation_risk", 0.0))
    resolution_probability = float(evaluation.get("metadata", {}).get("resolution_probability", 0.0))

    change_magnitude = _average_change_magnitude(round_context.get("impact_estimates", {}))
    if change_magnitude < settings.low_change_delta_threshold:
        run_control["consecutive_low_change_rounds"] += 1
    else:
        run_control["consecutive_low_change_rounds"] = 0

    conflict_signature = "|".join(sorted(evaluation.get("conflict_hotspots", [])))
    previous_signature = run_control.get("last_conflict_pattern_signature")
    repeated_rounds = run_control.get("repeated_conflict_pattern_rounds", 0)

    if conflict_signature and conflict_signature == previous_signature:
        repeated_rounds += 1
    else:
        repeated_rounds = 0

    run_control["last_conflict_pattern_signature"] = conflict_signature or None
    run_control["repeated_conflict_pattern_rounds"] = repeated_rounds

    stop_condition_met = False
    stop_reason = None

    if current_round >= max_rounds:
        stop_condition_met = True
        stop_reason = "max_rounds_reached"
    elif resolution_probability >= settings.resolution_threshold:
        stop_condition_met = True
        stop_reason = "resolution_threshold_reached"
    elif escalation_risk >= settings.escalation_threshold:
        stop_condition_met = True
        stop_reason = "escalation_threshold_reached"
    elif run_control["consecutive_low_change_rounds"] >= settings.low_change_round_limit:
        stop_condition_met = True
        stop_reason = "low_change_deadlock_detected"
    elif repeated_rounds >= settings.conflict_pattern_repeat_limit:
        stop_condition_met = True
        stop_reason = "repeated_conflict_pattern_detected"

    run_control["stop_condition_met"] = stop_condition_met
    run_control["stop_reason"] = stop_reason

    return {"run_control": run_control}