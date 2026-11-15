import json
import tempfile
import unittest
from pathlib import Path

from tools.goti_validate import DuplicateKeyError, load_json, validate_record


class GotiConformanceTests(unittest.TestCase):
    def test_public_examples_validate(self):
        root = Path(__file__).resolve().parents[1]
        examples = root / "open-spec" / "examples"
        for path in examples.glob("*.json"):
            if "recycled-content-claim" in path.name:
                kind = "claim"
            elif "agent-evaluation" in path.name:
                kind = "evaluation-run"
            else:
                continue
            with self.subTest(path=path.name):
                self.assertEqual(validate_record(kind, load_json(path)), [])

    def test_duplicate_object_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"id":"first","id":"second"}', encoding="utf-8")
            with self.assertRaises(DuplicateKeyError):
                load_json(path)

    def test_duplicate_test_ids_are_rejected(self):
        record = {
            "schema_version": "0.1.0", "id": "run-1", "agent_id": "agent-1",
            "agent_version_id": "v1", "suite": "smoke",
            "started_at": "2026-01-01T10:00:00Z", "status": "passed",
            "results": [
                {"test_id": "permission-check", "status": "passed"},
                {"test_id": "permission-check", "status": "passed"}
            ]
        }
        self.assertTrue(any("unique test_id" in e for e in validate_record("evaluation-run", record)))

    def test_naive_timestamp_is_rejected(self):
        record = {
            "schema_version": "0.1.0", "id": "run-2", "agent_id": "agent-1",
            "agent_version_id": "v1", "suite": "smoke",
            "started_at": "2026-01-01T10:00:00", "status": "passed",
            "results": []
        }
        self.assertTrue(any("explicit timezone" in e for e in validate_record("evaluation-run", record)))

    def test_human_approver_requires_identity_and_role(self):
        record = {
            "schema_version": "0.1.0", "id": "decision-1", "agent_id": "agent-1",
            "agent_version_id": "v1", "evaluation_id": "run-1", "decision": "ALLOW",
            "decided_at": "2026-01-01T10:00:00Z",
            "decision_actor": {"type": "human_approver", "id": "reviewer-1"}
        }
        self.assertTrue(any("require a non-empty actor id and role" in e
                            for e in validate_record("release-decision", record)))


if __name__ == "__main__":
    unittest.main()
