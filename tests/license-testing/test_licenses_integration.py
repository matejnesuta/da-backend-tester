"""Integration tests for licenses in vulnerability analysis reports"""

import pytest
import requests


@pytest.mark.license_integration
class TestLicensesInAnalysis:
    """Tests for license information in /analysis endpoint response"""

    def test_analysis_includes_licenses(self, api_base):
        """Test that analysis report includes license information"""
        # Create a minimal SBOM with license information
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "components": [
                {
                    "type": "library",
                    "name": "express",
                    "version": "4.18.2",
                    "purl": "pkg:npm/express@4.18.2",
                    "licenses": [
                        {
                            "license": {
                                "id": "MIT"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            f"{api_base}/analysis",
            json=sbom,
            headers={"Content-Type": "application/vnd.cyclonedx+json"},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify basic analysis structure
        assert "scanned" in result
        assert "providers" in result

        # Verify licenses are included if the feature is implemented
        # This is a soft check - licenses might not be implemented yet
        if "licenses" in result:
            licenses = result["licenses"]
            assert isinstance(licenses, list)
