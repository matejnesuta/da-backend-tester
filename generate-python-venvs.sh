#!/bin/bash
#
# Generate Python virtual environments for pip ecosystem test cases.
# Intended to run inside the container after build, using the container's
# Python for platform-independent results.
#
# Creates venv/ in each test directory alongside requirements.txt.
# The venv's Python binary (venv/bin/python3) should be used by clients.
#
# Usage: generate-python-venvs.sh [testfiles-dir]
#

set -e

TESTFILES_DIR="${1:-/testfiles}"

if [ ! -d "$TESTFILES_DIR" ]; then
    echo "Error: testfiles directory not found: $TESTFILES_DIR"
    exit 1
fi

echo "Generating Python virtual environments in $TESTFILES_DIR..."

# pip
for dir in "$TESTFILES_DIR"/pip/*/; do
    [ -f "$dir/requirements.txt" ] || continue
    test_case=$(basename "$dir")
    echo "  pip: $test_case"

    # Remove existing venv if present
    [ -d "$dir/venv" ] && rm -rf "$dir/venv"

    # Create new virtual environment in the test directory
    (cd "$dir" && python3 -m venv venv 2>/dev/null) || {
        echo "    WARNING: venv creation failed for $test_case"
        continue
    }

    # Install requirements using the venv's pip
    (cd "$dir" && ./venv/bin/pip install -q -r requirements.txt 2>/dev/null) || \
        echo "    WARNING: pip install failed for $test_case"
done

echo "Python virtual environment generation complete."
