# License Detection Test Cases

This directory contains test cases for validating license detection behavior across different package ecosystems.

## Structure

```
license-detection/
├── maven/
│   ├── license_in_manifest_only/     # License declared in pom.xml only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   ├── license_mismatched/           # Both manifest and file (different)
│   ├── license_md_variant/           # LICENSE.md file variant
│   ├── license_gpl/                  # GPL-3.0-only (STRONG_COPYLEFT category)
│   ├── license_gpl2/                 # GPL-2.0-only (STRONG_COPYLEFT category)
│   ├── license_bsd/                  # BSD-3-Clause (PERMISSIVE)
│   ├── license_bsd2/                 # BSD-2-Clause (PERMISSIVE)
│   └── no_license/                   # No license in manifest or file
├── npm/
│   ├── license_in_manifest_only/     # License in package.json only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   ├── license_mismatched/           # Both manifest and file (different)
│   ├── license_txt_variant/          # LICENSE.txt file variant
│   ├── license_lgpl/                 # LGPL-3.0-only (WEAK_COPYLEFT category)
│   ├── license_lgpl2/                # LGPL-2.1-only (WEAK_COPYLEFT category)
│   ├── license_agpl/                 # AGPL-3.0-only (STRONG_COPYLEFT category)
│   └── no_license/                   # No license in manifest or file
├── pnpm/
│   ├── license_in_manifest_only/     # License in package.json only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   └── license_mismatched/           # Both manifest and file (different)
├── yarn-berry/
│   ├── license_in_manifest_only/     # License in package.json only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   └── license_mismatched/           # Both manifest and file (different)
├── yarn-classic/
│   ├── license_in_manifest_only/     # License in package.json only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   └── license_mismatched/           # Both manifest and file (different)
├── cargo/
│   ├── license_in_manifest_only/     # License in Cargo.toml only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   └── license_mismatched/           # Both manifest and file (different)
├── poetry/
│   ├── license_in_manifest_only/     # License in pyproject.toml only
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   └── license_mismatched/           # Both manifest and file (different)
├── uv/
│   ├── license_in_manifest_only/     # License in pyproject.toml only (PEP 621)
│   ├── license_in_file_only/         # License in LICENSE file only
│   ├── license_matching/             # Both manifest and file (matching)
│   └── license_mismatched/           # Both manifest and file (different)
├── golang/
│   ├── license_file_detection/       # LICENSE file (Go has no manifest license)
│   └── no_license/                   # No LICENSE file
├── gradle-groovy/
│   ├── license_file_detection/       # LICENSE file (Gradle has no manifest license)
│   └── no_license/                   # No LICENSE file
├── gradle-kotlin/
│   ├── license_file_detection/       # LICENSE file (Gradle has no manifest license)
│   └── no_license/                   # No LICENSE file
└── pip/
    ├── license_file_detection/       # LICENSE file (Python has no manifest license)
    └── no_license/                   # No LICENSE file
```

## License Resolution Behavior

The backend uses a **fallback mechanism** for license detection:

- `manifestLicense` = Primary license field (manifest first, then LICENSE file as fallback)
- `fileLicense` = LICENSE file content (populated when LICENSE file exists)
- `mismatch` = true when manifest and LICENSE file declare different licenses

When there's no license in the manifest, `manifestLicense` falls back to the LICENSE file, so both fields will have the same value.

## Test Scenarios

### Ecosystems with Manifest License Support (Maven, npm, Cargo)

1. **Manifest only** - License in manifest, no LICENSE file
   - Expected: `manifestLicense` populated from manifest, `fileLicense` null, `mismatch` false

2. **File only** - No license in manifest, LICENSE file present
   - Expected: `manifestLicense` populated from LICENSE file (fallback), `fileLicense` populated from LICENSE file, `mismatch` false
   - Note: When no manifest license exists, the LICENSE file populates both fields via fallback mechanism

3. **Matching** - Same license in both manifest and LICENSE file
   - Expected: Both populated with same SPDX ID, `mismatch` false

4. **Mismatched** - Different licenses in manifest vs LICENSE file
   - Expected: `manifestLicense` from manifest, `fileLicense` from LICENSE file (different SPDX IDs), `mismatch` true

### Ecosystems without Manifest License Support (Go, Gradle, Python)

1. **File detection** - LICENSE file in project directory
   - Expected: `manifestLicense` populated from LICENSE file (fallback), `fileLicense` populated from LICENSE file, `mismatch` false
   - Note: These ecosystems always use LICENSE file for both fields since manifest license is not supported

2. **No license** - No LICENSE file present
   - Expected: `manifestLicense` null, `fileLicense` null, `mismatch` false

### LICENSE File Variants

Tests that the backend detects licenses from different file name variants:

1. **LICENSE.md** - Markdown license file
   - Expected: Same behavior as plain LICENSE file

2. **LICENSE.txt** - Text license file
   - Expected: Same behavior as plain LICENSE file

### License Categories

Tests different SPDX license categories beyond PERMISSIVE:

1. **STRONG_COPYLEFT** - GPL-2.0-only, GPL-3.0-only, AGPL-3.0-only
   - Requires derivative works to use the same license
   - AGPL additionally requires source disclosure for network services

2. **WEAK_COPYLEFT** - LGPL-2.1-only, LGPL-3.0-only
   - Allows linking with proprietary code
   - Modifications to LGPL code must remain under LGPL

3. **PERMISSIVE** - MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause
   - Minimal restrictions on use and redistribution
   - Can be combined with proprietary code

## Running Tests

```bash
# Run all license detection tests
./run-in-container.sh -m license_detection

# Run for specific ecosystem
./run-in-container.sh -m license_detection -k maven
./run-in-container.sh -m license_detection -k npm
./run-in-container.sh -m license_detection -k pnpm
./run-in-container.sh -m license_detection -k yarn-berry
./run-in-container.sh -m license_detection -k yarn-classic
./run-in-container.sh -m license_detection -k cargo
./run-in-container.sh -m license_detection -k poetry
./run-in-container.sh -m license_detection -k uv
./run-in-container.sh -m license_detection -k golang
./run-in-container.sh -m license_detection -k gradle-groovy
./run-in-container.sh -m license_detection -k gradle-kotlin
./run-in-container.sh -m license_detection -k pip

# Run specific test scenarios
./run-in-container.sh -m license_detection -k "mismatched"
./run-in-container.sh -m license_detection -k "no_license"
./run-in-container.sh -m license_detection -k "gpl"
```

## Expected Output Format

The `license` subcommand returns:

```json
{
  "manifestLicense": {
    "spdxId": "MIT",
    "category": "PERMISSIVE",
    "name": "MIT License",
    "identifiers": ["MIT"]
  },
  "fileLicense": {
    "spdxId": "Apache-2.0",
    "category": "PERMISSIVE",
    "name": "Apache License 2.0",
    "identifiers": ["Apache-2.0"]
  },
  "mismatch": true
}
```

## SPDX Detection

The tests verify automatic detection of common licenses from LICENSE file content:

**PERMISSIVE:**
- **MIT** - MIT License
- **Apache-2.0** - Apache License 2.0
- **BSD-2-Clause** - BSD 2-Clause "Simplified" License
- **BSD-3-Clause** - BSD 3-Clause "New" or "Revised" License

**STRONG_COPYLEFT:**
- **GPL-2.0-only** - GNU General Public License v2.0 only
- **GPL-3.0-only** - GNU General Public License v3.0 only
- **AGPL-3.0-only** - GNU Affero General Public License v3.0 only

**WEAK_COPYLEFT:**
- **LGPL-2.1-only** - GNU Lesser General Public License v2.1 only (currently categorized as UNKNOWN by backend)
- **LGPL-3.0-only** - GNU Lesser General Public License v3.0 only

The backend detects SPDX identifiers from LICENSE file content and categorizes them appropriately. Note that we use the current SPDX 3.0 format (e.g., `GPL-3.0-only` instead of deprecated `GPL-3.0`).

## Notes

- Lockfiles (package-lock.json, go.sum, etc.) are NOT required for license detection tests
- The `license` subcommand only reads manifest files and LICENSE files
- Tests validate behavior for both Java and JavaScript clients
