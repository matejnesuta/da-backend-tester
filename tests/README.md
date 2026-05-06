# Test Suites

This directory contains two independent test suites:

## Structure

```
tests/
├── client-testing/       # Client validation suite (default)
│   ├── src/tester/       # Client runner infrastructure
│   ├── testfiles/        # Ecosystem test cases (maven, npm, pip, etc.)
│   ├── __snapshots__/    # Syrupy snapshot files
│   ├── test_*.py         # Test files
│   ├── conftest.py       # Suite fixtures
│   └── pytest.ini        # Suite config
│
└── license-testing/      # License API suite
    ├── testfiles/        # License sample files
    ├── test_*.py         # Test files
    └── conftest.py       # Suite fixtures
```

## Client Testing (Default)

Tests DA client behavior against the backend using ecosystem-based test cases.

**Requires**: DA clients (Java and/or JavaScript)  
**Tests**: Client consistency, snapshot-based validation  

```bash
# Run client tests
./run-in-container.sh
./run-in-container.sh --suite client
python -m pytest tests/client-testing/

# With filters
./run-in-container.sh --ecosystem maven
./run-in-container.sh --client java
```

## License Testing

Tests backend license API endpoints directly via HTTP.

**Requires**: Backend running, TRUSTIFY_DA_BACKEND_URL set  
**Tests**: API contracts, assertion-based validation  

```bash
# Run license tests
export TRUSTIFY_DA_BACKEND_URL=https://backend
./run-in-container.sh --suite license  
python -m pytest tests/license-testing/

# With markers
python -m pytest tests/license-testing/ -m license_api
```

## Key Differences

| Aspect | Client Testing | License Testing |
|--------|----------------|-----------------|
| **Purpose** | Validate clients | Validate backend API |
| **Method** | Client runner | Direct HTTP |
| **Data** | Ecosystem manifests | License files |
| **Validation** | Snapshots | Assertions |
| **Dependencies** | DA clients | Backend URL |

## Adding Tests

### To client-testing:
1. Add manifest to `client-testing/testfiles/<ecosystem>/`
2. Run with `--snapshot-update` to create baseline
3. Commit snapshot to `client-testing/__snapshots__/`

### To license-testing:
1. Add test to appropriate `test_licenses*.py`
2. Use simple assertions (no snapshots)
3. Mark with `@pytest.mark.license_*`
