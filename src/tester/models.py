"""Data models for the tester"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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
