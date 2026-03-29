from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import wraps
from time import perf_counter
from typing import Any, Callable

from observability.trace_models import TraceEvent


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_run_id(state: dict, result: dict) -> str:
    return (
        result.get("run_control", {}).get("run_id")
        or state.get("run_control", {}).get("run_id")
        or "unknown_run"
    )


def _safe_scenario_id(state: dict, result: dict) -> str:
    return (
        result.get("scenario", {}).get("scenario_id")
        or state.get("scenario", {}).get("scenario_id")
        or state.get("raw_input", {}).get("scenario", {}).get("scenario_id")
        or "unknown_scenario"
    )


def _safe_round_id(state: dict, result: dict) -> int:
    return int(
        result.get("run_control", {}).get("current_round")
        or state.get("run_control", {}).get("current_round")
        or 0
    )


def _default_summary(node_name: str, result: dict) -> str:
    updated_keys = sorted(result.keys())
    return f"{node_name} completed; updated keys={updated_keys}"


def _default_actor_ids(state: dict, result: dict) -> list[str]:
    round_context = result.get("round_context") or state.get("round_context") or {}
    actor_ids: list[str] = []

    primary = round_context.get("selected_primary_actor")
    reactive = round_context.get("selected_reactive_actor")

    if primary:
        actor_ids.append(primary)
    if reactive:
        actor_ids.append(reactive)

    if not actor_ids:
        action_proposals = round_context.get("action_proposals", {})
        actor_ids.extend(list(action_proposals.keys()))

    return actor_ids


def _default_state_diff_summary(result: dict) -> dict[str, Any]:
    summary: dict[str, Any] = {"updated_keys": sorted(result.keys())}

    if "events" in result:
        summary["event_count"] = len(result["events"])
    if "trace_events" in result:
        summary["trace_event_count"] = len(result["trace_events"])

    return summary


def traced_node(
    node_name: str,
    event_type: str,
    summary_fn: Callable[[dict, dict], str] | None = None,
    actor_ids_fn: Callable[[dict, dict], list[str]] | None = None,
    state_diff_fn: Callable[[dict, dict], dict[str, Any]] | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: dict) -> dict:
            start = perf_counter()
            result = func(state)
            latency_ms = round((perf_counter() - start) * 1000.0, 3)

            trace_events = deepcopy(state.get("trace_events", []))

            summary = summary_fn(state, result) if summary_fn else _default_summary(node_name, result)
            actor_ids = actor_ids_fn(state, result) if actor_ids_fn else _default_actor_ids(state, result)
            state_diff_summary = state_diff_fn(state, result) if state_diff_fn else _default_state_diff_summary(result)

            trace_event = TraceEvent(
                run_id=_safe_run_id(state, result),
                scenario_id=_safe_scenario_id(state, result),
                round_id=_safe_round_id(state, result),
                node_name=node_name,
                event_type=event_type,
                timestamp=_utc_now_iso(),
                actor_ids=actor_ids,
                summary=summary,
                state_diff_summary=state_diff_summary,
                success=True,
                error_message=None,
                latency_ms=latency_ms,
            )

            trace_events.append(trace_event.model_dump())
            result["trace_events"] = trace_events
            return result

        return wrapper

    return decorator