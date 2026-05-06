# Go `replace` Directive Test

This test validates handling of the Go `replace` directive.

## Test Setup

- **Requires:** gin v1.7.7 (vulnerable: CVE-2023-26125, CVE-2023-29401)
- **Replaces:** gin v1.7.7 => gin v1.9.1 (patched)
- **Also requires:** go-restful v3.0.0 (CRITICAL: CVE-2022-1996)

## Expected Behavior

The `replace` directive overrides the version resolution. The scanner should
analyze the **replacement** version, not the original.

- gin v1.9.1 SHOULD be scanned (replacement) → no vulnerabilities
- go-restful v3.0.0 SHOULD be scanned → CRITICAL vulnerability
- Expected: Only go-restful vulnerability reported

## Why This Matters

The `replace` directive is commonly used for security patches, forks, or local
development. The scanner must analyze what actually gets built, not what's
declared in require statements.
