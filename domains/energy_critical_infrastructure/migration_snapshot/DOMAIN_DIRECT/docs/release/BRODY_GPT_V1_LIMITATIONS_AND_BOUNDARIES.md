# Brody GPT V1 — Limitations and Boundaries

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Version:** V1.0.0-RC-CLOSED  
**Date:** 2026-05-29  

This document states honestly and explicitly what Brody GPT V1 is, is not, proves, and does not prove. It is not a marketing document.

---

## Decision Authority

**Brody does not decide. `KX108_ONLY` decides.**

This is not a design preference — it is enforced simultaneously at three independent layers. Any module, route, or response that returns `allowed_to_decide=true` or `emits_act=true` is blocked unconditionally before reaching the caller (F47.1).

---

## V1 Technical Limitations

| Limitation | Detail | Future work |
|------------|--------|-------------|
| Formal Lean proof | Not available. V1 uses runtime smoke tests (474 checks) and unit tests (103/103). No theorem prover, no TLA+, no Coq, no Isabelle. | F50+ |
| KX108 kernel instantiated | `KX108_ONLY` is the declared decision authority in every response, but the actual kernel is not instantiated or callable in V1. It is a declared boundary, not an integrated one. | F50+ |
| Adversarial hardening | No red-teaming, no fuzzing, no adversarial test cases, no penetration testing performed. The F47.2 sanitizer covers word-boundary forbidden token injection but is not adversarially verified. | F50+ |
| Load testing | No performance testing, no concurrency testing, no stress testing. V1 runs on a single-process uvicorn instance at 127.0.0.1. | F50+ |
| Full Graphiti binding | Neo4j/Graphiti memory integration is outside V1 scope. `graphiti_write=false` and `neo4j_write=false` are enforced. | F50+ |
| Memory persistence | `memory_write=false` by design in V1. Brody does not store session state. | F50+ |
| Multi-instance deployment | V1 is single-instance, localhost only (127.0.0.1). No cloud, no containerization, no reverse proxy tested. | F50+ |
| Production hardening | V1 is not production-hardened. No TLS, no authentication, no rate limiting, no WAF. | F50+ |
| Legacy route boundary | Pre-F32 pipeline/governance routes use `_BOUNDARY` (4 flags) instead of the full 15-flag BOUNDARY. These routes are not Brody V1 routes (F33/F36/F38 use the full BOUNDARY), but exist in the same `periphery_ops.py`. Annotated as LEGACY in F47.4. | F50+ |

---

## Proof Scope

What the V1 proof chain covers:

| Claim | Evidence |
|-------|---------|
| `decision_authority=KX108_ONLY` in every response | 13/13 sovereignty flags enforced (F47.1); verified across 103 unit tests and 474 smoke checks |
| `allowed_to_decide=false`, `emits_act=false`, `emits_verdict=false` | Enforced unconditionally by `_SOVEREIGNTY_PROTECTED` in `safe_backend_response()` |
| No forbidden decision tokens in user-facing output | Word-boundary regex verified by F47.2 sanitizer (42/42 checks); 0 violations across all smoke runs |
| 7 surfaces READY_READONLY in nominal configuration | Verified in unit tests; `surfaces_ready` is dynamically computed at runtime (F3 note: value reflects whichever surfaces the orchestrator successfully queries) |
| No Neo4j writes, no memory writes | Verified by `test_f29_1_neo4j_manual_write_surface_guard.py` and all F33/F36/F38 tests |
| Live server boundary holds | 3 live-server proofs (F34B/F36B/F38); SHA256-anchored |

What the V1 proof chain does NOT cover:

| Claim | Status |
|-------|--------|
| Formal mathematical proof of boundary enforcement | NOT PROVEN — runtime smoke only |
| Proof that adversarial inputs cannot bypass the sanitizer | NOT PROVEN — not red-teamed |
| Proof that `KX108_ONLY` kernel actually enforces decisions | NOT APPLICABLE — kernel not instantiated in V1 |
| Multi-instance / distributed correctness | NOT TESTED |
| Long-running memory / session state correctness | NOT APPLICABLE — no memory in V1 |

---

## Overclaim Prevention

The following claims are explicitly NOT made about Brody GPT V1:

- **Not production-ready** — V1 is a controlled runtime proof, not a deployable production system.
- **Not certified** — No external certification, no standards compliance verified.
- **Not Lean-proven** — All Lean-related files in the repo are Python specifications, not formal proofs. See `docs/MATH_CORE_POG_INTEGRATION_REPORT.md`: "These are **not Lean-proven** — they are Python specifications."
- **Not cloud-ready** — No cloud deployment artifacts, no containerization, no external network exposure.
- **Not adversarially hardened** — The sanitizer and sovereignty layers are functional but untested against adversarial inputs.
- **Brody does not decide** — Brody is advisory context only. Any appearance of decision language in Brody's output is a sanitizer failure (none observed in V1).

---

## Known Findings (Post-F47)

All CONFIRMED findings from F44 were resolved in F47. Post-F47 state:

| ID | Finding | Post-F47 Status |
|----|---------|----------------|
| F1 | `_BOUNDARY` 4-flag legacy routes | RESOLVED — isolated and annotated (F47.4) |
| F2 | `controlled_response.text` unsanitized | RESOLVED — dual-layer sanitization (F47.2) |
| F3 | `surfaces_ready=7` nominal qualifier | CLARIFIED — documented as dynamic runtime value |
| F4 | Sovereignty override via merge order | RESOLVED — `_SOVEREIGNTY_PROTECTED` always wins (F47.1) |
| F5 | Token scan scope imprecise in docs | RESOLVED — docs corrected (F47.5) |
| F6 | `KERNEL_TRACE` stderr contains tokens | CLARIFIED — documented as internal computation only |
| F7 | `proof_links` static snapshot | ANNOTATED — static snapshot noted in code comment |

**0 CONFIRMED findings remain as of F48.**

---

## Upgrade Path (F50+)

The following items are deferred to F50+ and explicitly out of V1 scope:

1. KX108 kernel full integration and decision handoff
2. Formal Lean proof of boundary enforcement at periphery layer
3. Adversarial hardening (red-teaming, fuzzing, prompt injection)
4. Multi-instance deployment and performance testing
5. Full Graphiti/Brody deep memory binding
6. Cloud deployment artifacts (container, TLS, auth, WAF)
7. Expand legacy `_BOUNDARY` to 15 flags or deprecate legacy routes

---

*Brody GPT V1 · Limitations and Boundaries · READONLY · KX108_ONLY · 2026-05-29*
