from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TraceEvent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    run_id: str
    scenario_id: str
    round_id: int = Field(ge=0)
    node_name: str
    event_type: str
    timestamp: str
    actor_ids: List[str] = Field(default_factory=list)
    summary: str
    state_diff_summary: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    latency_ms: Optional[float] = None