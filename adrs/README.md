# Decision ADR Index

This folder contains decision-level ADRs for the current ActorScope-AI architecture.

## Included ADRs
- ADR-001: Separate canonical state, round-local state, and run-control state
- ADR-002: Use LangGraph for orchestration
- ADR-003: Use a hybrid round/turn simulation loop
- ADR-004: Use single-writer node ownership for mutable state
- ADR-005: Keep world mutation deterministic in v1
- ADR-006: Use dual memory and reserve Mem0 for distilled durable memory **(Implemented)**
- ADR-007: Use typed prompt contracts with Pydantic
- ADR-008: Enable LLM-backed nodes incrementally
- ADR-009: Use JSONL trace and markdown round summaries **(Implemented with enhancements)**
- ADR-010: Use modular usecases architecture for scenario management **(Implemented)**
- ADR-011: Provide LangGraph visualization export capabilities **(Implemented)**

These ADRs document concrete architectural decisions rather than package descriptions.

## Recent Implementation Updates
- **ADR-006**: Mem0 integration now fully operational with memory tracking in observability
- **ADR-009**: Enhanced observability includes memory operations, impact estimates, and detailed state diffs
- **ADR-010**: Modular usecases package supports both simple demos and complex geopolitical scenarios
- **ADR-011**: Graph visualization export provides PNG and Mermaid outputs for documentation
