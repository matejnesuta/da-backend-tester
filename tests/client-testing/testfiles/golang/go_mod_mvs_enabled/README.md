# Go MVS ENABLED Test

This test validates that the clients correctly implement Go's MVS algorithm when enabled.

## Test Setup

- **go.mod**: Declares `golang.org/x/text v0.14.0` (patched, no vulnerabilities)
- **go.sum**: Contains both `v0.3.7` (vulnerable: CVE-2022-32149) and `v0.14.0`
- **.env**: Sets `TRUSTIFY_DA_GO_MVS_LOGIC_ENABLED=true`

## Expected Behavior

With MVS Logic ENABLED:
- Should scan **ONLY** what MVS selected: v0.14.0
- Should NOT scan v0.3.7 (even though it's in go.sum)
- Should NOT report CVE-2022-32149 (only in v0.3.7)
- **Expected:** 0 vulnerabilities

## Why This Matters

This is the default and correct behavior. Go's MVS algorithm selects one version
per package. Scanning only the selected version matches what actually gets compiled
into the binary, avoiding false positives.

## Comparison

See [go_mod_mvs_disabled](../go_mod_mvs_disabled/) for the opposite behavior where
all versions in go.sum are scanned.
