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
