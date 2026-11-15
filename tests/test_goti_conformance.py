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
            elif "source-record" in path.name:
                kind = "source-record"
            elif "import-batch" in path.name:
                kind = "import-batch"
            elif "dependency-edge" in path.name:
                kind = "dependency-edge"
            elif "action-authorization-claims" in path.name:
                kind = "action-authorization-claims"
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

    def test_source_record_requires_stable_identity_and_type(self):
        record = {"schema_version": "0.1.0", "source_record_id": "LOT-1", "record_type": "material_lot", "payload": {"material_code": "rPP", "quantity": 10, "unit": "kg"}}
        self.assertEqual(validate_record("source-record", record), [])
        record["source_record_id"] = ""
        self.assertTrue(validate_record("source-record", record))

    def test_import_batch_is_bounded(self):
        item = {"schema_version": "0.1.0", "source_record_id": "P-1", "record_type": "product", "payload": {"product_code": "P-1", "name": "Product"}}
        record = {"schema_version": "0.1.0", "records": [item]}
        self.assertEqual(validate_record("import-batch", record), [])
        record["records"] = [item] * 101
        self.assertTrue(validate_record("import-batch", record))


    def test_dependency_edge_supports_source_to_claim_lineage(self):
        record = {
            "schema_version": "0.1.0",
            "id": "edge-1",
            "organisation_id": "org-1",
            "source": {"object_type": "source_record", "object_id": "source-1"},
            "dependent": {"object_type": "claim", "object_id": "claim-1"},
            "relationship": "supports",
            "created_at": "2026-11-15T20:00:00Z",
        }
        self.assertEqual(validate_record("dependency-edge", record), [])
        record["relationship"] = "invented_relationship"
        self.assertTrue(validate_record("dependency-edge", record))




    def test_agent_custody_grant_schema_and_example(self):
        import jsonschema
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "open-spec/schemas/agent-custody-grant.schema.json").read_text())
        example = json.loads((root / "open-spec/examples/agent-custody-grant.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(example, schema)

    def test_agent_action_contract_schemas_and_example(self):
        import jsonschema
        root = Path(__file__).resolve().parents[1]
        schema_dir = root / "open-spec" / "schemas"
        examples = root / "open-spec" / "examples"
        request_schema = json.loads((schema_dir / "agent-action-request.schema.json").read_text())
        request = json.loads((examples / "agent-action-request.json").read_text())
        jsonschema.Draft202012Validator.check_schema(request_schema)
        jsonschema.validate(request, request_schema)
        for name in ("agent-action-decision", "agent-control-policy"):
            schema = json.loads((schema_dir / f"{name}.schema.json").read_text())
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_agent_action_contract_rejects_unknown_decision(self):
        import jsonschema
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "open-spec" / "schemas" / "agent-action-decision.schema.json").read_text())
        receipt = {
            "schema_version":"goti-agent-action-decision-1.0","decision_id":"d-1",
            "decision":"MAYBE","reason":"test","action_digest":"a"*64,
            "policy_id":"p-1","policy_version":1,"policy_hash":"b"*64,
            "issued_at":"2026-11-15T20:00:00Z","expires_at":"2026-11-15T20:00:30Z"
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(receipt, schema)

    def test_dependency_edge_filename_is_not_misclassified_as_claim(self):
        from tools.goti_validate import infer_kind
        self.assertEqual(infer_kind(Path("dependency-edge-source-to-claim.json")), "dependency-edge")

    def test_signed_action_authorization_claims_schema_and_example(self):
        import jsonschema
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "open-spec/schemas/action-authorization-claims.schema.json").read_text())
        example = json.loads((root / "open-spec/examples/action-authorization-claims.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(example, schema)
        invalid = dict(example)
        invalid["action_digest"] = "not-a-digest"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid, schema)


if __name__ == "__main__":
    unittest.main()
