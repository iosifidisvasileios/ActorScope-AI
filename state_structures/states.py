"""Core state structures for a domain-agnostic multi-actor simulation engine.

This package defines the core data models for representing:
- actors and their stable profiles
- actor runtime state during a scenario
- pairwise relationships between actors
- the shared environment
- scenario-specific state
- simulation events
- evaluation outputs
- LangGraph thread-scoped graph state

Design intent
-------------
These models are deliberately generic. They are meant to support many kinds of
multi-actor environments such as corporations, political systems, negotiations,
game factions, family businesses, or any other setting with multiple actors who
have different roles, objectives, and constraints.

Recommended usage boundary
--------------------------
- LangGraph should manage the live `GraphState` for the current simulation.
- Mem0 should store long-term memory derived from scenarios and relationships.
- LLMs (via Ollama or APIs) should reason over slices of this state, not own it.
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, TypedDict
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    """Base model with strict field handling for predictable state updates."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class ActorProfile(StrictModel):
    """Stable, mostly non-changing description of an actor.

    This model should contain the actor's enduring characteristics rather than
    transient state for a single round of a scenario.
    """

    actor_id: str = Field(..., description="Unique stable actor identifier.")
    name: str = Field(..., description="Human-readable actor name.")
    role_label: str = Field(..., description="Short role label used in the environment.")
    role_description: Optional[str] = Field(
        default=None,
        description="Longer description of the actor's role and function.",
    )
    base_objectives: List[str] = Field(
        default_factory=list,
        description="Core goals the actor generally optimizes for.",
    )
    base_priorities: Dict[str, float] = Field(
        default_factory=dict,
        description="Relative priority weights, typically normalized by the application.",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Structural limits, obligations, or restrictions on the actor.",
    )
    capabilities: List[str] = Field(
        default_factory=list,
        description="Actions or powers the actor can realistically use.",
    )
    red_lines: List[str] = Field(
        default_factory=list,
        description="Outcomes or conditions the actor is unlikely to accept.",
    )
    interaction_style: Optional[str] = Field(
        default=None,
        description="High-level interaction tendency, e.g. diplomatic, aggressive, cautious.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific stable attributes.",
    )


class ActorState(StrictModel):
    """Dynamic, scenario-scoped state of an actor.

    This model should be updated during simulation rounds.
    """

    actor_id: str = Field(..., description="Reference to the owning actor profile.")
    current_objectives: List[str] = Field(
        default_factory=list,
        description="Objectives currently active in this scenario or round.",
    )
    current_position: Optional[str] = Field(
        default=None,
        description="Current stance or viewpoint held by the actor.",
    )
    perceived_risks: List[str] = Field(
        default_factory=list,
        description="Risks the actor believes are currently relevant.",
    )
    willingness_to_cooperate: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Current openness to cooperative solutions.",
    )
    defensiveness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Current defensiveness level.",
    )
    urgency: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How urgent the actor perceives the situation to be.",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Current confidence in the actor's position or leverage.",
    )
    latest_intended_action: Optional[str] = Field(
        default=None,
        description="Most recent intended next move.",
    )
    latent_assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions the actor is currently operating under.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific runtime attributes.",
    )


class RelationshipState(StrictModel):
    """Dynamic pairwise state from one actor toward another.

    This is directional by design. A->B can differ from B->A.
    """

    source_actor_id: str = Field(..., description="Actor whose perspective this relationship encodes.")
    target_actor_id: str = Field(..., description="Actor being evaluated by the source actor.")
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    alignment: float = Field(default=0.5, ge=0.0, le=1.0)
    conflict_level: float = Field(default=0.0, ge=0.0, le=1.0)
    dependency: float = Field(default=0.0, ge=0.0, le=1.0)
    influence: float = Field(default=0.0, ge=0.0, le=1.0)
    perceived_reliability: float = Field(default=0.5, ge=0.0, le=1.0)
    history_summary: Optional[str] = Field(
        default=None,
        description="Compressed summary of the recent relationship history.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific relationship attributes.",
    )


class EnvironmentState(StrictModel):
    """Shared environment in which actors operate."""

    environment_id: str = Field(..., description="Unique identifier for the environment.")
    environment_type: str = Field(
        ..., description="Broad type, e.g. corporation, politics, negotiation, guild."
    )
    description: str = Field(..., description="Summary of the shared environment.")
    actors: List[str] = Field(
        default_factory=list,
        description="Actor IDs currently present in the environment.",
    )
    rules: List[str] = Field(
        default_factory=list,
        description="Formal rules that structure action in the environment.",
    )
    norms: List[str] = Field(
        default_factory=list,
        description="Informal expectations or conventions.",
    )
    resources: List[str] = Field(
        default_factory=list,
        description="Scarce resources, levers, or assets in the environment.",
    )
    deadlines: List[str] = Field(
        default_factory=list,
        description="Relevant deadlines or time pressures.",
    )
    external_pressures: List[str] = Field(
        default_factory=list,
        description="Outside forces affecting the environment.",
    )
    active_issues: List[str] = Field(
        default_factory=list,
        description="Issues currently shaping the environment.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific environment attributes.",
    )


class ScenarioState(StrictModel):
    """Specific situation being simulated within an environment."""

    scenario_id: str = Field(..., description="Unique scenario identifier.")
    title: str = Field(..., description="Short scenario title.")
    trigger: str = Field(..., description="What initiated the situation.")
    context_summary: str = Field(..., description="Short summary of the situation.")
    stakeholders: List[str] = Field(
        default_factory=list,
        description="Actor IDs directly involved in the scenario.",
    )
    issue_map: List[str] = Field(
        default_factory=list,
        description="Core issues or dispute points in the scenario.",
    )
    known_facts: List[str] = Field(
        default_factory=list,
        description="Facts treated as known/accepted by the engine.",
    )
    uncertainties: List[str] = Field(
        default_factory=list,
        description="Unknowns, ambiguities, or disputed facts.",
    )
    success_conditions: List[str] = Field(
        default_factory=list,
        description="What would count as a successful outcome.",
    )
    failure_conditions: List[str] = Field(
        default_factory=list,
        description="What would count as a failed outcome.",
    )
    current_round: int = Field(default=0, ge=0)
    status: Literal["draft", "active", "paused", "resolved", "failed"] = Field(
        default="active"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific scenario attributes.",
    )


class EventState(StrictModel):
    """Single event or interaction occurring during the simulation."""

    event_id: str = Field(..., description="Unique event identifier.")
    round_id: int = Field(..., ge=0, description="Simulation round in which the event occurred.")
    event_type: str = Field(
        ..., description="High-level category such as message, proposal, escalation, intervention."
    )
    initiator: str = Field(..., description="Actor ID that initiated the event.")
    targets: List[str] = Field(
        default_factory=list,
        description="Actor IDs targeted or affected directly.",
    )
    summary: str = Field(..., description="Compact summary of what happened.")
    tone: Optional[str] = Field(
        default=None,
        description="Interaction tone, if relevant.",
    )
    claimed_intent: Optional[str] = Field(
        default=None,
        description="Intent stated or attributed to the initiator.",
    )
    observed_effects: Dict[str, float] = Field(
        default_factory=dict,
        description="Numeric deltas or scalar effects recorded by the engine.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific event attributes.",
    )


class EvaluationState(StrictModel):
    """Assessment layer summarizing the scenario's current state."""

    scenario_id: str = Field(..., description="Scenario being evaluated.")
    key_tensions: List[str] = Field(
        default_factory=list,
        description="Most salient tensions driving the scenario.",
    )
    coalitions: List[str] = Field(
        default_factory=list,
        description="Observed or emerging coalitions/blocs.",
    )
    conflict_hotspots: List[str] = Field(
        default_factory=list,
        description="Where the strongest conflict is concentrated.",
    )
    stability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    escalation_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    cooperation_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    likely_outcomes: List[str] = Field(
        default_factory=list,
        description="Most plausible next outcomes under current conditions.",
    )
    recommended_interventions: List[str] = Field(
        default_factory=list,
        description="Actions that could change the scenario trajectory.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional extension point for domain-specific evaluation attributes.",
    )


class GraphState(TypedDict):
    """Thread-scoped LangGraph state for one active simulation.

    Guidance:
    - Keep only scenario-relevant live state here.
    - Do not place full long-term memory blobs into this structure.
    - Use Mem0 to store durable memory across sessions or scenarios.
    """

    environment: Dict[str, Any]
    scenario: Dict[str, Any]
    actor_profiles: Dict[str, Dict[str, Any]]
    actor_states: Dict[str, Dict[str, Any]]
    relationships: Dict[str, Dict[str, Any]]
    events: List[Dict[str, Any]]
    evaluation: Dict[str, Any]
    active_actor_queue: List[str]
    stop_condition: bool


