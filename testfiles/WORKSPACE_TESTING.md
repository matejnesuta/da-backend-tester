# Workspace/Monorepo Testing Guide

This document explains how workspace/monorepo test cases are organized and executed.

## Overview

Workspace tests verify client behavior for JavaScript/TypeScript monorepos and Cargo workspaces:

1. **Lock File Walk-Up** - Client finds lock file at workspace root when analyzing a member package
2. **Batch Analysis** - Client discovers and analyzes all workspace packages in one request

## Test Case Structure

### Regular Test Cases (Lock File Walk-Up)

Tests that verify clients can analyze workspace member manifests by walking up to find the root lock file.

**Structure:**
```
testfiles/<ecosystem>/<test_name>/
├── package.json              # Root workspace config
├── package-lock.json         # Lock file at ROOT
├── packages/
│   └── package-a/
│       └── package.json      # Member manifest
└── .member-manifest          # Marker: points to packages/package-a/package.json
```

**Marker file (`.member-manifest`):**
```
packages/package-a/package.json
```

**How it works:**
- Discovery reads `.member-manifest` to find the actual manifest to analyze
- Test runs regular `stack` analysis on the member manifest
- Client walks up from member directory to find lock file at workspace root
- If analysis succeeds, lock file walk-up is working

**Examples:**
- `testfiles/npm/npm_workspace_member/` - npm workspace member
- `testfiles/yarn-classic/yarn_workspace_member/` - yarn-classic workspace member
- `testfiles/yarn-berry/yarn_workspace_member/` - yarn-berry workspace member
- `testfiles/cargo/cargo_workspace_member/` - Cargo workspace member

### Batch Analysis Test Cases

Tests that verify `stack-batch` command discovers and analyzes all workspace packages.

**Structure:**
```
testfiles/<ecosystem>/<test_name>/
├── package.json              # Root workspace config
├── package-lock.json         # Lock file at ROOT
├── packages/
│   ├── package-a/
│   │   └── package.json
│   └── package-b/
│       └── package.json
└── .workspace-batch          # Marker: indicates batch analysis test
```

**Marker file (`.workspace-batch`):**
```
# This directory should be tested with stack-batch analysis
expected_packages: 3
test_metadata: false
```

**Marker fields:**
- `expected_packages` - Number of packages expected in output (root + members)
- `test_metadata` - Set to `true` to test with `--metadata` flag

**How it works:**
- Discovery reads `.workspace-batch` marker
- Test runs `stack-batch <workspace-root>` command
- Client discovers all workspace members and generates batch analysis
- Output verified against snapshot

**Examples:**

**JavaScript:**
- `testfiles/npm/npm_workspace/` - Basic npm workspace
- `testfiles/pnpm/pnpm_workspace/` - pnpm workspace with pnpm-workspace.yaml
- `testfiles/npm/npm_workspace_with_invalid/` - Tests invalid package handling
- `testfiles/yarn-classic/yarn_workspace/` - yarn-classic workspace
- `testfiles/yarn-berry/yarn_workspace/` - yarn-berry workspace

**Rust:**
- `testfiles/cargo/cargo_virtual_workspace/` - Cargo virtual workspace
- `testfiles/cargo/cargo_workspace_with_root/` - Cargo workspace with root package

**Python:**
- `testfiles/uv/uv_workspace/` - uv workspace

## Test Execution

### All Tests
```bash
pytest test_vulnerability_analysis.py -v
```

### Lock File Walk-Up Tests Only
```bash
pytest test_vulnerability_analysis.py -k "npm_workspace_member"
```

### Batch Analysis Tests Only
```bash
pytest test_vulnerability_analysis.py::test_batch_workspace_analysis -v
```

### Generate Snapshots
```bash
pytest test_vulnerability_analysis.py --snapshot-update
```

## Adding New Test Cases

### Add Lock File Walk-Up Test

1. Create workspace structure with lock file at root
2. Add `.member-manifest` file pointing to the member manifest
3. Run tests

**Example:**
```bash
mkdir -p testfiles/npm/my_workspace_test/packages/member-pkg
echo '{"name":"member-pkg","version":"1.0.0"}' > testfiles/npm/my_workspace_test/packages/member-pkg/package.json
echo 'packages/member-pkg/package.json' > testfiles/npm/my_workspace_test/.member-manifest
# Generate lock file at root...
pytest test_vulnerability_analysis.py -k "my_workspace_test"
```

### Add Batch Analysis Test

1. Create workspace structure
2. Add `.workspace-batch` marker with configuration
3. Run tests

**Example:**
```bash
mkdir -p testfiles/pnpm/my_pnpm_workspace
# Create pnpm-workspace.yaml, package.json, etc...
cat > testfiles/pnpm/my_pnpm_workspace/.workspace-batch <<EOF
expected_packages: 3
test_metadata: false
EOF
pytest test_vulnerability_analysis.py::test_batch_workspace_analysis -k "my_pnpm_workspace"
```

## Implementation Details

- **Discovery**: `src/tester/discovery.py`
  - `discover_test_cases()` - Finds regular and member-manifest test cases
  - `discover_workspace_test_cases()` - Finds workspace-batch test cases

- **Runner**: `src/tester/runner.py`
  - `run_client()` - Regular component/stack analysis
  - `run_batch_analysis()` - Workspace batch analysis with flags

- **Tests**: `test_vulnerability_analysis.py`
  - `test_vulnerability_analysis()` - Regular tests (including member analysis)
  - `test_batch_workspace_analysis()` - Batch workspace tests

- **Parametrization**: `pytest_generate_tests()` dynamically creates test cases from discovered fixtures
