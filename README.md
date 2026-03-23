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
├── testfiles/              # Test cases organized by ecosystem
├── __snapshots__/          # Syrupy snapshot files (committed to git)
├── test_vulnerability_analysis.py  # Pytest test definitions
├── conftest.py             # Pytest fixtures and configuration
├── pytest.ini              # Pytest settings
├── entrypoint.sh           # Container entrypoint
├── generate-lockfiles.sh   # Lock file generation for JS ecosystems
├── Dockerfile              # Container image definition
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
  maven/
    pom_deps_with_no_ignore/
      pom.xml
  npm/
    package_json_deps_without_exhortignore_object/
      package.json
```

## Container Architecture

The container is **fully self-contained** and builds the Trustify DA clients from source during image build:

```
Container Build Process:
1. Install dependencies (Java, Node.js, Maven, Gradle, etc.)
2. Clone trustify-da-java-client repo -> build with Maven -> package JAR
3. Clone trustify-da-javascript-client repo -> build with npm -> install globally
4. Copy test framework code

Runtime Volume Mounts:
Host Machine          Container
─────────────        ──────────
./testfiles/  ─────> /testfiles/
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
  -t trustify-da-tester:custom .

# Build with GitHub token (for Java client Maven dependencies)
# Note: manage-container.sh automatically uses GITHUB_TOKEN from .env
docker build \
  --build-arg GITHUB_TOKEN=ghp_your_token_here \
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

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed
