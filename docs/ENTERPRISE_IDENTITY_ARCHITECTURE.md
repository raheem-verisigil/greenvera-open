# GreenVera Enterprise Identity Architecture

GreenVera uses a provider-neutral workforce identity model with OpenID Connect (OIDC) as the primary federation protocol. Microsoft Entra ID is the first planned enterprise identity adapter because of its broad adoption in Microsoft 365 and Azure-based organisations. Google Workspace/Cloud Identity and Okta are subsequent provider adapters; they are not represented as implemented integrations until their connectors and tests are delivered.

## Provider-neutral contract

Each identity adapter must produce the same verified principal:

- stable subject: immutable provider + tenant + directory object identifier;
- organisation: mapped by an administrator-controlled tenant allowlist;
- roles: mapped only from verified identity-provider application roles or groups;
- authentication method and provider metadata;
- token issue/expiry and revocation context.

The adapter must never accept an organisation ID, role, approver status or custodian authority from browser-supplied form fields. Identity establishes who the person is; GreenVera's own organisation policy establishes what that person may do.

## Microsoft Entra first adapter

The private engineering implementation provides a configuration-gated OIDC authorization-code flow with PKCE S256, signed state, nonce verification, tenant allowlisting, tenant-to-organisation mapping, ID-token signature/issuer/audience validation against Entra JWKS, and explicit application-role mapping. Unmapped users receive the least-privileged member role.

Required production follow-through includes SCIM lifecycle sync, group mapping, session revocation, back-channel logout or equivalent revocation events, BFF session cookies, audit, key rotation and independent security review. The connector must remain disabled until a customer's Entra application registration and tenant mapping are configured and validated.

## Integration order

1. Microsoft Entra ID — initial enterprise connector.
2. Google Workspace / Cloud Identity — next broad workforce ecosystem.
3. Okta — cross-platform enterprise identity provider.
4. Generic OIDC adapter — support other standards-compliant providers without provider lock-in.

This is an integration priority, not a claim that all four providers are already supported.

## Security boundaries

- Identity provider authentication does not itself confer GreenVera policy administrator, human approver or agent custodian privileges.
- Human approvals must use a distinct authenticated human principal from the action requester.
- Agent API keys are machine identities, not human identities.
- Disabling a user or removing an application role must lead to GreenVera session and permission revocation within a documented, tested propagation window.
- The GreenVera policy decision point and tool enforcement point remain authoritative for agent actions.
