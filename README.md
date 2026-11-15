# GreenVera Open

Open specifications and developer tools for environmental evidence and AI-agent assurance.

GreenVera Open publishes the **GreenVera Open Trust Interface (GOTI)** draft and OpenSpace developer tooling. The aim is portable evidence and assurance records across organisations, supply chains, software providers and AI-agent stacks—without forcing everyone onto one vendor or model.

## Contents
- [GOTI draft](open-spec/README.md)
- [JSON schemas](open-spec/schemas/)
- [Examples](open-spec/examples/)
- [Conformance profile](open-spec/CONFORMANCE.md)
- [Reference conformance runner](docs/GOTI_CONFORMANCE_RUNNER.md)
- [Run validator](tools/goti_validate.py)
- [OpenSpace Python SDK](sdk/python/README.md)
- [Developer quickstart](docs/OPENSPACE_PYTHON_QUICKSTART.md)

## Principles
Evidence before scores; portable records; vendor-neutral integration; tenant-controlled sharing; human accountability; append-only correction history; data minimisation; no implied certification.

## Status
GOTI is **Draft v0.1.0**, open for technical review. It is not a ratified industry standard, regulator-recognised framework, certification programme or legal-compliance determination. The Python SDK is a preview; API access is through controlled onboarding and the package is not represented as published on PyPI.

Schema validation checks structure only. It does not establish claim truth, evidence authenticity, agent security or legal compliance.

## Repository boundaries
This repository contains selected public specifications, SDK source and developer documentation. GreenVera's hosted backend, production configuration, credentials, customer information and internal deployment assets remain separate.

## Licensing
GOTI is Apache-2.0 under [open-spec/LICENSE](open-spec/LICENSE). The SDK is separately Apache-2.0 under [sdk/python/LICENSE](sdk/python/LICENSE). GreenVera names, logos and hosted services are not licensed by these files.
