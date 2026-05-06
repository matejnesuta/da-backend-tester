# Test: MATCH_MANIFEST_VERSIONS (Permissive Mode)

## Purpose
Tests the `MATCH_MANIFEST_VERSIONS=false` setting for Python pip packages.

## Expected Behavior
When `MATCH_MANIFEST_VERSIONS=false`:
- The API should ignore version differences between manifest and installed packages
- Analysis should proceed using the installed/resolved versions
- No error should be thrown for version mismatches
- The analysis output may show different versions than what's in requirements.txt

## Test Setup
- Uses a virtual environment (`TRUSTIFY_DA_PYTHON_VIRTUAL_ENV=true`)
- requirements.txt contains pinned versions of common packages
- The virtual environment may install different versions than declared
- This is the original/default behavior

## Reference
See Python Support documentation for MATCH_MANIFEST_VERSIONS feature.
