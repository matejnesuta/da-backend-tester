# Maven Test Scope Exclusion Test

This test validates that test-scoped dependencies are excluded from vulnerability analysis.

## Test Setup

All dependencies have `<scope>test</scope>`:
- junit 4.12 (test)
- log4j 1.2.17 (test, vulnerable)
- commons-collections 3.2.1 (test, vulnerable)

## Expected Behavior

Test-scoped dependencies should NOT be included in production vulnerability analysis:
- **Expected:** 0 dependencies scanned
- **Expected:** 0 vulnerabilities reported

## Why This Matters

Test dependencies are not shipped with the production application. Including them
in vulnerability scans creates false positives for production deployments.
