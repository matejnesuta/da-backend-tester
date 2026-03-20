"""Client runner for executing Trustify DA clients"""

import json
import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from .models import AnalysisType, ClientType
from .config import DEFAULT_TIMEOUT


class ClientRunner:
    """Handles execution of Trustify DA clients"""

    def __init__(self, java_client: Optional[str] = None, js_client: Optional[str] = None, backend_url: Optional[str] = None):
        """
        Initialize the client runner

        Args:
            java_client: Path to Java client JAR
            js_client: Path to JavaScript client executable
            backend_url: URL of the Trustify DA backend
        """
        # Expand paths (handles ~ and environment variables)
        self.java_client = os.path.expanduser(java_client) if java_client else None
        self.js_client = os.path.expanduser(js_client) if js_client else None
        self.backend_url = backend_url

    def run_client(
        self,
        client_type: ClientType,
        analysis_type: AnalysisType,
        manifest_path: Path,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Run the specified client and return the SBOM output

        Args:
            client_type: Which client to run (Java or JavaScript)
            analysis_type: Type of analysis (component or stack)
            manifest_path: Path to the manifest file
            timeout: Timeout in seconds (default: 300)

        Returns:
            Tuple of (success, sbom_dict, error_message)
        """
        if client_type == ClientType.JAVA:
            client_path = self.java_client
        else:
            client_path = self.js_client

        if not client_path:
            return False, None, f"{client_type.value} client path not configured"

        # Copy the entire test directory to a temporary location
        # This allows build tools (Gradle, Maven, etc.) to write cache files
        temp_dir = None
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp(prefix="trustify-test-")
            temp_path = Path(temp_dir)

            # Copy the entire test case directory, excluding build caches
            # Stale .gradle caches (from a different Gradle version) can break
            # features like version catalog auto-discovery
            test_dir = manifest_path.parent
            temp_test_dir = temp_path / test_dir.name
            shutil.copytree(
                test_dir, temp_test_dir, symlinks=True,
                ignore=shutil.ignore_patterns(
                    '.gradle', 'build', 'target', 'node_modules', '__pycache__',
                ),
            )

            # Get the new manifest path in the temp directory
            temp_manifest = temp_test_dir / manifest_path.name

            # Build the command
            cmd = self._build_command(client_type, client_path, analysis_type, temp_manifest)

            # Prepare environment with backend URL
            env = os.environ.copy()
            if self.backend_url:
                env['TRUSTIFY_DA_BACKEND_URL'] = self.backend_url

            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )

            if result.returncode != 0:
                return False, None, f"Command failed (exit code {result.returncode}): {result.stderr}"

            # Parse the JSON output
            try:
                sbom = json.loads(result.stdout)
                return True, sbom, None
            except json.JSONDecodeError as e:
                return False, None, f"Failed to parse JSON output: {e}"

        except subprocess.TimeoutExpired:
            return False, None, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, None, f"Unexpected error: {e}"
        finally:
            # Clean up temporary directory
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def _build_command(
        client_type: ClientType,
        client_path: str,
        analysis_type: AnalysisType,
        manifest_path: Path,
    ) -> list:
        """Build the command to execute the client"""
        if client_type == ClientType.JAVA:
            # Assume it's a JAR file
            return ["java", "-jar", client_path, analysis_type.value, str(manifest_path)]
        else:
            # Assume it's an executable or script
            return [client_path, analysis_type.value, str(manifest_path)]
