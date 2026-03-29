# ADR-003: Use a hybrid round/turn simulation loop

## Status
Accepted

## Context
The system needs both:
- global awareness of the scenario each round,
- and selective action so not every actor acts every time.

A fully synchronous model would force all actors to act each round.
A fully asynchronous model would make the simulation harder to compare and inspect.

## Decision
Use a hybrid round/turn loop.

For each round:
1. all active actors refresh interpretation,
2. one primary actor is selected,
3. an optional reactive actor may respond,
4. actions are applied sequentially,
5. the scenario is evaluated,
6. stop conditions are checked.

## Alternatives considered
### Fully synchronous rounds
Rejected because it forces too much simultaneous behavior and makes causality less clear.

### Fully asynchronous turns
Rejected for v1 because it increases scheduling complexity too early.

## Rationale
This model balances:
- structured round progression,
- selective actor action,
- clearer causality,
- and future extensibility.

## Consequences
- Each round has a clear interpretation phase and acting phase
- Primary/reactive actor selection becomes an explicit design concern
- The simulation stays inspectable while still allowing strategic interaction
