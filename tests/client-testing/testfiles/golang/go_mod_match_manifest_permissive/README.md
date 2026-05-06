# MATCH_MANIFEST_VERSIONS Permissive Test

Tests permissive behavior when manifest and resolved versions differ.

## Test Setup

- **go.mod declares:** `github.com/gin-gonic/gin v1.7.7` (vulnerable)
- **replace directive:** Changes it to `v1.9.1` (patched)
- **Mismatch:** Manifest says v1.7.7, resolved is v1.9.1
- **.env:** Sets `MATCH_MANIFEST_VERSIONS=false`

## Expected Behavior

With `MATCH_MANIFEST_VERSIONS=false` (permissive):
- Should CONTINUE analysis despite version mismatch
- Should analyze the **resolved** version (v1.9.1)
- Should NOT report gin vulnerabilities (v1.9.1 is patched)
- **Expected:** 0 vulnerabilities, analysis succeeds

## Why This Matters

In real projects, resolved versions often differ from manifest declarations due to:
- `replace` directives (security patches, forks)
- MVS selecting higher versions
- Transitive dependency upgrades

The permissive mode allows analysis to proceed with the actual resolved versions.

## Comparison

See [go_mod_match_manifest_strict](../go_mod_match_manifest_strict/) for strict mode
where this mismatch would cause an error.
