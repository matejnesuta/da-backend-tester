"""Tests for workspace/monorepo batch analysis"""

import json
import pytest
from pathlib import Path
from src.tester.models import ClientType
from conftest import normalize_result


# Workspace test fixtures
WORKSPACE_FIXTURES = {
    "npm_workspace": {
        "root": Path("tests/client-testing/testfiles/npm/npm_workspace"),
        "expected_packages": 3,  # root + 2 members
        "ecosystem": "npm",
    },
    "npm_workspace_with_invalid": {
        "root": Path("tests/client-testing/testfiles/npm/npm_workspace_with_invalid"),
        "expected_packages": 1,  # only valid package-a (invalid package should be skipped)
        "ecosystem": "npm",
    },
    "pnpm_workspace": {
        "root": Path("tests/client-testing/testfiles/pnpm/pnpm_workspace"),
        "expected_packages": 2,  # only members (package-a, package-b), not root
        "ecosystem": "pnpm",
    },
    "npm_workspace_member": {
        "member_manifest": Path("tests/client-testing/testfiles/npm/npm_workspace_member/packages/package-a/package.json"),
        "workspace_root": Path("tests/client-testing/testfiles/npm/npm_workspace_member"),
        "ecosystem": "npm",
    },
}


@pytest.fixture
def workspace_fixtures():
    """Provide workspace fixture definitions"""
    return WORKSPACE_FIXTURES


class TestBatchAnalysis:
    """Test suite for stack-batch workspace analysis"""

    def test_batch_npm_workspace(self, available_clients, client_runner, snapshot):
        """Test batch analysis on npm workspace"""
        workspace_root = WORKSPACE_FIXTURES["npm_workspace"]["root"]
        expected_count = WORKSPACE_FIXTURES["npm_workspace"]["expected_packages"]

        # Only test JavaScript client (Java doesn't support JS workspaces)
        if ClientType.JAVASCRIPT not in available_clients:
            pytest.skip("JavaScript client not available")

        success, result, error_msg = client_runner.run_batch_analysis(
            ClientType.JAVASCRIPT,
            workspace_root,
        )

        assert success, f"Batch analysis failed: {error_msg}"
        assert result is not None, "Batch analysis returned None"

        # Verify it's a dictionary with package keys
        assert isinstance(result, dict), "Batch result should be a dictionary"

        # Verify we have the expected number of packages
        package_keys = [k for k in result.keys() if k.startswith("pkg:")]
        assert len(package_keys) == expected_count, \
            f"Expected {expected_count} packages, got {len(package_keys)}: {package_keys}"

        # Snapshot comparison
        normalized = normalize_result(result)
        assert normalized == snapshot

    def test_batch_pnpm_workspace(self, available_clients, client_runner, snapshot):
        """Test batch analysis on pnpm workspace"""
        workspace_root = WORKSPACE_FIXTURES["pnpm_workspace"]["root"]
        expected_count = WORKSPACE_FIXTURES["pnpm_workspace"]["expected_packages"]

        # Only test JavaScript client
        if ClientType.JAVASCRIPT not in available_clients:
            pytest.skip("JavaScript client not available")

        success, result, error_msg = client_runner.run_batch_analysis(
            ClientType.JAVASCRIPT,
            workspace_root,
        )

        assert success, f"Batch analysis failed: {error_msg}"
        assert result is not None, "Batch analysis returned None"

        # Verify structure
        assert isinstance(result, dict), "Batch result should be a dictionary"

        package_keys = [k for k in result.keys() if k.startswith("pkg:")]
        assert len(package_keys) == expected_count, \
            f"Expected {expected_count} packages, got {len(package_keys)}: {package_keys}"

        # Snapshot comparison
        normalized = normalize_result(result)
        assert normalized == snapshot

    def test_batch_with_invalid_package_metadata(self, available_clients, client_runner):
        """Test batch analysis with invalid package and metadata flag"""
        workspace_root = WORKSPACE_FIXTURES["npm_workspace_with_invalid"]["root"]

        # Only test JavaScript client
        if ClientType.JAVASCRIPT not in available_clients:
            pytest.skip("JavaScript client not available")

        success, result, error_msg = client_runner.run_batch_analysis(
            ClientType.JAVASCRIPT,
            workspace_root,
            metadata=True,
        )

        assert success, f"Batch analysis failed: {error_msg}"
        assert result is not None, "Batch analysis returned None"

        # When metadata is enabled, should have metadata field
        assert "metadata" in result, "Expected metadata field in result"

        # Should have errors array with invalid package warning
        if "errors" in result["metadata"]:
            errors = result["metadata"]["errors"]
            assert len(errors) > 0, "Expected errors for invalid package"
            # Check that one error mentions the invalid package
            error_text = json.dumps(errors)
            assert "package-invalid" in error_text or "name" in error_text, \
                "Expected error about missing package name"

    def test_batch_concurrency_flag(self, available_clients, client_runner):
        """Test that batch analysis accepts concurrency flag"""
        workspace_root = WORKSPACE_FIXTURES["npm_workspace"]["root"]

        # Only test JavaScript client
        if ClientType.JAVASCRIPT not in available_clients:
            pytest.skip("JavaScript client not available")

        # Test with different concurrency values
        for concurrency in [1, 5]:
            success, result, error_msg = client_runner.run_batch_analysis(
                ClientType.JAVASCRIPT,
                workspace_root,
                concurrency=concurrency,
            )

            assert success, f"Batch analysis with concurrency={concurrency} failed: {error_msg}"
            assert result is not None, f"Batch analysis with concurrency={concurrency} returned None"

            # Just verify it runs successfully - we can't verify actual parallel behavior
            package_keys = [k for k in result.keys() if k.startswith("pkg:")]
            assert len(package_keys) > 0, "Should have at least one package"


class TestLockFileWalkUp:
    """Test suite for lock file walk-up from workspace members"""

    def test_workspace_member_finds_root_lock(self, available_clients, client_runner):
        """Test that analyzing a workspace member manifest finds lock file at workspace root"""
        from src.tester.models import AnalysisType

        member_manifest = WORKSPACE_FIXTURES["npm_workspace_member"]["member_manifest"]
        workspace_root = WORKSPACE_FIXTURES["npm_workspace_member"]["workspace_root"]

        # Only test JavaScript client
        if ClientType.JAVASCRIPT not in available_clients:
            pytest.skip("JavaScript client not available")

        # Run regular stack analysis on the workspace MEMBER manifest
        # The client should find the lock file at workspace root via --workspaceDir
        success, result, error_msg = client_runner.run_client(
            ClientType.JAVASCRIPT,
            AnalysisType.STACK,
            member_manifest,
            workspace_root=workspace_root,
        )

        # If this succeeds, it proves the client found the lock file at workspace root
        assert success, f"Analysis of workspace member failed (lock file not found?): {error_msg}"
        assert result is not None, "Analysis returned None"

        # Verify we got a valid result structure
        assert "providers" in result or "scanned" in result, \
            "Result should have providers or scanned field"
