# Go MVS DISABLED Test

This test validates behavior when MVS logic is explicitly disabled.

## Test Setup

- **go.mod**: Declares `golang.org/x/text v0.14.0` (patched, no vulnerabilities)
- **go.sum**: Contains both `v0.3.7` (vulnerable: CVE-2022-32149) and `v0.14.0`
- **.env**: Sets `TRUSTIFY_DA_GO_MVS_LOGIC_ENABLED=false`

## Expected Behavior

With MVS Logic DISABLED:
- Should scan **ALL** versions in go.sum: v0.3.7 and v0.14.0
- Should report vulnerabilities from v0.3.7 (CVE-2022-32149)
- **Expected:** 1+ vulnerabilities reported

## Why This Matters

When MVS is disabled, the scanner reports vulnerabilities in all transitive
versions listed in dependencies, not just what MVS selected. This can create
false positives but may be useful for comprehensive dependency auditing.

## Comparison

See [go_mod_mvs_enabled](../go_mod_mvs_enabled/) for the default (and recommended)
behavior where only MVS-selected versions are scanned.
