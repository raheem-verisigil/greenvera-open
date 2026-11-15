import pytest

from greenvera_openspace.client import OpenSpaceClient, _segment
from greenvera_openspace.gateway import GreenVeraToolGateway


def test_client_requires_issued_key_prefix():
    with pytest.raises(ValueError):
        OpenSpaceClient("not-a-key")


def test_client_rejects_non_https_remote_endpoint():
    with pytest.raises(ValueError, match="HTTPS"):
        OpenSpaceClient("gv_live_demo.ssssssssssssssssssssssssssssssssssssssss", base_url="http://api.example.com")


def test_client_allows_loopback_http_for_local_development():
    client = OpenSpaceClient("gv_live_demo.ssssssssssssssssssssssssssssssssssssssss", base_url="http://127.0.0.1:8000")
    assert client.base_url == "http://127.0.0.1:8000"


@pytest.mark.parametrize("url", [
    "https://user:password@example.com",
    "https://example.com/path?token=secret",
    "https://example.com/path#fragment",
])
def test_client_rejects_credentials_query_or_fragment_in_base_url(url):
    with pytest.raises(ValueError):
        OpenSpaceClient("gv_live_demo.ssssssssssssssssssssssssssssssssssssssss", base_url=url)


def test_client_encodes_resource_identifiers_as_single_path_segments():
    assert _segment("agent/other?x=1") == "agent%2Fother%3Fx%3D1"


def test_client_rejects_empty_or_overlong_resource_identifiers():
    with pytest.raises(ValueError):
        _segment("")
    with pytest.raises(ValueError):
        _segment("x" * 201)


def test_client_rejects_invalid_timeouts_and_response_limits():
    with pytest.raises(ValueError):
        OpenSpaceClient("gv_live_demo.ssssssssssssssssssssssssssssssssssssssss", timeout=0)
    with pytest.raises(ValueError):
        OpenSpaceClient("gv_live_demo.ssssssssssssssssssssssssssssssssssssssss", max_response_bytes=100)


def test_local_allow_receipt_cannot_bypass_signed_gateway_authorisation():
    from greenvera_openspace.client import GreenVeraError
    client = OpenSpaceClient("gv_live_test.secret")
    action = OpenSpaceClient.action_payload("agent-1","version-1","read_ledger","read","ledger/123",
                                            "low","internal","internal","reconcile")
    digest = client.canonical_action_digest(action)
    called = []
    operation = lambda: called.append("executed") or "ok"
    with pytest.raises(GreenVeraError, match="single-use authorisation"):
        client.execute_guarded({"decision":"ALLOW","action_digest":digest}, action, operation)
    assert called == []


def test_action_payload_includes_all_server_defaults_for_stable_digest():
    payload = OpenSpaceClient.action_payload("a", "v", "read_invoice", "read")
    assert payload == {
        "agent_id":"a","version_id":"v","tool_name":"read_invoice","action_name":"read",
        "resource":"","risk":"medium","data_classification":"internal","destination":"internal",
        "purpose":"","trace_id":None,"amount_minor":None,"currency":None,
    }
    client = OpenSpaceClient("gv_live_test.secret")
    assert client.canonical_action_digest(payload) == client.canonical_action_digest(dict(payload))


from greenvera_openspace.gateway import GreenVeraToolGateway


class FakeGatewayClient:
    def __init__(self):
        self.calls = []

    @staticmethod
    def action_payload(**kwargs):
        return kwargs

    def authorize_and_execute(self, action_payload, operation, ttl_seconds=30):
        self.calls.append((action_payload, ttl_seconds))
        return operation()


def test_tool_gateway_wraps_actual_tool_and_uses_trusted_resource_resolver():
    client = FakeGatewayClient()
    gateway = GreenVeraToolGateway(client, "agent-1", "version-1")
    called = []
    def read_invoice(invoice_id):
        called.append(invoice_id)
        return {"invoice_id": invoice_id}
    protected = gateway.protect(
        read_invoice,
        tool_name="read_invoice",
        action_name="read",
        resource_resolver=lambda invoice_id: f"invoices/{invoice_id}",
        risk="low",
    )
    assert protected("INV-1") == {"invoice_id":"INV-1"}
    assert called == ["INV-1"]
    assert client.calls[0][0]["resource"] == "invoices/INV-1"


def test_tool_gateway_rejects_missing_or_ambiguous_resource_scope():
    client = FakeGatewayClient()
    gateway = GreenVeraToolGateway(client, "agent-1", "version-1")
    def tool():
        return "executed"
    with pytest.raises(ValueError):
        gateway.protect(tool, tool_name="tool", action_name="run")
    with pytest.raises(ValueError):
        gateway.protect(tool, tool_name="tool", action_name="run",
                        resource="fixed", resource_resolver=lambda: "dynamic")
