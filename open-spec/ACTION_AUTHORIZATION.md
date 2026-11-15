# Signed Action Authorisation and Tool Gateway

GreenVera's draft action control protocol separates the **Policy Decision Point (PDP)** from the **Policy Enforcement Point (PEP)**. The PDP evaluates an action. The PEP is the actual runtime/tool boundary that prevents the model or agent from calling a protected tool directly.

## Required execution sequence

1. The integration constructs a canonical action request using trusted context: organisation, registered agent and version, tool, action, resource, risk, data classification, destination and (where applicable) transaction amount/currency.
2. The integration calls `POST /v1/control/actions/evaluate`.
3. `BLOCK` means do not call the tool. `REQUIRE_HUMAN_APPROVAL` means pause and route the exact decision to an authenticated human workflow. `ALLOW` is a policy decision, not by itself permission to execute.
4. For an `ALLOW`, call `POST /v1/control/decisions/{decision_id}/authorization` to mint a short-lived signed authorisation (1–60 seconds; default 30).
5. The PEP sends the token and the exact canonical action payload to `POST /v1/control/authorizations/consume`. GreenVera verifies issuer, audience, signature, expiry, organisation, policy hash, custodian grant, control epoch, action scope and digest. The decision is consumed once.
6. Only after successful consumption may the same PEP invoke the exact protected tool operation. If the tool call fails after consumption, do not replay the token; evaluate again and create a new decision.
7. Record the execution outcome and a correlation/trace identifier. Do not send prompts or raw confidential inputs by default.

## Security semantics

- Tokens are HMAC-SHA256 signed server-side, with issuer and audience validation. The signing secret must be generated and stored in a managed secret store; never commit it or expose it to browser code.
- Tokens are bound to a decision, agent version, policy version/hash, custodian grant, control epoch, tool, action, resource and canonical action digest.
- Tokens are single-use. Concurrent/replayed consumption is rejected by a database row lock and consumed marker.
- Policy changes, custodian replacement/revocation, expiry and emergency suspension invalidate pending authorisations.
- Production agents require the latest passing evaluation and a separate authenticated human release approval for that exact version.
- Emergency suspend increments the control epoch. Resume increments it again; old tokens and decisions are not restored.
- Fail closed on timeout, invalid token, mismatched payload, unknown identity, missing policy, unavailable control service or any non-ALLOW decision.
- The PEP must prevent alternate direct paths to the underlying tool. A wrapper that is optional or can be bypassed is not an enforcement boundary.

## API endpoints

- `PUT /v1/agents/{agent_id}/control-policy`
- `POST /v1/agents/{agent_id}/custodians`
- `POST /v1/control/actions/evaluate`
- `POST /v1/control/decisions/{decision_id}/approve`
- `POST /v1/control/decisions/{decision_id}/authorization`
- `POST /v1/control/authorizations/consume`
- `GET /v1/agents/{agent_id}/control-state`
- `POST /v1/agents/{agent_id}/suspend`
- `POST /v1/agents/{agent_id}/resume`

## Python SDK example

```python
from greenvera_openspace import OpenSpaceClient

client = OpenSpaceClient(api_key=GREENVERA_API_KEY)
action = client.action_payload(
    agent_id=AGENT_ID,
    version_id=VERSION_ID,
    tool_name="read_invoice",
    action_name="read",
    resource="invoices/INV-100",
    risk="low",
    data_classification="internal",
)

# The callable must be the exact protected operation behind this PEP.
result = client.authorize_and_execute(
    action_payload=action,
    operation=lambda: invoice_service.read("INV-100"),
)
```

The helper evaluates, requests a short-lived authorisation, consumes it once, then calls the supplied operation. It does not make an unwrapped tool safe: the integration must ensure every path to that tool passes through this function or an equivalent gateway.

## Interoperability

The contract is designed for adapters in LangChain/LangGraph, LlamaIndex, CrewAI, AutoGen, MCP tool servers, model gateways, enterprise API gateways and custom runtimes. These adapters must map framework calls into the same canonical action request and enforce the consume-before-execute sequence. Provider/framework adapters are separate integrations; do not infer that every platform is already connected.

## Limitations and operational requirements

This is a draft protocol and reference implementation, not a certified security product or guarantee that an organisation's entire estate is controlled. The current API requires a configured signing secret and a trusted organisation identity integration. Custodian subject IDs must be bound to the organisation's authoritative identity provider. The tool gateway must be deployed and tested at each protected integration point. Review key rotation, backup/restore, database concurrency, monitoring, incident response, penetration testing and high-availability behaviour before production customer workloads.
