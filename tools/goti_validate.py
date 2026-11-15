#!/usr/bin/env python3
"""Validate GOTI v0.1 JSON records and cross-record assurance rules.

Requires: pip install -r requirements-dev.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "open-spec" / "schemas"
SCHEMA_BY_KIND = {
    "claim": "claim.schema.json",
    "evidence": "evidence.schema.json",
    "evaluation-run": "evaluation-run.schema.json",
    "release-decision": "release-decision.schema.json",
    "source-record": "source-record.schema.json",
    "import-batch": "import-batch.schema.json",
}


class DuplicateKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=_unique_object)


def _has_explicit_timezone(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def semantic_errors(kind: str, record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("created_at", "started_at", "completed_at", "issued_at",
                  "expires_at", "valid_until", "decided_at", "source_updated_at"):
        if field in record and not _has_explicit_timezone(record[field]):
            errors.append(f"{field} must be an ISO 8601 timestamp with an explicit timezone")

    if kind == "evaluation-run":
        results = record.get("results", [])
        test_ids = [item.get("test_id") for item in results if isinstance(item, dict)]
        if len(test_ids) != len(set(test_ids)):
            errors.append("evaluation results must have unique test_id values")

    if kind == "release-decision":
        actor = record.get("decision_actor", {})
        if isinstance(actor, dict) and actor.get("type") == "human_approver":
            if not actor.get("id") or not actor.get("role"):
                errors.append("human_approver decisions require a non-empty actor id and role")
        if isinstance(actor, dict) and actor.get("type") == "policy_engine" and record.get("decision") in {
            "ALLOW", "ALLOW_WITH_CONDITIONS"
        } and not record.get("policy_version"):
            errors.append("policy_engine allow decisions require policy_version")

    return errors


def validate_record(kind: str, record: Any) -> list[str]:
    if kind not in SCHEMA_BY_KIND:
        return [f"unknown record kind {kind!r}; expected one of {', '.join(SCHEMA_BY_KIND)}"]
    schema_path = SCHEMA_DIR / SCHEMA_BY_KIND[kind]
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(str(part) for part in issue.absolute_path) or '$'}: {issue.message}"
        for issue in validator.iter_errors(record)
    ]
    if isinstance(record, dict):
        errors.extend(semantic_errors(kind, record))
    return errors


def infer_kind(path: Path) -> str | None:
    name = path.name.lower()
    for kind in SCHEMA_BY_KIND:
        if kind in name:
            return kind
    return None


def validate_path(path: Path) -> tuple[int, int]:
    files = [path] if path.is_file() else sorted(path.rglob("*.json"))
    checked = 0
    failures = 0
    for file_path in files:
        kind = infer_kind(file_path)
        if kind is None:
            print(f"SKIP {file_path}: filename must contain a GOTI record kind")
            continue
        checked += 1
        try:
            record = load_json(file_path)
            issues = validate_record(kind, record)
        except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
            issues = [str(exc)]
        if issues:
            failures += 1
            print(f"FAIL {file_path}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"PASS {file_path}")
    return checked, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "open-spec" / "examples")
    args = parser.parse_args()
    checked, failures = validate_path(args.path)
    print(f"\nGOTI conformance: {checked} file(s) checked, {failures} failure(s)")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
