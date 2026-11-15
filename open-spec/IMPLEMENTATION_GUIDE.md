# Implementing GOTI

## Evidence records
Create stable IDs in your namespace. Store source documents in controlled storage and reference them through access-controlled URIs. SHA-256 establishes byte-level identity, not authenticity or truth. Retain issuer, evidence type, scope, issue/expiry dates and limitations.

## Environmental claims
Give each claim an explicit subject, boundary and period. Link evidence to the exact claim version. Distinguish supplier declarations, primary operational records, certificates/test reports, software validation, expert assessment and independent assurance. Never silently upgrade one category into another.

## AI agent records
Register agents and immutable versions. Record model provider/name/revision, harness, tools, permissions and configuration digest. Run tests in the customer's environment. A critical failed test should block release eligibility under customer policy. Human approval must be attributable to a human identity; an API key is not a human identity.

## Data minimisation and corrections
Do not send prompts, personal information, credentials, tool arguments or full model outputs by default. Prefer bounded metadata and customer-side references. Preserve superseded records and identify dependent claims, products, reports and decisions for reassessment.
