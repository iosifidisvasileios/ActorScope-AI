from __future__ import annotations

from typing import Any

from config.settings import settings

try:
    from mem0 import Memory
except Exception:  # pragma: no cover
    Memory = None  # type: ignore


class Mem0Client:
    def __init__(self) -> None:
        self.enabled = settings.mem0_enabled and Memory is not None
        self._client = self._build_client() if self.enabled else None

    def _build_client(self) -> Any | None:
        if Memory is None:
            return None

        if not settings.mem0_use_ollama:
            return Memory()

        config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": settings.mem0_llm_model,
                    "temperature": 0.1,
                    "max_tokens": 2000,
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": settings.mem0_embedder_model,
                },
            },
        }

        return Memory.from_config(config)

    @property
    def is_enabled(self) -> bool:
        return self.enabled and self._client is not None

    def add_text(
        self,
        text: str,
        *,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        if not self.is_enabled:
            return None

        try:
            return self._client.add(
                text,
                user_id=user_id,
                metadata=metadata or {},
            )
        except Exception:
            return None

    def search(
        self,
        query: str,
        *,
        user_id: str,
        top_k: int | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        if not self.is_enabled:
            return []

        try:
            response = self._client.search(
                query,
                user_id=user_id,
            )
        except Exception:
            return []

        if isinstance(response, dict):
            results = response.get("results", [])
        elif isinstance(response, list):
            results = response
        else:
            results = []

        normalized: list[dict[str, Any]] = []
        for item in results:
            if not isinstance(item, dict):
                continue

            score = float(item.get("score", 1.0))
            if threshold is not None and score < threshold:
                continue

            normalized.append(item)

        if top_k is not None:
            normalized = normalized[:top_k]

        return normalized