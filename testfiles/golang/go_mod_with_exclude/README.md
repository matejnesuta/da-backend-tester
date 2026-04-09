# Go `exclude` Directive Test

This test validates handling of the Go `exclude` directive.

## Test Setup

- **Requires:** gin v1.7.7 (vulnerable)
- **Excludes:** gin v1.7.7 via `exclude` directive
- **Also requires:** golang.org/x/text v0.3.7 (vulnerable)

## Expected Behavior

The `exclude` directive prevents Go from using the specified version. Go's module
resolution should automatically select a different version (or fail resolution).

- gin v1.7.7 should NOT be scanned (excluded)
- golang.org/x/text v0.3.7 SHOULD be scanned (not excluded)
- Expected: Only golang.org/x/text vulnerability reported

## Why This Matters

The `exclude` directive is used to blacklist broken or vulnerable versions. The
scanner should respect this and not report vulnerabilities in excluded versions.
