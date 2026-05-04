# Validate Snapshot Content

You are validating that snapshot content logically matches the test case's manifest file, and checking cross-ecosystem consistency.

## Your Role

Verify that:
1. Backend response matches the manifest file
2. Ignore flags are respected
3. Dev dependencies and build dependencies are excluded
4. Cross-ecosystem equivalents produce consistent results (same packages, same vulnerability counts)

## What to Validate

### 1. Dependency Scoping - What Gets Analyzed

Different dependency types have different analysis rules:

**Maven (pom.xml):**
- ✅ `<dependencies>` (production) - analyzed
- ❌ `<scope>test</scope>` - NOT analyzed

**Gradle (build.gradle / build.gradle.kts):**
- ✅ `implementation`, `api`, `runtimeOnly` - analyzed  
- ❌ `testImplementation`, `testRuntimeOnly` - NOT analyzed
- **gradle-groovy and gradle-kotlin must have same packages & vulnerability counts** if dependencies are the same

**NPM/Yarn/pnpm (package.json):**
- ✅ `dependencies` - analyzed (unless ignored)
- ✅ `bundledDependencies` - analyzed (unless ignored)
- ⚠️ `peerDependencies` - may be analyzed if installed
- ⚠️ `optionalDependencies` - may be analyzed if successfully installed
- ❌ `devDependencies` - NOT analyzed
- **npm, pnpm, and yarn must have same packages & vulnerability counts** if package.json is identical

**Cargo (Cargo.toml):**
- ✅ `[dependencies]` - analyzed (unless ignored)
- ❌ `[dev-dependencies]` - NOT analyzed
- ❌ `[build-dependencies]` - NOT analyzed

**Go (go.mod):**
- ✅ `require` directives - analyzed
- Distinguish direct vs indirect

**Python (requirements.txt / pyproject.toml):**
- ✅ `[project.dependencies]` or `[tool.poetry.dependencies]` - analyzed
- ❌ `[tool.poetry.dev-dependencies]` - NOT analyzed  
- **poetry, uv, and possibly pip might have same packages & counts** if dependencies match

### 2. Ignore Flags

Packages marked with ignore flags should NOT appear in snapshots:

**package.json example:**
```json
{
  "dependencies": {
    "lodash": "4.17.19",
    "express": {
      "version": "4.17.1",
      "exhortignore": true
    }
  }
}
```

**Validation:**
- ✅ Ignored packages NOT in snapshot
- ❌ Ignored package in snapshot = backend bug

Ignore flag names:
- `exhortignore`
- `trustify-da-ignore`

### 3. Cross-Ecosystem Consistency

**Critical:** Equivalent package managers must produce semantically identical snapshots.

#### What Must Match:
- ✅ Package list (same packages reported)
- ✅ Direct vulnerability count
- ✅ Transitive vulnerability count
- ✅ CVE IDs (same set)

#### What May Differ:
- ⚠️ JSON structure/formatting
- ⚠️ Field ordering
- ⚠️ Ecosystem-specific metadata

#### Example Validation:

**Gradle Groovy vs Kotlin:**
```
✅ PASS:
gradle-groovy/test: log4j-core@2.14.0, 3 direct vulns, 0 transitive
gradle-kotlin/test: log4j-core@2.14.0, 3 direct vulns, 0 transitive

❌ FAIL:
gradle-groovy/test: 3 direct vulns
gradle-kotlin/test: 5 direct vulns (backend bug!)
```

**NPM vs pnpm vs Yarn:**
```
✅ PASS:
npm/test: lodash@4.17.19, 2 direct vulns
pnpm/test: lodash@4.17.19, 2 direct vulns
yarn-classic/test: lodash@4.17.19, 2 direct vulns

❌ FAIL:
npm/test: [lodash]
pnpm/test: [lodash, axios] (extra package - bug!)
```

## Validation Process

### Step 1: Read Manifest

Extract:
1. **Production dependencies** (should be in snapshot)
2. **Dev/build dependencies** (should NOT be in snapshot)
3. **Ignored dependencies** (should NOT be in snapshot)

### Step 2: Read Snapshot

Extract:
- Package list
- Direct vulnerability count
- Transitive vulnerability count
- CVE IDs

### Step 3: Cross-Reference

✅ **Good:**
- All production deps in snapshot (except ignored)
- Versions match declared ranges
- NO dev/build dependencies
- NO ignored packages

❌ **Red flags:**
- Ignored package in snapshot
- Dev/build dependency in snapshot
- Hallucinated packages
- Missing expected packages

### Step 4: Cross-Ecosystem Check (if applicable)

For equivalent tests (e.g., npm vs pnpm with same package.json):

Compare:
1. Package lists - should be identical
2. Direct vuln counts - should match
3. Transitive vuln counts - should match
4. CVE IDs - should be identical set

Report:
```
Cross-Ecosystem Consistency: npm vs pnpm
========================================

npm/test_with_lodash:
  Packages: lodash@4.17.19
  Direct vulns: 2
  Transitive vulns: 0
  CVEs: CVE-2020-8203, CVE-2021-23337

pnpm/test_with_lodash:
  Packages: lodash@4.17.19
  Direct vulns: 2
  Transitive vulns: 0
  CVEs: CVE-2020-8203, CVE-2021-23337

✅ CONSISTENT
```

Or if inconsistent:
```
gradle-groovy/test: 15 packages, 3 direct, 2 transitive
gradle-kotlin/test: 15 packages, 3 direct, 4 transitive

❌ INCONSISTENT: gradle-kotlin reports 2 extra transitive vulns
Backend discrimination detected!
```

## Common Issues

### 1. Dev/Build Dependencies Leak
```
❌ CRITICAL

Manifest:
  devDependencies: jest@26.0.0
  build-dependencies: cc@1.0.83

Snapshot includes:
  jest@26.0.0 (should NOT be analyzed!)
  
Backend bug: analyzed dev dependencies
```

### 2. Ignored Packages Leak
```
❌ CRITICAL

Manifest:
  express (exhortignore: true)
  
Snapshot includes:
  express@4.17.1
  
Backend bug: ignored package analyzed
```

### 3. Cross-Ecosystem Inconsistency
```
❌ Backend treats ecosystems differently

npm/test: 2 vulns
pnpm/test: 3 vulns (same package.json!)

Backend discrimination - investigate
```

### 4. Cross-Ecosystem Package Mismatch
```
❌ Different packages across ecosystems

gradle-groovy/test: [log4j-core, log4j-api]
gradle-kotlin/test: [log4j-core, log4j-api, slf4j] (extra!)

Backend inconsistency
```

## Commands to Use

```bash
# Read manifests
read testfiles/<ecosystem>/<test_name>/package.json
read testfiles/<ecosystem>/<test_name>/Cargo.toml

# Read snapshot
read __snapshots__/test_vulnerability_analysis/test_vulnerability_analysis[<test-params>].json

# Find equivalent tests
glob testfiles/npm/*<pattern>*/
glob testfiles/pnpm/*<pattern>*/
glob testfiles/gradle-*/*<pattern>*/

# Compare vulnerability counts
grep -c "CVE-" __snapshots__/.../test[...].json
```

## Cross-Ecosystem Equivalence Groups

**Must have same packages and vulnerability counts:**

| Group | Ecosystems | Condition |
|-------|-----------|-----------|
| Gradle | gradle-groovy, gradle-kotlin | Same dependencies |
| npm-family | npm, pnpm, yarn-classic, yarn-berry | Identical package.json |
| Python (uncertain) | poetry, uv | Same pyproject.toml |

## When to Use

- ✅ After creating a new test
- ✅ Testing cross-ecosystem consistency
- ✅ Investigating unexpected packages or vulnerability counts
- ✅ Before accepting `--snapshot-update`
- ✅ When suspecting package manager discrimination
- ✅ When testing ignore flags

## When NOT to Use

- ❌ Comparing old vs new snapshots (use `/review-snapshots`)
- ❌ Checking test structure (use `/verify-tests`)
- ❌ Creating new tests (use `/create-test`)

## Summary

This command validates:
1. ✅ Production dependencies analyzed
2. ✅ Dev/build dependencies NOT analyzed
3. ✅ Ignored packages NOT analyzed
4. ✅ Cross-ecosystem equivalents have same packages & vulnerability counts
