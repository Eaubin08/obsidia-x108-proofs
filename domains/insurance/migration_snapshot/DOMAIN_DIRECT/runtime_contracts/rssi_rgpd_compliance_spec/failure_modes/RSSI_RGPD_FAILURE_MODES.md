# RSSI_RGPD_FAILURE_MODES

Each failure must result in:

fail_closed
no_act
requires_x108_review
never_allow_by_default

| ID | Failure mode | Description | Required outcome |
|---|---|---|---|
| F03-FM-01 | rssi_claims_security_certification | RSSI material claims security is certified | fail_closed |
| F03-FM-02 | rgpd_claims_legal_compliance | RGPD material claims legal compliance | fail_closed |
| F03-FM-03 | iso_certification_claim | ISO readiness becomes certification | fail_closed |
| F03-FM-04 | dpo_review_bypassed | DPO/legal review is assumed complete | fail_closed |
| F03-FM-05 | personal_data_processing_authorized | Personal data processing is authorized by docs | fail_closed |
| F03-FM-06 | student_data_used_without_scope | Student data enters benchmark/runtime | fail_closed |
| F03-FM-07 | rssi_auto_block_attempt | RSSI control emits BLOCK directly | fail_closed |
| F03-FM-08 | rgpd_auto_allow_attempt | RGPD scope emits ALLOW directly | fail_closed |
| F03-FM-09 | evidence_ticket_used_as_decision | OS3 evidence replaces DecisionTicket | fail_closed |
| F03-FM-10 | context_packet_used_as_approval | ContextPacket treated as approval | fail_closed |
| F03-FM-11 | python_runtime_import | .py from source pack imported | fail_closed |
| F03-FM-12 | package_creation_attempt | packages/ created for F03 | fail_closed |
| F03-FM-13 | x108_override_attempt | RSSI/RGPD overrides X108 | fail_closed |
| F03-FM-14 | runtime_ready_claim | RSSI/RGPD pack claimed runtime-ready | fail_closed |
| F03-FM-15 | full_import_claim | All files claimed imported | fail_closed |
| F03-FM-16 | audit_passed_claim | Audit-readiness becomes audit passed | fail_closed |
| F03-FM-17 | security_policy_enforced_claim | Policy doc becomes enforcement | fail_closed |
| F03-FM-18 | data_retention_compliant_claim | Retention note becomes legal compliance | fail_closed |
| F03-FM-19 | boundary_missing | Missing RSSI/RGPD boundary | fail_closed |
| F03-FM-20 | fail_open_behavior | Any violation defaults to allow | fail_closed |