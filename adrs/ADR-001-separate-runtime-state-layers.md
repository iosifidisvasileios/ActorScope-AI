# ADR-001: Separate canonical state, round-local state, and run-control state

## Status
Accepted

## Context
The system simulates multiple actors over multiple rounds. Some information is durable across the run, some is only relevant inside a single round, and some only controls execution.

Without an explicit separation, the same fields would be reused for:
- long-lived simulation facts,
- temporary reasoning outputs,
- and graph execution flags.

That would make state mutation unclear and debugging difficult.

## Decision
The runtime state is divided into three layers:

### Canonical simulation state
Longer-lived state for the current run, such as:
- `actor_profiles`
- `actor_states`
- `relationships`
- `scenario`
- `environment`
- `events`
- `evaluation`

### Round-local state
Temporary state for a single round, such as:
- `actor_interpretations`
- `salience_scores`
- `selected_primary_actor`
- `selected_reactive_actor`
- `action_proposals`
- `impact_estimates`

### Run-control state
Execution control state, such as:
- `run_id`
- `current_round`
- `max_rounds`
- `stop_condition_met`
- `stop_reason`
- deadlock counters and pattern signatures

## Alternatives considered
### Store everything in one flat graph state
Rejected because temporary reasoning outputs and durable state would be mixed together.

### Store interpretation directly inside canonical `ActorState`
Partially rejected. Some actor fields remain canonical, but per-round reasoning outputs are kept in `round_context`.

## Rationale
This separation supports:
- cleaner node ownership,
- easier traceability,
- safer incremental LLM integration,
- and clearer debugging when a round behaves unexpectedly.

## Consequences
- The graph state includes `memory_context`, `round_context`, and `run_control`
- Per-round reasoning is not treated as durable fact by default
- Nodes can be designed around explicit ownership boundaries
