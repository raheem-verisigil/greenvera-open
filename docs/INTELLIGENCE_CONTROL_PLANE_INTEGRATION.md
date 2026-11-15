# Integrating an agent runtime with GreenVera's control plane

GreenVera separates the Policy Decision Point (PDP) from the Policy Enforcement Point (PEP). The PDP evaluates organisation policy. The PEP is installed at the actual tool boundary and prevents the model or agent from bypassing the decision.

## Required provisioning

1. Register an agent and immutable version.
2. Publish an organisation-approved control policy.
3. Assign an active human custodian with bounded tools, actions, resources, risk, data classification and transaction limits where relevant.
4. For production agents, record a passing evaluation and obtain a separate human release approval for that exact version and latest evaluation.
5. Deploy the PEP around every protected tool path. Remove or restrict alternate direct access paths.

Custodian subject identifiers must come from the organisation's authoritative identity provider. The reference API stores the supplied subject; directory verification and SCIM/SSO lifecycle synchronisation remain integration responsibilities.

## Secure tool-call flow

1. Build the canonical action payload from trusted runtime and application context. Do not blindly trust model-provided risk, classification, resource or transaction values.
2. Call the action evaluation endpoint.
3. BLOCK means do not invoke the tool. REQUIRE_HUMAN_APPROVAL means pause and route the exact decision to an authenticated human workflow.
4. An approver must be a distinct human subject from the requester. Re-evaluate after approval; never assume an earlier approval survives policy or custodian changes.
5. For ALLOW, request a short-lived signed authorisation (1–60 seconds; default 30).
6. Pass the returned token and exact canonical action payload to the authorisation consumption endpoint.
7. Only after successful one-time consumption may this same PEP invoke the exact protected operation.
8. If the operation fails after consumption, do not replay the token. Re-evaluate and issue a new decision/token according to the application's idempotency and recovery policy.
9. Record outcome metadata and trace ID. Do not transmit prompts or raw confidential tool inputs by default.

## Python gateway helper

~~~python
import os
from greenvera_openspace import OpenSpaceClient, GreenVeraToolGateway

client = OpenSpaceClient(api_key=os.environ["GREENVERA_API_KEY"])
action = client.action_payload(
    agent_id=AGENT_ID,
    version_id=VERSION_ID,
    tool_name="read_invoice",
    action_name="read",
    resource="invoices/INV-100",
    risk="low",
    data_classification="internal",
)

# This callable is the protected operation behind this enforcement point.
gateway = GreenVeraToolGateway(client, AGENT_ID, VERSION_ID)
protected_read = gateway.protect(
    invoice_service.read,
    tool_name="read_invoice",
    action_name="read",
    resource_resolver=lambda invoice_id: f"invoices/{invoice_id}",
    risk="low",
    data_classification="internal",
)
result = protected_read("INV-100")
~~~

The helper evaluates, obtains a short-lived signed authorisation, consumes it once, and only then invokes the callable. It cannot protect an alternate path that bypasses the helper. The legacy local-only execute_guarded method now fails closed; a local ALLOW receipt is not an execution capability.

## Emergency controls

- GET control-state: inspect suspension state and control epoch.
- POST suspend: organisation/security administrator emergency suspension.
- POST resume: reviewed resumption; increments epoch again.
- Suspension, resume, policy changes, custodian changes and revocation invalidate outstanding authorisations. Previously consumed operations cannot be retroactively undone.

## Non-negotiable PEP requirements

- Place the PEP at every path to the underlying tool. Optional wrappers are not enforcement.
- Fail closed on timeout, missing policy, invalid identity, invalid signature, expiry, replay, payload mismatch, service unavailability or any non-ALLOW decision.
- Derive tool, action, resource, transaction amount and data classification from trusted application context.
- Use separate identities for integration callers, human approvers and agent custodians.
- Do not expose API keys or action-signing secrets to browsers, models or end users.
- Apply tool-level idempotency and compensating actions for external side effects. GreenVera's one-time token prevents token replay; it cannot guarantee exactly-once behaviour inside a third-party tool.
- Store GREENVERA_ACTION_SIGNING_SECRET (at least 32 characters of cryptographically random material) in a managed secret store. The current reference uses one active HMAC key and does not yet provide multi-key overlap rotation.
- Enforce TLS, tenant-scoped access, audit retention, backup/restore, monitoring, rate limits and incident response.

## Integration scope

The canonical protocol is designed for LangChain/LangGraph, CrewAI, AutoGen, LlamaIndex, MCP tool servers, model gateways, enterprise API gateways and custom runtimes. Each framework adapter must map calls into the same action contract and enforce the PEP sequence. The current repository provides a generic Python client; it does not mean all listed platforms have already been connected.

## Production qualification

Before high-impact workloads, complete independent penetration testing, PostgreSQL concurrency/replay tests, secret rotation, backup/restore drills, load and failover testing, identity provider validation, security incident exercises and customer-specific gateway bypass testing. This is a production-oriented reference foundation, not a claim of completed certification or universal control over an unintegrated environment.
