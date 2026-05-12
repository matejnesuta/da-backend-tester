"""Pytest tests for license detection behavior"""

import pytest
from pathlib import Path
from src.tester.models import AnalysisType, ClientType


# Test cases for license detection
LICENSE_DETECTION_CASES = [
    # Maven: ecosystems with manifest license support
    {
        "name": "maven/license_in_manifest_only",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "maven/license_in_file_only",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "maven/license_matching",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "maven/license_mismatched",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # npm: ecosystems with manifest license support
    {
        "name": "npm/license_in_manifest_only",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_in_file_only",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_matching",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_mismatched",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # Go: no manifest license support, LICENSE file only (fallback populates manifestLicense)
    {
        "name": "golang/license_file_detection",
        "ecosystem": "golang",
        "manifest": "go.mod",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },

    # Gradle: no manifest license support, LICENSE file only (fallback populates manifestLicense)
    {
        "name": "gradle-groovy/license_file_detection",
        "ecosystem": "gradle-groovy",
        "manifest": "build.gradle",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },

    # Python/pip: no manifest license support, LICENSE file only (fallback populates manifestLicense)
    {
        "name": "pip/license_file_detection",
        "ecosystem": "pip",
        "manifest": "requirements.txt",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },

    # Cargo/Rust: ecosystems with manifest license support
    {
        "name": "cargo/license_in_manifest_only",
        "ecosystem": "cargo",
        "manifest": "Cargo.toml",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "cargo/license_in_file_only",
        "ecosystem": "cargo",
        "manifest": "Cargo.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "cargo/license_matching",
        "ecosystem": "cargo",
        "manifest": "Cargo.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "cargo/license_mismatched",
        "ecosystem": "cargo",
        "manifest": "Cargo.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # LICENSE file variants: LICENSE.md and LICENSE.txt
    {
        "name": "maven/license_md_variant",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_txt_variant",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },

    # Different license categories
    {
        "name": "maven/license_gpl",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "GPL-3.0-only", "category": "STRONG_COPYLEFT"},
            "fileLicense": {"spdxId": "GPL-3.0-only", "category": "STRONG_COPYLEFT"},
            "mismatch": False,
        }
    },
    {
        "name": "maven/license_gpl2",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "GPL-2.0-only", "category": "STRONG_COPYLEFT"},
            "fileLicense": {"spdxId": "GPL-2.0-only", "category": "STRONG_COPYLEFT"},
            "mismatch": False,
        }
    },
    {
        "name": "maven/license_bsd",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "BSD-3-Clause", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "BSD-3-Clause", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "maven/license_bsd2",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": {"spdxId": "BSD-2-Clause", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "BSD-2-Clause", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_lgpl",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "LGPL-3.0-only", "category": "WEAK_COPYLEFT"},
            "fileLicense": {"spdxId": "LGPL-3.0-only", "category": "WEAK_COPYLEFT"},
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_lgpl2",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "LGPL-2.1-only", "category": "UNKNOWN"},
            "fileLicense": {"spdxId": "LGPL-2.1-only", "category": "UNKNOWN"},
            "mismatch": False,
        }
    },
    {
        "name": "npm/license_agpl",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "AGPL-3.0-only", "category": "STRONG_COPYLEFT"},
            "fileLicense": {"spdxId": "AGPL-3.0-only", "category": "STRONG_COPYLEFT"},
            "mismatch": False,
        }
    },

    # pnpm: JavaScript ecosystem with manifest license support
    {
        "name": "pnpm/license_in_manifest_only",
        "ecosystem": "pnpm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "pnpm/license_in_file_only",
        "ecosystem": "pnpm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "pnpm/license_matching",
        "ecosystem": "pnpm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "pnpm/license_mismatched",
        "ecosystem": "pnpm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # yarn-berry: JavaScript ecosystem with manifest license support
    {
        "name": "yarn-berry/license_in_manifest_only",
        "ecosystem": "yarn-berry",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "yarn-berry/license_in_file_only",
        "ecosystem": "yarn-berry",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "yarn-berry/license_matching",
        "ecosystem": "yarn-berry",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "yarn-berry/license_mismatched",
        "ecosystem": "yarn-berry",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # yarn-classic: JavaScript ecosystem with manifest license support
    {
        "name": "yarn-classic/license_in_manifest_only",
        "ecosystem": "yarn-classic",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "yarn-classic/license_in_file_only",
        "ecosystem": "yarn-classic",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "yarn-classic/license_matching",
        "ecosystem": "yarn-classic",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "yarn-classic/license_mismatched",
        "ecosystem": "yarn-classic",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # poetry: Python ecosystem with manifest license support (pyproject.toml)
    {
        "name": "poetry/license_in_manifest_only",
        "ecosystem": "poetry",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "poetry/license_in_file_only",
        "ecosystem": "poetry",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "poetry/license_matching",
        "ecosystem": "poetry",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "poetry/license_mismatched",
        "ecosystem": "poetry",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # uv: Python ecosystem with manifest license support (PEP 621 pyproject.toml)
    {
        "name": "uv/license_in_manifest_only",
        "ecosystem": "uv",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "uv/license_in_file_only",
        "ecosystem": "uv",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "uv/license_matching",
        "ecosystem": "uv",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "uv/license_mismatched",
        "ecosystem": "uv",
        "manifest": "pyproject.toml",
        "expected": {
            "manifestLicense": {"spdxId": "MIT", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": True,
        }
    },

    # gradle-kotlin: no manifest license support, LICENSE file only
    {
        "name": "gradle-kotlin/license_file_detection",
        "ecosystem": "gradle-kotlin",
        "manifest": "build.gradle.kts",
        "expected": {
            "manifestLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "fileLicense": {"spdxId": "Apache-2.0", "category": "PERMISSIVE"},
            "mismatch": False,
        }
    },
    {
        "name": "gradle-kotlin/no_license",
        "ecosystem": "gradle-kotlin",
        "manifest": "build.gradle.kts",
        "expected": {
            "manifestLicense": None,
            "fileLicense": None,
            "mismatch": False,
        }
    },

    # gradle-groovy: no manifest license support - add no_license case
    {
        "name": "gradle-groovy/no_license",
        "ecosystem": "gradle-groovy",
        "manifest": "build.gradle",
        "expected": {
            "manifestLicense": None,
            "fileLicense": None,
            "mismatch": False,
        }
    },

    # pip: no manifest license support - add no_license case
    {
        "name": "pip/no_license",
        "ecosystem": "pip",
        "manifest": "requirements.txt",
        "expected": {
            "manifestLicense": None,
            "fileLicense": None,
            "mismatch": False,
        }
    },

    # No license scenario: neither manifest nor LICENSE file
    {
        "name": "maven/no_license",
        "ecosystem": "maven",
        "manifest": "pom.xml",
        "expected": {
            "manifestLicense": None,
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "npm/no_license",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "manifestLicense": None,
            "fileLicense": None,
            "mismatch": False,
        }
    },
    {
        "name": "golang/no_license",
        "ecosystem": "golang",
        "manifest": "go.mod",
        "expected": {
            "manifestLicense": None,
            "fileLicense": None,
            "mismatch": False,
        }
    },
]


@pytest.fixture(scope="session")
def license_detection_testfiles_dir(testfiles_dir):
    """Get the license-detection subdirectory"""
    # testfiles_dir points to either /testfiles or /testfiles/ecosystems
    # license-detection is always at /testfiles/license-detection
    if testfiles_dir.name == "ecosystems":
        return testfiles_dir.parent / "license-detection"
    else:
        return testfiles_dir / "license-detection"


@pytest.mark.license
@pytest.mark.license_detection
@pytest.mark.parametrize("test_case", LICENSE_DETECTION_CASES, ids=[tc["name"] for tc in LICENSE_DETECTION_CASES])
def test_license_detection(test_case, available_clients, client_runner, license_detection_testfiles_dir):
    """
    Test license detection behavior for different scenarios.

    This test validates:
    1. Manifest license detection (for ecosystems with support)
    2. LICENSE file fallback detection
    3. Mismatch detection when manifest and file differ
    4. SPDX identification from LICENSE file content
    """
    assert available_clients, "No clients available to test"

    # Build test case path
    test_dir = license_detection_testfiles_dir / test_case["name"]
    manifest_path = test_dir / test_case["manifest"]

    if not manifest_path.exists():
        pytest.skip(f"Test case not found: {test_case['name']}")

    # Run license analysis with each available client
    for client_type in available_clients:
        success, result, error_msg = client_runner.run_client(
            client_type, AnalysisType.LICENSE, manifest_path
        )

        assert success, f"{client_type.value} client failed: {error_msg}"
        assert result is not None, f"{client_type.value} returned None"

        # Verify license detection results
        expected = test_case["expected"]

        # Check mismatch flag
        assert result.get("mismatch") == expected["mismatch"], \
            f"Expected mismatch={expected['mismatch']}, got {result.get('mismatch')}"

        # Helper function to check license object (handles nested details structure)
        def check_license(actual, expected_data, field_name):
            if expected_data is None:
                assert actual is None, \
                    f"Expected no {field_name}, got {actual}"
            else:
                assert actual is not None, f"Expected {field_name} but got None"
                assert actual["spdxId"] == expected_data["spdxId"], \
                    f"Expected {field_name} SPDX {expected_data['spdxId']}, " \
                    f"got {actual.get('spdxId')}"
                # Category is now nested in details
                if "details" in actual and "category" in actual["details"]:
                    assert actual["details"]["category"] == expected_data["category"], \
                        f"Expected {field_name} category {expected_data['category']}, " \
                        f"got {actual['details'].get('category')}"
                elif "category" in actual:
                    # Fallback for old structure
                    assert actual["category"] == expected_data["category"], \
                        f"Expected {field_name} category {expected_data['category']}, " \
                        f"got {actual.get('category')}"

        # Check manifestLicense
        check_license(result.get("manifestLicense"), expected["manifestLicense"], "manifestLicense")

        # Check fileLicense
        check_license(result.get("fileLicense"), expected["fileLicense"], "fileLicense")


# Test cases for license compatibility checking (component/stack analysis)
LICENSE_COMPATIBILITY_CASES = [
    {
        "name": "npm/license_incompatible_gpl",
        "ecosystem": "npm",
        "manifest": "package.json",
        "expected": {
            "hasLicenseSummary": True,
            "projectLicenseSpdxId": "MIT",
            "expectIncompatibilities": True,  # GPL dependencies incompatible with MIT
        }
    },
]


@pytest.mark.license
@pytest.mark.license_compatibility
@pytest.mark.parametrize("test_case", LICENSE_COMPATIBILITY_CASES, ids=[tc["name"] for tc in LICENSE_COMPATIBILITY_CASES])
def test_license_compatibility(test_case, available_clients, client_runner, license_detection_testfiles_dir):
    """
    Test license compatibility checking in component/stack analysis.

    This test validates:
    1. Project license detection from LICENSE file and manifest
    2. Dependency license detection
    3. Incompatible license detection (e.g., MIT project with GPL dependencies)
    4. licenseSummary structure in component/stack analysis response
    """
    assert available_clients, "No clients available to test"

    # Build test case path
    test_dir = license_detection_testfiles_dir / test_case["name"]
    manifest_path = test_dir / test_case["manifest"]

    if not manifest_path.exists():
        pytest.skip(f"Test case not found: {test_case['name']}")

    # Run component analysis (which includes license compatibility checking)
    for client_type in available_clients:
        success, result, error_msg = client_runner.run_client(
            client_type, AnalysisType.COMPONENT, manifest_path
        )

        assert success, f"{client_type.value} client failed: {error_msg}"
        assert result is not None, f"{client_type.value} returned None"

        # Verify license summary exists in response
        expected = test_case["expected"]
        if expected["hasLicenseSummary"]:
            assert "licenseSummary" in result, "Expected licenseSummary in component analysis response"
            license_summary = result["licenseSummary"]

            # Check project license
            assert "projectLicense" in license_summary, "Expected projectLicense in licenseSummary"
            project_license = license_summary["projectLicense"]

            # Verify project license SPDX ID
            if "manifest" in project_license:
                manifest_license = project_license["manifest"]
                if manifest_license and "spdxId" in manifest_license:
                    assert manifest_license["spdxId"] == expected["projectLicenseSpdxId"], \
                        f"Expected project license {expected['projectLicenseSpdxId']}, " \
                        f"got {manifest_license['spdxId']}"

            # Check for incompatible dependencies
            assert "incompatibleDependencies" in license_summary, \
                "Expected incompatibleDependencies field in licenseSummary"

            incompatible_deps = license_summary["incompatibleDependencies"]
            if expected["expectIncompatibilities"]:
                assert len(incompatible_deps) > 0, \
                    "Expected incompatible dependencies but found none"
            else:
                assert len(incompatible_deps) == 0, \
                    f"Expected no incompatible dependencies but found {len(incompatible_deps)}"


@pytest.mark.license
@pytest.mark.license_check_disabled
def test_license_check_disabled(available_clients, client_runner, license_detection_testfiles_dir):
    """
    Test that license checking can be disabled via TRUSTIFY_DA_LICENSE_CHECK=false.

    When disabled:
    1. No licenseSummary should be present in the response
    2. No license checks should be performed
    3. No license diagnostics should be shown
    """
    import os

    assert available_clients, "No clients available to test"

    # Use a test case that would normally show license information
    test_dir = license_detection_testfiles_dir / "npm/license_incompatible_gpl"
    manifest_path = test_dir / "package.json"

    if not manifest_path.exists():
        pytest.skip("Test case not found: npm/license_incompatible_gpl")

    # Save original environment variable
    original_value = os.environ.get("TRUSTIFY_DA_LICENSE_CHECK")

    try:
        # Disable license checking
        os.environ["TRUSTIFY_DA_LICENSE_CHECK"] = "false"

        for client_type in available_clients:
            success, result, error_msg = client_runner.run_client(
                client_type, AnalysisType.COMPONENT, manifest_path
            )

            assert success, f"{client_type.value} client failed: {error_msg}"
            assert result is not None, f"{client_type.value} returned None"

            # Verify no license summary when disabled
            assert "licenseSummary" not in result or result.get("licenseSummary") is None, \
                "licenseSummary should not be present when TRUSTIFY_DA_LICENSE_CHECK=false"

    finally:
        # Restore original environment variable
        if original_value is None:
            os.environ.pop("TRUSTIFY_DA_LICENSE_CHECK", None)
        else:
            os.environ["TRUSTIFY_DA_LICENSE_CHECK"] = original_value
