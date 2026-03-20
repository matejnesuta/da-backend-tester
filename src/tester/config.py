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

# Default timeout for client execution (in seconds)
DEFAULT_TIMEOUT = 300
