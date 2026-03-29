from __future__ import annotations

import json

from prompts.contracts import ActionSelectionInput


def build_action_selection_prompts(
    payload: ActionSelectionInput,
) -> tuple[str, str]:
    system_prompt = """
You are simulating a single actor inside a multi-actor environment.

Your task is to select the single most likely next action for this actor.
You must stay actor-local and scenario-grounded.
Do not mutate state.
Do not describe multiple alternative actions.
Do not invent facts not supported by the provided input unless clearly framed as uncertainty.

Return JSON only.
Do not wrap the JSON in markdown fences.
""".strip()

    input_data = payload.model_dump(mode="json")

    user_prompt = f"""
Produce a JSON object with exactly these keys:

{{
  "actor_id": "string",
  "action_type": "propose | request | challenge | support | resist | escalate | deescalate | withhold | signal | reframe",
  "action_summary": "string",
  "target_actor_ids": ["string", "... up to 3"],
  "rationale_summary": "string",
  "expected_immediate_outcome": "string",
  "assertiveness_level": 0.0
}}

Rules:
- choose exactly one most likely action
- target_actor_ids must be valid actor ids from allowed_targets when allowed_targets is non-empty
- assertiveness_level must be between 0.0 and 1.0
- action_summary should be concrete
- rationale_summary should explain why this action follows from the actor's current interpretation
- expected_immediate_outcome should focus on short-term effects only
- if reactive_mode is true, generate a response rather than a fresh initiative

Input:
{json.dumps(input_data, ensure_ascii=False, indent=2)}
""".strip()

    return system_prompt, user_prompt