#!/bin/bash
#
# Wrapper script to run the DA backend tester in a container
# Supports both Docker and Podman
#
# The container has Trustify DA clients pre-built from source.
# You can optionally override them by setting environment variables.
#
# Usage:
#   ./run-in-container.sh [test_runner.py arguments]
#
# Examples:
#   ./run-in-container.sh --check-config
#   ./run-in-container.sh --ecosystem maven
#   ./run-in-container.sh --client java --ecosystem npm
#
# Optional: Override built-in clients with locally built versions:
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

echo "Using container runtime: $CONTAINER_RUNTIME"

# Configuration
IMAGE_NAME="trustify-da-tester"
IMAGE_TAG="latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default paths
TESTFILES_DIR="${SCRIPT_DIR}/testfiles"
JAVA_CLIENT="${TRUSTIFY_DA_JAVA_CLIENT:-}"
JS_CLIENT="${TRUSTIFY_DA_JS_CLIENT:-}"

# Build the container image if needed
build_image() {
    echo "Building container image: ${IMAGE_NAME}:${IMAGE_TAG}"

    # Pass GITHUB_TOKEN as build arg if set (for Java client Maven dependencies)
    BUILD_ARGS=()
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        BUILD_ARGS+=(--build-arg "GITHUB_TOKEN=${GITHUB_TOKEN}")
        echo "Using GITHUB_TOKEN from environment for Java client build"
    else
        echo "Note: No GITHUB_TOKEN set - Java client build may fail"
        echo "      Add GITHUB_TOKEN to .env file or export it to enable Java client build"
    fi

    $CONTAINER_RUNTIME build "${BUILD_ARGS[@]}" -t "${IMAGE_NAME}:${IMAGE_TAG}" "${SCRIPT_DIR}"
}

# Check if image exists
if ! $CONTAINER_RUNTIME image inspect "${IMAGE_NAME}:${IMAGE_TAG}" &> /dev/null; then
    echo "Image not found, building..."
    build_image
fi

# Prepare volume mounts and environment variables
VOLUME_ARGS=()
ENV_ARGS=()

# Check if --update-failed flag is present in arguments
UPDATE_MODE=false
for arg in "$@"; do
    if [ "$arg" = "--update-failed" ]; then
        UPDATE_MODE=true
        break
    fi
done

# Mount testfiles directory
# Always writable to allow failures file to be written
# (failures file is stored inside testfiles directory)
if [ -d "$TESTFILES_DIR" ]; then
    VOLUME_ARGS+=(-v "${TESTFILES_DIR}:/testfiles:z")
    if [ "$UPDATE_MODE" = true ]; then
        echo "⚠️  Mounting testfiles as READ-WRITE for snapshot updates"
    fi
else
    echo "Warning: testfiles directory not found at ${TESTFILES_DIR}"
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

# Info message about built-in clients
if [ ${#ENV_ARGS[@]} -eq 0 ]; then
    echo "Using built-in clients from container image"
    echo "(Set TRUSTIFY_DA_JAVA_CLIENT or TRUSTIFY_DA_JS_CLIENT to override)"
    echo ""
fi

# Run the container
echo "Running tests in container..."
echo ""
$CONTAINER_RUNTIME run --rm \
    "${VOLUME_ARGS[@]}" \
    "${ENV_ARGS[@]}" \
    "${IMAGE_NAME}:${IMAGE_TAG}" \
    "$@"
