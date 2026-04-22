OBSIDIA — ENGINE ↔ FORMAL ALIGNMENT AUDIT (V3) — INTEGRAL_KERNEL_0_9_3
Date: 2026-03-03T14:02:10.184067Z

Selection (auto-detected):
- engine_file: NOT FOUND (score=-1)
- os1_file: NOT FOUND (score=-1)
- api_main: NOT FOUND (score=-1)
- audit_log: NOT FOUND (score=-1)
- security: NOT FOUND (score=-1)

Static checks (original):
- FOUND_engine_file: FAIL
- FOUND_os1_file: FAIL
- FOUND_api_main: FAIL
- FOUND_audit_log: FAIL
- FOUND_security: FAIL
- ENGINE_uses_time_elapsed_key: FAIL
- ENGINE_uses_elapsed_s_key: FAIL
- OS1_reads_time_elapsed: FAIL
- OS1_has_elapsed_s_fallback: FAIL
- API_decision_enforces_auth: FAIL
- API_decision_appends_audit: FAIL
- API_decision_has_headers: FAIL
- OVERALL_STATIC_ORIGINAL: FAIL

Patch actions:

Static checks (patched):
- ENGINE_uses_time_elapsed_key: FAIL
- OS1_has_elapsed_s_fallback: FAIL
- OS1_reads_time_elapsed: FAIL
- API_decision_enforces_auth: FAIL
- API_decision_appends_audit: FAIL
- API_decision_has_headers: FAIL
- OVERALL_STATIC_PATCHED: FAIL

Note: runtime smoke test still recommended (start API + call /v1/decision once).