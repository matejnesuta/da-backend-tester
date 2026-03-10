"""Data models for the tester"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class AnalysisType(Enum):
    """Type of analysis to perform"""
    COMPONENT = "component"
    STACK = "stack"


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
    expected_component_sbom: Optional[Path]
    expected_stack_sbom: Optional[Path]


@dataclass
class TestResult:
    """Represents the result of a single test"""
    test_case: TestCase
    client_type: ClientType
    analysis_type: AnalysisType
    passed: bool
    error_message: Optional[str] = None
    diff_summary: Optional[str] = None
