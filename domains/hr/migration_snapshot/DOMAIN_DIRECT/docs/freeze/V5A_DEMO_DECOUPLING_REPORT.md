# V5A Demo Decoupling Report

**Date:** 2026-05-19
**Phase:** 0 — Classification
**Status:** DEMO_DECOUPLED — all elements classified

---

## Classification

### MIGRATED_TO_X108_PROOFS (0 items)

No Demo files were directly migrated. The 3 connector scripts are being **rewritten** as internal flows in Phase 1, not copied verbatim — they contain broken imports.

### ALREADY_INTERNAL (all functional modules)

| Module | Location in x108-proofs |
|--------|------------------------|
| ActionCandidate | `periphery/common.py` |
| ControlPlane | `periphery/control_plane.py` |
| OS3ReplayManifest | `periphery/os3_replay_manifest.py` |
| OS3ProofTicket (osi) | `periphery/os3_ticket.py` |
| GovernedStateVector | `periphery/math_core/governed_state.py` |
| Lyapunov | `periphery/math_core/lyapunov.py` |
| ProofOfGovernance | `periphery/math_core/proof_of_governance.py` |
| SovereignTicket | `periphery/world_calls/sovereign_ticket.py` |
| WorldCallClassifier | `periphery/world_calls/world_call_classifier.py` |
| ActionRiskClassifier | `periphery/world_calls/action_risk_classifier.py` |
| ObsidiaGateway | `periphery/world_calls/obsidia_gateway.py` |
| WorldActionBus | `periphery/world_calls/world_action_bus.py` |
| WorldActionStub | `periphery/world_action_controlled_runtime_stub.py` |
| FeedbackMemoryBridge | `periphery/feedback_memory_bridge_brody_readonly.py` |

### ARCHIVE_ONLY (3 files)

| File | Reason |
|------|--------|
| `Demo-obsidia-x108-proof/connectors/action_lifecycle_full_stack_flow.py` | Broken imports; superseded by 397 tests |
| `Demo-obsidia-x108-proof/connectors/feedback_memory_candidate_flow.py` | Redundant; tested in test_feedback_memory_candidate.py |
| `Demo-obsidia-x108-proof/connectors/world_action_dry_run_flow.py` | Broken imports; tested in test_world_action_gateway.py + test_world_action_no_real_act_v4.py |

### OBSOLETE (3 PS1 scripts — to be rewritten)

| Script | Action |
|--------|--------|
| `TEST_ACTION_LIFECYCLE_FULL_STACK.ps1` | Rewrite to call `demos/local_flows/v3_v4_full_stack_flow.py` |
| `TEST_FEEDBACK_MEMORY_CANDIDATE.ps1` | Rewrite to call `demos/local_flows/memory_brody_graphiti_flow.py` |
| `TEST_WORLD_ACTION_DRY_RUN.ps1` | Rewrite to call `demos/local_flows/world_call_gateway_flow.py` |

### MISSING_IN_X108_PROOFS (to be created in Phase 1)

| Item | Destination |
|------|-------------|
| `demos/` package | `demos/__init__.py` |
| `demos/local_flows/` package | `demos/local_flows/__init__.py` |
| 8 internal flow scripts | `demos/local_flows/*.py` |
| 6 internal runner scripts | `scripts/run_*.ps1` |
| 3 integration tests | `tests/integration/test_internal_demo_flows_*.py` |

---

## Demo Repo Disposition

```
Demo-obsidia-x108-proof = ARCHIVE / NON-CANONICAL
```

- **Keep** as historical reference (3 files, 6.5 KB)
- **Delete** none — files are harmless as-is
- **Do not develop** further — no new files, no patches
- **Do not reference** from scripts, tests, imports, or CI
- **Flag** in `.gitignore` or `REPO_BOUNDARY.md` as non-canonical

---

## Verification

| Check | Result |
|-------|--------|
| Zero Python imports from Demo | PASS |
| All 397 tests pass without Demo | PASS |
| All periphery modules self-contained | PASS |
| Demo connectors have broken imports | CONFIRMED (obsolete) |
| No functional dependency on Demo | CONFIRMED |

---

## Conclusion

**DEMO_DECOUPLED_PASS** — No operational dependency on Demo-obsidia-x108-proof. All 3 Demo files are archive-only. Phase 1 will create fresh internal flows in `demos/local_flows/` using correct module paths.
