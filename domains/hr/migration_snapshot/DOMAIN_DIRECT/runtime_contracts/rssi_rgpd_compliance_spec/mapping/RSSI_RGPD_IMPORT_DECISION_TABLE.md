# RSSI_RGPD_IMPORT_DECISION_TABLE

| Source family | Current status | Decision | Runtime allowed now? | Boundary |
|---|---|---|---|---|
| RSSI security docs | source audited | evidence-only spec candidates | false | RSSI_EVIDENCE_ONLY |
| RGPD / GDPR docs | source audited | compliance-scope guard candidates | false | RGPD_COMPLIANCE_SCOPE_GUARD |
| ISO readiness notes | source audited | readiness-only evidence candidates | false | RSSI_EVIDENCE_ONLY |
| DPO/legal notes | source audited | human-review placeholder only | false | RGPD_COMPLIANCE_SCOPE_GUARD |
| .py files | forbidden | DO_NOT_IMPORT_RUNTIME | false | NO_PYTHON |
| cache/runtime-freeze files | forbidden | ARCHIVE_ONLY | false | SOURCE_ONLY |
| critical action controls | controlled | IntentEnvelope candidate only | false | X108_GATEWAY_REQUIRED |