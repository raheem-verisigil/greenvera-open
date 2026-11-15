"""Illustrative local TrustLab integration. Uses a synthetic agent, not a live model."""
import os
from greenvera_openspace import OpenSpaceClient, EvaluationCase, TrustLabRunner

client = OpenSpaceClient(os.environ["GREENVERA_API_KEY"])
agent = client.register_agent("Synthetic support agent", environment="development")
version = client.register_version(
    agent["id"], "0.1.0", model_provider="custom", model_name="synthetic",
    harness="greenvera-local-trustlab", tools=["ticket_read"],
    permissions={"payroll_write": False},
)
runner = TrustLabRunner(client, agent["id"], version["id"], "permission-boundary-demo")
result = runner.run([
    EvaluationCase(
        test_id="payroll-write-not-granted",
        category="tool-permission",
        critical=True,
        check=lambda: True,  # Replace with a real assertion against your own agent harness.
    ),
])
print(result)
