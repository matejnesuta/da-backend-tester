# MATCH_MANIFEST_VERSIONS Strict Test

Tests strict behavior when manifest and resolved versions differ.

## Test Setup

- **go.mod declares:** `github.com/gin-gonic/gin v1.7.7` (vulnerable)
- **replace directive:** Changes it to `v1.9.1` (patched)
- **Mismatch:** Manifest says v1.7.7, resolved is v1.9.1
- **.env:** Sets `MATCH_MANIFEST_VERSIONS=true`

## Expected Behavior

With `MATCH_MANIFEST_VERSIONS=true` (strict):
- Should DETECT the version mismatch
- Should ERROR with a message like:
  ```
  Version mismatch detected:
  Package: github.com/gin-gonic/gin
  Manifest version: v1.7.7
  Resolved version: v1.9.1

  Suggestion: Set MATCH_MANIFEST_VERSIONS=false to continue with resolved versions
  ```
- Analysis should FAIL (not produce results)
- **Expected:** Error/failure, not a successful analysis

## Why This Matters

Strict mode ensures users are aware when their declared versions differ from
what's actually being analyzed. This can catch:
- Outdated go.mod files
- Unexpected version resolution
- Configuration drift

## Comparison

See [go_mod_match_manifest_permissive](../go_mod_match_manifest_permissive/) for
permissive mode where this mismatch is allowed and analysis continues.
