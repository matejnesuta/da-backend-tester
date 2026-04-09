# Mixed Configurations Test

Tests that only production dependencies are scanned, while test and compile-only dependencies are excluded.

## Test Setup

### Production Dependencies (should scan)
- `log4j:log4j:1.2.17` (implementation - vulnerable)
- `commons-collections:3.2.1` (implementation - vulnerable)
- `keycloak-core:20.0.0` (runtimeOnly - vulnerable, CVE-2022-3782)

### Compile-Only Dependencies (should exclude - not in runtime)
- `lombok:1.18.24` (compileOnly - annotation processing)
- `javax.servlet-api:4.0.1` (compileOnly - provided by server)

### Test Dependencies (should exclude - not in production)
- `junit:4.12` (testImplementation)
- `spring-core:5.3.18` (testImplementation - vulnerable but test-only)
- `mockito-core:4.0.0` (testCompileOnly)

## Expected Behavior

Only production runtime dependencies should be scanned:
- `runtimeClasspath` contains: log4j, commons-collections, keycloak-core
- `compileOnly` deps (lombok, servlet-api) are NOT in runtimeClasspath
- `testImplementation` deps are NOT in production runtimeClasspath
- Expected: **3 dependencies scanned** (log4j, commons-collections, keycloak-core)

## Why This Matters

- **compileOnly**: Dependencies needed only at compile time (like Lombok for annotation processing or Servlet API provided by the container) don't ship with the artifact
- **testImplementation/testCompileOnly**: Test dependencies don't ship with production code

Scanning these would create false positives for vulnerabilities that can't affect production.

## Gradle Configuration Mapping

| Gradle Configuration | Maven Equivalent | Include in Scan? |
|---------------------|------------------|------------------|
| implementation      | compile          | ✓ Yes            |
| runtimeOnly         | runtime          | ✓ Yes            |
| compileOnly         | provided         | ✗ No             |
| testImplementation  | test             | ✗ No             |
| testCompileOnly     | test + provided  | ✗ No             |
| testRuntimeOnly     | test             | ✗ No             |
