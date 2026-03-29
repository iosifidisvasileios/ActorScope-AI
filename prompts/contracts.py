from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

from state_structures import (
    ActorProfile,
    ActorState,
    EnvironmentState,
    EventState,
    RelationshipState,
    ScenarioState,
)

class PromptModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
    )


# -------------------------------------------------------------------
# Actor Interpretation
# -------------------------------------------------------------------

class ActorInterpretationInput(PromptModel):
    run_id: str
    scenario_id: str
    round_id: int
    actor_profile: ActorProfile
    actor_state: ActorState
    relevant_relationships: List[RelationshipState]
    scenario: ScenarioState
    environment: EnvironmentState
    recent_events: List[EventState] = Field(default_factory=list)
    retrieved_memories: List[str] = Field(default_factory=list)


class ActorInterpretationOutput(PromptModel):
    actor_id: str
    current_objectives: List[str] = Field(default_factory=list, max_length=5)
    viewpoint_summary: str
    perceived_risks: List[str] = Field(default_factory=list, max_length=5)
    strategic_posture: Literal[
        "cooperative",
        "guarded",
        "defensive",
        "assertive",
        "opportunistic",
        "escalatory",
    ]
    willingness_to_cooperate: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale_summary: str


# -------------------------------------------------------------------
# Action Selection
# -------------------------------------------------------------------

class ActionSelectionInput(PromptModel):
    run_id: str
    scenario_id: str
    round_id: int
    actor_id: str
    actor_interpretation: ActorInterpretationOutput
    actor_state: ActorState
    relevant_relationships: List[RelationshipState]
    scenario: ScenarioState
    environment: EnvironmentState
    recent_events: List[EventState] = Field(default_factory=list)
    allowed_targets: List[str] = Field(default_factory=list)
    reactive_mode: bool = False


class ActionSelectionOutput(PromptModel):
    actor_id: str
    action_type: Literal[
        "propose",
        "request",
        "challenge",
        "support",
        "resist",
        "escalate",
        "deescalate",
        "withhold",
        "signal",
        "reframe",
    ]
    action_summary: str
    target_actor_ids: List[str] = Field(default_factory=list, max_length=3)
    rationale_summary: str
    expected_immediate_outcome: str
    assertiveness_level: float = Field(ge=0.0, le=1.0)


# -------------------------------------------------------------------
# Interaction Impact
# -------------------------------------------------------------------

class InteractionImpactInput(PromptModel):
    run_id: str
    scenario_id: str
    round_id: int
    action_proposal: ActionSelectionOutput
    source_actor_state: ActorState
    target_actor_states: List[ActorState]
    relevant_relationships: List[RelationshipState]
    scenario: ScenarioState
    recent_events: List[EventState] = Field(default_factory=list)


class InteractionImpactOutput(PromptModel):
    actor_id: str
    action_type: str
    target_actor_ids: List[str] = Field(default_factory=list)

    trust_delta_by_target: Dict[str, float] = Field(default_factory=dict)
    alignment_delta_by_target: Dict[str, float] = Field(default_factory=dict)
    conflict_delta_by_target: Dict[str, float] = Field(default_factory=dict)

    defensiveness_delta_by_actor: Dict[str, float] = Field(default_factory=dict)
    urgency_delta_by_actor: Dict[str, float] = Field(default_factory=dict)
    cooperation_delta_by_actor: Dict[str, float] = Field(default_factory=dict)

    explanation: str


# -------------------------------------------------------------------
# Scenario Evaluation
# -------------------------------------------------------------------

class ScenarioEvaluationInput(PromptModel):
    run_id: str
    scenario_id: str
    round_id: int
    scenario: ScenarioState
    environment: EnvironmentState
    actor_states: List[ActorState]
    relationships: List[RelationshipState]
    recent_events: List[EventState] = Field(default_factory=list)


class ScenarioEvaluationOutput(PromptModel):
    scenario_id: str
    key_tensions: List[str] = Field(default_factory=list)
    conflict_hotspots: List[str] = Field(default_factory=list)
    coalitions: List[str] = Field(default_factory=list)
    stability_score: float = Field(ge=0.0, le=1.0)
    escalation_risk: float = Field(ge=0.0, le=1.0)
    cooperation_probability: float = Field(ge=0.0, le=1.0)
    resolution_probability: float = Field(ge=0.0, le=1.0)
    likely_outcomes: List[str] = Field(default_factory=list)
    recommended_interventions: List[str] = Field(default_factory=list)
    evaluation_summary: str