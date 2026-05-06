"""Tests for license identification using sample license files"""

import pytest
import requests


@pytest.mark.license_files
class TestLicenseIdentificationFromFiles:
    """Tests for /licenses/identify endpoint using sample license files"""

    @pytest.mark.parametrize("license_file,expected_id,expected_category", [
        # Permissive licenses
        ("LICENSE-MIT", "MIT", "PERMISSIVE"),
        ("LICENSE-Apache-2.0", "Apache-2.0", "PERMISSIVE"),
        ("LICENSE-BSD-3-Clause", "BSD-3-Clause", "PERMISSIVE"),
        ("LICENSE-Artistic-2.0", "Artistic-2.0", "PERMISSIVE"),
        ("LICENSE-0BSD", "0BSD", "PERMISSIVE"),
        # Weak copyleft licenses
        ("LICENSE-LGPL-2.1", "LGPL-2.1", "WEAK_COPYLEFT"),
        ("LICENSE-LGPL-3.0", "LGPL-3.0", "WEAK_COPYLEFT"),
        # Strong copyleft licenses
        ("LICENSE-GPL-2.0", "GPL-2.0", "STRONG_COPYLEFT"),
        ("LICENSE-GPL-3.0", "GPL-3.0", "STRONG_COPYLEFT"),
        ("LICENSE-AGPL-3.0", "AGPL-3.0", "STRONG_COPYLEFT"),
    ])
    def test_identify_license_from_file(
        self, api_base, license_samples_dir, license_file, expected_id, expected_category
    ):
        """Test identifying various licenses from their full text files"""
        license_path = license_samples_dir / license_file

        if not license_path.exists():
            pytest.skip(f"License file not found: {license_path}")

        with open(license_path, 'rb') as f:
            files = {
                'file': (license_file, f, 'text/plain')
            }

            response = requests.post(
                f"{api_base}/licenses/identify",
                files=files
            )

        assert response.status_code == 200, \
            f"Expected 200 for {license_file}, got {response.status_code}: {response.text}"

        result = response.json()

        # Verify structure
        assert "id" in result, "Response should have 'id' field"
        assert "name" in result, "Response should have 'name' field"
        assert "category" in result, "Response should have 'category' field"

        # Verify the license was identified correctly
        # The ID might have variations (e.g., GPL-3.0-only vs GPL-3.0)
        assert expected_id in result["id"] or result["id"] in expected_id, \
            f"Expected ID containing '{expected_id}', got '{result['id']}'"

        assert result["category"] == expected_category, \
            f"Expected category {expected_category}, got {result['category']}"
