# Trustify DA Backend Tester

Automated testing framework for [Trustify DA Java Client](https://github.com/guacsec/trustify-da-java-client) and [Trustify DA JavaScript Client](https://github.com/guacsec/trustify-da-javascript-client).

## Overview

This tester validates **backend response consistency** across multiple package ecosystems using snapshot testing:

- **Maven** (Java)
- **Gradle** (Java)
- **NPM** (JavaScript/Node.js)
- **pnpm** (JavaScript/Node.js)
- **Yarn** (Classic & Berry)
- **Go Modules** (Golang)
- **pip** (Python)

### How It Works

The tester uses **snapshot testing** (via [syrupy](https://github.com/syrupy-project/syrupy)) against a fixed backend dataset:

1. Clients send dependency manifests to the backend
2. Backend returns analysis results (vulnerability data, etc.)
3. Results are compared against stored snapshots
4. Any differences indicate either bugs or intentional changes that need review
5. Both Java and JavaScript clients are tested against the **same snapshots** to ensure consistency

## Structure

```
.
├── src/
│   └── tester/
│       ├── models.py       # Data models (TestCase, AnalysisType, ClientType)
│       ├── config.py       # Configuration constants
│       ├── discovery.py    # Test case discovery logic
│       └── runner.py       # Client execution
├── deploy/                 # Container deployment files
│   ├── Dockerfile          # Container image definition
│   ├── entrypoint.sh       # Container entrypoint
│   ├── generate-lockfiles.sh   # Lock file generation for JS ecosystems
│   ├── generate-python-venvs.sh # Virtual env generation for pip ecosystem
│   └── generate-all.sh     # Parallel generation wrapper
├── testfiles/              # Test data directory
│   ├── ecosystems/         # Test cases organized by package ecosystem
│   │   ├── maven/
│   │   ├── npm/
│   │   ├── pip/
│   │   └── ...
│   └── licenses/           # Sample license files (for optional license tests)
├── tests/                  # Optional/separate test suites
│   └── licenses/           # License API endpoint tests (see tests/licenses/README.md)
├── __snapshots__/          # Syrupy snapshot files (committed to git)
├── test_vulnerability_analysis.py  # Main: Vulnerability analysis tests
├── test_workspace_analysis.py      # Main: Workspace batch analysis tests
├── conftest.py             # Pytest fixtures and configuration
├── pytest.ini              # Pytest settings
├── manage-container.sh     # Container build/management script
├── run-in-container.sh     # Container test runner wrapper
└── README.md
```

## Usage

### Running Tests

#### Option 1: Using Container (Recommended)

The containerized approach provides a **self-contained environment** with:
- All package managers (Java, Node.js, Maven, Gradle, npm, pnpm, Yarn, Go, Python)
- **Pre-built Trustify DA clients** (Java and JavaScript) from source

**First time setup:**
```bash
# Make scripts executable
chmod +x run-in-container.sh manage-container.sh

# Create .env file with required configuration
cp .env.example .env
# Edit .env and set at minimum:
#   GITHUB_TOKEN       - GitHub token for building Java client dependencies
#   TRUSTIFY_DA_BACKEND_URL - URL of the Trustify DA backend

# Build the container image (includes building clients from source)
./manage-container.sh build
```

**Run tests:**
```bash
# Run all tests
./run-in-container.sh

# Test specific ecosystem
./run-in-container.sh --ecosystem maven

# Test specific client
./run-in-container.sh --client java

# Test multiple ecosystems
./run-in-container.sh --ecosystem maven --ecosystem npm
```

The wrapper script:
- Auto-detects Docker or Podman
- Builds the container image if needed (clones and builds clients from source)
- Mounts your testfiles directory into the container
- Mounts the `__snapshots__/` directory so snapshots persist to the host
- Passes all arguments through to pytest

**Optional: Override built-in clients**

To test locally-built clients instead of the built-in ones:

```bash
export TRUSTIFY_DA_JAVA_CLIENT=/path/to/custom-client.jar
export TRUSTIFY_DA_JS_CLIENT=/path/to/custom-js-client
./run-in-container.sh
```

#### Option 2: Direct Execution (Local)

Run tests directly on your host machine (requires all dependencies installed plus manually-built clients):

```bash
# Set client paths
export TRUSTIFY_DA_JAVA_CLIENT=/path/to/trustify-da-java-client.jar
export TRUSTIFY_DA_JS_CLIENT=/path/to/trustify-da-js-client

# Run all tests
python -m pytest

# Test specific ecosystem
python -m pytest --ecosystem maven

# Test specific client
python -m pytest --client java

# Test multiple ecosystems
python -m pytest --ecosystem maven --ecosystem npm

# Custom testfiles directory
python -m pytest --testfiles-dir /path/to/testfiles
```

### Command-line Options

```
--testfiles-dir PATH        Path to testfiles directory (default: ./testfiles)
--java-client PATH          Path to Java client JAR
--js-client PATH            Path to JavaScript client
--ecosystem NAME            Test only specific ecosystem (can be repeated)
--client TYPE               Test only specific client: java or javascript
--snapshot-update            Update snapshots with current client output (syrupy flag)
```

### Snapshot Testing Workflow

**Normal testing mode** - Compare against snapshots:
```bash
./run-in-container.sh
```

**Update snapshots** - Accept current outputs as the new expected values:
```bash
# Update all snapshots
./run-in-container.sh --snapshot-update

# Update snapshots for a specific ecosystem only, without deleting other ecosystems' snapshots
# Note: -n 1 is required to prevent syrupy from deleting unrelated snapshots
./run-in-container.sh --snapshot-update -n 1 --ecosystem maven
```

Snapshots are stored in the `__snapshots__/` directory at the project root. This directory is mounted into the container so updates persist to the host and can be committed to git.

### License Testing

The tester includes two types of license tests:

#### 1. License Snapshot Tests

License analysis tests run alongside vulnerability and batch tests in `test_vulnerability_analysis.py`:

```bash
# Run all tests (includes license, component, stack, and batch)
./run-in-container.sh

# Run only license tests using pytest markers
./run-in-container.sh -m license

# Run license tests for specific ecosystem
./run-in-container.sh -m license --ecosystem maven

# Update only license snapshots
./run-in-container.sh -m license --snapshot-update
```

**Key differences from vulnerability tests:**
- Uses the same manifest files from `testfiles/ecosystems/`
- Invokes clients with the `license` subcommand instead of `component` or `stack`
- Preserves license data in snapshots (vulnerability tests strip licenses)
- Stored in separate snapshot files, so updating license snapshots won't affect vulnerability snapshots

#### 2. License Detection Behavior Tests

Tests in `test_license_detection.py` validate license detection behavior using dedicated test cases:

```bash
# Run license detection tests
./run-in-container.sh -m license_detection

# Run for specific ecosystem
./run-in-container.sh -m license_detection -k maven
```

These tests verify:
- **Manifest license detection** - For ecosystems with license support (Maven, npm, Cargo)
- **LICENSE file fallback** - Automatic detection from LICENSE/LICENSE.md/LICENSE.txt
- **SPDX identification** - Detection of common licenses (MIT, Apache-2.0, GPL, etc.)
- **Mismatch detection** - When manifest and LICENSE file declare different licenses
- **Ecosystem-specific behavior** - Go, Gradle, Python always use LICENSE file

Test cases are in `testfiles/license-detection/` with scenarios for:
- License in manifest only
- License in LICENSE file only
- Both matching (no mismatch)
- Both mismatched (mismatch=true)

**Note:** The `license` subcommand reads only the manifest and LICENSE files, so lockfiles (package-lock.json, go.sum, etc.) are not required for these tests. If you need to add them, use the lockfile generation scripts in `deploy/`.

**Test markers:**
- `@pytest.mark.license` - License analysis tests
- `@pytest.mark.component` - Component vulnerability tests
- `@pytest.mark.stack` - Stack vulnerability tests

**Typical workflow when the backend changes:**
1. Run tests - review failures to verify changes are intentional
2. Update snapshots: `./run-in-container.sh --snapshot-update`
3. Re-run tests to verify all pass: `./run-in-container.sh`
4. Commit updated snapshots: `git add __snapshots__/ && git commit -m "Update snapshots for backend vX.Y.Z"`

## Test Case Format

Each test case directory should contain a manifest file (e.g., `pom.xml`, `package.json`, `go.mod`).

Example:
```
testfiles/
  ecosystems/
    maven/
      pom_deps_with_no_ignore/
        pom.xml
    npm/
      package_json_deps_without_exhortignore_object/
        package.json
  licenses/
    LICENSE-MIT
    LICENSE-Apache-2.0
    ...
```

## Container Architecture

The container is **fully self-contained** and builds the Trustify DA clients from source during image build:

```
Container Build Process:
1. Install dependencies (Java, Node.js, Maven, Gradle, Python, etc.)
2. Clone trustify-da-java-client repo -> build with Maven -> package JAR
3. Clone trustify-da-javascript-client repo -> build with npm -> install globally
4. Copy test framework code
5. Generate lock files for JS ecosystem test cases (npm, pnpm, yarn)
6. Generate Python virtual environments for pip ecosystem test cases

Runtime Volume Mounts:
Host Machine          Container
─────────────        ──────────
./testfiles/  ─────> /testfiles/      (includes ecosystems/ and licenses/)
./__snapshots__/ ──> /app/__snapshots__/

Built-in Clients:
/opt/clients/java-client.jar              (built from source)
/usr/local/bin/trustify-da-javascript-client  (built from source)
```

When you run `./run-in-container.sh`, it:
1. Detects your container runtime (Docker or Podman)
2. Builds the image if it doesn't exist (including building clients from source)
3. Mounts your testfiles and snapshots directories into the container
4. Executes pytest with your arguments

### Container Management

Use the `manage-container.sh` script for building and managing the container image:

```bash
# Build the container
./manage-container.sh build

# Rebuild from scratch (removes old image first)
./manage-container.sh rebuild

# Build without cache (slower but ensures fresh build)
./manage-container.sh build --no-cache

# Remove the container image
./manage-container.sh clean

# Check container status
./manage-container.sh status
```

**Build-time customization:**

```bash
# Build with specific client versions/branches
docker build \
  --build-arg JAVA_CLIENT_BRANCH=develop \
  --build-arg JS_CLIENT_BRANCH=feature-xyz \
  -f deploy/Dockerfile \
  -t trustify-da-tester:custom .

# Build with GitHub token (for Java client Maven dependencies)
# Note: manage-container.sh automatically uses GITHUB_TOKEN from .env
docker build \
  --build-arg GITHUB_TOKEN=ghp_your_token_here \
  -f deploy/Dockerfile \
  -t trustify-da-tester:latest .
```

## Configuration

The project uses a `.env` file for configuration. Copy the example and edit it:

```bash
cp .env.example .env
```

The `.env` file is loaded automatically by both `run-in-container.sh` and `manage-container.sh`.

See `.env.example` for all available options and documentation.

### Environment Variables

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | GitHub token with `read:packages` scope (required for building Java client) |
| `TRUSTIFY_DA_BACKEND_URL` | URL of the Trustify DA backend |
| `TRUSTIFY_DA_JAVA_CLIENT` | Path to Java client JAR (overrides built-in) |
| `TRUSTIFY_DA_JS_CLIENT` | Path to JavaScript client executable (overrides built-in) |

## Additional Test Suites

The main tests (above) validate DA client behavior against the backend using ecosystem test cases.

**Optional separate test suites** in `tests/` directory:

- **`tests/licenses/`** - Backend license API endpoint tests (HTTP-based, no clients needed)
  - Tests `/licenses`, `/licenses/{spdx}`, `/licenses/identify` endpoints
  - See [`tests/licenses/README.md`](tests/licenses/README.md) for usage
  - Run with: `python -m pytest tests/licenses/ -v`

## Claude Code Skills

If you're using [Claude Code](https://claude.ai/code), this repository includes custom skills to help with testing workflows:

- **`/create-test`** - Interactively create new test cases with proper structure
- **`/verify-tests`** - Validate existing test cases and find issues  
- **`/review-snapshots`** - Analyze snapshot differences and decide whether to accept changes
- **`/validate-snapshot`** - Verify snapshot content matches manifest (checks dev deps excluded, ignore flags respected, cross-ecosystem consistency)

See [.claude/README.md](.claude/README.md) for details.

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed
