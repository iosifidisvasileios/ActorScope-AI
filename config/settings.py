from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.constants import (
    DEFAULT_CONFLICT_PATTERN_REPEAT_LIMIT,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_ESCALATION_THRESHOLD,
    DEFAULT_FINAL_OUTPUT_FILE_NAME,
    DEFAULT_LOW_CHANGE_DELTA_THRESHOLD,
    DEFAULT_LOW_CHANGE_ROUND_LIMIT,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_PRIMARY_MODEL,
    DEFAULT_RESOLUTION_THRESHOLD,
    DEFAULT_SUMMARY_FILE_NAME,
    DEFAULT_TRACE_DIR,
    DEFAULT_TRACE_FILE_NAME,
)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ActorScope-AI"
    environment: str = "development"
    debug: bool = True

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = DEFAULT_PRIMARY_MODEL
    ollama_embedding_model: str = DEFAULT_EMBEDDING_MODEL
    ollama_temperature: float = Field(default=0.2, ge=0.0, le=1.0)

    mem0_enabled: bool = False
    mem0_use_ollama: bool = True

    mem0_user_prefix: str = "actor"
    mem0_relationship_prefix: str = "relationship"
    mem0_pattern_user_id: str = "scenario_patterns"

    mem0_top_k: int = Field(default=5, ge=1, le=20)
    mem0_search_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

    mem0_llm_model: str = "hf.co/unsloth/Llama-3.2-3B-Instruct-GGUF:BF16"
    mem0_embedder_model: str = "nomic-embed-text"



    use_llm_interpretation: bool = True
    use_llm_action_selection: bool = True

    mem0_api_key: str | None = None
    mem0_org_id: str | None = None
    mem0_project_id: str | None = None

    max_rounds: int = Field(default=DEFAULT_MAX_ROUNDS, ge=1)
    resolution_threshold: float = Field(default=DEFAULT_RESOLUTION_THRESHOLD, ge=0.0, le=1.0)
    escalation_threshold: float = Field(default=DEFAULT_ESCALATION_THRESHOLD, ge=0.0, le=1.0)
    low_change_delta_threshold: float = Field(default=DEFAULT_LOW_CHANGE_DELTA_THRESHOLD, ge=0.0, le=1.0)
    low_change_round_limit: int = Field(default=DEFAULT_LOW_CHANGE_ROUND_LIMIT, ge=1)
    conflict_pattern_repeat_limit: int = Field(default=DEFAULT_CONFLICT_PATTERN_REPEAT_LIMIT, ge=1)

    artifacts_dir: str = DEFAULT_TRACE_DIR
    trace_file_name: str = DEFAULT_TRACE_FILE_NAME
    final_output_file_name: str = DEFAULT_FINAL_OUTPUT_FILE_NAME
    summary_file_name: str = DEFAULT_SUMMARY_FILE_NAME

settings = AppSettings()