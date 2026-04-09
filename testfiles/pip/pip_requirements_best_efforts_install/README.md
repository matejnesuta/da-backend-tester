# Test: TRUSTIFY_DA_PYTHON_INSTALL_BEST_EFFORTS

## Purpose
Tests the "Best Efforts Installation" feature for Python pip packages.

## Expected Behavior
When `TRUSTIFY_DA_PYTHON_INSTALL_BEST_EFFORTS=true`:
- The API should install packages from requirements.txt WITHOUT respecting declared versions
- Instead, it should install versions compatible with the current Python version
- This increases the probability that automatic installation will succeed
- Must be used with `MATCH_MANIFEST_VERSIONS=false`

## Test Setup
- Uses a virtual environment (`TRUSTIFY_DA_PYTHON_VIRTUAL_ENV=true`)
- requirements.txt contains older/outdated versions that may not be compatible
- The best efforts mode should install newer compatible versions instead
- Analysis should proceed with the installed versions

## Background
Python pip packages are very sensitive to Python version changes. Each package version range is typically tailored for a specific Python version. This feature helps avoid installation failures by being flexible about versions.

## Reference
See Python Support documentation for TRUSTIFY_DA_PYTHON_INSTALL_BEST_EFFORTS feature.
