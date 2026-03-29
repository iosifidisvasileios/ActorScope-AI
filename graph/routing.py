from __future__ import annotations

from state_structures.graph_state import GraphState


def route_after_stop_check(state: GraphState) -> str:
    if state["run_control"].get("stop_condition_met", False):
        return "persist_memories"
    return "interpret_actors"