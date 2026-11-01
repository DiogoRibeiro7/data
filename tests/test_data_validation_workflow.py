"""Regression tests for CI path coverage and installed-wheel handoff smoke tests.

The workflow must cover newly added test files without manual allowlist edits.
"""

from __future__ import annotations

import fnmatch
import unittest
from pathlib import Path
from typing import Any, ClassVar

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "data-validation.yml"


class DataValidationWorkflowTests(unittest.TestCase):
    """Keep validation events and installed-package checks from drifting."""

    text: ClassVar[str]
    workflow: ClassVar[dict[str, Any]]
    paths: ClassVar[list[str]]

    @classmethod
    def setUpClass(cls) -> None:
        """Load GitHub's `on` key as a string, avoiding YAML 1.1 booleans."""

        cls.text = WORKFLOW.read_text(encoding="utf-8")
        payload = yaml.load(cls.text, Loader=yaml.BaseLoader)
        if not isinstance(payload, dict):
            raise AssertionError("data-validation workflow must be a mapping")
        cls.workflow = payload
        cls.paths = payload["on"]["pull_request"]["paths"]
        if not isinstance(cls.paths, list) or not all(
            isinstance(item, str) for item in cls.paths
        ):
            raise AssertionError("pull-request paths must be a list of strings")

    @classmethod
    def matches(cls, relative_path: str) -> bool:
        """Check a repository-relative path against the workflow's globs."""

        return any(fnmatch.fnmatchcase(relative_path, pattern) for pattern in cls.paths)

    def test_pull_request_and_main_have_identical_filters(self) -> None:
        self.assertEqual(
            self.workflow["on"]["push"]["paths"],
            self.paths,
        )
        self.assertEqual(len(self.paths), len(set(self.paths)))
        self.assertIn("main", self.workflow["on"]["push"]["branches"])

    def test_all_existing_tests_and_scripts_trigger_validation(self) -> None:
        for directory in ("tests", "scripts"):
            for file in (ROOT / directory).rglob("*.py"):
                relative = file.relative_to(ROOT).as_posix()
                with self.subTest(file=relative):
                    self.assertTrue(self.matches(relative))

    def test_new_files_and_important_generated_contracts_are_covered(self) -> None:
        for path in (
            "tests/future/test_new_feature.py",
            "scripts/new_validation/entrypoint.py",
            "src/data_registry/schemas/future.schema.json",
            "reports/future/quality.json",
            "templates/new-dataset.yaml",
            "datasets/new-dataset/metadata.yaml",
            "schemas/future.schema.json",
            ".github/workflows/data-validation.yml",
        ):
            with self.subTest(path=path):
                self.assertTrue(self.matches(path))

    def test_unrelated_prose_does_not_trigger_full_validation(self) -> None:
        for path in ("README.md", "docs/INGESTION_HANDOFF.md", "notes/notes.md"):
            with self.subTest(path=path):
                self.assertFalse(self.matches(path))

    def test_installed_wheel_smoke_tests_handoff_and_schema(self) -> None:
        self.assertIn("python -m build --wheel", self.text)
        self.assertIn("python -m pip install dist/*.whl", self.text)
        self.assertIn("PYTHONPATH= python -m unittest discover", self.text)
        self.assertIn("-p test_ingestion_handoff.py", self.text)
        versions = self.workflow["jobs"]["package-smoke"]["strategy"]["matrix"][
            "python-version"
        ]
        self.assertEqual(versions, ["3.12", "3.13", "3.14"])


if __name__ == "__main__":
    unittest.main()
