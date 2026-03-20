#!/bin/bash
#
# Generate lock files for JS ecosystem test cases.
# Intended to run inside the container after build, using the container's
# package managers (npm, pnpm, yarn) for platform-independent results.
#
# Usage: generate-lockfiles.sh [testfiles-dir]
#

set -e

TESTFILES_DIR="${1:-/testfiles}"

if [ ! -d "$TESTFILES_DIR" ]; then
    echo "Error: testfiles directory not found: $TESTFILES_DIR"
    exit 1
fi

echo "Generating lock files in $TESTFILES_DIR..."

# npm
for dir in "$TESTFILES_DIR"/npm/*/; do
    [ -f "$dir/package.json" ] || continue
    echo "  npm: $(basename "$dir")"
    (cd "$dir" && rm -f package-lock.json && npm install --package-lock-only --ignore-scripts 2>/dev/null) || echo "    WARNING: npm install failed for $(basename "$dir")"
done

# pnpm
for dir in "$TESTFILES_DIR"/pnpm/*/; do
    [ -f "$dir/package.json" ] || continue
    echo "  pnpm: $(basename "$dir")"
    (cd "$dir" && rm -f pnpm-lock.yaml && pnpm install --lockfile-only --ignore-scripts 2>/dev/null) || echo "    WARNING: pnpm install failed for $(basename "$dir")"
done

# yarn-classic
for dir in "$TESTFILES_DIR"/yarn-classic/*/; do
    [ -f "$dir/package.json" ] || continue
    echo "  yarn-classic: $(basename "$dir")"
    (cd "$dir" && rm -f yarn.lock && yarn install --ignore-scripts 2>/dev/null) || echo "    WARNING: yarn install failed for $(basename "$dir")"
done

# yarn-berry
for dir in "$TESTFILES_DIR"/yarn-berry/*/; do
    [ -f "$dir/package.json" ] || continue
    echo "  yarn-berry: $(basename "$dir")"
    (cd "$dir" && rm -f yarn.lock .pnp.cjs .pnp.loader.mjs && rm -rf .yarn/cache .yarn/unplugged .yarn/install-state.gz && yarn set version berry 2>/dev/null && yarn install 2>/dev/null) || echo "    WARNING: yarn berry install failed for $(basename "$dir")"
done

echo "Lock file generation complete."
