# RSSI_RGPD_TO_OS3_EVIDENCE_MAP

| Source object | Contract target | Allowed use | Forbidden use | Failure mode |
|---|---|---|---|---|
| RSSI checklist | OS3EvidenceTicket reference | audit-readiness evidence | security certification | fail_closed |
| RSSI control note | ContextPacket | advisory risk label | automatic block | fail_closed |
| RGPD principle | ContextPacket | compliance-scope warning | legal compliance claim | fail_closed |
| DPO review placeholder | OS3EvidenceTicket reference | future human review evidence | automatic approval | fail_closed |
| data governance row | ContextPacket | processing-risk context | data-processing authorization | fail_closed |
| ISO readiness note | OS3EvidenceTicket reference | readiness evidence | ISO certification | fail_closed |
| personal-data warning | ContextPacket | privacy risk guard | student data processing | fail_closed |
| critical action control | IntentEnvelope candidate | requires X108 review | direct ACT | fail_closed |

Rule:
RSSI/RGPD can create evidence and scope context.
RSSI/RGPD cannot certify, decide, or act.