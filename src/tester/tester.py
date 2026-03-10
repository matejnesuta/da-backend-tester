"""Main tester orchestration"""

import json
from pathlib import Path
from typing import List, Optional

from .models import TestCase, TestResult, AnalysisType, ClientType
from .discovery import TestDiscovery
from .runner import ClientRunner
from .comparator import SBOMComparator


class Tester:
    """Main tester class that orchestrates test execution"""

    def __init__(self, java_client: Optional[str] = None, js_client: Optional[str] = None):
        """
        Initialize the tester

        Args:
            java_client: Path to Java client
            js_client: Path to JavaScript client
        """
        self.runner = ClientRunner(java_client, js_client)
        self.comparator = SBOMComparator()

    def run_test(
        self,
        test_case: TestCase,
        client_type: ClientType,
        analysis_type: AnalysisType,
        update_snapshot: bool = False,
    ) -> TestResult:
        """
        Run a single test

        Args:
            test_case: The test case to run
            client_type: Which client to use
            analysis_type: Type of analysis to perform
            update_snapshot: If True, update the snapshot file with current output

        Returns:
            TestResult object
        """
        # Get the expected SBOM path
        if analysis_type == AnalysisType.COMPONENT:
            expected_path = test_case.expected_component_sbom
        else:
            expected_path = test_case.expected_stack_sbom

        if not expected_path:
            return TestResult(
                test_case=test_case,
                client_type=client_type,
                analysis_type=analysis_type,
                passed=False,
                error_message=f"No expected {analysis_type.value} SBOM file found",
            )

        # Run the client
        success, generated_sbom, error_msg = self.runner.run_client(
            client_type, analysis_type, test_case.manifest_path
        )

        if not success:
            return TestResult(
                test_case=test_case,
                client_type=client_type,
                analysis_type=analysis_type,
                passed=False,
                error_message=error_msg,
            )

        # If in update mode, write the snapshot and mark as passed
        if update_snapshot:
            try:
                with open(expected_path, 'w') as f:
                    json.dump(generated_sbom, f, indent=2)
                return TestResult(
                    test_case=test_case,
                    client_type=client_type,
                    analysis_type=analysis_type,
                    passed=True,
                    error_message=None,
                )
            except Exception as e:
                return TestResult(
                    test_case=test_case,
                    client_type=client_type,
                    analysis_type=analysis_type,
                    passed=False,
                    error_message=f"Failed to update snapshot: {e}",
                )

        # Load expected SBOM for comparison
        try:
            with open(expected_path, 'r') as f:
                expected_sbom = json.load(f)
        except Exception as e:
            return TestResult(
                test_case=test_case,
                client_type=client_type,
                analysis_type=analysis_type,
                passed=False,
                error_message=f"Failed to load expected SBOM: {e}",
            )

        # Compare SBOMs
        matches, diff_summary = self.comparator.compare_sboms(generated_sbom, expected_sbom)

        return TestResult(
            test_case=test_case,
            client_type=client_type,
            analysis_type=analysis_type,
            passed=matches,
            error_message=None if matches else "SBOM mismatch",
            diff_summary=diff_summary,
        )

    def run_all_tests(
        self,
        testfiles_dir: Path,
        clients: Optional[List[ClientType]] = None,
        ecosystems: Optional[List[str]] = None,
        update_mode: bool = False,
        snapshot_source: Optional[ClientType] = None,
        failed_tests_filter: Optional[List[dict]] = None,
    ) -> List[TestResult]:
        """
        Run all tests

        Args:
            testfiles_dir: Path to testfiles directory
            clients: List of clients to test (default: all configured)
            ecosystems: List of ecosystems to test (default: all)
            update_mode: If True, update snapshot files with current outputs
            snapshot_source: Which client to use as source for snapshots (only used if update_mode=True)
            failed_tests_filter: If provided, only run tests matching these failures

        Returns:
            List of test results
        """
        # Discover test cases
        test_cases = TestDiscovery.discover_test_cases(testfiles_dir)

        # Filter by ecosystem if specified
        if ecosystems:
            test_cases = [tc for tc in test_cases if tc.ecosystem in ecosystems]

        # Determine which clients to test
        if clients is None:
            clients = []
            if self.runner.java_client:
                clients.append(ClientType.JAVA)
            if self.runner.js_client:
                clients.append(ClientType.JAVASCRIPT)

        if not clients:
            print("Error: No clients configured")
            return []

        # Run all tests
        results = []

        # If in update mode, only run the source client
        if update_mode:
            if not snapshot_source:
                print("Error: snapshot_source must be specified when update_mode=True")
                return []
            clients_to_run = [snapshot_source]
        else:
            clients_to_run = clients

        # Build list of tests to run
        tests_to_run = []
        for test_case in test_cases:
            for client in clients_to_run:
                for analysis_type in [AnalysisType.COMPONENT, AnalysisType.STACK]:
                    # If filtering by failed tests, check if this test was in the failures
                    if failed_tests_filter:
                        should_run = any(
                            f['test_case'] == test_case.name and
                            f['client'] == client.value and
                            f['analysis_type'] == analysis_type.value
                            for f in failed_tests_filter
                        )
                        if not should_run:
                            continue

                    tests_to_run.append((test_case, client, analysis_type))

        total_tests = len(tests_to_run)
        current_test = 0

        for test_case, client, analysis_type in tests_to_run:
            current_test += 1
            action = "Updating" if update_mode else "Testing"
            print(
                f"[{current_test}/{total_tests}] {action} {test_case.name} "
                f"({client.value}, {analysis_type.value})...",
                end=" ",
            )

            result = self.run_test(test_case, client, analysis_type, update_snapshot=update_mode)
            results.append(result)

            if result.passed:
                status = "UPDATED" if update_mode else "PASS"
                print(status)
            else:
                print("FAIL")
                if result.error_message:
                    print(f"    Error: {result.error_message}")
                if result.diff_summary:
                    print(f"    Diff: {result.diff_summary}")

        # If in update mode, verify all clients match the updated snapshots
        if update_mode and not failed_tests_filter:
            print("\nVerifying all clients match updated snapshots...")
            # Get unique test cases that were updated
            updated_test_cases = list(set(test_case for test_case, _, _ in tests_to_run))

            for test_case in updated_test_cases:
                print(f"\n  {test_case.name}:")
                for client in clients:
                    for analysis_type in [AnalysisType.COMPONENT, AnalysisType.STACK]:
                        result = self.run_test(test_case, client, analysis_type, update_snapshot=False)
                        results.append(result)
                        status_icon = "✓" if result.passed else "✗"
                        print(f"    {status_icon} {client.value} {analysis_type.value}")
                        if not result.passed and result.diff_summary:
                            print(f"      {result.diff_summary}")

        return results

    @staticmethod
    def print_summary(results: List[TestResult]):
        """Print a summary of test results"""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests: {total}")
        print(f"Passed: {passed} ({100 * passed // total if total > 0 else 0}%)")
        print(f"Failed: {failed} ({100 * failed // total if total > 0 else 0}%)")

        if failed > 0:
            print("\nFailed tests:")
            for result in results:
                if not result.passed:
                    print(
                        f"  - {result.test_case.name} "
                        f"({result.client_type.value}, {result.analysis_type.value})"
                    )
                    if result.error_message:
                        print(f"    {result.error_message}")
