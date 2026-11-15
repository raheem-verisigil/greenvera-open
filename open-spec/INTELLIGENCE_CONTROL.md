# Agent Action Governance Interoperability

This draft interface defines portable policy inputs and decisions for AI agent actions. It is intended for agent frameworks, model gateways, enterprise software, identity providers, security platforms and governance products to interoperate without replacing one another.

## Contracts
- `schemas/agent-action-request.schema.json`: canonical proposed action context.
- `schemas/agent-control-policy.schema.json`: organisation policy envelope.
- `schemas/agent-action-decision.schema.json`: policy decision receipt.

## Enforcement semantics
- A Policy Decision Point evaluates a canonical action request against an organisation's active policy.
- A Policy Enforcement Point in the agent runtime, tool wrapper or gateway must execute only on a valid ALLOW receipt.
- BLOCK is denied.
- REQUIRE_HUMAN_APPROVAL pauses execution until a separately authenticated human approval is received.
- Missing policy, timeout, invalid response, signature failure, expired receipt or digest mismatch means deny.
- Decision receipts should be short-lived and bound to the exact action digest and policy hash.

## Signed, single-use action authorisation\n\nAn ALLOW decision is not itself an execution token. The reference flow can mint a short-lived signed authorisation bound to the exact decision, organisation, agent version, policy hash, custodian grant, control epoch, tool, action, resource and canonical action digest. The connected Policy Enforcement Point must consume the authorisation exactly once before calling the protected tool. Replays, expired tokens, changed policy/custodian state, emergency suspension and payload mismatches are rejected. See [Signed Action Authorisation and Tool Gateway](ACTION_AUTHORIZATION.md) and [claims schema](schemas/action-authorization-claims.schema.json).\n\n## Interoperability rules
- Preserve the organisation's identity and policy authority. A plugin cannot silently widen permissions.
- Tool names and resource identifiers must use stable namespaces.
- Classification and risk must be derived or validated by trusted organisation policy, not blindly accepted from the model.
- Record decision ID, policy version, action digest, actor, trace ID and execution outcome.
- Never transmit raw prompts or confidential payloads by default.
- A decision is an authorisation record, not proof of safety, correctness or legal compliance.

## Status
Draft interface for implementer feedback. It is not a formal standard, certification, regulatory approval or universal runtime enforcement mechanism.


For human accountability and bounded delegated permissions, see [Agent Custodian and Delegated Authority](AGENT_CUSTODIAN.md) and the [custody grant schema](schemas/agent-custody-grant.schema.json). The reference contract binds agent identity to a custodian, purpose, tools, actions, resource scope, risk ceiling, data classification, transaction limits and expiry.
