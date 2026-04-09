#!/bin/bash
#
# Generate all lockfiles and virtual environments in parallel.
# Runs both generate-lockfiles.sh and generate-python-venvs.sh concurrently.
#
# Usage: generate-all.sh [testfiles-dir] [max-parallel-jobs]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTFILES_DIR="${1:-/testfiles}"
MAX_JOBS="${2:-16}"

echo "Starting parallel generation of lockfiles and virtual environments..."
echo "Testfiles directory: $TESTFILES_DIR"
echo "Max parallel jobs per package manager: $MAX_JOBS"
echo ""

# Run both scripts in parallel
"$SCRIPT_DIR/generate-lockfiles.sh" "$TESTFILES_DIR" "$MAX_JOBS" &
lockfiles_pid=$!

"$SCRIPT_DIR/generate-python-venvs.sh" "$TESTFILES_DIR" "$MAX_JOBS" &
venvs_pid=$!

# Wait for both to complete
wait $lockfiles_pid
lockfiles_exit=$?

wait $venvs_pid
venvs_exit=$?

echo ""
echo "=============================================="
if [ $lockfiles_exit -eq 0 ] && [ $venvs_exit -eq 0 ]; then
    echo "✓ All generation tasks completed successfully"
    exit 0
else
    echo "✗ Some generation tasks failed"
    [ $lockfiles_exit -ne 0 ] && echo "  - Lockfiles generation failed (exit code: $lockfiles_exit)"
    [ $venvs_exit -ne 0 ] && echo "  - Python venvs generation failed (exit code: $venvs_exit)"
    exit 1
fi
