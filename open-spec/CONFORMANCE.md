# Draft v0.1 conformance profile

1. JSON parses without duplicate object keys.
2. Payload validates against its schema using JSON Schema Draft 2020-12.
3. Implementations preserve unknown optional extension fields.
4. IDs are stable and unique within the issuing organisation's namespace.
5. Timestamps are ISO 8601 date-time values with an explicit timezone.
6. Cross-organisation access requires an explicit, revocable permission grant.
7. A human release decision records a human identity and role; an API integration credential alone is not a human approver.
8. A passed aggregate evaluation cannot override a critical failed test.
9. Exported evidence preserves issuer, source, scope, dates, provenance and limitations.

Schema validation alone does not prove claim truth, evidence authenticity, agent security, legal compliance or independent assurance. Implementations should add semantic checks for referential integrity, tenant authorisation, chronology, revocation and policy-specific critical-test handling.
