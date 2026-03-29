from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from state_structures.states import EventState
from state_structures.graph_state import GraphState
from observability.logger import traced_node
from observability.serializers import (
    summarize_apply_updates,
    diff_apply_updates,
)

def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _relationship_key(source_actor_id: str, target_actor_id: str) -> str:
    return f"{source_actor_id}__{target_actor_id}"


def _base_deltas(action_type: str, assertiveness: float) -> dict:
    scale = 0.5 + assertiveness

    templates = {
        "propose": {"trust": 0.05, "alignment": 0.05, "conflict": -0.05, "defensiveness": -0.02, "urgency": 0.00, "cooperation": 0.05},
        "request": {"trust": 0.00, "alignment": 0.01, "conflict": 0.02, "defensiveness": 0.02, "urgency": 0.03, "cooperation": -0.01},
        "challenge": {"trust": -0.08, "alignment": -0.05, "conflict": 0.10, "defensiveness": 0.07, "urgency": 0.05, "cooperation": -0.05},
        "support": {"trust": 0.08, "alignment": 0.06, "conflict": -0.04, "defensiveness": -0.03, "urgency": -0.01, "cooperation": 0.06},
        "resist": {"trust": -0.04, "alignment": -0.02, "conflict": 0.06, "defensiveness": 0.04, "urgency": 0.03, "cooperation": -0.04},
        "escalate": {"trust": -0.12, "alignment": -0.08, "conflict": 0.15, "defensiveness": 0.10, "urgency": 0.08, "cooperation": -0.08},
        "deescalate": {"trust": 0.06, "alignment": 0.04, "conflict": -0.10, "defensiveness": -0.06, "urgency": -0.03, "cooperation": 0.08},
        "withhold": {"trust": -0.03, "alignment": -0.02, "conflict": 0.03, "defensiveness": 0.02, "urgency": 0.01, "cooperation": -0.04},
        "signal": {"trust": 0.01, "alignment": 0.01, "conflict": 0.00, "defensiveness": 0.00, "urgency": 0.00, "cooperation": 0.01},
        "reframe": {"trust": 0.02, "alignment": 0.03, "conflict": -0.02, "defensiveness": -0.01, "urgency": 0.00, "cooperation": 0.03},
    }

    template = templates.get(action_type, templates["signal"])
    return {key: value * scale for key, value in template.items()}

@traced_node(
    "apply_updates",
    "state_updated",
    summary_fn=summarize_apply_updates,
    state_diff_fn=diff_apply_updates,
)
def apply_updates(state: GraphState) -> dict:
    """
    Apply deterministic bounded updates based on the chosen action proposal.

    Slice 1:
    - uses deterministic action-type heuristics
    - appends one EventState per applied action
    """
    actor_states = deepcopy(state["actor_states"])
    relationships = deepcopy(state["relationships"])
    events = deepcopy(state["events"])
    round_context = deepcopy(state["round_context"])
    run_control = state["run_control"]

    impact_estimates = {}

    for actor_id, proposal in round_context.get("action_proposals", {}).items():
        action_type = proposal["action_type"]
        target_actor_ids = proposal.get("target_actor_ids", [])
        assertiveness = proposal.get("assertiveness_level", 0.5)

        deltas = _base_deltas(action_type, assertiveness)

        trust_delta_by_target = {}
        alignment_delta_by_target = {}
        conflict_delta_by_target = {}
        defensiveness_delta_by_actor = {}
        urgency_delta_by_actor = {}
        cooperation_delta_by_actor = {}

        # source actor effects
        source_state = actor_states[actor_id]
        source_state["latest_intended_action"] = proposal["action_summary"]
        source_state["confidence"] = _clamp(source_state.get("confidence", 0.5) + 0.02 * assertiveness)
        source_state["urgency"] = _clamp(source_state.get("urgency", 0.5) + max(0.0, deltas["urgency"] / 2.0))
        urgency_delta_by_actor[actor_id] = max(0.0, deltas["urgency"] / 2.0)
        cooperation_delta_by_actor[actor_id] = max(-0.05, min(0.05, deltas["cooperation"] / 2.0))

        for target_actor_id in target_actor_ids:
            rel_key = _relationship_key(actor_id, target_actor_id)
            reverse_rel_key = _relationship_key(target_actor_id, actor_id)

            if rel_key in relationships:
                relationships[rel_key]["trust"] = _clamp(relationships[rel_key]["trust"] + deltas["trust"])
                relationships[rel_key]["alignment"] = _clamp(relationships[rel_key]["alignment"] + deltas["alignment"])
                relationships[rel_key]["conflict_level"] = _clamp(relationships[rel_key]["conflict_level"] + deltas["conflict"])

            if reverse_rel_key in relationships:
                relationships[reverse_rel_key]["trust"] = _clamp(relationships[reverse_rel_key]["trust"] + deltas["trust"] * 0.5)
                relationships[reverse_rel_key]["alignment"] = _clamp(relationships[reverse_rel_key]["alignment"] + deltas["alignment"] * 0.5)
                relationships[reverse_rel_key]["conflict_level"] = _clamp(relationships[reverse_rel_key]["conflict_level"] + deltas["conflict"] * 0.5)

            target_state = actor_states[target_actor_id]
            target_state["defensiveness"] = _clamp(target_state.get("defensiveness", 0.0) + deltas["defensiveness"])
            target_state["urgency"] = _clamp(target_state.get("urgency", 0.5) + deltas["urgency"])
            target_state["willingness_to_cooperate"] = _clamp(
                target_state.get("willingness_to_cooperate", 0.5) + deltas["cooperation"]
            )

            trust_delta_by_target[target_actor_id] = deltas["trust"]
            alignment_delta_by_target[target_actor_id] = deltas["alignment"]
            conflict_delta_by_target[target_actor_id] = deltas["conflict"]
            defensiveness_delta_by_actor[target_actor_id] = deltas["defensiveness"]
            urgency_delta_by_actor[target_actor_id] = deltas["urgency"]
            cooperation_delta_by_actor[target_actor_id] = deltas["cooperation"]

        impact_estimates[actor_id] = {
            "actor_id": actor_id,
            "action_type": action_type,
            "target_actor_ids": target_actor_ids,
            "trust_delta_by_target": trust_delta_by_target,
            "alignment_delta_by_target": alignment_delta_by_target,
            "conflict_delta_by_target": conflict_delta_by_target,
            "defensiveness_delta_by_actor": defensiveness_delta_by_actor,
            "urgency_delta_by_actor": urgency_delta_by_actor,
            "cooperation_delta_by_actor": cooperation_delta_by_actor,
            "explanation": f"Deterministic Slice 1 impact mapping applied for action_type={action_type}.",
        }

        event = EventState(
            event_id=str(uuid4()),
            round_id=run_control["current_round"],
            event_type=action_type,
            initiator=actor_id,
            targets=target_actor_ids,
            summary=proposal["action_summary"],
            tone=action_type,
            claimed_intent=proposal["rationale_summary"],
            observed_effects={
                "target_count": float(len(target_actor_ids)),
                "assertiveness_level": float(assertiveness),
            },
        )
        events.append(event.model_dump())

    round_context["impact_estimates"] = impact_estimates

    return {
        "actor_states": actor_states,
        "relationships": relationships,
        "events": events,
        "round_context": round_context,
    }