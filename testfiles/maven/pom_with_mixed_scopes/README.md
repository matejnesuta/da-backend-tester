# Maven Mixed Scope Test

This test validates proper handling of different Maven dependency scopes.

## Test Setup

**Should be INCLUDED (production scopes):**
- log4j 1.2.17 (`compile` scope, vulnerable)
- commons-collections 3.2.1 (no scope = `compile`, vulnerable)
- keycloak-saml-core 1.8.1.Final (`runtime` scope, vulnerable)

**Should be EXCLUDED (non-production scopes):**
- junit 4.12 (`test` scope)
- spring-core 4.3.0.RELEASE (`test` scope, vulnerable)
- lombok 1.18.20 (`provided` scope)
- servlet-api 2.5 (`provided` scope, vulnerable)

## Expected Behavior

- **Expected:** 3 dependencies scanned (compile + runtime)
- **Expected:** 3+ vulnerabilities reported (from included deps only)
- Test and provided scopes should be excluded

## Why This Matters

Maven's scope system determines what's included in the final artifact:
- `compile` / `runtime` → shipped with application → should be scanned
- `test` / `provided` → not shipped → should be excluded from scans
