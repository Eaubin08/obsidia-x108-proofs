# CSSA convergence — Monde V5 vs X108 branches (audit read-only, 2026-10-08)

## Scope and rule
Repositories: Eaubin08/monde-obsidia and Eaubin08/obsidia-x108-proofs. Compared source files on named refs only. No runtime test or merge in this audit. These are evidence levels: VERIFIED_SOURCE, CANDIDATE, UNTESTED.

## Cross-repository matrix

| Concern | Monde observed | X108 feat/cssa-v01-active | Other X108 reference | Assessment |
| --- | --- | --- | --- | --- |
| Runtime discovery | Monde README calls X108 at ../sources/obsidia-x108-proofs, Kernel :3001, API/Brody/Native Memory :8000; scripts/read-local-sources.mjs reads actual local X108 HEAD/branch | Source/API implementation in X108, not Monde | main not authoritative by name | VERIFIED_SOURCE: Monde is observer/raccord; not evidence of X108 regression PASS |
| Decision boundary | README: KX108_ONLY, canonicalTruth=false | Brody exposes memory_write false / graphiti_write false in response paths | repair/brody-native-memory-cleanup-20261008 | VERIFIED_SOURCE for declarations; no live authorization claim |
| Memory backend | README names Native Memory | brody.py imports native memory response adapter but also conditionally imports graphiti_memory_readonly_activation and uses _graphiti_memory_state for readiness fields | repair/brody-native-memory-cleanup-20261008 removes the conditional Graphiti activation and bases memory readiness on native_memory_ready | CANDIDATE: manually inspect minimal diff and test; no blind cherry-pick |
| Graphiti route tests | No Graphiti runtime promise in examined Monde README | tests/api/test_brody_routes_registered.py still expects five /api/graphiti routes | same blob on main and repair branch | VERIFIED_SOURCE: legacy route expectations unchanged across compared refs |
| Graphiti write legacy contract | No Graphiti active claim | tests/api/test_f22b_readonly_intent_guard.py expects payload['graphiti_write']==False; existing readonly intent markers include denied Graphiti writes | same blob on main/repair | DO NOT remove negative safety assertions solely because backend deprecated; classify response shape separately |
| Native CRM/TASKS | Listed as native enterprise projections in Monde role, not the implementation | tests/integration/test_native_tasks_crm_v0.py present; common_v0.py encodes unsafe canonical IDs into filesystem-safe hash-based components | Test absent main; on feat/native-tasks-crm-v0 but common_v0.py is older and lacks filesystem_component_v0 | CANDIDATE: WinError 123 might be another path or pre-fix test environment; locate traceback exact line |
| SHA catalog | Monde doesn't certify X108 document hashes | periphery/agents/operational_source_catalog.py hashes raw bytes; operational_source_catalog.json is identical main and CSSA | .gitattributes merely sets whitespace=cr-at-eol, NOT EOL normalization | VERIFIED_SOURCE: core.autocrlf=true can change working tree bytes; compare git show HEAD:path vs working-tree bytes, do not refresh catalog blindly |
| Historical batch | Monde provides no original selector fixture | fixed ID 84a929c6f48a90c5 missing in scanned locations; separate synthetic suite PASS 2/2 on user's Windows | cannot replace historical receipt | HOLD |
| Formal proof | No Lean proof supplied by Monde | CI workflow adds Lean installation; local Windows lacked lake | Lean toolchain file v4.28.0 | LOCAL_PREREQUISITE_MISSING; proof not refuted |
| Broader regression | Monde cannot certify X108 | user's pinned SHA 681e668: 12,882 passed /117 failed /40 skipped /207 deselected | no head-to-head Linux run | HOLD; failures grouped by cause not test count |

## Next non-mutating checks
1. Reproduce one catalog mismatch with tracked Git blob raw bytes vs working copy raw bytes and check git ls-files --eol, retaining SHA evidence.
2. For CRM/TASKS WinError 123, capture full traceback to exact failing path. The current CSSA common_v0.py already hashes unsafe IDs; don't reapply an obsolete fix.
3. Compare brody.py exact repair diff around native readiness and Graphiti and check dependent APIs before porting.
4. Audit cross-platform worktree tests; distinguish CRLF assertion failures from Git identity/isolation semantics.
5. Run selected affected tests on Python 3.12/Linux CI and 3.14/Windows before claiming closure.
6. Keep historical missing evidence HOLD and synthetic proof separate.

No runtime/production mutation, no Graphiti resurrection, no kernel or main modification. 
