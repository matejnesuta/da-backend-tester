"""pytest configuration and fixtures for DA backend tester"""

import os
import copy
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv
from syrupy.extensions.json import JSONSnapshotExtension

from src.tester.models import ClientType, AnalysisType
from src.tester.discovery import TestDiscovery
from src.tester.runner import ClientRunner


# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def _deep_sort(obj):
    """Recursively sort all lists and normalize numbers in a nested dict/list structure."""
    if isinstance(obj, dict):
        return {k: _deep_sort(v) for k, v in obj.items() if not (k == "warnings" and v == {})}
    if isinstance(obj, list):
        sorted_items = [_deep_sort(item) for item in obj]
        try:
            return sorted(sorted_items, key=lambda x: json.dumps(x, sort_keys=True))
        except TypeError:
            return sorted_items
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    return obj


def normalize_result(result):
    """Normalize an analysis result for comparison: remove timestamps and sort lists."""
    normalized = copy.deepcopy(result)
    if isinstance(normalized, dict):
        if "metadata" in normalized and "timestamp" in normalized["metadata"]:
            del normalized["metadata"]["timestamp"]
        normalized.pop("licenseSummary", None)
        normalized.pop("licenses", None)
    return _deep_sort(normalized)


class NormalizedAnalysisResultExtension(JSONSnapshotExtension):
    """
    Custom syrupy extension for vulnerability analysis result snapshots that normalizes data before comparison.
    This removes fields that can vary between runs (like timestamps).
    """

    def serialize(self, data, **kwargs):
        """Normalize analysis result data and serialize to JSON"""
        normalized = self._normalize_result(data)
        return super().serialize(normalized, **kwargs)

    @staticmethod
    def _normalize_result(result):
        return normalize_result(result)


@pytest.fixture
def snapshot(snapshot):
    """Configure snapshot to use our custom analysis result serializer"""
    return snapshot.use_extension(NormalizedAnalysisResultExtension)


def pytest_addoption(parser):
    """Add custom command-line options"""
    parser.addoption(
        "--testfiles-dir",
        action="store",
        default=None,
        help="Path to testfiles directory (default: /testfiles in container, ./testfiles otherwise)",
    )
    parser.addoption(
        "--java-client",
        action="store",
        default=None,
        help="Path to Java client JAR (default: TRUSTIFY_DA_JAVA_CLIENT env var)",
    )
    parser.addoption(
        "--js-client",
        action="store",
        default=None,
        help="Path to JavaScript client (default: TRUSTIFY_DA_JS_CLIENT env var)",
    )
    parser.addoption(
        "--ecosystem",
        action="append",
        default=None,
        help="Test only specific ecosystem(s) (can be specified multiple times)",
    )
    parser.addoption(
        "--client",
        action="append",
        default=None,
        help="Test only specific client(s): java or javascript (can be specified multiple times)",
    )


@pytest.fixture(scope="session")
def testfiles_dir(request):
    """Get the testfiles directory path"""
    custom_dir = request.config.getoption("--testfiles-dir")
    if custom_dir:
        return Path(custom_dir)

    # Default to /testfiles if running in container, otherwise ./testfiles
    default_testfiles = Path("/testfiles") if Path("/testfiles").exists() else Path(__file__).parent / "testfiles"
    return default_testfiles


@pytest.fixture(scope="session")
def java_client_path(request):
    """Get the Java client path from CLI or environment"""
    cli_path = request.config.getoption("--java-client")
    return cli_path or os.getenv("TRUSTIFY_DA_JAVA_CLIENT")


@pytest.fixture(scope="session")
def js_client_path(request):
    """Get the JavaScript client path from CLI or environment"""
    cli_path = request.config.getoption("--js-client")
    return cli_path or os.getenv("TRUSTIFY_DA_JS_CLIENT")


@pytest.fixture(scope="session")
def backend_url():
    """Get the backend URL from environment"""
    return os.getenv("TRUSTIFY_DA_BACKEND_URL")


@pytest.fixture(scope="session")
def client_runner(java_client_path, js_client_path, backend_url):
    """Create a ClientRunner instance"""
    # Set environment variable for Python virtual env support
    # This allows the JavaScript client to handle Python projects by creating virtual envs
    if not os.getenv("TRUSTIFY_DA_PYTHON_VIRTUAL_ENV"):
        os.environ["TRUSTIFY_DA_PYTHON_VIRTUAL_ENV"] = "true"

    return ClientRunner(java_client_path, js_client_path, backend_url)


@pytest.fixture(scope="session")
def all_test_cases(testfiles_dir, request):
    """Discover all test cases"""
    test_cases = TestDiscovery.discover_test_cases(testfiles_dir)

    # Filter by ecosystem if specified
    ecosystems = request.config.getoption("--ecosystem")
    if ecosystems:
        test_cases = [tc for tc in test_cases if tc.ecosystem in ecosystems]

    return test_cases


@pytest.fixture(scope="session")
def available_clients(request, java_client_path, js_client_path):
    """Determine which clients are available to test"""
    # Check if specific clients were requested
    requested_clients = request.config.getoption("--client")

    clients = []
    if java_client_path and (not requested_clients or "java" in requested_clients):
        clients.append(ClientType.JAVA)
    if js_client_path and (not requested_clients or "javascript" in requested_clients):
        clients.append(ClientType.JAVASCRIPT)

    return clients


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "component: mark test as component analysis test"
    )
    config.addinivalue_line(
        "markers", "stack: mark test as stack analysis test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test parameters
        if hasattr(item, 'callspec'):
            params = item.callspec.params

            if 'analysis_type' in params:
                analysis_type = params['analysis_type']
                if analysis_type == AnalysisType.COMPONENT:
                    item.add_marker(pytest.mark.component)
                elif analysis_type == AnalysisType.STACK:
                    item.add_marker(pytest.mark.stack)
