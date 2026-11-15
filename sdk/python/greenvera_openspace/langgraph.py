"""Optional LangGraph/LangChain callback adapter for GreenVera OpenSpace.

Install with: pip install 'greenvera-openspace[langgraph]'
Only bounded execution metadata is emitted. Prompts, tool inputs, outputs,
messages and exception text are deliberately never sent to GreenVera.
"""
from __future__ import annotations

import time
import uuid
from typing import Any

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:  # Keep the core SDK dependency-free.
    class BaseCallbackHandler:  # type: ignore[no-redef]
        pass


class OpenSpaceLangGraphHandler(BaseCallbackHandler):
    """Callback handler compatible with LangGraph's LangChain callback system.

    Telemetry is best-effort by default: an observability outage should not
    silently change the customer's agent behaviour. Set fail_open=False when
    the customer explicitly wants telemetry delivery to be fail-closed.
    """

    def __init__(self, client: Any, agent_id: str, version_id: str, *, fail_open: bool = True):
        self.client = client
        self.agent_id = agent_id
        self.version_id = version_id
        self.fail_open = fail_open
        self._started: dict[str, float] = {}

    def _emit(self, event_type: str, *, severity: str = "info", run_id: Any = None,
              parent_run_id: Any = None, name: str | None = None, error_type: str | None = None, duration_ms: int | None = None):
        attrs: dict[str, str | int | float | bool | None] = {}
        if name:
            attrs["component"] = str(name)[:120]
        if run_id is not None:
            attrs["run_id"] = str(run_id)[:128]
        if parent_run_id is not None:
            attrs["parent_run_id"] = str(parent_run_id)[:128]
        if error_type:
            attrs["error_type"] = error_type[:120]
        if duration_ms is not None:
            attrs["duration_ms"] = max(0, min(int(duration_ms), 2147483647))
        try:
            return self.client.record_event(
                self.agent_id, self.version_id, event_type, severity,
                trace_id=str(run_id or uuid.uuid4()), attributes=attrs,
            )
        except Exception:
            if not self.fail_open:
                raise
            return None

    def _start(self, run_id: Any):
        self._started[str(run_id)] = time.monotonic()

    def _duration(self, run_id: Any) -> int | None:
        started = self._started.pop(str(run_id), None)
        return int((time.monotonic() - started) * 1000) if started is not None else None

    def on_chain_start(self, serialized: dict, inputs: dict, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        self._start(run_id)
        self._emit("langgraph.chain.started", run_id=run_id, parent_run_id=parent_run_id,
                   name=(serialized or {}).get("name", "chain"))

    def on_chain_end(self, outputs: dict, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        duration = self._duration(run_id)
        self._emit("langgraph.chain.completed", run_id=run_id, parent_run_id=parent_run_id,
                   duration_ms=duration)

    def on_chain_error(self, error: BaseException, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        self._duration(run_id)
        self._emit("langgraph.chain.failed", severity="high", run_id=run_id,
                   parent_run_id=parent_run_id, error_type=type(error).__name__)

    def on_llm_start(self, serialized: dict, prompts: list[str], *, run_id: Any, parent_run_id: Any = None, **kwargs):
        self._start(run_id)
        self._emit("langgraph.model.started", run_id=run_id, parent_run_id=parent_run_id,
                   name=(serialized or {}).get("name", "model"))

    def on_llm_end(self, response: Any, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        duration = self._duration(run_id)
        self._emit("langgraph.model.completed", run_id=run_id, parent_run_id=parent_run_id,
                   duration_ms=duration)

    def on_llm_error(self, error: BaseException, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        self._duration(run_id)
        self._emit("langgraph.model.failed", severity="high", run_id=run_id,
                   parent_run_id=parent_run_id, error_type=type(error).__name__)

    def on_tool_start(self, serialized: dict, input_str: str, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        self._start(run_id)
        self._emit("langgraph.tool.started", run_id=run_id, parent_run_id=parent_run_id,
                   name=(serialized or {}).get("name", "tool"))

    def on_tool_end(self, output: str, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        duration = self._duration(run_id)
        self._emit("langgraph.tool.completed", run_id=run_id, parent_run_id=parent_run_id,
                   duration_ms=duration)

    def on_tool_error(self, error: BaseException, *, run_id: Any, parent_run_id: Any = None, **kwargs):
        self._duration(run_id)
        self._emit("langgraph.tool.failed", severity="high", run_id=run_id,
                   parent_run_id=parent_run_id, error_type=type(error).__name__)
