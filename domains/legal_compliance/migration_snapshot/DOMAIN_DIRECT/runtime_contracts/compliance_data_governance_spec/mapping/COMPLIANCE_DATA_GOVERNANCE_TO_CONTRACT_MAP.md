# COMPLIANCE_DATA_GOVERNANCE_TO_CONTRACT_MAP

| Source object | Contract target | Allowed use | Forbidden use | Failure mode |
|---|---|---|---|---|
| privacy policy note | ContextPacket | privacy-risk context | legal compliance claim | fail_closed |
| data governance checklist | ContextPacket | governance advisory | runtime enforcement | fail_closed |
| retention note | ContextPacket | retention-scope warning | retention compliance claim | fail_closed |
| access-control note | ContextPacket | access-risk context | access enforcement claim | fail_closed |
| DPO/legal placeholder | OS3EvidenceTicket reference | future human review evidence | approval claim | fail_closed |
| compliance readiness note | OS3EvidenceTicket reference | readiness evidence | certification claim | fail_closed |
| personal-data processing candidate | IntentEnvelope candidate | requires X108 review | direct authorization | fail_closed |
| education-data warning | ContextPacket | student-data scope warning | student data use approval | fail_closed |