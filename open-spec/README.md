# GreenVera Open Trust Interface (GOTI)

**Draft v0.1.0 — open review candidate, not a ratified standard.**

GOTI defines portable JSON objects and HTTP integration patterns for exchanging environmental claim evidence and AI-agent assurance records across vendors. Organisations retain their existing models, agent frameworks, LCA tools, ERP systems, supplier portals and deployment platforms. Implementing the interface does not require GreenVera-hosted services.

## Principles
1. Evidence before score: preserve source, scope, method, time and limitations.
2. Portability: stable identifiers, versioned JSON schemas and exportable records.
3. Vendor neutrality: any provider can implement a connector.
4. Tenant control: the data owner controls access and sharing.
5. Human accountability: software checks and independent assurance remain distinct.
6. Append-only history: corrections supersede records; they do not silently erase them.
7. Data minimisation: raw prompts and confidential documents remain customer-side unless explicitly shared.
8. No implied certification or regulatory approval.

## Object families
Environmental: Claim, Evidence, ClaimEvidenceLink, Methodology, Assessment, Review, AuditEvent, Correction.
Agent trust: Agent, AgentVersion, EvaluationRun, TestResult, ExecutionTrace, ReleaseDecision, Incident, AssuranceAssessment.
Network: Organisation, SupplierRequest, PermissionGrant, Product, Material, Facility, ProductionBatch, Shipment.

Initial schemas cover Claim, Evidence, EvaluationRun and ReleaseDecision. This draft is open to technical review and is not recognised by a regulator, standards body or certification programme.

See [CONFORMANCE.md](CONFORMANCE.md) and [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md). Specification and schemas are Apache-2.0 under [LICENSE](LICENSE).


## Interoperability and source-system records

GOTI now includes draft `SourceRecord` and `ImportBatch` schemas for vendors that want to connect existing ERP, collection, supplier, LCA, product-data or assurance systems without replacing them.

The transport profile requires an organisation-authorised connector identity, bounded batches of 1–100 source records, an `Idempotency-Key` header, stable source identifiers, source issuer/update timestamps where available, immutable revisions when payloads change, and per-record validation outcomes.

The schemas do not define a vendor's API, certify a connector or prove imported data. Vendors retain their source systems and decide what is shared. See [INTEROPERABILITY.md](INTEROPERABILITY.md), [source-record schema](schemas/source-record.schema.json) and [import-batch schema](schemas/import-batch.schema.json).


## AI action governance

The draft Intelligence Control interface defines portable agent action requests, organisation policies and action decision receipts. See [INTELLIGENCE_CONTROL.md](INTELLIGENCE_CONTROL.md) and the `agent-action-*` / `agent-control-policy` schemas. These contracts are designed for independent runtime, gateway and enterprise-software integrations; enforcement remains the responsibility of an integrated policy enforcement point.
