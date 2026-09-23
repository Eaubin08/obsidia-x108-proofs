# F49 — Public Release Package Demo Export Pack

**Artifact:** `OBSIDIA_F49_PUBLIC_RELEASE_PACKAGE_DEMO_EXPORT_PACK_20260529_190000`  
**Palier:** F49  
**Parent:** F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK  
**Status:** PASS  
**Date:** 2026-05-29  

---

## Purpose

F49 assembles the public release documentation package for Brody GPT V1. It does not patch the runtime, does not change any logic, and does not add routes. It creates presentation-ready, honest documentation for external audiences.

**F49 is DOCS ONLY — no runtime changes, no patches, no commits until user validation.**

---

## Package Contents

| Document | Purpose |
|----------|---------|
| `docs/release/BRODY_GPT_V1_PUBLIC_RELEASE_PACKAGE.md` | Top-level overview for external audiences |
| `docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md` | Step-by-step terminal and API demo guide |
| `docs/release/BRODY_GPT_V1_PROOF_INDEX_F42_F48.md` | Indexed proof chain with SHA256 references |
| `docs/release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md` | Explicit honest limitations — no overclaims |

---

## Release Documentation SHA256

| Document | SHA256 (first 16) |
|----------|-------------------|
| PUBLIC_RELEASE_PACKAGE.md | `1588678220B18FE7...` |
| DEMO_COMMANDS.md | `8A4FDFFB2903290D...` |
| PROOF_INDEX_F42_F48.md | `5AE80256DA4522CB...` |
| LIMITATIONS_AND_BOUNDARIES.md | `E6CD9E807FB7CE28...` |

---

## Proof Chain Referenced

| Palier | Role | Manifest SHA256 (first 16) |
|--------|------|---------------------------|
| F42 | Final release seal | `D11CCF61E0640286...` |
| F43 | Live server audit | `5F42AFEA3E31EF99...` |
| F44 | Integrity audit (7 findings) | `B3A1FF877520BADA...` |
| F45 | Terminal observation battery | `99DD2A966C379766...` |
| F46 | Hardening plan | `C2DCB18BBFB485C8...` |
| F47 | Hardening patch (0 confirmed remaining) | `C06BF8471417B4C8...` |
| F48 | Release readiness check | `2C4E8FA9E87DA36B...` |

---

## V1 Metrics (current)

| Metric | Value |
|--------|-------|
| Unit tests | **103/103 PASS** |
| Smoke checks (cumulative) | **474** |
| Live-server proofs | **3** |
| API routes | **7 READY_READONLY** |
| Git tags (F24→F48) | **17** |
| Forbidden tokens in output | **0** |
| Sovereignty flags enforced | **13/13** |
| Confirmed findings remaining | **0** |

---

## Explicit Non-Claims

This package explicitly does NOT claim:

- Production-ready
- Certified
- Lean-proven
- Cloud-ready
- Brody decides
- KX108 kernel instantiated

---

## Boundary Contract (preserved)

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |
| `brody_decision` | `false` |

---

## F49 Constraints Verified

| Constraint | Status |
|------------|--------|
| No runtime patches | CONFIRMED |
| No code changes | CONFIRMED |
| No new routes | CONFIRMED |
| No Neo4j writes | CONFIRMED |
| No kernel mutation | CONFIRMED |
| No X108 mutation | CONFIRMED |
| No overclaims | CONFIRMED |
| KX108_ONLY preserved | CONFIRMED |

---

## JSON Artifact

`docs/runtime/OBSIDIA_F49_PUBLIC_RELEASE_PACKAGE_DEMO_EXPORT_PACK_20260529_190000.json`  
SHA256: `38C99478926AED9FDAF2E525E5B53C569B234B9217D1092A5784791A06D354A0`

---

## Next Step

Commit F49 after user validation:

```
git add docs/release/ docs/runtime/OBSIDIA_F49_* .runtime_freezes/F49_*/
git commit -m "docs: add F49 public release package demo export pack"
git tag "BRODY_F49_PUBLIC_RELEASE_PACKAGE_DEMO_EXPORT_PACK_PALIER_20260529"
```

---

*F49 · DOCS ONLY · READONLY · KX108_ONLY · 2026-05-29*
