from __future__ import annotations

from config.settings import settings
from memory.filters import (
    actor_memory_user_id,
    relationship_memory_user_id,
    scenario_pattern_user_id,
)
from memory.mem0_client import Mem0Client


def retrieve_actor_memories(
    client: Mem0Client,
    actor_ids: list[str],
    scenario_title: str,
) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}

    for actor_id in actor_ids:
        memories = client.search(
            query=scenario_title,
            user_id=actor_memory_user_id(actor_id),
            top_k=settings.mem0_top_k,
            threshold=settings.mem0_search_threshold,
        )
        results[actor_id] = [
            item.get("memory", "")
            for item in memories
            if item.get("memory")
        ]

    return results


def retrieve_relationship_memories(
    client: Mem0Client,
    relationship_keys: list[str],
    scenario_title: str,
) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}

    for relationship_key in relationship_keys:
        memories = client.search(
            query=scenario_title,
            user_id=relationship_memory_user_id(relationship_key),
            top_k=settings.mem0_top_k,
            threshold=settings.mem0_search_threshold,
        )
        results[relationship_key] = [
            item.get("memory", "")
            for item in memories
            if item.get("memory")
        ]

    return results


def retrieve_scenario_pattern_memories(
    client: Mem0Client,
    environment_type: str,
    scenario_title: str,
) -> list[str]:
    query = f"{environment_type}: {scenario_title}"
    memories = client.search(
        query=query,
        user_id=scenario_pattern_user_id(),
        top_k=settings.mem0_top_k,
        threshold=settings.mem0_search_threshold,
    )
    return [
        item.get("memory", "")
        for item in memories
        if item.get("memory")
    ]