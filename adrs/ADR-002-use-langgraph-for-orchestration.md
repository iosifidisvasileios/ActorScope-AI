# ADR-002: Use LangGraph for orchestration

## Status
Accepted

## Context
The system is not a single prompt pipeline. It requires:
- multiple nodes,
- shared state,
- looping behavior across rounds,
- conditional stopping,
- and future extensibility for human-in-the-loop and richer control.

## Decision
Use LangGraph as the orchestration layer for the live simulation.

LangGraph is responsible for:
- graph construction,
- node execution order,
- round progression,
- conditional routing,
- and state passing between nodes.

## Alternatives considered
### Plain Python orchestration
Rejected because it would work initially but would become harder to manage once the simulation loop and branching behavior grew.

### Fully agent-chat-style orchestration
Rejected because this system requires explicit state ownership and controlled progression, not only free agent conversation.

## Rationale
LangGraph matches the design of:
- node-based execution,
- explicit shared state,
- iterative loops,
- and future extensions.

## Consequences
- The system is implemented as a graph of nodes
- Routing and node business logic remain separate
- The architecture is prepared for more complex control later without redesigning the whole runtime
