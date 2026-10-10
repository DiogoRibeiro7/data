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
        self.assertIn(
            "required-files: '[\"snapshot-manifest.json\","
            "\"snapshot-summary.md\",\"snapshot-provenance.json\"]'",
            self.text,
        )

    def test_release_assets_receive_github_artifact_attestations(self) -> None:
        self.assertIn("id-token: write", self.text)
        self.assertIn("attestations: write", self.text)
        self.assertIn("uses: actions/attest@v4", self.text)
        self.assertIn('subject-path: "release-material/*"', self.text)

    def test_archive_profile_defaults_to_metadata_only(self) -> None:
        self.assertIn('default: "release-metadata"', self.text)
        self.assertIn("eligible-canonical-bytes", self.text)
        self.assertIn("scripts/generate_archive_bundle.py", self.text)
        self.assertIn('--profile "${{ inputs.archive_profile }}"', self.text)
        self.assertIn('name: ${{ inputs.snapshot_tag }}-archive', self.text)

    def test_data_repo_keeps_domain_specific_preparation(self) -> None:
        for command in (
            "scripts/validate_repository.py",
            "scripts/generate_external_catalog.py",
            "scripts/generate_consumer_catalog.py",
            "scripts/registry_quality.py",
            "scripts/generate_provenance_debt.py",
            "scripts/generate_preservation_eligibility.py",
            "scripts/generate_registry_changelog.py",
            "scripts/create_snapshot.py",
            "scripts/generate_archive_bundle.py",
        ):
            self.assertIn(command, self.text)

    def test_data_repo_no_longer_duplicates_release_mutation_logic(self) -> None:
        self.assertNotIn("gh release create", self.text)
        self.assertNotIn('git tag -a "$SNAPSHOT_TAG"', self.text)
        self.assertNotIn("git ls-remote --exit-code --tags origin", self.text)


if __name__ == "__main__":
    unittest.main()
