# Go MVS ENABLED Test

This test validates that the clients correctly implement Go's MVS algorithm when enabled.

## Test Setup

- **go.mod**: Same as `go_mod_mvs_versions` - 7 direct dependencies with complex transitive dependency graph
- **go.sum**: Contains 438 lines with multiple versions of packages (e.g., golang.org/x/text has 7 different versions)
- **.env**: Sets `TRUSTIFY_DA_GO_MVS_LOGIC_ENABLED=true`

## Expected Behavior

With MVS Logic ENABLED (default):
- Should scan **ONLY** what MVS selected from the dependency graph
- For golang.org/x/text: should scan ONLY v0.9.0 (MVS-selected), NOT v0.3.7
- Should NOT report CVE-2022-32149 (only affects v0.3.7 which MVS didn't select)
- Should scan approximately 142 total modules (matching the MVS-resolved dependency graph)
- **Expected:** Only vulnerabilities from MVS-selected versions

## Why This Matters

This is the default and correct behavior. Go's MVS algorithm selects one version
per package. Scanning only the selected version matches what actually gets compiled
into the binary, avoiding false positives from older versions that are in go.sum
but not actually used.

## Comparison

See [go_mod_mvs_disabled](../go_mod_mvs_disabled/) for the opposite behavior where
all versions in go.sum are scanned, potentially creating false positives.
