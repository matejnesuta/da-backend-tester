#!/bin/bash
#
# Generate Python virtual environments for pip ecosystem test cases.
# Intended to run inside the container after build, using the container's
# Python for platform-independent results.
#
# Creates venv/ in each test directory alongside requirements.txt.
# The venv's Python binary (venv/bin/python3) should be used by clients.
#
# Usage: generate-python-venvs.sh [testfiles-dir] [max-parallel-jobs]
#

# Allow individual venv creation to fail without stopping the script
# set -e

TESTFILES_DIR="${1:-/testfiles}"
MAX_JOBS="${2:-16}"  # Default to 16 parallel jobs

if [ ! -d "$TESTFILES_DIR" ]; then
    echo "Error: testfiles directory not found: $TESTFILES_DIR"
    exit 1
fi

echo "Generating Python virtual environments in $TESTFILES_DIR (max $MAX_JOBS parallel jobs)..."

# pip - process directories in parallel
job_count=0
for dir in "$TESTFILES_DIR"/pip/*/; do
    [ -f "$dir/requirements.txt" ] || continue
    (
        test_case=$(basename "$dir")
        echo "  pip: $test_case"

        # Remove existing venv if present
        [ -d "$dir/venv" ] && rm -rf "$dir/venv"

        # Create new virtual environment in the test directory
        if ! (cd "$dir" && python3 -m venv venv 2>&1 >/dev/null); then
            echo "    WARNING: venv creation failed for $test_case"
            exit 1
        fi

        # Install requirements using the venv's pip (retry up to 3 times)
        for attempt in 1 2 3; do
            if (cd "$dir" && ./venv/bin/pip install -q -r requirements.txt 2>&1 >/dev/null); then
                break
            elif [ $attempt -lt 3 ]; then
                echo "    WARNING: pip install attempt $attempt failed for $test_case, retrying..."
                sleep 1
            else
                echo "    WARNING: pip install failed for $test_case after 3 attempts"
            fi
        done
    ) &
    ((job_count++))

    # Wait if we've hit the job limit
    if [ $job_count -ge $MAX_JOBS ]; then
        wait -n 2>/dev/null || true
        ((job_count--))
    fi
done

# Wait for remaining jobs
wait

echo "Python virtual environment generation complete."
echo ""
echo "=== Verification ==="

# Count directories and generated venvs
pip_dirs=$(find "$TESTFILES_DIR"/pip -maxdepth 1 -type d -name "*" ! -name "pip" 2>/dev/null | wc -l)
pip_venvs=$(find "$TESTFILES_DIR"/pip -maxdepth 2 -type d -name "venv" 2>/dev/null | wc -l)
echo "PIP: $pip_venvs/$pip_dirs virtual environments generated"
