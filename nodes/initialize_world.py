from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from config.settings import settings
from state_structures import (
    ActorProfile,
    ActorState,
    EnvironmentState,
    EvaluationState,
    RelationshipState,
    ScenarioState,
)
from state_structures.graph_state import GraphState
from observability.logger import traced_node


def _build_actor_profiles(raw_actors: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    actor_profiles: Dict[str, Dict[str, Any]] = {}

    for raw_actor in raw_actors:
        profile = ActorProfile(**raw_actor)
        actor_profiles[profile.actor_id] = profile.model_dump()

    return actor_profiles


def _build_actor_states(actor_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    actor_states: Dict[str, Dict[str, Any]] = {}

    for actor_id in actor_ids:
        state = ActorState(actor_id=actor_id)
        actor_states[actor_id] = state.model_dump()

    return actor_states


def _relationship_key(source_actor_id: str, target_actor_id: str) -> str:
    return f"{source_actor_id}__{target_actor_id}"


def _build_relationships(raw_relationships: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    relationships: Dict[str, Dict[str, Any]] = {}

    for raw_relationship in raw_relationships:
        relationship = RelationshipState(**raw_relationship)
        key = _relationship_key(
            relationship.source_actor_id,
            relationship.target_actor_id,
        )
        relationships[key] = relationship.model_dump()

    return relationships

@traced_node("initialize_world", "node_end")
def initialize_world(state: GraphState) -> dict:
    """
    Build the baseline GraphState from raw_input.
    """
    raw_input = state["raw_input"]

    raw_environment = raw_input["environment"]
    raw_scenario = raw_input["scenario"]
    raw_actors = raw_input["actors"]
    raw_relationships = raw_input.get("relationships", [])

    environment = EnvironmentState(**raw_environment)

    actor_profiles = _build_actor_profiles(raw_actors)
    actor_ids = list(actor_profiles.keys())

    actor_states = _build_actor_states(actor_ids)
    relationships = _build_relationships(raw_relationships)

    scenario = ScenarioState(**raw_scenario)
    evaluation = EvaluationState(scenario_id=scenario.scenario_id)

    run_id = str(uuid4())

    return {
        "environment": environment.model_dump(),
        "scenario": scenario.model_dump(),
        "actor_profiles": actor_profiles,
        "actor_states": actor_states,
        "relationships": relationships,
        "events": [],
        "evaluation": evaluation.model_dump(),
        "memory_context": {
            "actor_memories": {},
            "relationship_memories": {},
            "scenario_pattern_memories": [],
            "retrieval_metadata": {},
        },
        "round_context": {
            "actor_interpretations": {},
            "salience_scores": {},
            "selected_primary_actor": None,
            "selected_reactive_actor": None,
            "action_proposals": {},
            "impact_estimates": {},
        },
        "run_control": {
            "run_id": run_id,
            "current_round": 0,
            "max_rounds": settings.max_rounds,
            "stop_condition_met": False,
            "stop_reason": None,
            "consecutive_low_change_rounds": 0,
            "last_conflict_pattern_signature": None,
            "repeated_conflict_pattern_rounds": 0,
        },
    }