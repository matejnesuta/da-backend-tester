"""Test case discovery logic"""

from pathlib import Path
from typing import List, Optional

from .models import TestCase
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

                # Find the manifest file
                manifest_path = TestDiscovery._find_manifest(test_dir, ecosystem)
                if not manifest_path:
                    continue

                test_case = TestCase(
                    name=f"{ecosystem}/{test_dir.name}",
                    ecosystem=ecosystem,
                    manifest_path=manifest_path,
                )
                test_cases.append(test_case)

        return test_cases

    @staticmethod
    def _find_manifest(test_dir: Path, ecosystem: str) -> Optional[Path]:
        """Find the manifest file in the test directory"""
        patterns = MANIFEST_PATTERNS.get(ecosystem, [])

        for pattern in patterns:
            manifest_path = test_dir / pattern
            if manifest_path.exists():
                return manifest_path

        return None

