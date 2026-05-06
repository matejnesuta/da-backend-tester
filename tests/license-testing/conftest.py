"""Pytest configuration for license testing suite"""

import pytest
from pathlib import Path


def pytest_configure(config):
    """Configure pytest markers for license tests"""
    config.addinivalue_line(
        "markers", "license_api: tests for license API endpoints"
    )
    config.addinivalue_line(
        "markers", "license_integration: tests for license integration with analysis"
    )
    config.addinivalue_line(
        "markers", "license_files: tests for license file identification"
    )


@pytest.fixture(scope="session")
def license_samples_dir():
    """Get the license samples directory"""
    return Path(__file__).parent / "testfiles"
