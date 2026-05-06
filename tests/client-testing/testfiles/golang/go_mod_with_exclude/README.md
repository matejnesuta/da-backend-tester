# Go `exclude` Directive Test

This test validates handling of the Go `exclude` directive.

## Test Setup

- **Requires:** gin v1.8.1 (safe version)
- **Excludes:** gin v1.7.7 via `exclude` directive (vulnerable)
- **Also requires:** golang.org/x/text v0.3.7 (vulnerable)

## Expected Behavior

The `exclude` directive prevents Go from using the specified version. Go's module
resolution will use the required v1.8.1 instead.

- gin v1.8.1 SHOULD be scanned (the required version)
- gin v1.7.7 should NOT be scanned (excluded)
- golang.org/x/text v0.3.7 SHOULD be scanned (not excluded)
- Expected: Both gin v1.8.1 and golang.org/x/text vulnerabilities reported

## Why This Matters

The `exclude` directive is used to blacklist broken or vulnerable versions. The
scanner should respect this and not report vulnerabilities in excluded versions.
