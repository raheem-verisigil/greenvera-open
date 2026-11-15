# GOTI interoperability profile (draft)

## Purpose

Allow existing software vendors and organisations to exchange structured evidence lineage without migrating their users to GreenVera or surrendering source-system ownership.

## Transport requirements

A conforming implementation should provide:
- organisation-authorised, tenant-scoped ingestion;
- TLS in transit;
- an idempotency key per import request;
- bounded batches of 1–100 source records;
- stable source-system record identifiers;
- explicit source issuer and source update timestamps when available;
- duplicate detection and immutable revisions;
- per-record validation outcomes;
- audit records for connector registration and import completion.

The exact authentication mechanism is implementation-specific. Never put long-lived secrets in payloads or URLs. A vendor must not access another organisation's data without explicit authorisation.

## Record families

The source-record profile supports supplier, material lot, collection event, processing batch, production batch, product, shipment, evidence and claim records. Payloads remain source-system-specific JSON objects. Implementations must publish and version their field mappings; they must not silently convert units, infer missing facts or rewrite source data.

## Example request

```http
POST /v1/interoperability/connectors/{connector_id}/imports
Authorization: Bearer <organisation-issued-credential>
Idempotency-Key: erp-export-2026-11-15-0001
Content-Type: application/json
```

Body: see [import-batch-material-lot.json](examples/import-batch-material-lot.json).

## Trust boundaries

A schema-valid source record is not an independently verified fact. A payload digest establishes equality under an implementation's canonicalisation algorithm; it does not establish authorship or truth. A supplier declaration remains a supplier declaration. A mass-balance result remains a calculation under its stated assumptions.

Implementations should distinguish source assertions, calculated values, evidence documents and metadata, reviewer conclusions, independent assurance, unresolved conflicts and corrections.

## Versioning and compatibility

This profile is a draft. Implementations should pin schema and mapping versions, reject unknown record types unless explicitly configured for extensions, and preserve source fields rather than silently dropping them. Breaking changes require a new schema version.

## Current reference implementation boundary

GreenVera's private backend currently implements generic authenticated JSON ingestion, source-record hashes, idempotent retries, tenant-scoped connector records and append-only revisions. It does not yet ship native vendor connectors, CSV/XLSX parsing, scheduled sync, webhook signature verification or universal ERP integrations. Those capabilities require separately reviewed adapters and source-owner permission.