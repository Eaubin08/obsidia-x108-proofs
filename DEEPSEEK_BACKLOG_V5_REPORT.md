# DeepSeek Backlog V5 Report — Obsidia X-108

**Date:** 2026-05-19
**Status:** V3/V4 complete — deferred items identified for V5

---

## Items Deferred to V5

### 1. Documentation Gaps (LOW priority, 12 items)

The following documentation directories are absent despite having corresponding source code:

| Doc Directory | Source Code Present | Tests Present | Priority |
|---------------|--------------------|---------------|----------|
| `docs/world_calls/` | `periphery/world_calls/` (12 modules) | 5 test files | MEDIUM |
| `docs/brody/` | `periphery/brody/` (5 modules) | 2 test files | MEDIUM |
| `docs/graphiti/` | `periphery/graphiti/` (3 modules) | 2 test files | MEDIUM |
| `docs/context/` | `periphery/context/` (5 modules) | tests via integration | LOW |
| `docs/interface/` | `periphery/interface/` (4 modules) | 1 test file | LOW |
| `docs/math/` | `periphery/math_core/` (6 modules) | 1 test file | LOW |
| `docs/education/` | `periphery/education/` | 1 test file | LOW |
| `docs/bias/` | `periphery/bias/` (2 modules) | 1 test file | LOW |
| `docs/language/` | `periphery/language/` | 1 test file | LOW |
| `docs/github/` | `periphery/github/` | 1 test file | LOW |
| `docs/mcp/` | `periphery/mcp/` | 1 test file | LOW |
| `docs/benchmarks/` | `periphery/benchmarks/` | 1 test file | LOW |

**Recommended action:** Create a README.md in each directory documenting the module's interface contract, invariant boundaries, and non-sovereignty guarantees.

### 2. Demo Repo Population (MEDIUM priority)

`Demo-obsidia-x108-proof/` has only 3 connector Python files. Missing:
- `.TEST_V3_V4_FULL_STACK_ALL.ps1`
- `.TEST_V4_CONTROLLED_RUNTIME_ALL.ps1`
- `.TEST_MEMORY_ALL.ps1`
- Full pipeline demo scripts
- Configuration files
- README

**Recommended action:** Populate the Demo repo with the test runner scripts and a README explaining the demo flow.

### 3. Additional Non-Sovereignty Test Coverage (LOW priority)

The following non-sovereignty assertions are implicitly covered by existing tests but could benefit from dedicated negative tests:

| Invariant | Current Coverage | Suggested V5 Test |
|-----------|-----------------|-------------------|
| BDF cannot emit ACT | Implicit via `test_bdf_router_no_act.py` | Dedicated `test_bdf_no_act.py` in non_sovereignty |
| HexaFlux cannot authorize | Implicit via `test_hexaflux_transition_no_authority.py` | Dedicated `test_hexaflux_no_authority.py` in non_sovereignty |
| Reverse OS no write | `test_reverse_os_projection_readonly.py` | Dedicated `test_reverse_os_no_write.py` in non_sovereignty |
| Number encoding no authority | `test_crypto_boundary_no_security_claim.py` | Dedicated `test_number_encoding_no_authority.py` |
| Physics no authority | `test_symbolic_physics_claim_gate.py` | Dedicated `test_physics_no_authority.py` |

### 4. Manifest Completeness (LOW priority)

`MANIFEST_SHA256.json` covers top-level and some subdirectory files. A V5 improvement would be a recursive SHA-256 manifest covering every file in the repo, with a root hash anchored in `merkle_seal.json`.

### 5. CI/CD Pipeline Definition (MEDIUM priority)

No CI configuration was included in the V3/V4 overlay. A V5 pipeline should:
- Run `python -m pytest tests/ -q` on every commit
- Verify `git diff -- sigma/ proofs/lean/ formal/tla/ merkle_seal.json` is empty
- Block any change that modifies a protected file
- Generate a fresh MANIFEST_SHA256.json

---

## Items NOT Deferred — Verified Complete

| Item | Status |
|------|--------|
| All 11 phases | COMPLETE |
| 397 tests | PASSED |
| Protected files | UNTOUCHED |
| Sovereignty invariants | ENFORCED |
| Overlay zip | CLEAN |
| Kernel contamination | ZERO |
| Brody no decision | VERIFIED |
| Graphiti no write | VERIFIED |
| Gencoin not token | VERIFIED |
| Wallet no connection | VERIFIED |
| WorldCall dry-run only | VERIFIED |
| Memory promotion not automatic | VERIFIED |

---

## Risk Assessment for V5

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Documentation drift | LOW | LOW | Docs are descriptive, not normative |
| Demo repo incomplete | MEDIUM | LOW | Blocked by missing scripts; V5 should create them |
| CI/CD missing | MEDIUM | MEDIUM | Manual verification suffices for now; CI is hygiene |
| Test coverage gaps | LOW | LOW | Non-sovereignty invariants are already enforced in positive tests |

---

## Recommended V5 Initiation Order

1. Populate Demo repo with test runner scripts (unblocks demo capability)
2. Create CI/CD pipeline (automation hygiene)
3. Fill documentation gaps (completeness)
4. Add dedicated non-sovereignty negative tests (defense-in-depth)
5. Recursive SHA-256 manifest (cryptographic completeness)

---

## Conclusion

**V3/V4 is complete and stable.** The 5 backlog items are all LOW/MEDIUM priority and do not block the freeze. No sovereignty-critical items are deferred.
