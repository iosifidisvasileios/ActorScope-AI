from __future__ import annotations

from copy import deepcopy

from memory.mem0_client import Mem0Client
from memory.retrieval import (
    retrieve_actor_memories,
    retrieve_relationship_memories,
    retrieve_scenario_pattern_memories,
)
from observability.logger import traced_node
from state_structures.graph_state import GraphState


@traced_node("retrieve_memories", "memory_retrieval")
def retrieve_memories(state: GraphState) -> dict:
    memory_context = deepcopy(state.get("memory_context", {}))
    run_control = state["run_control"]

    actor_ids = list(state["actor_profiles"].keys())
    relationship_keys = list(state["relationships"].keys())
    scenario_title = state["scenario"]["title"]
    environment_type = state["environment"]["environment_type"]

    client = Mem0Client()

    if client.is_enabled:
        actor_memories = retrieve_actor_memories(client, actor_ids, scenario_title)
        relationship_memories = retrieve_relationship_memories(
            client,
            relationship_keys,
            scenario_title,
        )
        scenario_pattern_memories = retrieve_scenario_pattern_memories(
            client,
            environment_type,
            scenario_title,
        )
        retrieval_mode = "mem0"
    else:
        actor_memories = {actor_id: [] for actor_id in actor_ids}
        relationship_memories = {key: [] for key in relationship_keys}
        scenario_pattern_memories = []
        retrieval_mode = "stub"

    retrieval_metadata = memory_context.get("retrieval_metadata", {})
    retrieval_metadata["last_retrieval_round"] = run_control["current_round"]
    retrieval_metadata["retrieval_mode"] = retrieval_mode
    retrieval_metadata["actor_memory_count"] = sum(len(v) for v in actor_memories.values())
    retrieval_metadata["relationship_memory_count"] = sum(len(v) for v in relationship_memories.values())
    retrieval_metadata["scenario_pattern_memory_count"] = len(scenario_pattern_memories)

    return {
        "memory_context": {
            "actor_memories": actor_memories,
            "relationship_memories": relationship_memories,
            "scenario_pattern_memories": scenario_pattern_memories,
            "retrieval_metadata": retrieval_metadata,
        }
    }