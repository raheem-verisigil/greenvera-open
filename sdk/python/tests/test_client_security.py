import pytest

from greenvera_openspace.client import OpenSpaceClient, _segment


def test_client_requires_issued_key_prefix():
    with pytest.raises(ValueError):
        OpenSpaceClient("not-a-key")


def test_client_rejects_non_https_remote_endpoint():
    with pytest.raises(ValueError, match="HTTPS"):
        OpenSpaceClient("gv_live_demo.secret", base_url="http://api.example.com")


def test_client_allows_loopback_http_for_local_development():
    client = OpenSpaceClient("gv_live_demo.secret", base_url="http://127.0.0.1:8000")
    assert client.base_url == "http://127.0.0.1:8000"


@pytest.mark.parametrize("url", [
    "https://user:password@example.com",
    "https://example.com/path?token=secret",
    "https://example.com/path#fragment",
])
def test_client_rejects_credentials_query_or_fragment_in_base_url(url):
    with pytest.raises(ValueError):
        OpenSpaceClient("gv_live_demo.secret", base_url=url)


def test_client_encodes_resource_identifiers_as_single_path_segments():
    assert _segment("agent/other?x=1") == "agent%2Fother%3Fx%3D1"


def test_client_rejects_empty_or_overlong_resource_identifiers():
    with pytest.raises(ValueError):
        _segment("")
    with pytest.raises(ValueError):
        _segment("x" * 201)


def test_client_rejects_invalid_timeouts_and_response_limits():
    with pytest.raises(ValueError):
        OpenSpaceClient("gv_live_demo.secret", timeout=0)
    with pytest.raises(ValueError):
        OpenSpaceClient("gv_live_demo.secret", max_response_bytes=100)
