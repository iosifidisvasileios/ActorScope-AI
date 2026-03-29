# ADR-008: Enable LLM-backed nodes incrementally

## Status
Accepted

## Context
Multiple nodes could be made LLM-backed:
- interpretation,
- action selection,
- interaction impact,
- evaluation.

Switching many nodes to LLM behavior at once would make it hard to isolate failures.

## Decision
Enable LLM-backed behavior incrementally.

Order chosen:
1. `interpret_actors`
2. `select_actions`
3. later consider evaluation support
4. keep updates deterministic

## Alternatives considered
### Convert all reasoning nodes at once
Rejected because failures would be difficult to localize.

### Delay all LLM integration until later
Rejected because the system’s purpose requires actor-level interpretation and action realism.

## Rationale
Incremental rollout preserves a stable deterministic baseline while validating contracts step by step.

## Consequences
- Deterministic fallbacks remain important
- Node-by-node verification is possible
- The system can evolve without losing debuggability
