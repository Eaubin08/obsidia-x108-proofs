# COMPLIANCE_DATA_GOVERNANCE_FAILURE_MODES

Each failure must result in:

fail_closed
no_act
requires_x108_review
never_allow_by_default

| ID | Failure mode | Description | Required outcome |
|---|---|---|---|
| F10-FM-01 | legal_compliance_claim | Legal compliance is claimed | fail_closed |
| F10-FM-02 | rgpd_compliance_claim | RGPD compliance is claimed | fail_closed |
| F10-FM-03 | iso_certification_claim | ISO/security certification is claimed | fail_closed |
| F10-FM-04 | personal_data_processing_authorized | Personal-data processing is authorized | fail_closed |
| F10-FM-05 | student_data_processing_authorized | Student data usage is approved | fail_closed |
| F10-FM-06 | retention_compliance_claim | Retention note becomes compliance claim | fail_closed |
| F10-FM-07 | access_enforcement_claim | Access policy becomes enforced runtime | fail_closed |
| F10-FM-08 | audit_passed_claim | Readiness becomes audit passed | fail_closed |
| F10-FM-09 | runtime_policy_execution | Policy executes at runtime | fail_closed |
| F10-FM-10 | evidence_ticket_used_as_decision | OS3 evidence replaces DecisionTicket | fail_closed |
| F10-FM-11 | context_packet_used_as_approval | ContextPacket treated as approval | fail_closed |
| F10-FM-12 | python_runtime_import | .py imported from pack | fail_closed |
| F10-FM-13 | package_creation_attempt | packages/ created for F10 | fail_closed |
| F10-FM-14 | x108_override_attempt | Compliance layer overrides X108 | fail_closed |
| F10-FM-15 | runtime_ready_claim | F10 pack claimed runtime-ready | fail_closed |
| F10-FM-16 | full_import_claim | All files claimed imported | fail_closed |
| F10-FM-17 | memory_write_attempt | Compliance layer writes memory | fail_closed |
| F10-FM-18 | graph_write_attempt | Compliance layer writes graph | fail_closed |
| F10-FM-19 | boundary_missing | Missing compliance boundary | fail_closed |
| F10-FM-20 | fail_open_behavior | Any violation defaults to allow | fail_closed |