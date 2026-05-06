"""Test case discovery logic"""

from pathlib import Path
from typing import List, Optional

from .models import TestCase, WorkspaceTestCase
from .config import MANIFEST_PATTERNS


class TestDiscovery:
    """Discovers test cases from the testfiles directory"""

    @staticmethod
    def discover_test_cases(testfiles_dir: Path) -> List[TestCase]:
        """
        Discover all test cases in the testfiles directory

        Args:
            testfiles_dir: Path to the testfiles directory

        Returns:
            List of discovered test cases
        """
        test_cases = []

        if not testfiles_dir.exists():
            print(f"Error: Test files directory not found: {testfiles_dir}")
            return test_cases

        # Iterate through ecosystem directories
        for ecosystem_dir in testfiles_dir.iterdir():
            if not ecosystem_dir.is_dir():
                continue

            ecosystem = ecosystem_dir.name

            # Find all test case directories within this ecosystem
            for test_dir in ecosystem_dir.iterdir():
                if not test_dir.is_dir():
                    continue

                # Check for .member-manifest marker (for workspace member tests)
                member_marker = test_dir / ".member-manifest"
                workspace_root = None
                if member_marker.exists():
                    # Use the path specified in the marker file
                    relative_path = member_marker.read_text().strip()
                    manifest_path = test_dir / relative_path
                    if not manifest_path.exists():
                        print(f"Warning: Member manifest not found: {manifest_path}")
                        continue
                    # For member tests, test_dir is the workspace root
                    workspace_root = test_dir
                else:
                    # Find the manifest file normally
                    manifest_path = TestDiscovery._find_manifest(test_dir, ecosystem)
                    if not manifest_path:
                        continue

                test_case = TestCase(
                    name=f"{ecosystem}/{test_dir.name}",
                    ecosystem=ecosystem,
                    manifest_path=manifest_path,
                    workspace_root=workspace_root,
                )
                test_cases.append(test_case)

        return test_cases

    @staticmethod
    def discover_workspace_test_cases(testfiles_dir: Path) -> List[WorkspaceTestCase]:
        """
        Discover workspace test cases (identified by .workspace-batch marker file)

        Args:
            testfiles_dir: Path to the testfiles directory

        Returns:
            List of discovered workspace test cases
        """
        workspace_test_cases = []

        if not testfiles_dir.exists():
            print(f"Error: Test files directory not found: {testfiles_dir}")
            return workspace_test_cases

        # Iterate through ecosystem directories
        for ecosystem_dir in testfiles_dir.iterdir():
            if not ecosystem_dir.is_dir():
                continue

            ecosystem = ecosystem_dir.name

            # Find all test case directories within this ecosystem
            for test_dir in ecosystem_dir.iterdir():
                if not test_dir.is_dir():
                    continue

                # Check for .workspace-batch marker
                marker_file = test_dir / ".workspace-batch"
                if not marker_file.exists():
                    continue

                # Parse marker file for metadata
                expected_packages = 0
                test_metadata = False
                if marker_file.exists():
                    content = marker_file.read_text()
                    for line in content.splitlines():
                        if line.startswith("expected_packages:"):
                            expected_packages = int(line.split(":")[1].strip())
                        elif line.startswith("test_metadata:"):
                            test_metadata = line.split(":")[1].strip().lower() == "true"

                workspace_test_case = WorkspaceTestCase(
                    name=f"{ecosystem}/{test_dir.name}",
                    ecosystem=ecosystem,
                    workspace_root=test_dir,
                    expected_package_count=expected_packages,
                )
                # Store test_metadata as an attribute for later use
                workspace_test_case.test_metadata = test_metadata
                workspace_test_cases.append(workspace_test_case)

        return workspace_test_cases

    @staticmethod
    def _find_manifest(test_dir: Path, ecosystem: str) -> Optional[Path]:
        """Find the manifest file in the test directory"""
        patterns = MANIFEST_PATTERNS.get(ecosystem, [])

        for pattern in patterns:
            manifest_path = test_dir / pattern
            if manifest_path.exists():
                return manifest_path

        return None

