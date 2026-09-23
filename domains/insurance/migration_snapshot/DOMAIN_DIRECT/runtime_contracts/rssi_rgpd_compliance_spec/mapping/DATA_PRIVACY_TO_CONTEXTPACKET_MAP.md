# DATA_PRIVACY_TO_CONTEXTPACKET_MAP

| Data/privacy concern | ContextPacket field candidate | Required boundary | Forbidden claim |
|---|---|---|---|
| personal data | privacy_risk_context | RGPD_COMPLIANCE_SCOPE_GUARD | processing approved |
| educational data | education_data_scope | RGPD_COMPLIANCE_SCOPE_GUARD | student data authorized |
| security control | security_evidence_context | RSSI_EVIDENCE_ONLY | security certified |
| audit note | audit_readiness_context | RSSI_EVIDENCE_ONLY | audit passed |
| retention note | retention_scope_context | RGPD_COMPLIANCE_SCOPE_GUARD | legally compliant |
| access control note | access_risk_context | RSSI_EVIDENCE_ONLY | access enforced |
| incident note | incident_readiness_context | RSSI_EVIDENCE_ONLY | incident response certified |