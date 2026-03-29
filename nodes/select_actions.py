from __future__ import annotations

from copy import deepcopy
from statistics import mean

from config.settings import settings
from llm.ollama_client import OllamaChatClient
from llm.structured_generation import StructuredGenerationError, generate_structured_output
from prompts.action_selection import build_action_selection_prompts
from prompts.contracts import ActionSelectionInput, ActionSelectionOutput
from state_structures.graph_state import GraphState
from observability.logger import traced_node
from observability.serializers import (
    summarize_select_actions,
    diff_select_actions,
)

def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _actor_relationships(actor_id: str, state: GraphState) -> list[dict]:
    rels = []
    for rel in state["relationships"].values():
        if rel["source_actor_id"] == actor_id or rel["target_actor_id"] == actor_id:
            rels.append(rel)
    return rels


def _avg_conflict(actor_id: str, state: GraphState) -> float:
    rels = _actor_relationships(actor_id, state)
    if not rels:
        return 0.0
    return mean(rel.get("conflict_level", 0.0) for rel in rels)


def _avg_influence(actor_id: str, state: GraphState) -> float:
    rels = _actor_relationships(actor_id, state)
    if not rels:
        return 0.0
    return mean(rel.get("influence", 0.0) for rel in rels)


def _compute_salience(actor_id: str, state: GraphState) -> float:
    actor_state = state["actor_states"][actor_id]
    scenario = state["scenario"]

    urgency = actor_state.get("urgency", 0.5)
    confidence = actor_state.get("confidence", 0.5)
    avg_conflict = _avg_conflict(actor_id, state)
    avg_influence = _avg_influence(actor_id, state)
    stakeholder_bonus = 0.15 if actor_id in scenario.get("stakeholders", []) else 0.0

    score = (
        0.35 * urgency
        + 0.20 * avg_conflict
        + 0.20 * avg_influence
        + 0.10 * confidence
        + stakeholder_bonus
    )
    return _clamp(score)


def _pick_target_candidates(primary_actor_id: str, state: GraphState) -> list[str]:
    candidates = []

    for rel in state["relationships"].values():
        if rel["source_actor_id"] == primary_actor_id:
            candidates.append((rel["target_actor_id"], rel.get("conflict_level", 0.0)))

    candidates.sort(key=lambda item: item[1], reverse=True)

    ordered_targets = [actor_id for actor_id, _ in candidates]

    if ordered_targets:
        return ordered_targets[:3]

    return [actor_id for actor_id in state["actor_profiles"].keys() if actor_id != primary_actor_id][:3]


def _action_type_from_posture(posture: str) -> str:
    mapping = {
        "cooperative": "propose",
        "guarded": "request",
        "defensive": "resist",
        "assertive": "challenge",
        "opportunistic": "reframe",
        "escalatory": "escalate",
    }
    return mapping.get(posture, "signal")


def _assertiveness_from_posture(posture: str, confidence: float) -> float:
    base = {
        "cooperative": 0.45,
        "guarded": 0.50,
        "defensive": 0.60,
        "assertive": 0.75,
        "opportunistic": 0.55,
        "escalatory": 0.90,
    }.get(posture, 0.50)
    return _clamp((base + confidence) / 2.0)


def _deterministic_action_proposal(
    actor_id: str,
    interpretation: dict,
    state: GraphState,
) -> dict:
    target_actor_ids = _pick_target_candidates(actor_id, state)[:1]
    action_type = _action_type_from_posture(interpretation["strategic_posture"])
    assertiveness_level = _assertiveness_from_posture(
        interpretation["strategic_posture"],
        interpretation["confidence"],
    )

    action_summary = (
        f"{actor_id} will likely {action_type} "
        f"{'toward ' + ', '.join(target_actor_ids) if target_actor_ids else 'without a direct target'}."
    )
    rationale_summary = (
        f"Action derived from posture={interpretation['strategic_posture']} "
        f"and confidence={interpretation['confidence']:.2f}."
    )
    expected_immediate_outcome = (
        "The action will shift local alignment/conflict dynamics and affect short-term cooperation."
    )

    return {
        "actor_id": actor_id,
        "action_type": action_type,
        "action_summary": action_summary,
        "target_actor_ids": target_actor_ids,
        "rationale_summary": rationale_summary,
        "expected_immediate_outcome": expected_immediate_outcome,
        "assertiveness_level": assertiveness_level,
    }

@traced_node(
    "select_actions",
    "action_selected",
    summary_fn=summarize_select_actions,
    state_diff_fn=diff_select_actions,
)
def select_actions(state: GraphState) -> dict:
    """
    Compute actor salience and propose actions for the selected actor(s).

    Slice 1.2:
    - salience remains deterministic
    - primary actor selection remains deterministic
    - action selection uses Ollama when enabled
    - deterministic fallback remains available
    """
    round_context = deepcopy(state["round_context"])
    salience_scores: dict[str, float] = {}

    for actor_id in state["actor_profiles"].keys():
        salience_scores[actor_id] = _compute_salience(actor_id, state)

    primary_actor_id = max(salience_scores, key=salience_scores.get)
    interpretation = round_context["actor_interpretations"][primary_actor_id]
    allowed_targets = _pick_target_candidates(primary_actor_id, state)

    deterministic_result = _deterministic_action_proposal(
        actor_id=primary_actor_id,
        interpretation=interpretation,
        state=state,
    )

    if not getattr(settings, "use_llm_action_selection", True):
        action_result = deterministic_result
    else:
        client = OllamaChatClient()
        try:
            payload = ActionSelectionInput(
                run_id=state["run_control"]["run_id"],
                scenario_id=state["scenario"]["scenario_id"],
                round_id=state["run_control"]["current_round"],
                actor_id=primary_actor_id,
                actor_interpretation=interpretation,
                actor_state=state["actor_states"][primary_actor_id],
                relevant_relationships=_actor_relationships(primary_actor_id, state),
                scenario=state["scenario"],
                environment=state["environment"],
                recent_events=state["events"][-5:],
                allowed_targets=allowed_targets,
                reactive_mode=False,
            )

            system_prompt, user_prompt = build_action_selection_prompts(payload)

            structured_output: ActionSelectionOutput = generate_structured_output(
                client=client,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                output_model=ActionSelectionOutput,
            )

            action_result = structured_output.model_dump()
        except StructuredGenerationError:
            action_result = deterministic_result

    round_context["salience_scores"] = salience_scores
    round_context["selected_primary_actor"] = primary_actor_id
    round_context["selected_reactive_actor"] = None
    round_context["action_proposals"] = {
        primary_actor_id: action_result
    }

    return {"round_context": round_context}