#!/bin/bash
#
# Generate lock files for ecosystem test cases.
# Intended to run inside the container after build, using the container's
# package managers (npm, pnpm, yarn, poetry, uv) for platform-independent results.
#
# Usage: generate-lockfiles.sh [testfiles-dir] [max-parallel-jobs]
#

# Allow individual package installs to fail without stopping the script
# set -e

TESTFILES_DIR="${1:-/testfiles}"
MAX_JOBS="${2:-16}"  # Default to 16 parallel jobs per package manager

if [ ! -d "$TESTFILES_DIR" ]; then
    echo "Error: testfiles directory not found: $TESTFILES_DIR"
    exit 1
fi

echo "Generating lock files in $TESTFILES_DIR (max $MAX_JOBS parallel jobs per package manager)..."

# Process each package manager in parallel
(
    echo "  Starting npm installations..."
    job_count=0
    for dir in "$TESTFILES_DIR"/npm/*/; do
        [ -f "$dir/package.json" ] || continue
        (
            name=$(basename "$dir")
            echo "  npm: $name"
            cd "$dir" && rm -f package-lock.json
            # Retry up to 3 times on failure
            for attempt in 1 2 3; do
                if npm install --package-lock-only --ignore-scripts 2>&1 >/dev/null; then
                    break
                elif [ $attempt -lt 3 ]; then
                    echo "    WARNING: npm install attempt $attempt failed for $name, retrying..."
                    sleep 1
                else
                    echo "    WARNING: npm install failed for $name after 3 attempts"
                fi
            done
        ) &
        ((job_count++))
        if [ $job_count -ge $MAX_JOBS ]; then
            wait -n 2>/dev/null || true
            ((job_count--))
        fi
    done
    wait
    echo "  npm installations complete"
) &
npm_pid=$!

(
    echo "  Starting pnpm installations..."
    job_count=0
    for dir in "$TESTFILES_DIR"/pnpm/*/; do
        [ -f "$dir/package.json" ] || continue
        (
            name=$(basename "$dir")
            echo "  pnpm: $name"
            cd "$dir" && rm -f pnpm-lock.yaml
            # Retry up to 3 times on failure
            for attempt in 1 2 3; do
                if pnpm install --lockfile-only --ignore-scripts 2>&1 >/dev/null; then
                    break
                elif [ $attempt -lt 3 ]; then
                    echo "    WARNING: pnpm install attempt $attempt failed for $name, retrying..."
                    sleep 1
                else
                    echo "    WARNING: pnpm install failed for $name after 3 attempts"
                fi
            done
        ) &
        ((job_count++))
        if [ $job_count -ge $MAX_JOBS ]; then
            wait -n 2>/dev/null || true
            ((job_count--))
        fi
    done
    wait
    echo "  pnpm installations complete"
) &
pnpm_pid=$!

(
    echo "  Starting yarn-classic installations..."
    # Yarn classic has cache contention issues, so use lower parallelism
    yarn_max_jobs=$((MAX_JOBS < 4 ? MAX_JOBS : 4))
    job_count=0
    for dir in "$TESTFILES_DIR"/yarn-classic/*/; do
        [ -f "$dir/package.json" ] || continue
        (
            name=$(basename "$dir")
            echo "  yarn-classic: $name"
            cd "$dir" && rm -f yarn.lock
            # Retry up to 3 times on failure
            for attempt in 1 2 3; do
                if yarn install --ignore-scripts 2>&1 >/dev/null; then
                    break
                elif [ $attempt -lt 3 ]; then
                    echo "    WARNING: yarn install attempt $attempt failed for $name, retrying..."
                    sleep 1
                else
                    echo "    WARNING: yarn install failed for $name after 3 attempts"
                fi
            done
        ) &
        ((job_count++))
        if [ $job_count -ge $yarn_max_jobs ]; then
            wait -n 2>/dev/null || true
            ((job_count--))
        fi
    done
    wait
    echo "  yarn-classic installations complete"
) &
yarn_classic_pid=$!

(
    echo "  Starting yarn-berry installations..."
    job_count=0
    for dir in "$TESTFILES_DIR"/yarn-berry/*/; do
        [ -f "$dir/package.json" ] || continue
        (
            name=$(basename "$dir")
            echo "  yarn-berry: $name"
            cd "$dir" && rm -f yarn.lock .pnp.cjs .pnp.loader.mjs && rm -rf .yarn/cache .yarn/unplugged .yarn/install-state.gz
            # Retry up to 3 times on failure
            for attempt in 1 2 3; do
                if yarn set version berry 2>&1 >/dev/null && yarn install 2>&1 >/dev/null; then
                    break
                elif [ $attempt -lt 3 ]; then
                    echo "    WARNING: yarn berry install attempt $attempt failed for $name, retrying..."
                    rm -rf .yarn/cache 2>/dev/null
                    sleep 1
                else
                    echo "    WARNING: yarn berry install failed for $name after 3 attempts"
                fi
            done
        ) &
        ((job_count++))
        if [ $job_count -ge $MAX_JOBS ]; then
            wait -n 2>/dev/null || true
            ((job_count--))
        fi
    done
    wait
    echo "  yarn-berry installations complete"
) &
yarn_berry_pid=$!

(
    echo "  Starting poetry lock generation..."
    job_count=0
    for dir in "$TESTFILES_DIR"/poetry/*/; do
        [ -f "$dir/pyproject.toml" ] || continue
        (
            name=$(basename "$dir")
            echo "  poetry: $name"
            cd "$dir" && rm -f poetry.lock
            # Retry up to 3 times on failure
            for attempt in 1 2 3; do
                if poetry lock --no-interaction 2>&1 >/dev/null; then
                    break
                elif [ $attempt -lt 3 ]; then
                    echo "    WARNING: poetry lock attempt $attempt failed for $name, retrying..."
                    sleep 1
                else
                    echo "    WARNING: poetry lock failed for $name after 3 attempts"
                fi
            done
        ) &
        ((job_count++))
        if [ $job_count -ge $MAX_JOBS ]; then
            wait -n 2>/dev/null || true
            ((job_count--))
        fi
    done
    wait
    echo "  poetry lock generation complete"
) &
poetry_pid=$!

(
    echo "  Starting uv lock generation..."
    job_count=0
    for dir in "$TESTFILES_DIR"/uv/*/; do
        [ -f "$dir/pyproject.toml" ] || continue
        (
            name=$(basename "$dir")
            echo "  uv: $name"
            cd "$dir" && rm -f uv.lock
            # Retry up to 3 times on failure
            for attempt in 1 2 3; do
                if uv lock 2>&1 >/dev/null; then
                    break
                elif [ $attempt -lt 3 ]; then
                    echo "    WARNING: uv lock attempt $attempt failed for $name, retrying..."
                    sleep 1
                else
                    echo "    WARNING: uv lock failed for $name after 3 attempts"
                fi
            done
        ) &
        ((job_count++))
        if [ $job_count -ge $MAX_JOBS ]; then
            wait -n 2>/dev/null || true
            ((job_count--))
        fi
    done
    wait
    echo "  uv lock generation complete"
) &
uv_pid=$!

# Wait for all package managers to complete
wait $npm_pid
wait $pnpm_pid
wait $yarn_classic_pid
wait $yarn_berry_pid
wait $poetry_pid
wait $uv_pid

echo "Lock file generation complete."
echo ""
echo "=== Verification ==="

# Count directories and generated files
npm_dirs=$(find "$TESTFILES_DIR"/npm -maxdepth 1 -type d -name "*" ! -name "npm" | wc -l)
npm_locks=$(find "$TESTFILES_DIR"/npm -name "package-lock.json" 2>/dev/null | wc -l)
echo "NPM: $npm_locks/$npm_dirs lockfiles generated"

pnpm_dirs=$(find "$TESTFILES_DIR"/pnpm -maxdepth 1 -type d -name "*" ! -name "pnpm" 2>/dev/null | wc -l)
pnpm_locks=$(find "$TESTFILES_DIR"/pnpm -name "pnpm-lock.yaml" 2>/dev/null | wc -l)
echo "PNPM: $pnpm_locks/$pnpm_dirs lockfiles generated"

yarn_classic_dirs=$(find "$TESTFILES_DIR"/yarn-classic -maxdepth 1 -type d -name "*" ! -name "yarn-classic" 2>/dev/null | wc -l)
yarn_classic_locks=$(find "$TESTFILES_DIR"/yarn-classic -maxdepth 2 -name "yarn.lock" 2>/dev/null | wc -l)
echo "YARN-CLASSIC: $yarn_classic_locks/$yarn_classic_dirs lockfiles generated"

yarn_berry_dirs=$(find "$TESTFILES_DIR"/yarn-berry -maxdepth 1 -type d -name "*" ! -name "yarn-berry" 2>/dev/null | wc -l)
yarn_berry_locks=$(find "$TESTFILES_DIR"/yarn-berry -maxdepth 2 -name "yarn.lock" 2>/dev/null | wc -l)
echo "YARN-BERRY: $yarn_berry_locks/$yarn_berry_dirs lockfiles generated"

poetry_dirs=$(find "$TESTFILES_DIR"/poetry -maxdepth 1 -type d -name "*" ! -name "poetry" 2>/dev/null | wc -l)
poetry_locks=$(find "$TESTFILES_DIR"/poetry -name "poetry.lock" 2>/dev/null | wc -l)
echo "POETRY: $poetry_locks/$poetry_dirs lockfiles generated"

uv_dirs=$(find "$TESTFILES_DIR"/uv -maxdepth 1 -type d -name "*" ! -name "uv" 2>/dev/null | wc -l)
uv_locks=$(find "$TESTFILES_DIR"/uv -name "uv.lock" 2>/dev/null | wc -l)
echo "UV: $uv_locks/$uv_dirs lockfiles generated"

total_expected=$((npm_dirs + pnpm_dirs + yarn_classic_dirs + yarn_berry_dirs + poetry_dirs + uv_dirs))
total_generated=$((npm_locks + pnpm_locks + yarn_classic_locks + yarn_berry_locks + poetry_locks + uv_locks))
echo "---"
echo "Total: $total_generated/$total_expected lockfiles generated"
