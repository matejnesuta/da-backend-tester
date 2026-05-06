#!/bin/bash
#
# Wrapper script to run tests in a container
# Supports both Docker and Podman
#
# Usage:
#   ./run-in-container.sh [--suite client|license] [pytest arguments]
#
# Test Suites:
#   client (default) - Client validation tests (requires DA clients)
#   license          - License API tests (requires backend running)
#
# Examples:
#   ./run-in-container.sh                      # Run client tests (default)
#   ./run-in-container.sh --suite client       # Run client tests explicitly
#   ./run-in-container.sh --suite license      # Run license API tests
#   ./run-in-container.sh --ecosystem maven    # Run client tests for maven
#   ./run-in-container.sh --suite license -v   # Run license tests verbosely
#
# Optional: Override built-in clients for client testing:
#   export TRUSTIFY_DA_JAVA_CLIENT=/path/to/client.jar
#   export TRUSTIFY_DA_JS_CLIENT=/path/to/js-client
#   ./run-in-container.sh
#

set -e

# Load .env file if it exists
if [ -f "$(dirname "${BASH_SOURCE[0]}")/.env" ]; then
    set -a
    source "$(dirname "${BASH_SOURCE[0]}")/.env"
    set +a
fi

# Detect container runtime (podman or docker)
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
else
    echo "Error: Neither podman nor docker found in PATH"
    exit 1
fi

show_help() {
    cat << 'EOF'
Trustify DA Backend Tester - Container Runner

Usage:
    ./run-in-container.sh [--suite <suite>] [pytest arguments]

Options:
    --suite <suite>    Choose test suite: 'client' (default) or 'license'
    -h, --help         Show this help message

Test Suites:
    client (default)   Test DA clients against backend using ecosystem manifests
                       Requires: DA clients (built-in or via env vars)

    license            Test backend license API endpoints directly
                       Requires: TRUSTIFY_DA_BACKEND_URL environment variable

Examples:
    # Client tests (default)
    ./run-in-container.sh
    ./run-in-container.sh --ecosystem maven
    ./run-in-container.sh --client java --ecosystem npm

    # License tests
    export TRUSTIFY_DA_BACKEND_URL=https://backend-url
    ./run-in-container.sh --suite license
    ./run-in-container.sh --suite license -v
    ./run-in-container.sh --suite license -m license_api

Environment Variables:
    TRUSTIFY_DA_BACKEND_URL       Backend URL (required for license tests)
    TRUSTIFY_DA_JAVA_CLIENT       Override Java client JAR path
    TRUSTIFY_DA_JS_CLIENT         Override JavaScript client path

Pytest Help:
    For pytest-specific options, use: ./run-in-container.sh [--suite <suite>] --help
EOF
}

# Check for help flag first
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

echo "Using container runtime: $CONTAINER_RUNTIME"

# Parse --suite parameter
TEST_SUITE="client"  # default
if [ "$1" = "--suite" ]; then
    shift
    TEST_SUITE="$1"
    shift
    if [[ ! "$TEST_SUITE" =~ ^(client|license)$ ]]; then
        echo "Error: Invalid suite '$TEST_SUITE'. Must be 'client' or 'license'"
        exit 1
    fi
fi

echo "Test suite: $TEST_SUITE"

# Configuration
IMAGE_NAME="trustify-da-tester"
IMAGE_TAG="latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Suite-specific paths
if [ "$TEST_SUITE" = "client" ]; then
    TESTFILES_DIR="${SCRIPT_DIR}/tests/client-testing/testfiles"
    TEST_PATH="tests/client-testing"
    SNAPSHOTS_DIR="${SCRIPT_DIR}/tests/client-testing/__snapshots__"
else
    TESTFILES_DIR="${SCRIPT_DIR}/tests/license-testing/testfiles"
    TEST_PATH="tests/license-testing"
    SNAPSHOTS_DIR=""  # License tests don't use snapshots
fi

JAVA_CLIENT="${TRUSTIFY_DA_JAVA_CLIENT:-}"
JS_CLIENT="${TRUSTIFY_DA_JS_CLIENT:-}"

# Check if image exists
if ! $CONTAINER_RUNTIME image inspect "${IMAGE_NAME}:${IMAGE_TAG}" &> /dev/null; then
    echo "Error: Container image '${IMAGE_NAME}:${IMAGE_TAG}' not found."
    echo "Build it first with: ./manage-container.sh build"
    exit 1
fi

# Prepare volume mounts and environment variables
VOLUME_ARGS=()
ENV_ARGS=()

# Mount testfiles directory
if [ -d "$TESTFILES_DIR" ]; then
    VOLUME_ARGS+=(-v "${TESTFILES_DIR}:/testfiles:z")
else
    echo "Warning: testfiles directory not found at ${TESTFILES_DIR}"
fi

# Mount snapshots directory for client tests only
if [ "$TEST_SUITE" = "client" ]; then
    mkdir -p "$SNAPSHOTS_DIR"
    VOLUME_ARGS+=(-v "${SNAPSHOTS_DIR}:/app/tests/client-testing/__snapshots__:z")
fi

# Optional: Override built-in clients with custom versions
# Mount Java client if configured
if [ -n "$JAVA_CLIENT" ] && [ -f "$JAVA_CLIENT" ]; then
    # Mount the JAR file directly into the container
    VOLUME_ARGS+=(-v "${JAVA_CLIENT}:/clients/java-client.jar:ro,z")
    # Tell the container where to find it
    ENV_ARGS+=(-e "TRUSTIFY_DA_JAVA_CLIENT=/clients/java-client.jar")
    echo "Using custom Java client: $JAVA_CLIENT -> /clients/java-client.jar"
fi

# Mount JavaScript client if configured
if [ -n "$JS_CLIENT" ] && [ -f "$JS_CLIENT" ]; then
    # Mount the executable directly into the container
    VOLUME_ARGS+=(-v "${JS_CLIENT}:/clients/js-client:ro,z")
    # Tell the container where to find it
    ENV_ARGS+=(-e "TRUSTIFY_DA_JS_CLIENT=/clients/js-client")
    echo "Using custom JavaScript client: $JS_CLIENT -> /clients/js-client"
fi

# Pass backend URL if configured
if [ -n "${TRUSTIFY_DA_BACKEND_URL:-}" ]; then
    ENV_ARGS+=(-e "TRUSTIFY_DA_BACKEND_URL=${TRUSTIFY_DA_BACKEND_URL}")
    echo "Using backend URL: ${TRUSTIFY_DA_BACKEND_URL}"
fi

# Info messages
if [ "$TEST_SUITE" = "client" ]; then
    if [ ${#ENV_ARGS[@]} -eq 0 ]; then
        echo "Using built-in clients from container image"
        echo "(Set TRUSTIFY_DA_JAVA_CLIENT or TRUSTIFY_DA_JS_CLIENT to override)"
        echo ""
    fi
else
    echo "License tests require TRUSTIFY_DA_BACKEND_URL to be set"
    if [ -z "${TRUSTIFY_DA_BACKEND_URL:-}" ]; then
        echo "Warning: TRUSTIFY_DA_BACKEND_URL not set - tests will be skipped"
    fi
    echo ""
fi

# Run the container
echo "Running ${TEST_SUITE} tests in container..."
echo ""
$CONTAINER_RUNTIME run --rm \
    --network host \
    "${VOLUME_ARGS[@]}" \
    "${ENV_ARGS[@]}" \
    "${IMAGE_NAME}:${IMAGE_TAG}" \
    "${TEST_PATH}" "$@"
