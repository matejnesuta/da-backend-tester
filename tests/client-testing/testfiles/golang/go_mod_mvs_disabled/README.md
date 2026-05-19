# Go MVS DISABLED Test

This test validates behavior when MVS logic is explicitly disabled.

## Test Setup

- **go.mod**: Same as `go_mod_mvs_versions` - 7 direct dependencies with complex transitive dependency graph
- **go.sum**: Contains 439 lines with multiple versions of packages (e.g., golang.org/x/text has 7 different versions)
- **.env**: Sets `TRUSTIFY_DA_GO_MVS_LOGIC_ENABLED=false`

## Expected Behavior

With MVS Logic DISABLED:
- Should scan **ALL** versions listed in go.sum, not just what MVS selected
- For golang.org/x/text: should scan v0.3.7 (vulnerable: CVE-2022-32149) even though MVS selected v0.9.0
- Should report significantly more dependencies than the MVS-enabled case
- **Expected:** More vulnerabilities reported due to scanning older/vulnerable versions

## Why This Matters

When MVS is disabled, the scanner reports vulnerabilities in all transitive
versions listed in go.sum, not just what MVS selected. This can create
false positives but may be useful for comprehensive dependency auditing where
you want to know about ALL versions that were ever considered.

## Comparison

See [go_mod_mvs_versions](../go_mod_mvs_versions/) for the default (and recommended)
MVS-enabled behavior where only MVS-selected versions are scanned.
