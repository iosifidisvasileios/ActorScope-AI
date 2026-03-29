from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class RawScenarioInput(TypedDict, total=False):
    environment: Dict[str, Any]
    scenario: Dict[str, Any]
    actors: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]


class MemoryContext(TypedDict, total=False):
    actor_memories: Dict[str, List[str]]
    relationship_memories: Dict[str, List[str]]
    scenario_pattern_memories: List[str]
    retrieval_metadata: Dict[str, Any]


class ActorInterpretationRecord(TypedDict, total=False):
    actor_id: str
    current_objectives: List[str]
    viewpoint_summary: str
    perceived_risks: List[str]
    strategic_posture: str
    willingness_to_cooperate: float
    confidence: float
    rationale_summary: str


class ActionProposalRecord(TypedDict, total=False):
    actor_id: str
    action_type: str
    action_summary: str
    target_actor_ids: List[str]
    rationale_summary: str
    expected_immediate_outcome: str
    assertiveness_level: float


class ImpactEstimateRecord(TypedDict, total=False):
    actor_id: str
    action_type: str
    target_actor_ids: List[str]
    trust_delta_by_target: Dict[str, float]
    alignment_delta_by_target: Dict[str, float]
    conflict_delta_by_target: Dict[str, float]
    defensiveness_delta_by_actor: Dict[str, float]
    urgency_delta_by_actor: Dict[str, float]
    cooperation_delta_by_actor: Dict[str, float]
    explanation: str


class RoundContext(TypedDict, total=False):
    actor_interpretations: Dict[str, ActorInterpretationRecord]
    salience_scores: Dict[str, float]
    selected_primary_actor: Optional[str]
    selected_reactive_actor: Optional[str]
    action_proposals: Dict[str, ActionProposalRecord]
    impact_estimates: Dict[str, ImpactEstimateRecord]


class RunControl(TypedDict, total=False):
    run_id: str
    current_round: int
    max_rounds: int
    stop_condition_met: bool
    stop_reason: Optional[str]
    consecutive_low_change_rounds: int
    last_conflict_pattern_signature: Optional[str]
    repeated_conflict_pattern_rounds: int


class GraphState(TypedDict, total=False):
    raw_input: RawScenarioInput

    environment: Dict[str, Any]
    scenario: Dict[str, Any]
    actor_profiles: Dict[str, Dict[str, Any]]
    actor_states: Dict[str, Dict[str, Any]]
    relationships: Dict[str, Dict[str, Any]]
    events: List[Dict[str, Any]]
    evaluation: Dict[str, Any]

    memory_context: MemoryContext
    round_context: RoundContext
    run_control: RunControl

    trace_events: List[Dict[str, Any]]