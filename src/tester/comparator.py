"""Response comparison logic"""

import copy
from typing import Dict, Tuple, Optional


class SBOMComparator:
    """Handles backend response comparison and validation"""

    @staticmethod
    def compare_sboms(generated: Dict, expected: Dict) -> Tuple[bool, Optional[str]]:
        """
        Compare generated response with expected response

        Args:
            generated: Generated response dictionary
            expected: Expected response dictionary

        Returns:
            Tuple of (matches, diff_summary)
        """
        # Normalize both responses by removing timestamp fields
        generated_normalized = SBOMComparator._normalize_sbom(generated)
        expected_normalized = SBOMComparator._normalize_sbom(expected)

        # Compare the normalized responses
        if generated_normalized == expected_normalized:
            return True, None

        # Generate a diff summary
        diff_summary = SBOMComparator._generate_diff_summary(
            generated_normalized, expected_normalized
        )
        return False, diff_summary

    @staticmethod
    def _normalize_sbom(sbom: Dict) -> Dict:
        """
        Normalize response by removing fields that can vary between runs
        (like timestamps)
        """
        normalized = copy.deepcopy(sbom)

        # Remove timestamp from metadata if present
        if "metadata" in normalized and "timestamp" in normalized["metadata"]:
            del normalized["metadata"]["timestamp"]

        return normalized

    @staticmethod
    def _generate_diff_summary(generated: Dict, expected: Dict) -> str:
        """Generate a human-readable diff summary"""
        differences = []

        # Compare top-level keys
        gen_keys = set(generated.keys())
        exp_keys = set(expected.keys())

        if gen_keys != exp_keys:
            missing = exp_keys - gen_keys
            extra = gen_keys - exp_keys
            if missing:
                differences.append(f"Missing keys: {missing}")
            if extra:
                differences.append(f"Extra keys: {extra}")

        # Compare components count
        gen_components = len(generated.get("components", []))
        exp_components = len(expected.get("components", []))
        if gen_components != exp_components:
            differences.append(
                f"Component count mismatch: expected {exp_components}, got {gen_components}"
            )

        # Compare dependencies count
        gen_deps = len(generated.get("dependencies", []))
        exp_deps = len(expected.get("dependencies", []))
        if gen_deps != exp_deps:
            differences.append(
                f"Dependency count mismatch: expected {exp_deps}, got {gen_deps}"
            )

        # Compare spec version
        if generated.get("specVersion") != expected.get("specVersion"):
            differences.append(
                f"Spec version mismatch: expected {expected.get('specVersion')}, "
                f"got {generated.get('specVersion')}"
            )

        if not differences:
            differences.append("Responses differ in content details")

        return "; ".join(differences)
