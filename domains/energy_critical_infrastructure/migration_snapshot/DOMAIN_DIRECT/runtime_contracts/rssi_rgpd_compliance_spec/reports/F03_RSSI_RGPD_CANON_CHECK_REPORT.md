# F03_RSSI_RGPD_CANON_CHECK_REPORT

Status: F03_RSSI_RGPD_CANON_CHECK_READY

## Why this check exists

The first F03 terminal run produced F03 files but failed during manifest generation because the manifest pipeline used $.FullName instead of $_.FullName.

The first run also reported:
- RSSI/RGPD rows: 2739 / 2739

That means the first row filter was too broad and captured the whole F78C matrix.

## Repair performed

- Required F03 files checked.
- F03 READY report checked.
- F03 SCOPE_OK checked.
- Strict RSSI/RGPD XLSX matrix rebuilt.
- Strict RSSI/RGPD zip inventory rebuilt.
- SHA256 manifest created.
- No runtime created.
- No .py created.
- No packages created.

## Counts

F78C total rows: 2739
Initial broad RSSI/RGPD rows: 2739
Strict RSSI/RGPD rows: 488

Strict RSSI/RGPD zips found: 15
Strict RSSI/RGPD zip internal files: 2440

F03 files: 13
F03 manifest rows: 13

.py under runtime_contracts: 0
packages exists: False

## Canon note

Strict matrix did not capture all F78C rows.

## Claim-scope

F03 remains:
- SPEC_ONLY
- DOCS_ONLY
- RSSI_EVIDENCE_ONLY
- RGPD_COMPLIANCE_SCOPE_GUARD
- no legal certification
- no ISO certification
- no security certification
- no runtime enforcement
- no personal-data processing authorization

## Verdict

F03_RSSI_RGPD_CANON_CHECK_READY