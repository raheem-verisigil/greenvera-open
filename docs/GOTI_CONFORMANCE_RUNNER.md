# GOTI conformance runner (Draft v0.1.0)

The repository includes a reference validator for the four published record types:
Claim, Evidence, Agent Evaluation Run and Agent Release Decision.

## Run locally

From the repository root:

```bash
python -m pip install -r requirements-dev.txt
python tools/goti_validate.py open-spec/examples
python -m unittest discover -s tests -p "test_goti_conformance.py" -v
```

Validate a single file by passing its path. The filename must contain one of
`claim`, `evidence`, `evaluation-run` or `release-decision` so the matching
schema can be selected.

## Checks performed

- JSON parsing rejects duplicate object keys.
- JSON Schema Draft 2020-12 validation runs with format checking enabled.
- Date-time fields must include an explicit UTC offset or `Z`.
- Evaluation test identifiers must be unique within a run.
- Human approver decisions must include both an identity and role.
- Policy-engine allow decisions must identify the policy version.

The GitHub Actions workflow runs the example validation and unit tests on
Python 3.10, 3.11 and 3.12 for relevant pushes and pull requests.

## Limits

This is a reference structural and semantic validator, not a certification
service, security assessment, legal-compliance engine or proof that a claim,
document or agent is truthful or safe. It does not yet verify cross-record
referential integrity, cryptographic signatures, tenant authorisation,
permission revocation, chronology across records or whether a release decision
correctly references a particular evaluation's critical failures. Those checks
require a connected implementation and are explicitly outside this runner's
current scope.
