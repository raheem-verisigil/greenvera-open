# Agent Custodian and Delegated Authority

This draft contract describes how an organisation assigns an accountable human custodian to an AI agent and bounds the authority delegated to that agent.

## Grant semantics
A grant binds an organisation's agent to a named custodian subject, department, purpose, allowlisted tools/actions, resource prefixes, maximum risk, maximum data classification, external destination permission, optional transaction ceiling and expiry.

- An agent without an active, unexpired grant must be denied by a connected GreenVera policy decision point.
- A tool must appear in both the organisation's active agent policy and the custodian's delegated tool list.
- Action and resource scopes are additional constraints, not replacements for application-level object authorisation.
- Tools listed in `transaction_controlled_tools` must supply an amount in minor currency units and an ISO 4217 currency code; missing or over-limit amounts are denied.
- Revocation and replacement invalidate pending approvals bound to the previous grant.
- The custodian subject should be selected from the organisation's authoritative identity provider. The current reference implementation accepts a supplied subject string; automated directory membership verification is an integration requirement, not yet claimed as implemented.

## Reference API
- `POST /v1/agents/{agent_id}/custodians`: assign or replace the primary custodian.
- `GET /v1/agents/{agent_id}/custodians`: retrieve grant history.
- `POST /v1/agents/{agent_id}/custodians/{grant_id}/revoke`: revoke a grant.
- `GET /v1/custodians/me/agents`: list agents assigned to the authenticated subject.

## Enforcement
The agent runtime or tool gateway must call the policy decision endpoint before every protected action and enforce the response at the actual tool boundary. GreenVera's registry cannot intercept calls that bypass an integrated enforcement point. Do not rely on model prompts or self-reported tool metadata as security controls.

This is a draft interoperability interface, not a certification, identity proof, legal determination or guarantee of runtime enforcement.
