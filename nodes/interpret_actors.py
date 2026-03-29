from __future__ import annotations

from copy import deepcopy
from statistics import mean

from config.settings import settings
from llm.ollama_client import OllamaChatClient
from llm.structured_generation import StructuredGenerationError, generate_structured_output
from prompts.actor_interpretation import build_actor_interpretation_prompts
from prompts.contracts import ActorInterpretationInput, ActorInterpretationOutput
from state_structures.graph_state import GraphState
from observability.logger import traced_node
from observability.serializers import (
    summarize_interpret_actors,
    diff_interpret_actors,
)
def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _get_relevant_relationships(actor_id: str, state: GraphState) -> list[dict]:
    relationships = []
    for rel in state["relationships"].values():
        if rel["source_actor_id"] == actor_id or rel["target_actor_id"] == actor_id:
            relationships.append(rel)
    return relationships


def _avg_conflict(relationships: list[dict]) -> float:
    if not relationships:
        return 0.0
    return mean(rel.get("conflict_level", 0.0) for rel in relationships)


def _derive_strategic_posture(actor_state: dict, relationships: list[dict]) -> str:
    willingness = actor_state.get("willingness_to_cooperate", 0.5)
    defensiveness = actor_state.get("defensiveness", 0.0)
    confidence = actor_state.get("confidence", 0.5)
    avg_conflict = _avg_conflict(relationships)

    if avg_conflict > 0.75 and willingness < 0.30:
        return "escalatory"
    if defensiveness > 0.65:
        return "defensive"
    if willingness > 0.70 and avg_conflict < 0.40:
        return "cooperative"
    if confidence > 0.65:
        return "assertive"
    if avg_conflict > 0.50:
        return "guarded"
    return "opportunistic"


def _deterministic_interpretation(
    actor_id: str,
    actor_profile: dict,
    actor_state: dict,
    scenario: dict,
    relevant_relationships: list[dict],
    actor_memories: list[str],
) -> dict:
    strategic_posture = _derive_strategic_posture(actor_state, relevant_relationships)

    base_objectives = actor_profile.get("base_objectives", [])
    current_objectives = actor_state.get("current_objectives") or base_objectives[:3]
    perceived_risks = actor_state.get("perceived_risks", [])[:5]

    if not perceived_risks:
        if actor_profile.get("red_lines"):
            perceived_risks = actor_profile["red_lines"][:2]
        elif relevant_relationships and _avg_conflict(relevant_relationships) > 0.5:
            perceived_risks = ["Relationship deterioration", "Loss of leverage"]
        else:
            perceived_risks = ["Strategic misalignment"]

    memory_hint = actor_memories[0] if actor_memories else "No prior durable memory available."

    viewpoint_summary = (
        f"{actor_profile['name']} ({actor_profile['role_label']}) views the scenario as "
        f"centered on {scenario['title']}. The actor is currently operating from a "
        f"{strategic_posture} posture."
    )

    rationale_summary = (
        f"Interpretation based on current urgency={actor_state.get('urgency', 0.5):.2f}, "
        f"confidence={actor_state.get('confidence', 0.5):.2f}, "
        f"willingness_to_cooperate={actor_state.get('willingness_to_cooperate', 0.5):.2f}, "
        f"and observed relationship conflict={_avg_conflict(relevant_relationships):.2f}. "
        f"Memory hint: {memory_hint}"
    )

    return {
        "actor_id": actor_id,
        "current_objectives": current_objectives[:5],
        "viewpoint_summary": viewpoint_summary,
        "perceived_risks": perceived_risks[:5],
        "strategic_posture": strategic_posture,
        "willingness_to_cooperate": _clamp(actor_state.get("willingness_to_cooperate", 0.5)),
        "confidence": _clamp(actor_state.get("confidence", 0.5)),
        "rationale_summary": rationale_summary,
    }

@traced_node(
    "interpret_actors",
    "actor_interpretation",
    summary_fn=summarize_interpret_actors,
    state_diff_fn=diff_interpret_actors,
)
def interpret_actors(state: GraphState) -> dict:
    """
    Build round-local actor interpretations.

    Ownership:
    - increments current_round
    - resets round_context
    - writes round_context.actor_interpretations

    For Slice 1.1:
    - uses Ollama for interpretation when enabled
    - falls back to deterministic logic on failure
    """
    run_control = deepcopy(state["run_control"])
    run_control["current_round"] += 1

    round_context = {
        "actor_interpretations": {},
        "salience_scores": {},
        "selected_primary_actor": None,
        "selected_reactive_actor": None,
        "action_proposals": {},
        "impact_estimates": {},
    }

    scenario = state["scenario"]
    environment = state["environment"]
    actor_profiles = state["actor_profiles"]
    actor_states = state["actor_states"]
    events = state["events"]
    memory_context = state["memory_context"]

    client = OllamaChatClient() if settings.use_llm_interpretation else None

    for actor_id, actor_profile in actor_profiles.items():
        actor_state = actor_states[actor_id]
        relevant_relationships = _get_relevant_relationships(actor_id, state)
        actor_memories = memory_context.get("actor_memories", {}).get(actor_id, [])

        deterministic_result = _deterministic_interpretation(
            actor_id=actor_id,
            actor_profile=actor_profile,
            actor_state=actor_state,
            scenario=scenario,
            relevant_relationships=relevant_relationships,
            actor_memories=actor_memories,
        )

        if not settings.use_llm_interpretation or client is None:
            round_context["actor_interpretations"][actor_id] = deterministic_result
            continue

        try:
            payload = ActorInterpretationInput(
                run_id=run_control["run_id"],
                scenario_id=scenario["scenario_id"],
                round_id=run_control["current_round"],
                actor_profile=actor_profile,
                actor_state=actor_state,
                relevant_relationships=relevant_relationships,
                scenario=scenario,
                environment=environment,
                recent_events=events[-5:],
                retrieved_memories=actor_memories,
            )

            system_prompt, user_prompt = build_actor_interpretation_prompts(payload)

            structured_output: ActorInterpretationOutput = generate_structured_output(
                client=client,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                output_model=ActorInterpretationOutput,
            )

            round_context["actor_interpretations"][actor_id] = structured_output.model_dump()
        except StructuredGenerationError:
            round_context["actor_interpretations"][actor_id] = deterministic_result

    return {
        "run_control": run_control,
        "round_context": round_context,
    }