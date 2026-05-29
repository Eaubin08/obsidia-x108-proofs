# OBSIDIA F45 — Canonical Observation Terminal Test Battery

**Audit ID:** F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY  
**Timestamp:** 20260529_090000  
**Mode:** AUDIT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**HEAD:** 265b330  
**Parent audit:** F44_CANONICAL_INTEGRITY_AUDIT_SINCE_20260526  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_STATUS=PASS_WITH_CONFIRMED_FINDINGS
PARENT=F44_CANONICAL_INTEGRITY_AUDIT_SINCE_20260526
HEAD=265b330
F2_CONTROLLED_RESPONSE_TEXT_UNSANITIZED_CLASSIFICATION=CONFIRMED
F4_BASE_UPDATE_OVERRIDE_CLASSIFICATION=CONFIRMED
F6_KERNEL_TRACE_FORBIDDEN_TOKENS_CLASSIFICATION=DOC_ONLY
F1_BOUNDARY_TRUNCATED_CLASSIFICATION=CONFIRMED_LEGACY_ONLY
F3_SURFACES_READY_ENV_DEPENDENT_CLASSIFICATION=DOC_ONLY
F5_TOKEN_SCAN_SCOPE_CLASSIFICATION=CONFIRMED_LEGACY_SCOPE
F7_HARDCODED_PROOF_LINKS_CLASSIFICATION=DOC_ONLY
CONFIRMED_FINDINGS=4
FALSE_POSITIVES=0
DOC_ONLY=3
NEEDS_PATCH=0
NEEDS_MORE_REVIEW=0
BASELINE_TESTS=103/103
KX108_ONLY_PRESERVED=true
BRODY_DECISION=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
PATCH=NO  COMMIT=NO  TAG=NO  PUSH=NO
```

---

## CLASSIFICATION TABLE

| Finding | F44 Severity | F45 Classification |
|---------|-------------|-------------------|
| `F2_controlled_response_text_unsanitized` | MEDIUM | **CONFIRMED** |
| `F4_base_update_override` | MEDIUM | **CONFIRMED** |
| `F6_kernel_trace_forbidden_tokens` | LOW-MEDIUM | **DOC_ONLY** |
| `F1_boundary_truncated` | LOW | **CONFIRMED_LEGACY_ONLY** |
| `F3_surfaces_ready_env_dependent` | LOW | **DOC_ONLY** |
| `F5_token_scan_scope` | LOW | **CONFIRMED_LEGACY_SCOPE** |
| `F7_hardcoded_proof_links` | LOW | **DOC_ONLY** |

---

## F2_controlled_response_text_unsanitized

**F44 Severity:** MEDIUM  
**F45 Classification:** `CONFIRMED`

- **confirmed_injections_count:** `11`
- **false_positive_substring_count:** `9`
- **safe_backend_response_sanitizes_nested:** `False`

### Evidence

```json
{
  "case": "isolated_ALLOW",
  "user_input": "ALLOW",
  "text_excerpt": "Demande re\u00e7ue : \u00ab ALLOW \u00bb\nDomaine consult\u00e9 : bank.\nContexte disponible : 7 surfaces runtime op\u00e9rationnelles (brody_runtime_context, monitoring_adapters, neo4j_guide_bridge, operator_view_packet, sigma",
  "forbidden_tokens_word_boundary": [
    "ALLOW"
  ],
  "forbidden_tokens_substring_only": [],
  "sanitized_at_route": false
}
```

```json
{
  "case": "isolated_HOLD",
  "user_input": "HOLD",
  "text_excerpt": "Demande re\u00e7ue : \u00ab HOLD \u00bb\nDomaine consult\u00e9 : bank.\nContexte disponible : 7 surfaces runtime op\u00e9rationnelles (brody_runtime_context, monitoring_adapters, neo4j_guide_bridge, operator_view_packet, sigma_",
  "forbidden_tokens_word_boundary": [
    "HOLD"
  ],
  "forbidden_tokens_substring_only": [],
  "sanitized_at_route": false
}
```

```json
{
  "case": "isolated_BLOCK",
  "user_input": "BLOCK",
  "text_excerpt": "Demande re\u00e7ue : \u00ab BLOCK \u00bb\nDomaine consult\u00e9 : bank.\nContexte disponible : 7 surfaces runtime op\u00e9rationnelles (brody_runtime_context, monitoring_adapters, neo4j_guide_bridge, operator_view_packet, sigma",
  "forbidden_tokens_word_boundary": [
    "BLOCK"
  ],
  "forbidden_tokens_substring_only": [],
  "sanitized_at_route": false
}
```

---

## F4_base_update_override

**F44 Severity:** MEDIUM  
**F45 Classification:** `CONFIRMED`

- **confirmed_overrides_count:** `11`
- **pydantic_schema_blocks_injection:** `True`

### Evidence

```json
{
  "injected": {
    "decision_authority": "BRODY_OVERRIDE"
  },
  "result_sovereignty_flags": {
    "decision_authority": "BRODY_OVERRIDE",
    "allowed_to_decide": null,
    "emits_act": false,
    "emits_verdict": false,
    "kernel_mutation": false,
    "x108_mutation": null,
    "neo4j_write": null,
    "brody_decision": null
  }
}
```

```json
{
  "injected": {
    "allowed_to_decide": true
  },
  "result_sovereignty_flags": {
    "decision_authority": "KX108_ONLY",
    "allowed_to_decide": true,
    "emits_act": false,
    "emits_verdict": false,
    "kernel_mutation": false,
    "x108_mutation": null,
    "neo4j_write": null,
    "brody_decision": null
  }
}
```

```json
{
  "injected": {
    "emits_act": true
  },
  "result_sovereignty_flags": {
    "decision_authority": "KX108_ONLY",
    "allowed_to_decide": null,
    "emits_act": true,
    "emits_verdict": false,
    "kernel_mutation": false,
    "x108_mutation": null,
    "neo4j_write": null,
    "brody_decision": null
  }
}
```

---

## F6_kernel_trace_forbidden_tokens

**F44 Severity:** LOW-MEDIUM  
**F45 Classification:** `DOC_ONLY`

- **stdout_captured_bytes:** `1178`
- **api_response_clean:** `True`

### Evidence

```json
{
  "source": "stdout_during_f36_call",
  "stdout_length": 1178,
  "stdout_sample": "\ud83d\udd0d [KERNEL_TRACE] Bank state active. Amount: 0.0\n\ud83d\udd0d [KERNEL_TRACE] Aggregate Audit for Domain.BANK | Verdict: ANALYZE | Integrity: 0.5 | Severity: S4\n\ud83d\udd0d [KERNEL_TRACE] Sovereign Audit for bank | Verdict: ANALYZE | Gate: BLOCK | Integrity: 0.5 | Governance: 0.95 | Readiness: 0.66 | Severity: S4\n\ud83d\udd0d [KERNEL_TRACE] Bank state active. Amount: 10.0\n\ud83d\udd0d [KERNEL_TRACE] Bank state active. Amount: 10.0\n\ud83d\udd0d [KERNEL_TRACE] Aggregate Audit for Domain.BANK | Verdict: ANALYZE | Integrity: 0.5 | Severity: S2\n\ud83d\udd0d [KERNEL_",
  "forbidden_tokens_word_boundary": [
    "ALLOW",
    "BLOCK",
    "VERDICT"
  ],
  "forbidden_tokens_substring": [
    "ALLOW",
```

```json
{
  "source": "api_response_controlled_response_text",
  "response_length": 565,
  "forbidden_tokens_word_boundary": []
}
```

```json
{
  "source": "api_response_top_level_string_values",
  "forbidden_string_values": {}
}
```

---

## F1_boundary_truncated

**F44 Severity:** LOW  
**F45 Classification:** `CONFIRMED_LEGACY_ONLY`

- **ops_boundary_flag_count:** `4`
- **v1_module_boundary_flag_count:** `15`
- **v1_routes_unaffected:** `True`

### Evidence

```json
{
  "ops_boundary_keys": [
    "decision_authority",
    "emits_act",
    "memory_write",
    "readonly"
  ],
  "ops_boundary_values": {
    "readonly": true,
    "emits_act": false,
    "memory_write": false,
    "decision_authority": "KX108_ONLY"
  },
  "f32_boundary_flag_count": 15,
  "f36_boundary_flag_count": 15,
  "f37_boundary_flag_count": 15,
  "flags_missing_from_ops": [
    "advisory_only",
    "allowed_to_decide",
    "brody_decision",
    "can_decide",
    "can_emit_act",
    "context_signal_only",
    "emits_verdict",
    "graphiti_write",
    "kernel_mutation",
    "neo4j_write",
    "runtime_execute",
    "x108_mutation"
  ],
  "ops_boundary_occurrences_in_source": 70,
  "v1_routes_use_ops_boundary": false
}
```

---

## F3_surfaces_ready_env_dependent

**F44 Severity:** LOW  
**F45 Classification:** `DOC_ONLY`

- **surfaces_ready_observed:** `7`
- **dynamically_computed:** `True`
- **hardcoded_in_source:** `False`

### Evidence

```json
{
  "surfaces_ready": 7,
  "surfaces_total": 7,
  "surface_statuses": {
    "sigma_dispatcher": "READY",
    "tree_signal_packet": "READY",
    "monitoring_adapters": "READY",
    "operator_view_packet": "READY",
    "brody_runtime_context": "READY",
    "workflow_governance_readonly": "READY",
    "neo4j_guide_bridge": "READY"
  },
  "dynamically_computed": true,
  "expected_surface_names": [
    "sigma_dispatcher",
    "tree_signal_packet",
    "monitoring_adapters",
    "operator_view_packet",
    "brody_runtime_context",
    "workflow_governance_readonly",
    "neo4j_guide_bridge"
  ]
}
```

```json
{
  "hardcoded_7_in_source": false,
  "source_fragment": "def build_f32_full_runtime_integration_packet(\n    *,\n    domain: str = \"bank\",\n    sigma_payload: dict[str, Any] | None = None,\n    sop_text: str = (\n        \"1. Read readonly request\\n\"\n        \"2. "
}
```

---

## F5_token_scan_scope

**F44 Severity:** LOW  
**F45 Classification:** `CONFIRMED_LEGACY_SCOPE`

- **f36_runtime_scans_own_output:** `False`
- **f37_runtime_scans_scenario_text:** `True`
- **safe_response_scans_controlled_response_text:** `False`

### Evidence

```json
{
  "f36_declares_forbidden_tokens": true,
  "f36_runtime_scans_own_output": false,
  "f37_runtime_scans_scenario_text": true,
  "f37_scans_controlled_response_text_field": true,
  "f37_scan_covers_nested_json": false,
  "f37_scan_covers_proof_fields": false,
  "f37_scan_covers_stdout": false,
  "safe_response_scan_covers_controlled_response_text": false
}
```

```json
{
  "regex_trap_cases": [
    {
      "text": "ALLOW",
      "found": true,
      "expected": true,
      "correct": true,
      "note": "should match"
    },
    {
      "text": "reactivity",
      "found": false,
      "expected": false,
      "correct": true,
      "note": "REACT is not word-boundary match in REACTIVITY"
    },
    {
      "text": "interaction",
      "found": false,
      "expected": false,
      "correct": true,
      "note": "ACT is not word-boundary match in INTERACTION"
    },
    {
      "text": "BLOCK_CHAIN",
      "found": false,
      "expected": false,
      "correct": true,
      "note": "BLOCK inside compound \u2014 depends on locale"
    },
    {
      "text": "ACTOR",
      "found": false,
      "expected": false,
      "correct": true,
      "note": "ACT 
```

---

## F7_hardcoded_proof_links

**F44 Severity:** LOW  
**F45 Classification:** `DOC_ONLY`

- **links_checked:** `3`
- **links_exist:** `3`
- **links_broken:** `0`

### Evidence

```json
{
  "path": "docs/runtime/F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json",
  "exists": true,
  "full_path": "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs_REMOTE_A5F21C6B\\docs\\runtime\\F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json"
}
```

```json
{
  "path": "docs/runtime/OBSIDIA_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438.md",
  "exists": true,
  "full_path": "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs_REMOTE_A5F21C6B\\docs\\runtime\\OBSIDIA_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438.md"
}
```

```json
{
  "path": ".runtime_freezes/F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438/MANIFEST_SHA256.json",
  "exists": true,
  "full_path": "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs_REMOTE_A5F21C6B\\.runtime_freezes\\F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_20260529_024438\\MANIFEST_SHA256.json"
}
```

---

## TERMINAL FINAL

```
F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_STATUS=PASS_WITH_CONFIRMED_FINDINGS
PATCH=NO  COMMIT=NO  TAG=NO  PUSH=NO
NEXT=commit F45 → tag BRODY_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_PALIER_20260529
```

*F45 Terminal Test Battery · AUDIT_ONLY · READONLY · KX108_ONLY · Generated 2026-05-29*