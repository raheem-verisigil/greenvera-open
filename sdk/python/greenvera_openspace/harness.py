"""Small, framework-neutral runtime instrumentation helpers.

The adapter records metadata only. It deliberately does not capture prompts,
tool arguments, model responses, credentials, or customer payloads.
"""
from __future__ import annotations
import hashlib
import json
import time
import uuid
from typing import Any, Callable
from .client import OpenSpaceClient


def stable_digest(value: Any) -> str:
    """Return a SHA-256 digest without transmitting the original value."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


class OpenSpaceHarness:
    def __init__(self, client: OpenSpaceClient, agent_id: str, version_id: str, trace_id_factory: Callable[[], str] | None = None):
        self.client = client
        self.agent_id = agent_id
        self.version_id = version_id
        self.trace_id_factory = trace_id_factory or (lambda: str(uuid.uuid4()))

    def event(self, event_type: str, severity: str = "info", attributes: dict | None = None,
              payload_for_digest: Any | None = None):
        """Submit a bounded metadata event; optional payload is hashed locally only."""
        digest = stable_digest(payload_for_digest) if payload_for_digest is not None else None
        return self.client.record_event(
            self.agent_id, self.version_id, event_type, severity,
            trace_id=self.trace_id_factory(), attributes=attributes or {}, payload_digest=digest,
        )


    def tool_decision(self, tool_name: str, allowed: bool, reason_code: str = ""):
        """Record a tool permission decision without recording tool arguments."""
        if not tool_name or len(tool_name) > 120:
            raise ValueError("tool_name must contain 1–120 characters")
        if not isinstance(allowed, bool):
            raise TypeError("allowed must be a boolean")
        return self.event(
            "tool.permission.allowed" if allowed else "tool.permission.denied",
            severity="info" if allowed else "high",
            attributes={"tool_name": tool_name, "allowed": allowed, "reason_code": reason_code[:120]},
        )

    def policy_decision(self, policy_id: str, outcome: str, reason_code: str = ""):
        """Record a policy outcome; only bounded identifiers and reason codes are sent."""
        if outcome not in {"allow", "deny", "require_approval", "escalate"}:
            raise ValueError("Unsupported policy outcome")
        return self.event(
            "policy.decision",
            severity="high" if outcome in {"deny", "escalate"} else "info",
            attributes={"policy_id": policy_id[:120], "outcome": outcome, "reason_code": reason_code[:120]},
        )

    def instrument(self, function: Callable, event_type: str = "agent.execution"):
        """Wrap a synchronous function and emit success/failure metadata.

        The wrapped function's inputs and outputs are never sent to GreenVera.
        """
        def wrapped(*args, **kwargs):
            started = time.monotonic()
            trace_id = self.trace_id_factory()
            try:
                result = function(*args, **kwargs)
            except Exception as exc:
                self.client.record_event(
                    self.agent_id, self.version_id, event_type + ".failed", "high",
                    trace_id=trace_id,
                    attributes={"exception_type": type(exc).__name__, "duration_ms": int((time.monotonic()-started)*1000)},
                )
                raise
            self.client.record_event(
                self.agent_id, self.version_id, event_type + ".completed", "info",
                trace_id=trace_id,
                attributes={"duration_ms": int((time.monotonic()-started)*1000)},
            )
            return result
        wrapped.__name__ = getattr(function, "__name__", "openspace_wrapped")
        wrapped.__doc__ = getattr(function, "__doc__", None)
        return wrapped
