"""Contracts for the snapshot release workflow delegation."""

from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "snapshot-release.yml"


class SnapshotWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_publication_delegates_to_shared_collection(self) -> None:
        self.assertIn(
            "DiogoRibeiro7/git-actions-collection/.github/workflows/snapshot-release.yml@",
            self.text,
        )
        self.assertIn("dry-run: ${{ !inputs.publish_release }}", self.text)

    def test_data_repo_keeps_domain_specific_preparation(self) -> None:
        for command in (
            "scripts/validate_repository.py",
            "scripts/generate_external_catalog.py",
            "scripts/generate_consumer_catalog.py",
            "scripts/registry_quality.py",
            "scripts/generate_provenance_debt.py",
            "scripts/generate_lifecycle_report.py",
            "scripts/generate_static_distribution.py",
            "scripts/create_snapshot.py",
            "scripts/generate_release_provenance.py",
        ):
            self.assertIn(command, self.text)

    def test_provenance_is_generated_after_snapshot_material(self) -> None:
        snapshot_position = self.text.index("scripts/create_snapshot.py")
        provenance_position = self.text.index("scripts/generate_release_provenance.py")
        upload_position = self.text.index("actions/upload-artifact@")
        self.assertLess(snapshot_position, provenance_position)
        self.assertLess(provenance_position, upload_position)

    def test_data_repo_no_longer_duplicates_release_mutation_logic(self) -> None:
        self.assertNotIn("gh release create", self.text)
        self.assertNotIn('git tag -a "$SNAPSHOT_TAG"', self.text)
        self.assertNotIn("git ls-remote --exit-code --tags origin", self.text)


if __name__ == "__main__":
    unittest.main()
