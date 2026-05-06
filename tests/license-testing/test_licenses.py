"""Pytest tests for license functionality"""

import pytest
import requests


@pytest.mark.license_api
class TestLicensesEndpoint:
    """Tests for the /licenses POST endpoint"""

    def test_fetch_licenses_for_purls(self, api_base):
        """Test fetching licenses for a set of package URLs"""
        # Test with common packages that have well-known licenses
        request_data = {
            "purls": [
                "pkg:maven/commons-io/commons-io@2.11.0",
                "pkg:npm/express@4.18.2",
                "pkg:pypi/requests@2.28.1",
            ]
        }

        response = requests.post(
            f"{api_base}/licenses",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        result = response.json()
        assert isinstance(result, list), "Response should be a list of LicenseProviderResult"

        # Verify structure
        if len(result) > 0:
            provider_result = result[0]
            assert "status" in provider_result
            assert "summary" in provider_result
            assert "packages" in provider_result

            # Verify status structure
            status = provider_result["status"]
            assert "ok" in status
            assert "name" in status
            assert "code" in status
            assert "message" in status

            # Verify summary structure
            summary = provider_result["summary"]
            assert "total" in summary
            assert "concluded" in summary
            assert "permissive" in summary
            assert "weakCopyleft" in summary
            assert "strongCopyleft" in summary
            assert "unknown" in summary

            # Verify packages structure
            packages = provider_result["packages"]
            assert isinstance(packages, dict)

            # Check that we got results for our requested PURLs
            for purl in request_data["purls"]:
                if purl in packages:
                    pkg_license = packages[purl]
                    # Each package should have concluded and/or evidence
                    assert "concluded" in pkg_license or "evidence" in pkg_license

    def test_fetch_licenses_empty_purls(self, api_base):
        """Test with empty PURLs list"""
        request_data = {"purls": []}

        response = requests.post(
            f"{api_base}/licenses",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    def test_fetch_licenses_invalid_purl(self, api_base):
        """Test with invalid PURL format"""
        request_data = {
            "purls": [
                "not-a-valid-purl",
            ]
        }

        response = requests.post(
            f"{api_base}/licenses",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )

        # May return 200 with error in status, or 422 for invalid request
        assert response.status_code in [200, 422]

    def test_fetch_licenses_mixed_ecosystems(self, api_base):
        """Test fetching licenses from multiple package ecosystems"""
        request_data = {
            "purls": [
                "pkg:maven/org.apache.commons/commons-lang3@3.12.0",
                "pkg:npm/lodash@4.17.21",
                "pkg:pypi/django@4.2.0",
                "pkg:golang/github.com/gin-gonic/gin@v1.9.0",
            ]
        }

        response = requests.post(
            f"{api_base}/licenses",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    def test_fetch_licenses_copyleft_packages(self, api_base):
        """Test packages with copyleft licenses"""
        request_data = {
            "purls": [
                # GPL packages (strong copyleft)
                "pkg:pypi/ansible@2.9.27",
                # LGPL packages (weak copyleft)
                "pkg:maven/org.hibernate/hibernate-core@5.6.0.Final",
            ]
        }

        response = requests.post(
            f"{api_base}/licenses",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify we got copyleft categories
        if len(result) > 0 and "summary" in result[0]:
            summary = result[0]["summary"]
            # At least one should be categorized as copyleft
            assert (summary.get("weakCopyleft", 0) + summary.get("strongCopyleft", 0)) > 0


@pytest.mark.license_api
class TestLicenseSpdxEndpoint:
    """Tests for the /licenses/{spdxExpression} GET endpoint"""

    @pytest.mark.parametrize("spdx_id,expected_category", [
        # Permissive licenses
        ("MIT", "PERMISSIVE"),
        ("Apache-2.0", "PERMISSIVE"),
        ("BSD-2-Clause", "PERMISSIVE"),
        ("BSD-3-Clause", "PERMISSIVE"),
        ("ISC", "PERMISSIVE"),
        ("Zlib", "PERMISSIVE"),
        ("Artistic-2.0", "PERMISSIVE"),
        ("0BSD", "PERMISSIVE"),
        ("BSL-1.0", "PERMISSIVE"),
        # Weak copyleft licenses
        ("LGPL-2.0", "WEAK_COPYLEFT"),
        ("LGPL-2.1", "WEAK_COPYLEFT"),
        ("LGPL-3.0", "WEAK_COPYLEFT"),
        ("MPL-2.0", "WEAK_COPYLEFT"),
        ("EPL-1.0", "WEAK_COPYLEFT"),
        ("EPL-2.0", "WEAK_COPYLEFT"),
        ("CDDL-1.0", "WEAK_COPYLEFT"),
        ("CDDL-1.1", "WEAK_COPYLEFT"),
        # Strong copyleft licenses
        ("GPL-2.0", "STRONG_COPYLEFT"),
        ("GPL-3.0", "STRONG_COPYLEFT"),
        ("AGPL-3.0", "STRONG_COPYLEFT"),
    ])
    def test_fetch_license_by_spdx(self, api_base, spdx_id, expected_category):
        """Test fetching license information by SPDX identifier"""
        response = requests.get(f"{api_base}/licenses/{spdx_id}")

        assert response.status_code == 200, f"Expected 200 for {spdx_id}, got {response.status_code}: {response.text}"

        result = response.json()

        # Verify structure
        assert "identifiers" in result
        assert "expression" in result
        assert "name" in result
        assert "category" in result

        # Verify the category matches expected
        assert result["category"] == expected_category, \
            f"Expected {spdx_id} to be {expected_category}, got {result['category']}"

        # Verify identifiers structure
        identifiers = result["identifiers"]
        assert isinstance(identifiers, list)
        if len(identifiers) > 0:
            identifier = identifiers[0]
            assert "id" in identifier
            assert "name" in identifier
            assert "category" in identifier
            assert "isDeprecated" in identifier
            assert "isOsiApproved" in identifier
            assert "isFsfLibre" in identifier

    def test_fetch_license_not_found(self, api_base):
        """Test fetching non-existent license returns UNKNOWN category"""
        response = requests.get(f"{api_base}/licenses/NONEXISTENT-LICENSE-ID")
        assert response.status_code == 200

        result = response.json()
        assert result["category"] == "UNKNOWN", \
            f"Non-existent license should be categorized as UNKNOWN, got {result['category']}"
        assert result["expression"] == "NONEXISTENT-LICENSE-ID"
        assert result["name"] == "NONEXISTENT-LICENSE-ID"


@pytest.mark.license_api
class TestLicenseExceptionSuffixes:
    """Tests for exception suffixes that convert strong copyleft to weak copyleft"""

    @pytest.mark.parametrize("license_with_exception", [
        # Test all exception suffixes from spec using proper SPDX format
        # Format: "LICENSE WITH EXCEPTION" (space-separated, uppercase WITH)
        "GPL-2.0-or-later WITH Classpath-exception-2.0",
        "GPL-2.0-only WITH Classpath-exception-2.0",
        "GPL-2.0-or-later WITH GCC-exception-2.0",
        "GPL-3.0-or-later WITH GCC-exception-3.1",
        "GPL-2.0-or-later WITH CLISP-exception-2.0",
        "GPL-2.0-or-later WITH i2p-gpl-java-exception",
        "GPL-2.0-or-later WITH Libtool-exception",
        "GPL-3.0-or-later WITH OCCT-exception-1.0",
        "GPL-2.0-or-later WITH openvpn-openssl-exception",
        "GPL-2.0-or-later WITH Nokia-Qt-exception-1.1",
    ])
    def test_exception_suffixes_convert_to_weak_copyleft(self, api_base, license_with_exception):
        """Test that GPL licenses with exception suffixes are categorized as WEAK_COPYLEFT"""
        response = requests.get(f"{api_base}/licenses/{license_with_exception}")

        assert response.status_code == 200, \
            f"Expected 200 for {license_with_exception}, got {response.status_code}: {response.text}"

        result = response.json()

        # Licenses with exception suffixes should be weak copyleft, not strong
        assert result["category"] == "WEAK_COPYLEFT", \
            f"Expected {license_with_exception} to be WEAK_COPYLEFT (due to exception), got {result['category']}"


@pytest.mark.license_api
class TestLicenseCategorization:
    """Tests for license categorization logic"""

    def test_permissive_licenses(self, api_base):
        """Test that permissive licenses are correctly categorized"""
        permissive_licenses = [
            "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC",
            "Apache-2.0", "Zlib", "Artistic-2.0", "0BSD", "BSL-1.0"
        ]

        for license_id in permissive_licenses:
            response = requests.get(f"{api_base}/licenses/{license_id}")

            if response.status_code == 200:
                result = response.json()
                assert result["category"] == "PERMISSIVE", \
                    f"{license_id} should be PERMISSIVE, got {result['category']}"

    def test_weak_copyleft_licenses(self, api_base):
        """Test that weak copyleft licenses are correctly categorized"""
        weak_copyleft_licenses = [
            "LGPL-2.0", "LGPL-2.1", "LGPL-3.0",
            "MPL-2.0", "EPL-1.0", "EPL-2.0",
            "CDDL-1.0", "CDDL-1.1"
        ]

        for license_id in weak_copyleft_licenses:
            response = requests.get(f"{api_base}/licenses/{license_id}")

            if response.status_code == 200:
                result = response.json()
                assert result["category"] == "WEAK_COPYLEFT", \
                    f"{license_id} should be WEAK_COPYLEFT, got {result['category']}"

    def test_strong_copyleft_licenses(self, api_base):
        """Test that strong copyleft licenses are correctly categorized"""
        strong_copyleft_licenses = [
            "GPL-2.0", "GPL-3.0", "AGPL-3.0"
        ]

        for license_id in strong_copyleft_licenses:
            response = requests.get(f"{api_base}/licenses/{license_id}")

            if response.status_code == 200:
                result = response.json()
                assert result["category"] == "STRONG_COPYLEFT", \
                    f"{license_id} should be STRONG_COPYLEFT, got {result['category']}"
