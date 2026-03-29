# ADR-006: Use dual memory and reserve Mem0 for distilled durable memory

## Status
Accepted

## Context
The system needs both:
- rich per-run history for inspection,
- and durable cross-run memory for actor, relationship, and scenario-pattern knowledge.

Storing raw run history in long-term memory would create noise and reduce usefulness.

## Decision
Use dual memory.

### Runtime history
Stored in graph state and artifacts:
- events
- trace records
- round-by-round summaries

### Durable memory
Stored in Mem0 after distillation:
- actor memory
- relationship memory
- scenario-pattern memory

## Alternatives considered
### Put all history into Mem0
Rejected because long-term memory should not become a dump of raw run traces.

### No long-term memory
Rejected because cross-run continuity is one of the system’s explicit goals.

## Rationale
This separation preserves high-value memory while keeping the simulation explainable.

## Consequences
- Retrieval happens before reasoning
- Persistence happens after the run
- Distillation is an explicit architectural step, not an afterthought
