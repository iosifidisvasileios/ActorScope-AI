from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from llm.ollama_client import OllamaChatClient

T = TypeVar("T", bound=BaseModel)


class StructuredGenerationError(Exception):
    pass


def _extract_json_block(text: str) -> str:
    stripped = text.strip()

    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced_match:
        return fenced_match.group(1)

    generic_fenced_match = re.search(r"```\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if generic_fenced_match:
        return generic_fenced_match.group(1)

    first = stripped.find("{")
    last = stripped.rfind("}")
    if first != -1 and last != -1 and last > first:
        return stripped[first:last + 1]

    raise StructuredGenerationError("No JSON object found in model response.")


def generate_structured_output(
    client: OllamaChatClient,
    system_prompt: str,
    user_prompt: str,
    output_model: type[T],
) -> T:
    raw_text = client.invoke(system_prompt=system_prompt, user_prompt=user_prompt)

    try:
        json_text = _extract_json_block(raw_text)
        data = json.loads(json_text)
        return output_model.model_validate(data)
    except (json.JSONDecodeError, ValidationError, StructuredGenerationError) as exc:
        raise StructuredGenerationError(
            f"Failed to parse structured output for {output_model.__name__}: {exc}"
        ) from exc