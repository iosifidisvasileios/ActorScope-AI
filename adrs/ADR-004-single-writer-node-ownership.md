# ADR-004: Use single-writer node ownership for mutable state

## Status
Accepted

## Context
Multiple nodes read the same state. If several nodes can write the same fields, the system becomes difficult to reason about and debug.

This is especially risky in a mixed deterministic/LLM system.

## Decision
Adopt a single-writer principle for mutable state.

Each major state area has one owning node:
- `initialize_world` initializes baseline state
- `retrieve_memories` writes only memory context
- `interpret_actors` writes round-local interpretations
- `select_actions` writes salience and action proposals
- `apply_updates` mutates canonical dynamic state and appends events
- `evaluate_scenario` writes evaluation state
- `check_stop_conditions` writes stop/control fields
- `persist_memories` handles memory persistence outputs

## Alternatives considered
### Loose multi-writer updates
Rejected because the same field could be changed by several nodes for different reasons, which would make failures difficult to diagnose.

## Rationale
Single-writer ownership keeps the graph understandable and makes incremental changes safer.

## Consequences
- Node responsibility boundaries are explicit
- Debugging state transitions is easier
- LLM outputs can be isolated from deterministic mutation layers
