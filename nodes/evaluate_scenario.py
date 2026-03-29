from __future__ import annotations

from statistics import mean

from state_structures.states import EvaluationState
from state_structures.graph_state import GraphState
from observability.logger import traced_node
from observability.serializers import (
    summarize_evaluate_scenario,
    diff_evaluate_scenario,
)
def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))

@traced_node(
    "evaluate_scenario",
    "scenario_evaluated",
    summary_fn=summarize_evaluate_scenario,
    state_diff_fn=diff_evaluate_scenario,
)
def evaluate_scenario(state: GraphState) -> dict:
    """
    Deterministic scenario evaluation for Slice 1.

    Writes EvaluationState only.
    Resolution probability and summary are stored in metadata for now.
    """
    relationships = list(state["relationships"].values())
    actor_states = list(state["actor_states"].values())
    scenario = state["scenario"]

    avg_conflict = mean(rel.get("conflict_level", 0.0) for rel in relationships) if relationships else 0.0
    avg_trust = mean(rel.get("trust", 0.5) for rel in relationships) if relationships else 0.5
    avg_alignment = mean(rel.get("alignment", 0.5) for rel in relationships) if relationships else 0.5
    avg_cooperation = mean(actor.get("willingness_to_cooperate", 0.5) for actor in actor_states) if actor_states else 0.5
    avg_defensiveness = mean(actor.get("defensiveness", 0.0) for actor in actor_states) if actor_states else 0.0
    avg_urgency = mean(actor.get("urgency", 0.5) for actor in actor_states) if actor_states else 0.5

    conflict_hotspots = [
        f"{rel['source_actor_id']}->{rel['target_actor_id']}"
        for rel in relationships
        if rel.get("conflict_level", 0.0) >= 0.60
    ]

    coalitions = [
        f"{rel['source_actor_id']}<->{rel['target_actor_id']}"
        for rel in relationships
        if rel.get("trust", 0.0) >= 0.65 and rel.get("alignment", 0.0) >= 0.65
    ]

    stability_score = _clamp((avg_trust + avg_alignment + avg_cooperation + (1.0 - avg_conflict)) / 4.0)
    escalation_risk = _clamp((0.55 * avg_conflict) + (0.25 * avg_defensiveness) + (0.20 * avg_urgency))
    cooperation_probability = _clamp((avg_trust + avg_alignment + avg_cooperation) / 3.0)
    resolution_probability = _clamp((0.60 * cooperation_probability) + (0.40 * stability_score) - (0.20 * escalation_risk))

    key_tensions = list(scenario.get("issue_map", []))[:3]
    if not key_tensions and conflict_hotspots:
        key_tensions = ["Escalating actor-to-actor conflict"]

    likely_outcomes = []
    if escalation_risk >= 0.85:
        likely_outcomes.append("High likelihood of escalation if no intervention occurs.")
    elif resolution_probability >= 0.80:
        likely_outcomes.append("Plausible movement toward short-term stabilization or resolution.")
    else:
        likely_outcomes.append("Scenario likely remains contested with partial movement only.")

    recommended_interventions = []
    if escalation_risk > 0.65:
        recommended_interventions.append("Introduce de-escalation or neutral mediation.")
    if cooperation_probability < 0.45:
        recommended_interventions.append("Reframe incentives toward shared interests.")
    if not recommended_interventions:
        recommended_interventions.append("Maintain structured dialogue and monitor relationship shifts.")

    evaluation_summary = (
        f"Stability={stability_score:.2f}, escalation_risk={escalation_risk:.2f}, "
        f"cooperation_probability={cooperation_probability:.2f}, "
        f"resolution_probability={resolution_probability:.2f}."
    )

    evaluation = EvaluationState(
        scenario_id=scenario["scenario_id"],
        key_tensions=key_tensions,
        coalitions=coalitions,
        conflict_hotspots=conflict_hotspots,
        stability_score=stability_score,
        escalation_risk=escalation_risk,
        cooperation_probability=cooperation_probability,
        likely_outcomes=likely_outcomes,
        recommended_interventions=recommended_interventions,
        metadata={
            "resolution_probability": resolution_probability,
            "evaluation_summary": evaluation_summary,
        },
    )

    return {"evaluation": evaluation.model_dump()}