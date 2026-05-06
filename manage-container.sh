#!/bin/bash
# Container management script for Trustify DA Backend Tester

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="trustify-da-tester"
IMAGE_TAG="latest"

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
else
    echo "Error: Neither podman nor docker found in PATH"
    exit 1
fi

# Load .env file if it exists
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    source "${SCRIPT_DIR}/.env"
    set +a
fi

# Functions
show_help() {
    cat << EOF
Container Management Script for Trustify DA Backend Tester

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    build       Build the container image
    rebuild     Remove existing image and build fresh
    clean       Remove the container image
    status      Show container image information
    logs        Show build logs (if available)
    help        Show this help message

Options:
    --no-cache      Build without using cache (slower, but ensures fresh build)
    --verbose       Show detailed build output

Examples:
    $0 build                  # Build the container
    $0 rebuild                # Clean and rebuild
    $0 build --no-cache       # Build from scratch without cache
    $0 clean                  # Remove container image
    $0 status                 # Check if image exists

Environment Variables:
    GITHUB_TOKEN             GitHub token for building Java client (from .env)

EOF
}

build_container() {
    local no_cache=""
    local verbose=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-cache)
                no_cache="--no-cache"
                shift
                ;;
            --verbose)
                verbose="--progress=plain"
                shift
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    echo "Building container image: ${IMAGE_NAME}:${IMAGE_TAG}"
    echo "Using container runtime: ${CONTAINER_RUNTIME}"

    # Pass GITHUB_TOKEN as build arg if set
    BUILD_ARGS=()
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        BUILD_ARGS+=(--build-arg "GITHUB_TOKEN=${GITHUB_TOKEN}")
        echo "Using GITHUB_TOKEN from environment for Java client build"
    else
        echo "Warning: No GITHUB_TOKEN set - Java client build may fail"
        echo "         Set GITHUB_TOKEN in .env file to enable Java client build"
    fi

    # Pass client repo/branch overrides if set
    [ -n "${TRUSTIFY_DA_JAVA_CLIENT_REPO:-}" ] && BUILD_ARGS+=(--build-arg "JAVA_CLIENT_REPO=${TRUSTIFY_DA_JAVA_CLIENT_REPO}")
    [ -n "${TRUSTIFY_DA_JAVA_CLIENT_BRANCH:-}" ] && BUILD_ARGS+=(--build-arg "JAVA_CLIENT_BRANCH=${TRUSTIFY_DA_JAVA_CLIENT_BRANCH}")
    [ -n "${TRUSTIFY_DA_JS_CLIENT_REPO:-}" ] && BUILD_ARGS+=(--build-arg "JS_CLIENT_REPO=${TRUSTIFY_DA_JS_CLIENT_REPO}")
    [ -n "${TRUSTIFY_DA_JS_CLIENT_BRANCH:-}" ] && BUILD_ARGS+=(--build-arg "JS_CLIENT_BRANCH=${TRUSTIFY_DA_JS_CLIENT_BRANCH}")

    # Build command
    $CONTAINER_RUNTIME build \
        ${no_cache} \
        ${verbose} \
        "${BUILD_ARGS[@]}" \
        -t "${IMAGE_NAME}:${IMAGE_TAG}" \
        -f "${SCRIPT_DIR}/deploy/Dockerfile" \
        "${SCRIPT_DIR}"

    echo ""
    echo "✓ Container image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}"

    # Generate lock files and Python venvs in parallel
    generate_all
}

generate_all() {
    local testfiles_dir="${SCRIPT_DIR}/tests/client-testing/testfiles"
    local max_jobs="${1:-16}"  # Default to 16 parallel jobs

    if [ -d "$testfiles_dir" ]; then
        echo ""
        echo "Generating lockfiles for client test suite..."
        $CONTAINER_RUNTIME run --rm \
            -v "${testfiles_dir}:/testfiles:z" \
            --entrypoint /bin/bash \
            "${IMAGE_NAME}:${IMAGE_TAG}" \
            /app/generate-all.sh /testfiles "$max_jobs"
    else
        echo "Warning: Client testfiles directory not found at ${testfiles_dir}"
        echo "Skipping lockfile generation"
    fi
}

clean_container() {
    echo "Removing container image: ${IMAGE_NAME}:${IMAGE_TAG}"

    if $CONTAINER_RUNTIME image inspect "${IMAGE_NAME}:${IMAGE_TAG}" &> /dev/null; then
        $CONTAINER_RUNTIME rmi "${IMAGE_NAME}:${IMAGE_TAG}"
        echo "✓ Container image removed"
    else
        echo "Container image not found, nothing to clean"
    fi
}

rebuild_container() {
    echo "Rebuilding container image..."
    clean_container
    echo ""
    build_container "$@"
}

show_status() {
    echo "Container Image Status"
    echo "======================"
    echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
    echo "Runtime: ${CONTAINER_RUNTIME}"
    echo ""

    if $CONTAINER_RUNTIME image inspect "${IMAGE_NAME}:${IMAGE_TAG}" &> /dev/null; then
        echo "Status: EXISTS"
        echo ""
        $CONTAINER_RUNTIME image inspect "${IMAGE_NAME}:${IMAGE_TAG}" --format='Created: {{.Created}}
Size: {{.Size}} bytes ({{.VirtualSize}} virtual)
ID: {{.Id}}'
    else
        echo "Status: NOT FOUND"
        echo ""
        echo "Run '$0 build' to create the image"
    fi
}

show_logs() {
    echo "Recent build logs not available (use 'build --verbose' for detailed output)"
    echo ""
    echo "To see detailed build output, run:"
    echo "  $0 build --verbose"
}

# Main script
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    build)
        build_container "$@"
        ;;
    rebuild)
        rebuild_container "$@"
        ;;
    clean)
        clean_container
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
