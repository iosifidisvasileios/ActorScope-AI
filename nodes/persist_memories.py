from __future__ import annotations

from copy import deepcopy

from memory.distillation import (
    distill_actor_memories,
    distill_relationship_memories,
    distill_scenario_pattern_memories,
)
from memory.mem0_client import Mem0Client
from observability.logger import traced_node
from state_structures.graph_state import GraphState


@traced_node("persist_memories", "memory_persisted")
def persist_memories(state: GraphState) -> dict:
    memory_context = deepcopy(state["memory_context"])
    retrieval_metadata = memory_context.get("retrieval_metadata", {})

    actor_memories = distill_actor_memories(state)
    relationship_memories = distill_relationship_memories(state)
    scenario_pattern_memories = distill_scenario_pattern_memories(state)

    client = Mem0Client()

    persisted_count = 0
    persistence_mode = "stub"

    if client.is_enabled:
        persistence_mode = "mem0"

        for item in actor_memories + relationship_memories + scenario_pattern_memories:
            result = client.add_text(
                item["text"],
                user_id=item["user_id"],
                metadata=item["metadata"],
            )
            if result is not None:
                persisted_count += 1

    retrieval_metadata["persistence_mode"] = persistence_mode
    retrieval_metadata["persistence_status"] = "completed"
    retrieval_metadata["persisted_count"] = persisted_count
    retrieval_metadata["distilled_actor_memory_count"] = len(actor_memories)
    retrieval_metadata["distilled_relationship_memory_count"] = len(relationship_memories)
    retrieval_metadata["distilled_scenario_pattern_memory_count"] = len(scenario_pattern_memories)

    memory_context["retrieval_metadata"] = retrieval_metadata
    return {"memory_context": memory_context}