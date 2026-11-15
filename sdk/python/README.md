# GreenVera OpenSpace Python SDK

A lightweight, model-agnostic client and customer-side evaluation harness for recording AI agent trust evidence in GreenVera.

> **Status:** preview release. API access is currently provisioned through controlled onboarding. This SDK does not certify agents, execute private agents, or deploy workloads.

## Install

The package is prepared for PyPI distribution. Until the first signed release is published, install from a source checkout:

```bash
python -m pip install ./sdk/python
```

Optional LangGraph adapter dependency:

```bash
python -m pip install "./sdk/python[langgraph]"
```

## Quick start

```python
import os
from greenvera_openspace import OpenSpaceClient

client = OpenSpaceClient(
    api_key=os.environ["GREENVERA_API_KEY"],
    base_url=os.getenv(
        "GREENVERA_API_URL",
        "https://greenvera-api-production.up.railway.app",
    ),
)
print(client.capabilities())
```

Use GreenVeraToolGateway to wrap existing Python callables at the actual tool boundary. See [the integration guide](../../docs/INTELLIGENCE_CONTROL_PLANE_INTEGRATION.md) for custodian provisioning, production release gating, signed one-time action authorisations and emergency controls. For supplier evidence reuse, see [the Supplier Vault SDK guide](../../docs/SUPPLIER_VAULT_SDK.md).

## Data handling

The client sends the fields explicitly passed to its methods. Do not send prompts, model responses, personal data, credentials or raw tool arguments. Use metadata and digests unless you have an approved data-processing agreement and explicit configuration for other data.

## Security

- Keep API keys in server-side secret storage.
- Use HTTPS for remote endpoints.
- Rotate and revoke credentials through the GreenVera onboarding team until self-service key management is released.
- Pin dependency versions and review the SDK before production use.
- A policy ALLOW receipt alone is not an execution token. Use authorize_and_execute() at the actual protected tool boundary.
- The action signing secret is server-side only and must be stored in a managed secret store.
- Report vulnerabilities privately to security@greenvera.earth.

## License

Apache-2.0. The SDK license does not grant rights to GreenVera trademarks or imply certification or endorsement.
