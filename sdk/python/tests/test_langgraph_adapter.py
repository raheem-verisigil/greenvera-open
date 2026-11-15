from greenvera_openspace.langgraph import OpenSpaceLangGraphHandler


class FakeClient:
    def __init__(self):
        self.events = []
        self.fail = False

    def record_event(self, *args, **kwargs):
        if self.fail:
            raise RuntimeError("telemetry unavailable")
        self.events.append((args, kwargs))
        return {"accepted": True}


def test_langgraph_adapter_records_metadata_without_payloads():
    client = FakeClient()
    handler = OpenSpaceLangGraphHandler(client, "agent-1", "version-1")
    handler.on_tool_start({"name": "payroll_lookup"}, "sensitive payroll arguments", run_id="run-1")
    handler.on_tool_end("sensitive payroll output", run_id="run-1")
    assert len(client.events) == 2
    rendered = repr(client.events)
    assert "sensitive payroll arguments" not in rendered
    assert "sensitive payroll output" not in rendered
    assert all(item[1]["trace_id"] == "run-1" for item in client.events)


def test_langgraph_adapter_fails_open_by_default():
    client = FakeClient()
    client.fail = True
    handler = OpenSpaceLangGraphHandler(client, "agent-1", "version-1")
    assert handler.on_llm_start({"name": "model"}, ["private prompt"], run_id="run-2") is None


def test_langgraph_adapter_can_be_configured_fail_closed():
    client = FakeClient()
    client.fail = True
    handler = OpenSpaceLangGraphHandler(client, "agent-1", "version-1", fail_open=False)
    try:
        handler.on_llm_start({"name": "model"}, [], run_id="run-3")
    except RuntimeError:
        pass
    else:
        raise AssertionError("fail_open=False must propagate telemetry failure")
