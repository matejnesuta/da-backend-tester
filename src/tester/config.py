"""Configuration for the tester"""

from typing import Dict, List

# Manifest file patterns for each ecosystem
MANIFEST_PATTERNS: Dict[str, List[str]] = {
    "maven": ["pom.xml"],
    "gradle-groovy": ["build.gradle"],
    "gradle-kotlin": ["build.gradle.kts"],
    "golang": ["go.mod"],
    "npm": ["package.json"],
    "pip": ["requirements.txt"],
    "pnpm": ["package.json"],
    "yarn-berry": ["package.json"],
    "yarn-classic": ["package.json"],
    "cargo": ["Cargo.toml"],
}

# Default timeout for client execution (in seconds)
DEFAULT_TIMEOUT = 300
