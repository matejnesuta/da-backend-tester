#!/usr/bin/env python3
"""
Trustify DA Backend Tester - Main entry point
"""

import os
import sys
import argparse
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed. Install it with: pip install python-dotenv")
    print("Or export environment variables manually.")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tester import Tester, ClientType


def main():
    parser = argparse.ArgumentParser(
        description="Test Trustify DA clients for SBOM generation"
    )
    # Default to /testfiles if running in container, otherwise ./testfiles
    default_testfiles = Path("/testfiles") if Path("/testfiles").exists() else Path(__file__).parent / "testfiles"
    parser.add_argument(
        "--testfiles-dir",
        type=Path,
        default=default_testfiles,
        help="Path to testfiles directory (default: /testfiles in container, ./testfiles otherwise)",
    )
    parser.add_argument(
        "--java-client",
        type=str,
        help="Path to Java client JAR (default: TRUSTIFY_DA_JAVA_CLIENT env var)",
    )
    parser.add_argument(
        "--js-client",
        type=str,
        help="Path to JavaScript client (default: TRUSTIFY_DA_JS_CLIENT env var)",
    )
    parser.add_argument(
        "--ecosystem",
        action="append",
        help="Test only specific ecosystem(s) (can be specified multiple times)",
    )
    parser.add_argument(
        "--client",
        choices=["java", "javascript"],
        action="append",
        help="Test only specific client(s) (can be specified multiple times)",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration and exit",
    )
    parser.add_argument(
        "--update-failed",
        action="store_true",
        help="Re-run and update snapshots for previously failed tests only",
    )
    parser.add_argument(
        "--source",
        choices=["java", "javascript"],
        default="java",
        help="Which client to use as source for snapshot updates (default: java)",
    )
    parser.add_argument(
        "--failures-file",
        type=Path,
        default=None,
        help="Path to failures cache file (default: <testfiles-dir>/.test-failures.json)",
    )

    args = parser.parse_args()

    # Set default failures file path inside testfiles directory
    # This ensures it's accessible both in container and on host
    if args.failures_file is None:
        # If running in container (/testfiles), put it there
        # If running locally (./testfiles), put it in project root
        if str(args.testfiles_dir) == "/testfiles":
            args.failures_file = Path("/testfiles/.test-failures.json")
        else:
            args.failures_file = Path(__file__).parent / ".test-failures.json"

    # Get client paths from args or environment
    java_client = args.java_client or os.getenv("TRUSTIFY_DA_JAVA_CLIENT")
    js_client = args.js_client or os.getenv("TRUSTIFY_DA_JS_CLIENT")
    backend_url = os.getenv("TRUSTIFY_DA_BACKEND_URL")

    # Check configuration if requested
    if args.check_config:
        print("\n" + "=" * 80)
        print("CONFIGURATION CHECK")
        print("=" * 80)
        print(f"Java client:       {java_client if java_client else 'NOT CONFIGURED'}")
        if java_client:
            exists = Path(java_client).exists()
            print(f"  Exists: {'Yes' if exists else 'No - FILE NOT FOUND'}")
        print(f"JavaScript client: {js_client if js_client else 'NOT CONFIGURED'}")
        if js_client:
            exists = Path(js_client).exists()
            print(f"  Exists: {'Yes' if exists else 'No - FILE NOT FOUND'}")
        print(f"Backend URL:       {backend_url if backend_url else 'NOT CONFIGURED'}")
        print(f"Testfiles dir:     {args.testfiles_dir}")
        exists = args.testfiles_dir.exists()
        print(f"  Exists: {'Yes' if exists else 'No - DIRECTORY NOT FOUND'}")
        print("=" * 80)

        if not java_client and not js_client:
            print("\nNo clients configured!")
            print("\nTo fix this, either:")
            print("1. Create a .env file with TRUSTIFY_DA_JAVA_CLIENT and/or TRUSTIFY_DA_JS_CLIENT")
            print("2. Export environment variables in your shell:")
            print("   export TRUSTIFY_DA_JAVA_CLIENT=/path/to/client.jar")
            print("3. Use command-line arguments:")
            print("   ./test_runner.py --java-client /path/to/client.jar")
            sys.exit(1)
        sys.exit(0)

    # Create tester
    tester = Tester(java_client=java_client, js_client=js_client)

    # Convert client strings to ClientType enums
    clients = None
    if args.client:
        clients = [ClientType(c) for c in args.client]

    # Handle update-failed mode
    update_mode = args.update_failed
    source_client = None
    failed_tests_filter = None

    if update_mode:
        source_client = ClientType(args.source)

        # Load failed tests from cache
        if args.failures_file.exists():
            try:
                with open(args.failures_file, 'r') as f:
                    failures_data = json.load(f)
                    failed_tests_filter = failures_data.get('failures', [])

                print(f"\n⚠️  UPDATE FAILED MODE")
                print(f"Using {source_client.value} client as source for snapshots")
                print(f"Loaded {len(failed_tests_filter)} failed test(s) from {args.failures_file}")
                print(f"Testfiles directory: {args.testfiles_dir}\n")
            except Exception as e:
                print(f"Error loading failures file: {e}")
                sys.exit(1)
        else:
            print(f"\nNo failures file found at {args.failures_file}")
            print("Run tests normally first to generate failures cache")
            sys.exit(1)

    # Run tests
    results = tester.run_all_tests(
        testfiles_dir=args.testfiles_dir,
        clients=clients,
        ecosystems=args.ecosystem,
        update_mode=update_mode,
        snapshot_source=source_client,
        failed_tests_filter=failed_tests_filter,
    )

    # Print summary
    tester.print_summary(results)

    # Save failed tests to cache (unless in update mode)
    if not update_mode:
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            failures_data = {
                'timestamp': str(Path(__file__).parent),
                'total_tests': len(results),
                'failed_count': len(failed_results),
                'failures': [
                    {
                        'test_case': r.test_case.name,
                        'ecosystem': r.test_case.ecosystem,
                        'client': r.client_type.value,
                        'analysis_type': r.analysis_type.value,
                        'error': r.error_message,
                    }
                    for r in failed_results
                ]
            }
            try:
                with open(args.failures_file, 'w') as f:
                    json.dump(failures_data, f, indent=2)
                print(f"\n💾 Saved {len(failed_results)} failure(s) to {args.failures_file}")
                print(f"   Run './run-in-container.sh --update-failed' to update these snapshots")
            except Exception as e:
                print(f"\nWarning: Could not save failures file: {e}")

    # Exit with error code if any tests failed
    failed_count = sum(1 for r in results if not r.passed)
    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
