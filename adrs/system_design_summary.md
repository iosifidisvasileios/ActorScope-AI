# System Design Summary (Compact)

## Purpose

This document gives a compact overview of the current design so a reader or another LLM can understand the system without reviewing the full discussion history.

---

## 1. System goal

The project is a **domain-agnostic multi-actor simulation engine**.

It is meant to model environments where multiple actors:
- have different roles, objectives, priorities, and constraints,
- relate to one another through trust, conflict, alignment, influence, or dependency,
- interpret the same situation differently,
- act and react over time,
- and move toward different possible outcomes.

The manager/direct-report example was only illustrative. The system is **not** limited to workplace scenarios.

---

## 2. Chosen stack

### Core technologies
- **LangGraph** for runtime orchestration
- **Mem0** for durable long-term memory
- **Ollama** for LLM inference

### Responsibility split
- **LangGraph** owns the live simulation flow and current run state
- **Mem0** stores reusable memory across runs
- **Ollama** reasons over selected state slices and returns structured outputs

---

## 3. Core architecture

The system is **state-driven**, not just a set of chatting agents.

It is built around these core state structures:
- `ActorProfile`
- `ActorState`
- `RelationshipState`
- `EnvironmentState`
- `ScenarioState`
- `EventState`
- `EvaluationState`
- `GraphState`

### State governance
State is handled using **strict ownership plus derived fields**.

Field categories:
- **Initialization-only**: set during setup and then treated as stable
- **Mutable**: updated during simulation
- **Derived**: computed from other state
- **Memory-worthy**: distilled and optionally stored in Mem0

---

## 4. V1 scope

V1 should support:
- defining a scenario with multiple actors
- representing environment, actors, runtime state, and relationships
- running a bounded simulation across a fixed number of rounds
- generating per-actor standpoint summaries
- estimating likely outcomes
- recommending interventions
- persisting distilled long-term memory in Mem0

### Explicitly deferred from V1
- UI
- human-in-the-loop
- advanced graph memory
- scenario libraries
- learned update policies
- broader productization features

---

## 5. Simulation model

### High-level philosophy
The system should not start with agents immediately talking.

It should first build the world:
1. define actors
2. define relationships
3. define environment
4. define scenario
5. initialize runtime state
6. retrieve relevant memory
7. begin simulation rounds

### Chosen loop style
**Hybrid round/turn model**

Each round:
- refreshes interpretation for all active actors
- selects exactly one primary actor
- optionally allows one reactive actor
- applies actions sequentially
- evaluates the scenario afterward

### Run lifecycle
1. input intake
2. world construction
3. initial memory retrieval
4. round loop
5. stop decision
6. memory distillation and persistence
7. final output assembly
8. artifact/log generation

---

## 6. Memory design

### Chosen strategy
**Dual memory**

### Meaning
- detailed run history stays in runtime state and artifacts
- durable reusable knowledge goes into Mem0

### Memory categories for Mem0
- **actor memory**
- **relationship memory**
- **scenario-pattern memory**

### Not stored in Mem0 in V1
- raw prompts
- full event logs
- per-turn noise
- low-confidence speculation

---

## 7. Update model

### Chosen strategy
**Hybrid**

### Meaning
- LLMs produce structured reasoning and proposed effects
- deterministic code validates, clamps, and applies updates

### LLM responsibilities
- actor interpretation
- action selection
- interaction impact estimation
- scenario evaluation

### Deterministic responsibilities
- schema validation
- range checks
- ownership enforcement
- bounded updates
- stop logic
- persistence control

---

## 8. LangGraph nodes

### Selected node map
1. `initialize_world`
2. `retrieve_memories`
3. `interpret_actors`
4. `select_actions`
5. `apply_updates`
6. `evaluate_scenario`
7. `check_stop_conditions`
8. `persist_memories`

### Node responsibilities
- `initialize_world`: build baseline state
- `retrieve_memories`: load memory into context only
- `interpret_actors`: create round-local actor interpretations
- `select_actions`: compute salience and choose actions
- `apply_updates`: mutate canonical dynamic state and append events
- `evaluate_scenario`: write assessment state
- `check_stop_conditions`: decide whether the run ends
- `persist_memories`: distill and store durable memories

---

## 9. Canonical state vs round-local state

This distinction is important.

### Canonical state
Longer-lived simulation state, such as:
- actor dynamic fields like defensiveness, urgency, confidence, willingness to cooperate
- relationship fields like trust, conflict, alignment
- scenario facts
- event history
- evaluation state

### Round-local state
Temporary state for one round, such as:
- actor interpretations
- salience scores
- selected actors
- action proposals
- impact estimates

### Run-control state
Execution control fields, such as:
- `run_id`
- `current_round`
- `max_rounds`
- `stop_condition_met`
- `stop_reason`

### Refined `GraphState`
The runtime state should include at least:
- `environment`
- `scenario`
- `actor_profiles`
- `actor_states`
- `relationships`
- `events`
- `evaluation`
- `memory_context`
- `round_context`
- `run_control`

---

## 10. Prompt contracts

The system uses **strict typed prompt contracts**.

### 1. ActorInterpretation
Purpose:
- determine how an actor currently understands the scenario

Typical output:
- current objectives
- viewpoint summary
- perceived risks
- strategic posture
- willingness to cooperate
- confidence
- rationale summary

Stored in:
- `round_context.actor_interpretations`

### 2. ActionSelection
Purpose:
- determine the next action of the selected actor

Typical output:
- action type
- action summary
- target actor ids
- rationale
- expected immediate outcome
- assertiveness level

Stored in:
- `round_context.action_proposals`

### 3. InteractionImpact
Purpose:
- estimate bounded effects of an action

Typical output:
- trust/alignment/conflict deltas by target
- defensiveness/urgency/cooperation deltas by actor
- explanation

Stored in:
- `round_context.impact_estimates`

### 4. ScenarioEvaluation
Purpose:
- assess the scenario after updates

Typical output:
- key tensions
- conflict hotspots
- coalitions
- stability score
- escalation risk
- cooperation probability
- resolution probability
- likely outcomes
- recommended interventions
- evaluation summary

Stored in:
- `evaluation`

---

## 11. Stop logic

### Chosen strategy
**Layered stop logic**

The run stops if any of these are true:
1. maximum rounds reached
2. resolution probability crosses threshold
3. escalation risk crosses threshold
4. state change remains too small for consecutive rounds
5. the same conflict pattern repeats without progress

### Selected starter defaults
- `max_rounds = 7`
- `resolution_threshold = 0.80`
- `escalation_threshold = 0.85`
- `low_change_delta_threshold = 0.05`
- `low_change_round_limit = 2`
- `conflict_pattern_repeat_limit = 2`

---

## 12. Output contract

Each completed run should return a structured result containing:
- scenario summary
- per-actor standpoint summaries
- relationship hotspot summary
- key tensions
- likely outcomes
- recommended interventions
- stop reason
- round count
- uncertainty or confidence notes

---

## 13. Package structure

### Chosen structure
Medium-granularity layered structure

### Initial package tree
- `state_structures/`
- `graph/`
- `nodes/`
- `prompts/`
- `memory/`
- `llm/`
- `evaluation/`
- `observability/`
- `config/`
- `adrs/`
- `tests/`
- `main.py`

### Reserved for later
- `domains/`

### ADR coverage
The intended initial ADR set covers:
- `state_structures`
- `graph`
- `nodes`
- `prompts`
- `memory`
- `llm`
- `evaluation`
- `observability`
- `config`

---

## 14. Observability

### Chosen approach
**JSONL event tracing plus run summary artifacts**

### Required artifacts per run
- `trace.jsonl`
- `final_output.json`
- `summary.md`

### Canonical trace fields
At minimum:
- `run_id`
- `scenario_id`
- `round_id`
- `node_name`
- `event_type`
- `timestamp`
- `actor_ids`
- `summary`
- `state_diff_summary`
- `success`
- `error_message`
- `latency_ms`

### Suggested event types
- `node_start`
- `node_end`
- `memory_retrieval`
- `actor_interpretation`
- `action_selected`
- `impact_estimated`
- `state_updated`
- `scenario_evaluated`
- `stop_checked`
- `memory_persisted`
- `artifact_written`
- `error`

---

## 15. Implementation-ready conclusion

The system is now sufficiently specified to begin implementation.

### Immediate implementation priorities
1. refine `GraphState`
2. create prompt contract models
3. create config defaults for stop thresholds
4. scaffold package tree
5. implement LangGraph skeleton nodes
6. wire observability
7. add Mem0 retrieval/persistence stubs
8. add Ollama structured-generation stubs

This is the current baseline for implementation.