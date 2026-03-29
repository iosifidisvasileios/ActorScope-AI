from __future__ import annotations

from typing import Any

from memory.filters import (
    actor_memory_user_id,
    relationship_memory_user_id,
    scenario_pattern_user_id,
)


def distill_actor_memories(state: dict) -> list[dict[str, Any]]:
    actor_profiles = state.get("actor_profiles", {})
    actor_states = state.get("actor_states", {})
    evaluation = state.get("evaluation", {})
    scenario = state.get("scenario", {})
    environment = state.get("environment", {})

    distilled: list[dict[str, Any]] = []

    for actor_id, profile in actor_profiles.items():
        actor_state = actor_states.get(actor_id, {})

        text = (
            f"Actor {profile.get('name', actor_id)} in role {profile.get('role_label')} "
            f"ended scenario '{scenario.get('title')}' with "
            f"willingness_to_cooperate={actor_state.get('willingness_to_cooperate')}, "
            f"defensiveness={actor_state.get('defensiveness')}, "
            f"urgency={actor_state.get('urgency')}, "
            f"confidence={actor_state.get('confidence')}."
        )

        distilled.append(
            {
                "user_id": actor_memory_user_id(actor_id),
                "text": text,
                "metadata": {
                    "memory_type": "actor_memory",
                    "actor_id": actor_id,
                    "scenario_id": scenario.get("scenario_id"),
                    "environment_type": environment.get("environment_type"),
                    "escalation_risk": evaluation.get("escalation_risk"),
                },
            }
        )

    return distilled


def distill_relationship_memories(state: dict) -> list[dict[str, Any]]:
    relationships = state.get("relationships", {})
    scenario = state.get("scenario", {})

    distilled: list[dict[str, Any]] = []

    for relationship_key, rel in relationships.items():
        text = (
            f"Relationship {relationship_key} ended scenario '{scenario.get('title')}' with "
            f"trust={rel.get('trust')}, "
            f"alignment={rel.get('alignment')}, "
            f"conflict_level={rel.get('conflict_level')}, "
            f"perceived_reliability={rel.get('perceived_reliability')}."
        )

        distilled.append(
            {
                "user_id": relationship_memory_user_id(relationship_key),
                "text": text,
                "metadata": {
                    "memory_type": "relationship_memory",
                    "relationship_key": relationship_key,
                    "source_actor_id": rel.get("source_actor_id"),
                    "target_actor_id": rel.get("target_actor_id"),
                    "scenario_id": scenario.get("scenario_id"),
                },
            }
        )

    return distilled


def distill_scenario_pattern_memories(state: dict) -> list[dict[str, Any]]:
    evaluation = state.get("evaluation", {})
    scenario = state.get("scenario", {})
    environment = state.get("environment", {})
    run_control = state.get("run_control", {})

    text = (
        f"In environment_type={environment.get('environment_type')}, scenario '{scenario.get('title')}' "
        f"ended after {run_control.get('current_round')} rounds with "
        f"stop_reason={run_control.get('stop_reason')}, "
        f"escalation_risk={evaluation.get('escalation_risk')}, "
        f"cooperation_probability={evaluation.get('cooperation_probability')}, "
        f"likely_outcomes={evaluation.get('likely_outcomes', [])}."
    )

    return [
        {
            "user_id": scenario_pattern_user_id(),
            "text": text,
            "metadata": {
                "memory_type": "scenario_pattern_memory",
                "scenario_id": scenario.get("scenario_id"),
                "environment_type": environment.get("environment_type"),
            },
        }
    ]