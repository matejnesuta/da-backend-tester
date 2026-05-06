"""Pytest configuration - routes to appropriate test suite configs"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def pytest_configure(config):
    """Configure pytest based on which test suite is being run"""
    # Determine which suite by checking the test paths
    test_paths = [str(p) for p in config.args if not p.startswith('-')]

    if any('license-testing' in p for p in test_paths):
        config.option.markexpr = config.option.markexpr or ''
    elif any('client-testing' in p for p in test_paths):
        config.option.markexpr = config.option.markexpr or ''


# Common fixtures that both suites can use

@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def backend_url():
    """Get the backend URL from environment (used by license tests)"""
    url = os.getenv("TRUSTIFY_DA_BACKEND_URL")
    if not url:
        pytest.skip("TRUSTIFY_DA_BACKEND_URL not set")
    return url.rstrip("/")


@pytest.fixture(scope="session")
def api_base(backend_url):
    """Get the API base URL (used by license tests)"""
    return f"{backend_url}/api/v5"


@pytest.fixture(scope="session")
def license_samples_dir(project_root):
    """Get the directory containing license sample files"""
    return project_root / "tests" / "license-testing" / "testfiles"
