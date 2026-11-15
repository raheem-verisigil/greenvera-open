# OpenSpace Python SDK quickstart

The SDK is designed to run inside your own application, CI runner or agent harness. It sends version metadata, test outcomes and bounded operational events to GreenVera. It does not send raw prompts, tool arguments or model responses through the supplied helpers.

## Install from a source checkout

The SDK is not yet published to the public Python Package Index. From a checkout of this repository:

```bash
python -m venv .venv
. .venv/bin/activate
pip install ./sdk/python
```

For the optional LangGraph callback adapter:

```bash
pip install "./sdk/python[langgraph]"
```

## Configure credentials

Obtain a sandbox API key through GreenVera's controlled onboarding process. Keep it in your server-side secret manager or environment:

```bash
export GREENVERA_API_KEY="gv_live_..."
export GREENVERA_API_URL="https://greenvera-api-production.up.railway.app"
```

Never commit the key, place it in browser code, or include it in issue reports.

## Register an agent and version

```python
import os
from greenvera_openspace import OpenSpaceClient, EvaluationCase, TrustLabRunner

client = OpenSpaceClient(
    api_key=os.environ["GREENVERA_API_KEY"],
    base_url=os.getenv("GREENVERA_API_URL", "https://greenvera-api-production.up.railway.app"),
)

agent = client.register_agent(
    "Supplier support agent",
    environment="development",
    description="Answers supplier evidence questions; cannot approve compliance claims.",
)
version = client.register_version(
    agent["id"],
    "0.1.0",
    model_provider="your-provider",
    model_name="your-model",
    harness="your-harness",
    tools=["supplier_record_read"],
    permissions={"supplier_record_write": False},
    configuration=b"hash only; do not upload private configuration",
)
```

## Run customer-side tests

```python
runner = TrustLabRunner(client, agent["id"], version["id"], "starter-safety-suite")

result = runner.run([
    EvaluationCase(
        "supplier-data-read-allowed",
        lambda: True,  # Replace with a real assertion against your harness.
        category="permissions",
    ),
    EvaluationCase(
        "unauthorised-claim-approval-denied",
        lambda: True,  # Replace with a real assertion against your harness.
        category="permissions",
        critical=True,
    ),
])
print(result)
```

The examples above use placeholders. A test only has value when its check actually exercises your agent, tools and policy enforcement. A submitted result is evidence of what your runner reports; GreenVera does not independently reproduce the test.

## Record a metadata-only runtime event

```python
from greenvera_openspace import OpenSpaceHarness

instrumentation = OpenSpaceHarness(client, agent["id"], version["id"])
instrumentation.tool_decision("supplier_record_write", allowed=False, reason_code="read_only_policy")
```

## Release governance

A passed evaluation makes a version eligible for a human approval workflow; it does not deploy the application. Human release approval and rejection require a user JWT carrying the `org_admin` or `release_approver` role. API integration keys are not human approvers.

## Important boundaries

- Use synthetic or non-sensitive data during the controlled pilot.
- Customer-side test design and execution remain your responsibility.
- Metadata telemetry is not full observability, alerting or anomaly detection.
- Assurance maturity labels are not certifications or guarantees.
- GreenVera does not deploy your agent or make your legal/compliance decisions.
