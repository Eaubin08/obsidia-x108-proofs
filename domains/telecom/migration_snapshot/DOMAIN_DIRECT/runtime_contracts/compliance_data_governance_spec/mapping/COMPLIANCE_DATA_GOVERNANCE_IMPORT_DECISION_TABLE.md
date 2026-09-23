# COMPLIANCE_DATA_GOVERNANCE_IMPORT_DECISION_TABLE

| Source family | Current status | Decision | Runtime allowed now? | Boundary |
|---|---|---|---|---|
| RGPD/GDPR docs | source audited | scope-guard candidates | false | RGPD_COMPLIANCE_SCOPE_GUARD |
| data governance docs | source audited | advisory context candidates | false | RGPD_COMPLIANCE_SCOPE_GUARD |
| compliance readiness docs | source audited | evidence-only candidates | false | RSSI_EVIDENCE_ONLY |
| DPO/legal notes | source audited | human-review placeholder only | false | RGPD_COMPLIANCE_SCOPE_GUARD |
| .py files | forbidden | DO_NOT_IMPORT_RUNTIME | false | NO_PYTHON |
| cache/runtime freeze files | forbidden | ARCHIVE_ONLY / QUARANTINE | false | SOURCE_ONLY |
| processing action candidates | controlled | IntentEnvelope candidate only | false | X108_GATEWAY_REQUIRED |