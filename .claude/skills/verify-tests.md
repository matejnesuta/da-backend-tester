# Verify Test Cases

You are validating test case structure for the Trustify DA backend tester.

## Your Role

Scan the testfiles/ directory and verify that all test cases have proper structure.

## What to Check

### 1. Required Manifest Files

Each ecosystem requires specific manifest files:

| Ecosystem | Required Files |
|-----------|---------------|
| maven | pom.xml |
| gradle-groovy | build.gradle |
| gradle-kotlin | build.gradle.kts |
| npm | package.json, package-lock.json |
| pnpm | package.json, pnpm-lock.yaml |
| yarn-classic | package.json, yarn.lock |
| yarn-berry | package.json, .yarnrc.yml, .yarn/ |
| cargo | Cargo.toml, Cargo.lock |
| golang | go.mod, go.sum |
| pip | requirements.txt |
| poetry | pyproject.toml, poetry.lock |
| uv | pyproject.toml, uv.lock |

### 2. Workspace Test Markers

**Workspace member tests** must have:
- `.member-manifest` file
- Content: relative path to the member's manifest (e.g., `packages/package-a/package.json`)
- The referenced manifest must exist

**Workspace batch tests** must have:
- `.workspace-batch` file
- Content format:
  ```
  expected_packages: <number>
  test_metadata: <true|false>
  ```

### 3. Directory Structure

Expected: `testfiles/<ecosystem>/<test_name>/`

Check for:
- Properly named ecosystem directories
- Descriptive test names
- No orphaned files
- Consistent naming conventions

## Verification Process

1. **Glob for all test directories**: `testfiles/**/`
2. **For each test directory**:
   - Identify ecosystem from parent directory name
   - Check for required manifest files
   - Check for workspace markers if present
   - Validate marker content format
3. **Report findings**:
   - ✅ Valid test cases
   - ⚠️  Warning: missing lock files (might be intentional)
   - ❌ Missing required manifest
   - ❌ Invalid marker file format
   - ❌ Marker points to non-existent file

## Output Format

```
Test Case Verification Report
============================

✅ VALID (45 test cases)
  - testfiles/npm/package_json_deps_without_exhortignore_object/
  - testfiles/maven/pom_deps_with_no_ignore/
  ...

⚠️  WARNINGS (3 test cases)
  - testfiles/npm/new_test_case/
    Missing: package-lock.json (run generate-lockfiles.sh)

❌ ERRORS (2 test cases)
  - testfiles/cargo/broken_test/
    Missing required: Cargo.toml
  - testfiles/npm/bad_workspace/
    .member-manifest points to non-existent: packages/app/package.json

Summary: 45 valid, 3 warnings, 2 errors
```

## Commands to Use

- `glob testfiles/*/` - List ecosystem directories
- `glob testfiles/<ecosystem>/*/` - List test cases for ecosystem
- `read <path>/.member-manifest` - Check workspace member marker
- `read <path>/.workspace-batch` - Check workspace batch marker
- `read <path>/package.json` - Verify manifest exists

Start by asking which scope to verify (all tests, specific ecosystem, or specific test).
