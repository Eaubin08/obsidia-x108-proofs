# Brody GPT V1 — Proof Index F42→F48

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Proof chain:** F42 → F43 → F44 → F45 → F46 → F47 → F48  
**Date:** 2026-05-29  

All SHA256 values are computed from the freeze manifest files in `.runtime_freezes/`.

---

## F42 — Brody GPT V1 Final Release Seal

**Tag:** `BRODY_F42_BRODY_GPT_V1_FINAL_RELEASE_SEAL_PALIER_20260529`  
**Role:** Sealed V1 runtime at HEAD `b67b2c3`. Canonical V1 tag applied.  
**Freeze manifest SHA256:** `D11CCF61E06402862042DF118A4CFB8C58F1D63FB74F0461D3DEC05100646420`  

Key artifacts:
- `docs/runtime/OBSIDIA_F42_BRODY_GPT_V1_FINAL_RELEASE_REPORT_20260529_080000.json`
- `docs/runtime/OBSIDIA_F42_BRODY_GPT_V1_FINAL_RELEASE_REPORT_20260529_080000.md`

V1 canonical tag: `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME_FINAL_20260529`

---

## F43 — Live Server / Port Matrix Audit

**Tag:** `BRODY_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_PALIER_20260529`  
**Role:** Verified V1 API routes live on ports 8011/9010/8000. Confirmed all 7 routes READY_READONLY on live uvicorn.  
**Freeze manifest SHA256:** `5F42AFEA3E31EF999E1463DCBC141782140EAA6D352CB8C5FA49D2362888E21E`  

Key artifacts:
- `docs/runtime/OBSIDIA_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000.json`
- `docs/runtime/OBSIDIA_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000.md`
- `docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md`

Results: 7/7 routes READY_READONLY · boundary contract confirmed on live uvicorn

---

## F44 — Canonical Integrity Audit

**Tag:** `BRODY_F44_CANONICAL_INTEGRITY_AUDIT_PALIER_20260529`  
**Role:** Independent post-seal audit identifying 7 findings (F1→F7) and 8 clean confirmations (C1→C8).  
**Freeze manifest SHA256:** `B3A1FF877520BADAC1E7CF3FDC0AEA527AAAE40FF2897B0F982B412E9944E84B`  

Key artifacts:
- `docs/runtime/OBSIDIA_F44_CANONICAL_INTEGRITY_AUDIT_20260529_090000.json`
- `docs/runtime/OBSIDIA_F44_CANONICAL_INTEGRITY_AUDIT_20260529_090000.md`

Findings summary:
| ID | Finding | Severity |
|----|---------|---------|
| F1 | `_BOUNDARY` truncated (4 of 15 flags) in legacy routes | LOW |
| F2 | `controlled_response.text` embeds user_input without scan | MEDIUM |
| F3 | `surfaces_ready=7` environment-dependent | LOW |
| F4 | `base.update(data)` merge order allows sovereignty override | MEDIUM |
| F5 | Forbidden token scan scope imprecise in docs | LOW |
| F6 | `KERNEL_TRACE` stderr contains forbidden tokens (internal only) | LOW |
| F7 | Hardcoded `proof_links` in workbench connector | LOW |

Clean confirmations (C1→C8): all boundary flags correct, no live mutations, no Neo4j writes, no memory writes, KERNEL_TRACE properly internal.

---

## F45 — Terminal Observation Battery

**Tag:** `BRODY_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_PALIER_20260529`  
**Role:** Terminal-tested each F44 finding one by one. Classified findings. No patches.  
**Freeze manifest SHA256:** `99DD2A966C379766451938E25F200ECA5813C1B912A7253087F8651F5E623416`  

Key artifacts:
- `docs/runtime/OBSIDIA_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_20260529_090000.json`
- `docs/runtime/OBSIDIA_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_20260529_090000.md`
- `docs/demo/OBSIDIA_F45_CANONICAL_OBSERVATION_FINDINGS.md`

Classifications:
| ID | Pre-F47 Classification |
|----|----------------------|
| F1 | CONFIRMED_LEGACY_ONLY |
| F2 | CONFIRMED_PARTIAL |
| F3 | DOC_ONLY |
| F4 | CONFIRMED_ARCHITECTURAL |
| F5 | CONFIRMED_LEGACY_SCOPE |
| F6 | DOC_ONLY |
| F7 | DOC_ONLY |

Baseline: 103/103 PASS · KX108_ONLY preserved

---

## F46 — Canonical Hardening Plan

**Tag:** `BRODY_F46_CANONICAL_HARDENING_PLAN_PALIER_20260529`  
**Role:** Defined patch sequence F47.1→F47.6. No patches applied. PUBLIC_READINESS_GATE set to BLOCKED_UNTIL_F47_HARDENING.  
**Freeze manifest SHA256:** `C2DCB18BBFB485C8A8693A88A2C28D8EEF506D4101F68EDB3CB17533F81064D6`  

Key artifacts:
- `docs/runtime/OBSIDIA_F46_CANONICAL_HARDENING_PLAN_20260529_095000.json`
- `docs/runtime/OBSIDIA_F46_CANONICAL_HARDENING_PLAN_20260529_095000.md`
- `docs/demo/OBSIDIA_F46_PUBLIC_READINESS_GATE.md`
- `docs/demo/OBSIDIA_F46_F47_PATCH_SEQUENCE.md`

---

## F47 — Canonical Hardening Patch Sequence

**Tag:** `BRODY_F47_CANONICAL_HARDENING_PATCH_PALIER_20260529`  
**Role:** Applied 6-phase hardening. Resolved F2 and F4 (CONFIRMED findings). Corrected F1/F5/F6/F3/F7 (doc/isolation). 103/103 tests still PASS. PUBLIC_READINESS_GATE: LIFTED.  
**Freeze manifest SHA256:** `C06BF8471417B4C8C538B06EEF09487019D652ED0AD8A9AF95CB000E077940C2`  

Key artifacts:
- `docs/runtime/OBSIDIA_F47_CANONICAL_HARDENING_PATCH_SEQUENCE_20260529_181500.json`
- `docs/runtime/OBSIDIA_F47_CANONICAL_HARDENING_PATCH_SEQUENCE_20260529_181500.md`
- `docs/demo/OBSIDIA_F47_HARDENING_RESULTS.md`

Patches applied:
| Phase | Name | Verif |
|-------|------|-------|
| F47.1 | Protected Response Envelope | 13/13 sovereignty flags |
| F47.2 | Controlled Response Text Sanitizer | 42/42 sanitizer checks |
| F47.3 | Nested Scan Scope Verification | 9/9 nested checks |
| F47.4 | Legacy Boundary Isolation | annotated |
| F47.5 | Documentation Wording Corrections | 5 files |
| F47.6 | Regression Verification | 103/103 PASS |

Post-F47 findings: **0 CONFIRMED remaining**

---

## F48 — Post-Hardening Release Readiness Check

**Tag:** `BRODY_F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK_PALIER_20260529`  
**Role:** Independent post-F47 verification. Confirmed all checks PASS. No regression. SHA256 manifest 10/10 verified. PUBLIC_RELEASE_GATE: LIFTED.  
**Freeze manifest SHA256:** `2C4E8FA9E87DA36B394C92FAFAB2087F24E68181C53EC4A4A48878EB251A1D7E`  

Key artifacts:
- `docs/runtime/OBSIDIA_F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK_20260529_183000.json`
- `docs/runtime/OBSIDIA_F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK_20260529_183000.md`
- `docs/demo/OBSIDIA_F48_RELEASE_READINESS_DECISION.md`

F48 checks:
| Check | Result |
|-------|--------|
| Git state | CLEAN |
| Baseline tests | 103/103 PASS |
| F47.1 sovereignty | PASS 13/13 |
| F47.2 sanitizer | PASS 42/42 |
| F47.3 nested scan | PASS 9/9 |
| Freeze manifests F43→F47 | 5/5 PRESENT |
| F47 SHA256 recompute | 10/10 OK |
| Docs overclaim scan | CLEAN |
| KX108_ONLY present | CONFIRMED |
| Public release gate | LIFTED |

---

## Proof Chain Summary

```
F42 (SEAL) → F43 (LIVE) → F44 (AUDIT) → F45 (TEST) → F46 (PLAN) → F47 (PATCH) → F48 (VERIFY)
```

| Palier | Tag | Manifest SHA256 (first 16) |
|--------|-----|---------------------------|
| F42 | BRODY_F42_...PALIER_20260529 | D11CCF61E0640286... |
| F43 | BRODY_F43_...PALIER_20260529 | 5F42AFEA3E31EF99... |
| F44 | BRODY_F44_...PALIER_20260529 | B3A1FF877520BADA... |
| F45 | BRODY_F45_...PALIER_20260529 | 99DD2A966C379766... |
| F46 | BRODY_F46_...PALIER_20260529 | C2DCB18BBFB485C8... |
| F47 | BRODY_F47_...PALIER_20260529 | C06BF8471417B4C8... |
| F48 | BRODY_F48_...PALIER_20260529 | 2C4E8FA9E87DA36B... |

---

*Brody GPT V1 · Proof Index F42→F48 · READONLY · KX108_ONLY · 2026-05-29*
