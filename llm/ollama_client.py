from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from config.settings import settings


class OllamaChatClient:
    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
        temperature: float | None = None,
    ) -> None:
        self.model_name = model_name or settings.ollama_chat_model
        self.base_url = base_url or settings.ollama_base_url
        self.temperature = settings.ollama_temperature if temperature is None else temperature

        self._model = ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
        )

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        response = self._model.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        return str(response.content)