"""Configuration for the tester"""

from typing import Dict, List

# Manifest file patterns for each ecosystem
MANIFEST_PATTERNS: Dict[str, List[str]] = {
    "maven": ["pom.xml"],
    "gradle": ["build.gradle", "build.gradle.kts"],
    "golang": ["go.mod"],
    "npm": ["package.json"],
    "pip": ["requirements.txt"],
    "pnpm": ["package.json"],
    "yarn-berry": ["package.json"],
    "yarn-classic": ["package.json"],
}

# Expected SBOM file name patterns
EXPECTED_SBOM_PATTERNS: Dict[str, List[str]] = {
    "component": [
        "component_analysis_expected_sbom.json",
        "expected_component_sbom.json",
        "expected_sbom_component_analysis.json",
    ],
    "stack": [
        "stack_analysis_expected_sbom.json",
        "expected_stack_sbom.json",
        "expected_sbom_stack_analysis.json",
    ],
}

# Default timeout for client execution (in seconds)
DEFAULT_TIMEOUT = 300
