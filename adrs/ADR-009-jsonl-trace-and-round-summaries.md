# ADR-009: Use JSONL trace as canonical observability format with markdown round summaries

## Status
**Implemented with enhancements**

## Context
The system needs both:
- machine-readable execution and decision traces,
- and human-readable run summaries.

Simple console logging is not enough for debugging multi-round actor decisions.

## Decision
Use:
- `trace.jsonl` as the canonical machine-readable trace,
- `summary.md` as a human-readable run report,
- `final_output.json` as the structured final result.

The trace records:
- node execution,
- round number,
- actor ids,
- decisions,
- evaluation outputs,
- stop decisions,
- latency,
- memory operations (retrieval and persistence),
- impact estimates,
- state diff summaries.

The markdown summary is derived from the trace.

## Alternatives considered
### Console logs only
Rejected because they are not reliable as a run artifact.

### Markdown only
Rejected because structured replay and debugging need a machine-readable source of truth.

## Rationale
This split supports both automated inspection and human understanding.

## Consequences
- Observability is first-class
- Round-by-round decision analysis is possible
- Future tools can parse the trace without depending on the markdown summary
- Memory operations are fully tracked and visible in traces
- Enhanced serializers provide detailed state diff information
- Memory hints and impact estimates are captured for each round
- Artifacts include comprehensive memory operation summaries
