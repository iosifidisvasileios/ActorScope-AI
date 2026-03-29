# ADR-007: Use typed prompt contracts with Pydantic

## Status
Accepted

## Context
The system integrates LLM reasoning into a strongly stateful simulation. Free-form text responses would make the runtime fragile and increase parsing ambiguity.

## Decision
Use typed prompt contracts backed by Pydantic models for:
- actor interpretation,
- action selection,
- interaction impact,
- scenario evaluation.

Each prompt has:
- an input model,
- an output model,
- bounded numeric fields where needed,
- and explicit validation.

## Alternatives considered
### Free-form prompt outputs with ad hoc parsing
Rejected because the graph depends on structured data and predictable node boundaries.

## Rationale
Typed contracts keep the LLM layer compatible with the rest of the architecture.

## Consequences
- Prompt behavior is testable
- Validation failures can trigger fallbacks
- State updates do not depend on brittle string parsing
