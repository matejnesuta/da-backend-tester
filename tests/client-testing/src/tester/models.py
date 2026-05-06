"""Data models for the tester"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AnalysisType(Enum):
    """Type of analysis to perform"""
    COMPONENT = "component"
    STACK = "stack"
    STACK_BATCH = "stack-batch"


class ClientType(Enum):
    """Type of client to test"""
    JAVA = "java"
    JAVASCRIPT = "javascript"


@dataclass
class TestCase:
    """Represents a single test case"""
    name: str
    ecosystem: str
    manifest_path: Path
    workspace_root: Path = None  # For workspace member tests, points to workspace root


@dataclass
class WorkspaceTestCase:
    """Represents a workspace test case for batch analysis"""
    name: str
    ecosystem: str
    workspace_root: Path
    expected_package_count: int = 0  # Number of packages expected in workspace
