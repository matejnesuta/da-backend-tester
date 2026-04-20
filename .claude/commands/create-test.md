# Create Test Case

You are helping create a new test case for the Trustify DA backend tester.

## Your Role

Guide the user through creating a new test case by:

1. **Understanding the ecosystem** - Ask what they want to test:
   - Maven (pom.xml)
   - Gradle (build.gradle / build.gradle.kts)
   - NPM (package.json + package-lock.json)
   - pnpm (package.json + pnpm-lock.yaml)
   - Yarn Classic (package.json + yarn.lock)
   - Yarn Berry (package.json + .yarn/)
   - Cargo (Cargo.toml + Cargo.lock)
   - Go (go.mod + go.sum)
   - pip (requirements.txt)
   - Poetry (pyproject.toml + poetry.lock)
   - uv (pyproject.toml + uv.lock)

2. **Understanding the scenario** - What type of test:
   - Simple dependency test
   - Test with vulnerabilities
   - Test with ignore patterns
   - Workspace member test (single package in a monorepo)
   - Workspace batch test (analyze entire monorepo)

3. **Creating the structure**:
   - `testfiles/<ecosystem>/<descriptive_name>/`
   - Appropriate manifest file(s)
   - Lock files if needed
   - Marker files for workspace tests

## Workspace Tests

### Workspace Member Test
Tests that the client can analyze a workspace member by walking up to find the root lock file.

Structure:
```
testfiles/<ecosystem>/<test_name>/
├── package.json              # Root workspace config
├── package-lock.json         # Lock file at ROOT
├── packages/
│   └── package-a/
│       └── package.json      # Member manifest
└── .member-manifest          # Marker: points to packages/package-a/package.json
```

Marker file content:
```
packages/package-a/package.json
```

### Workspace Batch Test
Tests that `stack-batch` discovers and analyzes all workspace packages.

Structure:
```
testfiles/<ecosystem>/<test_name>/
├── package.json              # Root workspace config
├── package-lock.json         # Lock file at ROOT
├── packages/
│   ├── package-a/
│   │   └── package.json
│   └── package-b/
│       └── package.json
└── .workspace-batch          # Marker: indicates batch test
```

Marker file content:
```
# This directory should be tested with stack-batch analysis
expected_packages: 3
test_metadata: false
```

## Process

1. Ask clarifying questions first
2. Create the directory structure using Write tool
3. Generate realistic manifest content with dependencies
4. Create lock files if needed (or note that generate-lockfiles.sh should be run)
5. Verify the structure matches the test type

## Examples

**Simple NPM test with vulnerabilities:**
- testfiles/npm/package_json_with_lodash_vulnerability/
- package.json with old lodash version
- package-lock.json (can be generated later)

**pnpm workspace member:**
- testfiles/pnpm/pnpm_workspace_member/
- pnpm-workspace.yaml at root
- .member-manifest pointing to packages/app/package.json

**Maven with dependencies:**
- testfiles/maven/pom_with_log4j_vulnerability/
- pom.xml with vulnerable log4j version

Always verify file paths and ask before creating to ensure correctness!
