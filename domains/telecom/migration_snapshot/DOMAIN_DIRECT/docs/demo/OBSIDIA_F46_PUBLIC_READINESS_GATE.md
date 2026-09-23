# Brody GPT V1 — Public Readiness Gate

**Date:** 2026-05-29  
**Based on:** F44 Integrity Audit + F45 Terminal Test Battery + F46 Hardening Plan  
**Mode:** AUDIT_ONLY · READONLY

---

## GATE STATUS

```
PUBLIC_RELEASE_GATE=BLOCKED_UNTIL_F47_HARDENING
```

---

## What is blocked and why

| Gate | Status | Reason |
|------|--------|--------|
| Internal demo (controlled environment) | ✅ OPEN | V1 sealed, 103/103, 474/474, boundary confirmed |
| Investor / jury presentation | ✅ OPEN | Proof chain honest, F41 narrative accurate |
| Public API exposure | ❌ BLOCKED | F2 + F4 confirmed — see below |
| Production deployment | ❌ BLOCKED | F2 + F4 + no production hardening in V1 scope |
| Certified formal proof | ❌ BLOCKED | V1 = RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN by design |

---

## Blocking findings

### F2 — Forbidden tokens survive into controlled_response.text

Terminal test (F45) confirmed: injecting `user_input="ALLOW"` or `"DECIDE"` causes the word to appear verbatim in `controlled_response.text` returned to the caller. `safe_backend_response()` does not sanitize nested fields.

**Impact:** Any user-facing API consumer could read a response containing forbidden sovereign-decision tokens embedded in Brody's explanation text. This contradicts the documented guarantee that Brody's responses contain no forbidden token emissions.

**Blocked until:** F47.2 patch confirmed + F45 battery shows 0 confirmed injection cases.

---

### F4 — safe_backend_response() does not enforce sovereignty

Terminal test (F45) confirmed: `base.update(data)` allows data to override all 8 sovereignty flags in `safe_backend_response()`. A module returning `{"allowed_to_decide": True}` would propagate that value.

**Current V1 protection:** Pydantic HTTP schema blocks external injection. All V1 modules return correct BOUNDARY. Gap is latent, not currently exploitable via public routes.

**Impact for public release:** Public-facing API must have a true enforcement layer, not a convenience merger. `safe_backend_response()` must be hardened before any external consumer can rely on it as a sovereignty guarantee.

**Blocked until:** F47.1 patch — `data.update(base)` merge order confirmed + 103/103 still pass.

---

## What is confirmed clean (not blocking)

| Item | Status |
|------|--------|
| KX108_ONLY decision authority in all V1 routes | ✅ CONFIRMED |
| allowed_to_decide=False in all V1 modules | ✅ CONFIRMED |
| No actual Neo4j writes in any V1 route | ✅ CONFIRMED |
| No kernel mutations in any V1 route | ✅ CONFIRMED |
| surfaces_ready dynamically computed (not hardcoded) | ✅ CONFIRMED |
| all_mutations_false dynamically computed (not hardcoded) | ✅ CONFIRMED |
| KERNEL_TRACE tokens internal only (not in API responses) | ✅ CONFIRMED |
| Word-boundary regex correct (8/8 trap cases) | ✅ CONFIRMED |
| proof_status=RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN everywhere | ✅ CONFIRMED |
| V1 scope honest (no claimed Lean proof, no KX108 instantiation) | ✅ CONFIRMED |
| Hardcoded proof_links point to real existing files | ✅ CONFIRMED |

---

## How to lift the gate

Complete F47 hardening sequence in order:

```
F47.1 → Fix safe_backend_response() merge order (data.update(base))
F47.2 → Sanitize controlled_response.text + f36 guard
F47.3 → Verify scan scope complete
F47.4 → Annotate legacy _BOUNDARY
F47.5 → Correct documentation claims
F47.6 → 103/103 + 474/474 + F45 battery → 0 CONFIRMED findings
F47.7 → Commit + tag BRODY_F47_CANONICAL_HARDENING_PATCH
```

When F47.6 shows 0 CONFIRMED findings from F45 battery:

```
PUBLIC_RELEASE_GATE=OPEN
```

---

## What the gate does NOT block

- **V1 seal integrity** — `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME_FINAL_20260529` remains valid
- **Internal use** — Controlled demo, investor presentations, audit review
- **Proof chain** — F24→F45 palier chain remains intact
- **Baseline tests** — 103/103 PASS unchanged

The gate is about **public API exposure** and **production deployment**, not about V1 architectural validity.

---

*F46 Public Readiness Gate · AUDIT_ONLY · READONLY · KX108_ONLY · 2026-05-29*
