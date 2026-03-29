from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from graph.routing import route_after_stop_check
from nodes.apply_updates import apply_updates
from nodes.check_stop_conditions import check_stop_conditions
from nodes.evaluate_scenario import evaluate_scenario
from nodes.initialize_world import initialize_world
from nodes.interpret_actors import interpret_actors
from nodes.persist_memories import persist_memories
from nodes.retrieve_memories import retrieve_memories
from nodes.select_actions import select_actions
from state_structures.graph_state import GraphState


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("initialize_world", initialize_world)
    graph.add_node("retrieve_memories", retrieve_memories)
    graph.add_node("interpret_actors", interpret_actors)
    graph.add_node("select_actions", select_actions)
    graph.add_node("apply_updates", apply_updates)
    graph.add_node("evaluate_scenario", evaluate_scenario)
    graph.add_node("check_stop_conditions", check_stop_conditions)
    graph.add_node("persist_memories", persist_memories)

    graph.add_edge(START, "initialize_world")
    graph.add_edge("initialize_world", "retrieve_memories")
    graph.add_edge("retrieve_memories", "interpret_actors")
    graph.add_edge("interpret_actors", "select_actions")
    graph.add_edge("select_actions", "apply_updates")
    graph.add_edge("apply_updates", "evaluate_scenario")
    graph.add_edge("evaluate_scenario", "check_stop_conditions")

    graph.add_conditional_edges(
        "check_stop_conditions",
        route_after_stop_check,
        {
            "interpret_actors": "interpret_actors",
            "persist_memories": "persist_memories",
        },
    )

    graph.add_edge("persist_memories", END)

    return graph.compile()