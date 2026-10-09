# CSSA — Passe 2 : convergence administrative native (lot A)

Date: 2026-10-09. Workspace: `feat/cssa-v01-active` only. Historical repository is read-only; no changes to Universal/kernel/main.

## Prior art checked

Historical F3H-D already implements exact four native mutations (CRM CASE, TASK, CRM interaction, follow-up), preflight for each against KX108 and shadow apply before commit. Code: `organizations/cssa/native_ops/cssa_native_ops_bridge_v0.py` in `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-` at branch `feat/f3h-h-cssa-real-readonly-pilot-preflight-v0`. Architecture: `docs/architecture/F3H_D_CSSA_NATIVE_OPS_BRIDGE_V0.md`, with historical 181 PASS run 37609707350. This is historical evidence, not freshly replayed.

Universal native primitive already exists: `periphery/native_ops/intake_bundle_v0.py` and work-action projector in `obsidia-x108-proofs`. There is NO justification to duplicate canonical CRM/TASK mutation logic.

## Implemented this pass

`periphery/cssa_administrative_batch_pass2_v0.py` creates a single read-only administrative batch from genuine historical dataclass assessments. Each case follows `F3G assessor -> CSSA semantic adapter -> bound canonical native intake plan OR HOLD/BLOCK`; explicit binding is required for each case. No binding, no presumed date, owner or evidence. Colliding historical identifiers are rejected. Results aggregate disposition, plan and reasons without native mutations or external effects.

Tests: `tests/test_cssa_administrative_batch_pass2_v0.py` uses real original F3G G/H/I catalogs to test mixed outcomes across 31 fixtures: contract 5, compliance 5, institutions 10, root-cause 11. All original catalogs are SIMULATED_NOT_OBSERVED. Three tests added, conditional on `CSSA_HISTORICAL_REPO`; if not configured, they SKIP.

## Important limitation and next gates

This is not yet a genuine operational native commit from an observed CSSA document: historical assessments are synthetic, and binding refs passed to the batch are fixture strings, not authenticated permissions. Hence even a valid plan never creates a canonical CRM object, KX108 ALLOW, external action or genuine receipt. Avoid misleading `PASS2_CLOSED` until all administration families (F3F, licence, staffing, delegation) and end-to-end provenance are included and regression accepts them.

The next internal build in Pass 2 is an explicit provenance and authorization intake gate, reusing existing F3H-D canonical native mutation code in isolated sandbox. It must distinguish a simulated operator test from real CSSA authority and ensure any missing source/auth leaves HOLD/BLOCK. Current Universal E2E with CSSA deadlines only does not prove all F3G families.

Previous validated baseline: 185 PASS, 1 SKIP. This batch adds three new optional tests; expected with historical repo configured: 188 PASS, 1 SKIP, subject to local pytest; without config expect 185 PASS, 4 SKIP. This is not an observed test result.

Boundaries: `KX108_ONLY`, no merge/push `main`, no real CSSA account connection, mail send, calendar, provider call, authority inference or external effect.