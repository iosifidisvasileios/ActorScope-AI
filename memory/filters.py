from __future__ import annotations

from config.settings import settings


def actor_memory_user_id(actor_id: str) -> str:
    return f"{settings.mem0_user_prefix}:{actor_id}"


def relationship_memory_user_id(relationship_key: str) -> str:
    return f"{settings.mem0_relationship_prefix}:{relationship_key}"


def scenario_pattern_user_id() -> str:
    return settings.mem0_pattern_user_id