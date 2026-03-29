# ADR-005: Keep world mutation deterministic in v1

## Status
Accepted

## Context
The system uses LLMs for interpretation and action selection, but uncontrolled LLM-driven mutation of trust, conflict, urgency, and cooperation would make the simulation unstable and hard to verify.

## Decision
Keep `apply_updates` deterministic in v1.

LLMs may:
- interpret actor stance,
- select likely actions,
- later assist with evaluation.

But mutation of canonical simulation state is applied by deterministic logic with bounded values.

## Alternatives considered
### Make state updates fully LLM-driven
Rejected for v1 because it would make results less predictable and much harder to debug.

### Make all reasoning deterministic
Rejected because the system is explicitly designed to model nuanced actor viewpoints and actions.

## Rationale
This hybrid split gives:
- realistic interpretation and action generation,
- controlled state mutation,
- and much better traceability.

## Consequences
- `apply_updates` remains a core control layer
- LLM integration can expand gradually without destabilizing the simulation
- Evaluation and stop logic can still rely on bounded state
