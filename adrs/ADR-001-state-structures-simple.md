# ADR-001: Why the core state classes exist

- **Status:** Accepted
- **Date:** 2026-03-28
- **Related package:** `state_structures`

## Context

The project needs a generic simulation engine for multiple actors in a shared environment.

The main design need was to separate:
- stable actor definitions,
- dynamic scenario state,
- pairwise relationships,
- simulation history,
- final evaluation,
- LangGraph runtime state.

## Decision

We created a small set of core classes, each with one clear responsibility.

### `ActorProfile`
Represents the **stable identity** of an actor.

Why it exists:
- to store role, goals, constraints, capabilities, and red lines,
- to keep long-lived actor information separate from temporary scenario behavior,
- to support reuse of the same actor across multiple scenarios.

### `ActorState`
Represents the **current state** of an actor inside one scenario.

Why it exists:
- to track what the actor currently wants,
- to capture temporary stance, urgency, confidence, defensiveness, and intended action,
- to allow state changes across simulation rounds without mutating the profile.

### `RelationshipState`
Represents the **directional relationship** from one actor to another.

Why it exists:
- to model trust, alignment, conflict, dependency, and influence,
- because actor interaction is central to the project,
- because A's view of B can differ from B's view of A.

### `EnvironmentState`
Represents the **shared environment** in which actors operate.

Why it exists:
- to capture rules, norms, resources, deadlines, and external pressures,
- to keep environment-level constraints separate from actor-level state,
- to support different domains using the same core model.

### `ScenarioState`
Represents the **specific situation** being simulated.

Why it exists:
- to define the trigger, context, stakeholders, known facts, uncertainties, and success/failure conditions,
- to separate one scenario from another inside the same environment,
- to provide the main container for scenario progression.

### `EventState`
Represents a **record of something that happened** during the simulation.

Why it exists:
- to keep a structured history of actions, statements, interventions, and effects,
- to make the simulation inspectable and replayable,
- to avoid hiding important changes inside free-form LLM text.

### `EvaluationState`
Represents the **current assessment** of the scenario.

Why it exists:
- to store escalation risk, cooperation probability, likely outcomes, and recommended interventions,
- to separate analysis outputs from raw simulation events,
- to give the system a structured result layer.

### `GraphState`
Represents the **LangGraph working state** for one running simulation.

Why it exists:
- to bundle the current scenario data passed between LangGraph nodes,
- to hold live state only for the active run,
- to keep runtime orchestration separate from long-term memory.

## Additional decision

The classes are intentionally **domain-agnostic**.

Why:
- the project should support various scenarios,
- the core package should stay reusable,
- domain-specific data can be added later through `metadata` or extension models.

## Consequences

Positive:
- cleaner separation of concerns,
- easier LangGraph node design,
- easier testing of state transitions,
- easier extension to new scenario types.

Tradeoff:
- some domain-specific use cases will need extra fields later,
- the generic core is slightly less convenient than a highly specialized model.

## Guidance

Use these classes as the base contract of the system.
Do not mix stable profile data, runtime state, relationship data, and evaluation results into one object.
Keep long-term memory outside these classes unless it is needed for the active simulation.
