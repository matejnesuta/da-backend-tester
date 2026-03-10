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

The tester uses **snapshot testing** against a fixed backend dataset:

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
│       ├── models.py       # Data models (TestCase, TestResult, enums)
│       ├── config.py       # Configuration constants
│       ├── discovery.py    # Test case discovery logic
│       ├── runner.py       # Client execution
│       ├── comparator.py   # SBOM comparison logic
│       └── tester.py       # Main orchestration
├── testfiles/              # Test cases organized by ecosystem
├── test_runner.py          # Main entry point
└── README.md
```

## Usage

### Running Tests

#### Option 1: Using Container (Recommended)

The containerized approach provides a **self-contained environment** with:
- All package managers (Java, Node.js, Maven, Gradle, npm, pnpm, Yarn, Go, Python)
- **Pre-built Trustify DA clients** (Java and JavaScript) from source
- Isolation and reproducibility

**First time setup:**
```bash
# Make the wrapper script executable
chmod +x run-in-container.sh

# Build the container image (includes building clients from source)
./run-in-container.sh --check-config
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
- Passes all arguments through to test_runner.py

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
python test_runner.py

# Test specific ecosystem
python test_runner.py --ecosystem maven

# Test specific client
python test_runner.py --client java

# Test multiple ecosystems
python test_runner.py --ecosystem maven --ecosystem npm

# Custom testfiles directory
python test_runner.py --testfiles-dir /path/to/testfiles
```

### Command-line Options

```
--testfiles-dir PATH        Path to testfiles directory (default: ./testfiles)
--java-client PATH          Path to Java client JAR
--js-client PATH            Path to JavaScript client
--ecosystem NAME            Test only specific ecosystem (can be repeated)
--client TYPE               Test only specific client: java or javascript
--check-config              Check configuration and exit
--update-failed             Re-run and update snapshots for previously failed tests
--source {java,javascript}  Which client to use for snapshot updates (default: java)
--failures-file PATH        Path to failures cache file (default: testfiles/.test-failures.json)
```

### Snapshot Testing Workflow

**Normal testing mode** - Compare against snapshots:
```bash
./run-in-container.sh

# Failed tests are automatically cached to .test-failures.json
```

**Update failed snapshots** - Accept current outputs for previously failed tests:
```bash
# Step 1: Run tests normally (failures are cached)
./run-in-container.sh --ecosystem maven
# Output: 10 tests run, 2 failed
# Failures saved to .test-failures.json

# Step 2: Review the diffs and decide if changes are acceptable

# Step 3: Update ONLY the failed snapshots
./run-in-container.sh --update-failed
# Only re-runs the 2 failed tests and updates their snapshots

# Step 4: Verify all clients still match
./run-in-container.sh --ecosystem maven
# All tests should now pass
```

**Advanced options:**
```bash
# Use JavaScript client as source of truth for updates
./run-in-container.sh --update-failed --source javascript

# Update failed tests for specific ecosystem only
# (requires running tests for that ecosystem first)
./run-in-container.sh --ecosystem npm  # Generates failures
./run-in-container.sh --update-failed  # Updates those failures
```

After updating snapshots, the tool automatically verifies that **both clients produce identical outputs**. If they differ, tests will fail, indicating a consistency issue between implementations.

## Test Case Format

Each test case directory should contain:

- A manifest file (e.g., `pom.xml`, `package.json`, `go.mod`)
- Snapshot files (backend response snapshots):
  - `component_analysis_expected_sbom.json` or `expected_component_sbom.json`
  - `stack_analysis_expected_sbom.json` or `expected_stack_sbom.json`

**Note:** These files are called "expected_sbom" for historical reasons, but they actually contain **backend API responses**, not raw SBOMs. Both Java and JavaScript clients are tested against the same snapshot files to ensure consistency.

Example:
```
testfiles/
  maven/
    pom_deps_with_no_ignore/
      pom.xml
      component_analysis_expected_sbom.json  # Snapshot of backend response
      stack_analysis_expected_sbom.json      # Snapshot of backend response
```

### When Backend Changes

When the backend dataset or API responses change:

1. Run tests - failures are automatically cached to `.test-failures.json`
2. Review the diff output to verify changes are intentional
3. Update failed snapshots: `./run-in-container.sh --update-failed`
4. Re-run tests to verify all pass
5. Commit updated snapshots: `git add testfiles/ .test-failures.json && git commit -m "Update snapshots for backend vX.Y.Z"`

**Note:** The `.test-failures.json` file is used for tracking failed tests between runs. You can add it to `.gitignore` if you don't want to commit it, but it's useful for sharing failure context with team members.

## Container Architecture

The container is **fully self-contained** and builds the Trustify DA clients from source during image build:

```
Container Build Process:
1. Install dependencies (Java, Node.js, Maven, Gradle, etc.)
2. Clone trustify-da-java-client repo → build with Maven → package JAR
3. Clone trustify-da-javascript-client repo → build with npm → install globally
4. Copy test framework code

Runtime Volume Mounts:
Host Machine          Container
─────────────        ──────────
./testfiles/  ─────> /testfiles/ (read-only)

Built-in Clients:
/opt/clients/java-client.jar              (built from source)
/usr/local/bin/trustify-da-javascript-client  (built from source)
```

When you run `./run-in-container.sh`, it:
1. Detects your container runtime (Docker or Podman)
2. Builds the image if it doesn't exist (including building clients from source)
3. Mounts your testfiles directory to `/testfiles` in the container
4. Executes `test_runner.py` with your arguments

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

# Show help
./manage-container.sh help
```

**Manual container builds:**

```bash
# Force rebuild (will pull latest client code from GitHub)
docker build --no-cache -t trustify-da-tester:latest .
# or with podman
podman build --no-cache -t trustify-da-tester:latest .
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

## Future Extensions

The framework is designed to be extended for:

- Backend vulnerability testing
- HTML report parsing
- JSON validation of vulnerability results
- Performance benchmarking

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed
