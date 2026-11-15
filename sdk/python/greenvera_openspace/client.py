"""Server-side GreenVera OpenSpace API client (standard library only).

Security properties:
- Requires an explicitly issued API key.
- HTTPS is mandatory except for loopback development hosts.
- Credentials are never put in URLs.
- Resource identifiers are URL-escaped.
- Response bodies are bounded and must be JSON.
- No automatic retries: callers decide whether a failed write is safe to repeat.
Never place API keys in browser JavaScript, notebooks shared publicly, or source control.
"""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class GreenVeraError(RuntimeError):
    """An HTTP or transport error returned by the GreenVera API."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"GreenVera API {status}: {detail}")


def _validate_base_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise ValueError("base_url must be an absolute HTTPS URL")
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not loopback:
        raise ValueError("HTTPS is required except for loopback development")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("base_url must not contain credentials, query, or fragment")
    return value.rstrip("/")


def _segment(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 200:
        raise ValueError("Resource identifiers must contain 1–200 characters")
    return urllib.parse.quote(value, safe="")


class OpenSpaceClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://greenvera-api-production.up.railway.app",
        timeout: float = 20,
        max_response_bytes: int = 2 * 1024 * 1024,
    ):
        if not isinstance(api_key, str) or not api_key.startswith("gv_live_") or any(c in api_key for c in "\\r\\n"):
            raise ValueError("An issued GreenVera API key is required")
        if timeout <= 0 or timeout > 120:
            raise ValueError("timeout must be greater than 0 and at most 120 seconds")
        if max_response_bytes < 1024 or max_response_bytes > 10 * 1024 * 1024:
            raise ValueError("max_response_bytes must be between 1 KiB and 10 MiB")
        self.api_key = api_key
        self.base_url = _validate_base_url(base_url)
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None):
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("API path must be an absolute path on the configured host")
        data = None if payload is None else json.dumps(payload, separators=(",", ":"), allow_nan=False).encode()
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "greenvera-openspace-python/0.1.1",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" not in content_type.lower():
                    raise GreenVeraError(response.status, "API returned a non-JSON response")
                body = response.read(self.max_response_bytes + 1)
                if len(body) > self.max_response_bytes:
                    raise GreenVeraError(response.status, "API response exceeded configured size limit")
                if not body:
                    return {}
                try:
                    return json.loads(body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise GreenVeraError(response.status, "API returned invalid JSON") from exc
        except urllib.error.HTTPError as exc:
            body = exc.read(min(self.max_response_bytes, 8192)).decode(errors="replace")
            raise GreenVeraError(exc.code, body) from exc
        except urllib.error.URLError as exc:
            raise GreenVeraError(0, str(exc.reason)) from exc

    def capabilities(self):
        return self._request("GET", "/v1/openspace/capabilities")

    def list_agents(self):
        return self._request("GET", "/v1/agents")

    def register_agent(self, name: str, environment: str = "development", description: str = "", tags: list[str] | None = None):
        return self._request("POST", "/v1/agents", {"name": name, "environment": environment, "description": description, "tags": tags or []})

    def register_version(self, agent_id: str, version: str, model_provider: str = "custom", model_name: str = "unspecified",
                         harness: str = "custom", tools: list[str] | None = None, permissions: dict | None = None,
                         configuration: bytes | None = None, change_summary: str = ""):
        digest = hashlib.sha256(configuration).hexdigest() if configuration is not None else None
        return self._request("POST", f"/v1/agents/{_segment(agent_id)}/versions", {
            "version": version, "model_provider": model_provider, "model_name": model_name,
            "harness": harness, "tools": tools or [], "permissions": permissions or {},
            "configuration_digest": digest, "change_summary": change_summary,
        })

    def record_evaluation(self, agent_id: str, version_id: str, suite: str, results: list[dict], dimensions: dict | None = None):
        safe_dimensions = dict(dimensions or {})
        safe_dimensions["version_id"] = version_id
        return self._request("POST", f"/v1/agents/{_segment(agent_id)}/evaluations", {
            "suite": suite, "results": results, "dimensions": safe_dimensions,
        })

    def record_event(self, agent_id: str, version_id: str, event_type: str, severity: str = "info",
                     trace_id: str | None = None, attributes: dict | None = None, payload_digest: str | None = None):
        return self._request("POST", f"/v1/agents/{_segment(agent_id)}/telemetry", {
            "version_id": version_id, "event_type": event_type, "severity": severity,
            "trace_id": trace_id, "attributes": attributes or {}, "payload_digest": payload_digest,
        })

    def request_release(self, agent_id: str, version_id: str, evaluation_id: str | None = None, reason: str = ""):
        return self._request("POST", f"/v1/agents/{_segment(agent_id)}/release-decisions", {
            "version_id": version_id, "evaluation_id": evaluation_id, "action": "request_release", "reason": reason,
        })

    def approve_release(self, agent_id: str, version_id: str, evaluation_id: str, reason: str):
        return self._request("POST", f"/v1/agents/{_segment(agent_id)}/release-decisions", {
            "version_id": version_id, "evaluation_id": evaluation_id, "action": "approve", "reason": reason,
        })

    def reject_release(self, agent_id: str, version_id: str, evaluation_id: str | None, reason: str):
        return self._request("POST", f"/v1/agents/{_segment(agent_id)}/release-decisions", {
            "version_id": version_id, "evaluation_id": evaluation_id, "action": "reject", "reason": reason,
        })

    def evidence(self, agent_id: str, version_id: str):
        return self._request("GET", f"/v1/agents/{_segment(agent_id)}/versions/{_segment(version_id)}/evidence")

    def monitoring(self, agent_id: str):
        return self._request("GET", f"/v1/agents/{_segment(agent_id)}/monitoring")

    def assurance(self, agent_id: str):
        return self._request("GET", f"/v1/agent-assurance/{_segment(agent_id)}")
