"""Contracts for external-source disappearance and preservation policy."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads(
    (
        ROOT / "preservation" / "external-disappearance-policy-v1.json"
    ).read_text(encoding="utf-8")
)
POLICY_SCHEMA = json.loads(
    (
        ROOT / "schemas" / "external-disappearance-policy-v1.schema.json"
    ).read_text(encoding="utf-8")
)
EXTERNAL_SCHEMA = json.loads(
    (ROOT / "schemas" / "external-metadata-v1.schema.json").read_text(
        encoding="utf-8"
    )
)


class ExternalDisappearancePolicyTests(unittest.TestCase):
    def test_committed_policy_validates_against_schema(self) -> None:
        Draft202012Validator(POLICY_SCHEMA).validate(POLICY)

    def minimal_external(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "status": "external-reference",
            "id": "example",
            "title": "Example",
            "publisher": "Example Publisher",
            "source_url": "https://example.test/data",
            "storage": "authoritative-upstream",
        }

    def test_moved_state_requires_replacement_and_evidence(self) -> None:
        metadata = self.minimal_external()
        metadata["availability"] = {
            "state": "moved",
            "last_reviewed": "2026-10-10",
        }
        errors = list(Draft202012Validator(EXTERNAL_SCHEMA).iter_errors(metadata))
        messages = "\n".join(error.message for error in errors)
        self.assertIn("replacement_url", messages)
        self.assertIn("evidence", messages)

    def test_terminal_state_requires_evidence(self) -> None:
        metadata = self.minimal_external()
        metadata["availability"] = {
            "state": "permanently-unavailable",
            "last_reviewed": "2026-10-10",
        }
        errors = list(Draft202012Validator(EXTERNAL_SCHEMA).iter_errors(metadata))
        messages = "\n".join(error.message for error in errors)
        self.assertIn("evidence", messages)

    def test_live_state_remains_optional_and_backward_compatible(self) -> None:
        metadata = self.minimal_external()
        Draft202012Validator(EXTERNAL_SCHEMA).validate(metadata)


if __name__ == "__main__":
    unittest.main()
