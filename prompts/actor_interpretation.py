from __future__ import annotations

import json

from prompts.contracts import ActorInterpretationInput


def build_actor_interpretation_prompts(
    payload: ActorInterpretationInput,
) -> tuple[str, str]:
    system_prompt = """
You are simulating a single actor inside a multi-actor environment.

Your task is to produce the actor's current interpretation of the situation.
You must stay actor-local and scenario-grounded.
Do not act like an omniscient narrator.
Do not choose the actor's final action.
Do not invent facts not supported by the provided input unless clearly implied as uncertainty.

Return JSON only.
Do not wrap the JSON in markdown fences.
""".strip()

    input_data = payload.model_dump(mode="json")

    user_prompt = f"""
Produce a JSON object with exactly these keys:

{{
  "actor_id": "string",
  "current_objectives": ["string", "... up to 5"],
  "viewpoint_summary": "string",
  "perceived_risks": ["string", "... up to 5"],
  "strategic_posture": "cooperative | guarded | defensive | assertive | opportunistic | escalatory",
  "willingness_to_cooperate": 0.0,
  "confidence": 0.0,
  "rationale_summary": "string"
}}

Rules:
- willingness_to_cooperate must be between 0.0 and 1.0
- confidence must be between 0.0 and 1.0
- current_objectives should be concise
- perceived_risks should be concise
- viewpoint_summary should reflect the actor's perspective only
- rationale_summary should briefly explain why this interpretation makes sense

Input:
{json.dumps(input_data, ensure_ascii=False, indent=2)}
""".strip()

    return system_prompt, user_prompt