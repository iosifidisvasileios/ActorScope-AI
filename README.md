# ActorScope-AI

<p align="center">
  <strong>Stateful multi-actor simulation for reasoning about viewpoints, tension, influence, and outcomes.</strong>
</p>

<p align="center">
  <em>LangGraph orchestration • Ollama-backed reasoning • Mem0 durable memory • Typed state and observability</em>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11+-blue">
  <img alt="Poetry" src="https://img.shields.io/badge/dependency%20manager-poetry-blueviolet">
  <img alt="LangGraph" src="https://img.shields.io/badge/orchestration-LangGraph-111827">
  <img alt="Ollama" src="https://img.shields.io/badge/LLM-Ollama-0f766e">
  <img alt="Mem0" src="https://img.shields.io/badge/memory-Mem0-7c3aed">
  <img alt="Status" src="https://img.shields.io/badge/status-architecture--first-orange">
</p>

---

## What it is

**ActorScope-AI** is a simulation engine for analyzing how multiple actors behave inside a shared environment.

Instead of collapsing a situation into one summary or one chatbot response, ActorScope-AI models it as a **stateful multi-actor system** with:

- explicit actors
- directional relationships
- shared environment and scenario state
- round-by-round reasoning
- structured decisions
- durable memory across runs
- traceable outcomes

The goal is to understand questions such as:

- What is each actor optimizing for?
- Who is most likely to act next?
- What action is most likely to be taken?
- Where are the key tensions?
- What outcomes are plausible?
- What interventions could change the trajectory?

---

## Why this project exists

Many real situations are not single-agent problems.

They involve:
- different incentives
- asymmetries of power and dependency
- partial alignment and partial conflict
- changing interpretations across time
- reactions to previous actions

ActorScope-AI is designed to model those dynamics explicitly.

Potential environments include:
- organizations
- negotiations
- alliances
- political systems
- geopolitical settings
- other multi-party strategic environments

---

## Core idea

The system separates simulation into three layers.

### Canonical state
Longer-lived run state:
- actors
- relationships
- environment
- scenario
- event history
- evaluation

### Round-local reasoning
Temporary per-round state:
- actor interpretations
- salience scores
- selected actors
- action proposals
- impact estimates

### Run control
Execution state:
- run id
- current round
- stop conditions
- deadlock/escalation counters

This keeps the system inspectable and extensible.

---

## Architecture snapshot

### Stack
- **LangGraph** for orchestration
- **Ollama** for LLM-backed reasoning
- **Mem0** for durable memory
- **Pydantic** for typed state and contracts

### Current execution model
- world-first initialization
- hybrid round/turn loop
- all actors interpret the scenario each round
- one primary actor acts each round
- deterministic mutation of world state
- per-round evaluation and stop checks
- run artifacts for inspection

### Current LLM usage
At the current stage:
- **actor interpretation** is LLM-backed
- **action selection** is LLM-backed
- **state mutation** remains deterministic
- **evaluation** remains deterministic

That split is intentional. It keeps reasoning flexible while preserving control over world updates.

---

## Key features

### Multi-actor simulation
Actors can carry:
- roles
- base objectives
- priorities
- constraints
- capabilities
- red lines
- interaction styles

### Relationship-aware reasoning
Relationships are directional and can encode:
- trust
- alignment
- conflict
- dependency
- influence
- perceived reliability

### Hybrid reasoning and control
Use LLMs where perspective and action choice matter, while keeping mutation bounded and deterministic.

### Durable memory
Store and retrieve:
- actor memory
- relationship memory
- scenario-pattern memory

### Decision observability
Each run can produce:
- `trace.jsonl`
- `final_output.json`
- `summary.md`

So you can inspect not only the outcome, but also **how the system reached it**.

---

## Repository structure

```text
.
├── adrs/
├── config/
├── domains/
├── evaluation/
├── graph/
├── llm/
├── memory/
├── nodes/
├── observability/
├── prompts/
├── state_structures/
├── tests/
├── main.py
└── pyproject.toml
```

### Notable packages
- `state_structures/` — domain models and runtime graph state
- `graph/` — LangGraph assembly and routing
- `nodes/` — simulation nodes
- `prompts/` — typed prompt contracts and prompt builders
- `llm/` — Ollama wrappers and structured generation
- `memory/` — Mem0 retrieval, distillation, persistence
- `observability/` — trace models and artifact generation

---

## Quick start

### Prerequisites
- Python 3.11+
- Poetry
- Ollama running locally

### 1. Install dependencies

```bash
poetry install
```

### 2. Check Ollama

Make sure Ollama is running and your models are available.

```bash
ollama list
```

### 3. Create `.env`

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.1:8b
OLLAMA_TEMPERATURE=0.2

USE_LLM_INTERPRETATION=true
USE_LLM_ACTION_SELECTION=true

MEM0_ENABLED=false
MEM0_USE_OLLAMA=true
MEM0_LLM_MODEL=llama3.1:8b
MEM0_EMBEDDER_MODEL=nomic-embed-text
MEM0_TOP_K=5
MEM0_SEARCH_THRESHOLD=0.3
```

### 4. Run the demo

```bash
poetry run python main.py
```

### 5. Inspect artifacts

After the run, inspect:

- `artifacts/trace.jsonl`
- `artifacts/final_output.json`
- `artifacts/summary.md`

---

## Current status

ActorScope-AI is in an **architecture-first implementation phase**.

### Already in place
- typed state model
- LangGraph execution loop
- LLM-backed interpretation and action selection
- deterministic update and stop logic
- decision trace and round summaries
- decision-level ADRs

### Still evolving
- richer memory usage during reasoning
- broader scenario coverage
- stronger test coverage
- future UI and interaction layers
- more advanced evaluation logic

---

## Design principles

The project currently follows these decisions:

- domain-agnostic core
- state-driven execution
- single-writer ownership for mutable state
- deterministic world mutation
- incremental LLM rollout
- dual memory: runtime history vs durable memory
- observability as a first-class concern

---

## Example questions this system can support

- What are the likely standpoints of the actors involved?
- Which actor becomes central as the situation evolves?
- What action is most likely to happen next?
- Which relationships are deteriorating or strengthening?
- Is the scenario moving toward deadlock, escalation, or stabilization?
- What interventions might improve the trajectory?

---

## Roadmap direction

The long-term direction is to support richer multi-actor simulation while preserving:
- explicit state
- controlled execution
- inspectable decisions
- reusable memory
- extensibility for future interfaces

---

## License

Add your preferred license here.
