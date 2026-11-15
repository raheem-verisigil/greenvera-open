"""Local TrustLab runner for customer-owned test harnesses.

Test functions run inside the customer's environment. Only test identifiers,
status, severity metadata and optional evidence references are submitted.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
from .client import OpenSpaceClient


@dataclass(frozen=True)
class EvaluationCase:
    test_id: str
    check: Callable[[], bool | dict[str, Any]]
    category: str = "general"
    critical: bool = False
    evidence_ref: str = ""


class TrustLabRunner:
    def __init__(self, client: OpenSpaceClient, agent_id: str, version_id: str, suite: str):
        self.client = client
        self.agent_id = agent_id
        self.version_id = version_id
        self.suite = suite

    def run(self, cases: list[EvaluationCase], dimensions: dict | None = None):
        if not cases:
            raise ValueError("TrustLab requires at least one explicit evaluation case")
        ids = [case.test_id for case in cases]
        if len(ids) != len(set(ids)):
            raise ValueError("Evaluation test_id values must be unique within a suite")
        results = []
        for case in cases:
            try:
                outcome = case.check()
                if isinstance(outcome, dict):
                    passed = outcome.get("passed") is True
                    note = str(outcome.get("note", ""))[:1000]
                    evidence_ref = str(outcome.get("evidence_ref", case.evidence_ref))[:500]
                else:
                    passed = outcome is True
                    note = ""
                    evidence_ref = case.evidence_ref
                results.append({
                    "test_id": case.test_id, "category": case.category,
                    "status": "passed" if passed else "failed",
                    "critical": case.critical, "note": note, "evidence_ref": evidence_ref,
                })
            except Exception as exc:
                results.append({
                    "test_id": case.test_id, "category": case.category,
                    "status": "failed", "critical": case.critical,
                    "note": "Harness exception: " + type(exc).__name__,
                    "evidence_ref": case.evidence_ref,
                })
        return self.client.record_evaluation(
            self.agent_id, self.version_id, self.suite, results, dimensions=dimensions,
        )
