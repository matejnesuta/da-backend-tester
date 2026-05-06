# Test: MATCH_MANIFEST_VERSIONS (Strict Mode)

## Purpose
Tests the `MATCH_MANIFEST_VERSIONS=true` setting for Python pip packages.

## Expected Behavior
When `MATCH_MANIFEST_VERSIONS=true`:
- The API should compare declared versions in requirements.txt against installed/resolved versions
- If there is a version mismatch, it should throw an error
- The error message should contain:
  - Package name
  - Declared version (from manifest)
  - Installed version (from environment)
  - Suggestion to set `MATCH_MANIFEST_VERSIONS=false` to ignore differences

## Test Setup
- Uses a virtual environment (`TRUSTIFY_DA_PYTHON_VIRTUAL_ENV=true`)
- requirements.txt contains pinned versions of common packages
- The virtual environment may install different versions than declared

## Reference
See Python Support documentation for MATCH_MANIFEST_VERSIONS feature.
