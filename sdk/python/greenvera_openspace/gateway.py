"""Framework-neutral Python Policy Enforcement Point for GreenVera.

Wrap the actual callable that reaches a protected external tool. Never expose
an alternate unguarded path to the underlying callable.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from .client import OpenSpaceClient


class GreenVeraToolGateway:
    """Creates fail-closed wrappers for existing Python agent tools."""

    def __init__(self, client: OpenSpaceClient, agent_id: str, version_id: str):
        self.client = client
        self.agent_id = agent_id
        self.version_id = version_id

    def protect(
        self,
        tool: Callable[..., Any],
        *,
        tool_name: str,
        action_name: str,
        resource: str | None = None,
        resource_resolver: Callable[..., str] | None = None,
        risk: str = "medium",
        data_classification: str = "internal",
        destination: str = "internal",
        purpose: str = "",
        amount_resolver: Callable[..., int | None] | None = None,
        currency_resolver: Callable[..., str | None] | None = None,
        trace_id_resolver: Callable[..., str | None] | None = None,
        ttl_seconds: int = 30,
    ) -> Callable[..., Any]:
        """Wrap a tool; resource must be fixed or derived by trusted application code."""
        if not callable(tool):
            raise TypeError("tool must be callable")
        if not tool_name or not action_name:
            raise ValueError("tool_name and action_name are required")
        if (resource is None) == (resource_resolver is None):
            raise ValueError("Provide exactly one of resource or resource_resolver")
        if ttl_seconds < 1 or ttl_seconds > 60:
            raise ValueError("ttl_seconds must be between 1 and 60")

        @wraps(tool)
        def guarded(*args, **kwargs):
            resolved_resource = resource_resolver(*args, **kwargs) if resource_resolver else resource
            if not isinstance(resolved_resource, str) or not resolved_resource:
                raise ValueError("Trusted resource resolver must return a non-empty string")
            amount = amount_resolver(*args, **kwargs) if amount_resolver else None
            currency = currency_resolver(*args, **kwargs) if currency_resolver else None
            trace_id = trace_id_resolver(*args, **kwargs) if trace_id_resolver else None
            if (amount is None) != (currency is None):
                raise ValueError("amount_resolver and currency_resolver must both return values or both return None")
            payload = self.client.action_payload(
                agent_id=self.agent_id,
                version_id=self.version_id,
                tool_name=tool_name,
                action_name=action_name,
                resource=resolved_resource,
                risk=risk,
                data_classification=data_classification,
                destination=destination,
                purpose=purpose,
                trace_id=trace_id,
                amount_minor=amount,
                currency=currency,
            )
            return self.client.authorize_and_execute(
                action_payload=payload,
                operation=lambda: tool(*args, **kwargs),
                ttl_seconds=ttl_seconds,
            )

        return guarded
