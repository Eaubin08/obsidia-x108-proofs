# Post-CG100 Runtime Integration — Truth Report

Branch: `source/cg9-cognitive-provider-binder-20260901`
Scope: closing the AgentResult → ContextPacket → X108 runtime gap identified by CG93/CG97.
CG100 closes the numbered sequence. No CG101+ layer was created.

This document states what is proven, what is integrated but dry-run, and what is
still not integrated. No flag is raised without evidence.

---

## A. CLOSED / PROVEN

| Item | Evidence |
|---|---|
| Canonical `AgentResult → ContextPacket` binder | `periphery/context/agent_result_context_adapter.py`; 9 tests in `tests/periphery/test_agent_result_context_adapter.py` |
| Canonical runtime flow agent → context → X108 | `periphery/context/agent_x108_context_flow.py`; 21 tests in `tests/periphery/test_agent_x108_context_flow.py` |
| Real API caller wired | `POST /api/periphery/governance/agent-x108-context` in `apps/obsidia_api/routes/periphery_ops.py`; 11 tests in `tests/api/test_agent_x108_context_route.py` |
| Provenance preserved end to end | `agent_id`, `agent_layer`, `action_id`, `evidence_refs`, `recommended_gate`, agent notes asserted against the real `AgentResult` |
| Canonical validator + X108 context boundary pass | `validate_context_packet()` and `check_x108_context_boundary()` return `valid/passed` with zero violations on the real projection |
| Receipt lifecycle closed | `CanonicalRuntimeReceiptFlow.run()` now calls `.complete()` on a real sealed result, `.fail()` otherwise; 8 tests in `tests/cli/providers/test_canonical_runtime_receipt_lifecycle_v1.py` |
| Non-sovereignty invariants locked | `emits_act`, `emits_decision`, `memory_write`, `kernel_mutation`, `runtime_allowed_now` all False; `decision_authority == "KX108_ONLY"` |
| Fail closed | Pre-gate failure reports `BLOCK` / `X108_FAIL_CLOSED` and never reaches admission; a mutated ContextPacket raises before admission |
| CG93/CG97 assertions reconciled with fact | `scripts/kernel/kx108_runtime_link_facts_v1.py` detects the link from the filesystem; CG97 rejects a surface lying in either direction |

---

## B. INTEGRATED BUT DRY-RUN

The whole agent → X108 path is wired to `runtime_wiring.x108_admission_stub.evaluate_dry_run()`.

- Observable decisions are bounded to `BLOCK` / `HOLD` / `ALLOW_CONTEXT_ONLY`.
- `ACT` is structurally unreachable: it is absent from `VALID_DRY_RUN_DECISIONS`
  and from `ADMISSIBLE_DECISIONS`, and both are asserted.
- `DecisionTicketDryRun.dry_run` is always True; hashes, Merkle root and replay
  remain honest `NOT_COMPUTED` / `NOT_RUN` placeholders.
- World action stays `dry_run_only=True`, `world_action_allowed=False`.

This is a real binding to a dry-run gate, not a real gate.

---

## C. NOT INTEGRATED

- No real X108-gated execution path is activated
  (`REAL_X108_GATED_EXECUTION_PATH_NOT_ACTIVATED`).
- No real proof chain: hashing, Merkle sealing, RFC3161 anchoring and replay
  are not computed on this path.
- The 52 agent configurations are declarative only and are never executed
  (HTTP 422 `AGENTS52_CONFIG_NOT_EXECUTABLE`).

---

## D. HISTORICAL / ARCHIVE

Untouched, and deliberately excluded from the canonical pytest perimeter by
`pytest.ini` (`norecursedirs` / `addopts`), never deleted or repaired:

- `proofs/V18_3_1/`, `_FREEZE/`, `freeze/`, `_source_packs/`, `.runtime_freezes/`
- LEGACY test modules importing a removed `agents.*` layout:
  `tests/sigma_stress_test.py`, `tests/test_agents_functional.py`,
  `tests/test_consensus_inprocess.py`, `tests/test_sigma_v18_9.py`
- `periphery/modules_agents/agent_registry.py`: a legacy mirror of
  `periphery/agent_registry.py`. Verified non-divergent — same 14 agent ids
  bound to the same callables in `periphery.agents.*` — and not imported by
  the runtime. Left in place.

---

## E. BLOCKING BEFORE RUNTIME E2E

1. No real execution: every decision is a dry-run stub verdict.
2. No proof chain computed on the agent → X108 path.
3. No X108 runtime consent mechanism; `runtime_allowed_now` is structurally False.

## F. BLOCKING BEFORE GLOBAL RUNTIME

4. Only 14 operational agents are wired; the remaining declared configurations
   are documentary and require human validation.
5. Mission / provider execution surfaces remain sandboxed with all authority
   flags False.

## G. BLOCKING BEFORE PRODUCTION

6. Everything in E and F.
7. Pre-existing unrelated debt in `tests/api/*brody*` (10 failures, present
   before this work and untouched by it).
8. No release, deployment or freeze authorization exists, by design.

---

## Flag state — none raised

| Flag | Value | Why |
|---|---|---|
| `canonical_agent_context_adapter_present` | **true** | Detected as a repository fact; binder + flow both exist and are tested |
| `runtime_end_to_end_validated` | **false** | The path ends in a dry-run stub; no real execution occurs |
| `runtime_globally_validated` | **false** | Only one runtime link is closed |
| `runtime_allowed_now` | **false** | Structurally locked in `ContextPacket.validate_invariants()` |
| `production_ready` | **false** | See E, F, G |
| `release_ready` | **false** | See E, F, G |
| `deployment_ready` | **false** | See E, F, G |
| `final_freeze` | **false** | See E, F, G |
| `activation_authorized` | **false** | `runtime_activation_authorized` is False in every release/freeze proof |

An adapter existing is not a runtime being validated. The first is a fact; the
second would require real gated execution, which does not exist here.

---

## Reproduction

```bash
# canonical perimeter
python -m pytest tests/cli/kernel tests/cli/providers tests/non_sovereignty \
  tests/periphery tests/api/test_agent_x108_context_route.py \
  tests/integration/test_full_stack_static_bank.py \
  tests/integration/test_full_stack_static_gps.py \
  tests/integration/test_full_stack_static_trading.py \
  tests/integration/test_os3_gencoin_chain.py -q

# the new runtime path alone
python -m pytest tests/periphery/test_agent_x108_context_flow.py \
  tests/api/test_agent_x108_context_route.py \
  tests/cli/providers/test_canonical_runtime_receipt_lifecycle_v1.py -q

# manifest
python scripts/generate_recursive_manifest.py
python scripts/verify_recursive_manifest.py

# after any world-action test run
git restore -- audit/world_action_bus.jsonl
```
