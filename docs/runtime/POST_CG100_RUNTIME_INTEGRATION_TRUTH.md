# Post-CG100 Runtime Integration — Truth Report

Branch: `feat/r5-governed-runtime-e2e-20260903` (base `f62ef0ac`)
Scope: R4 closed the agent → ContextPacket → X108 dry-run link. R5 closes the
governed **internal** runtime cycle: a real sovereign verdict gating a real
canonical provider execution.
CG100 closes the numbered sequence. No CG101+ layer was created.

No flag is raised without evidence. An internal governed execution is **not**
external world actuation, and the two claims are kept apart everywhere below.

---

## A. CLOSED / PROVEN

| Item | Evidence |
|---|---|
| Canonical `AgentResult → ContextPacket` binder | `periphery/context/agent_result_context_adapter.py`; 9 tests |
| Agent → context → X108 dry-run flow | `periphery/context/agent_x108_context_flow.py`; 21 tests |
| API caller | `POST /api/periphery/governance/agent-x108-context`; 11 tests |
| Receipt lifecycle | `.complete()` only on a real sealed result, `.fail()` otherwise; 8 tests |
| **Governed internal runtime cycle** | `scripts/obsidia_governed_runtime_cycle_v1.py`; 27 tests in `tests/integration/test_canonical_governed_runtime_e2e_v1.py` |
| **Real sovereign verdict** | `sigma.guard.GuardX108.decide()` via `periphery.sigma_bridge`; the dry-run stub is not consulted |
| **Cryptographic evidence verification** | `build_os3_ticket` + `run_replay` → `replay_status == PASS`, 64-hex input/output/trace/merkle |
| **Fail closed** | BLOCK, HOLD, tampered ticket, failed replay, no bound surface → provider invocation count `== 0` |
| **Real provider invocation** | verified ALLOW → count `== 1`, through the real `CanonicalExecutionFlow → Orchestrator → MissionExecutionRouter` |
| **Sealed envelope + terminal receipt** | `envelope.status == SEALED`, `receipt.status == COMPLETED`, `result_ref == runtime_id` |
| **Readonly feedback** | `build_memory_candidate` → `memory_write_allowed == False` on every path |
| Runtime link facts | `scripts/kernel/kx108_runtime_link_facts_v1.py` detects from disk; 5 tests |

---

## B. INTERNAL REAL RUNTIME

The chain actually traversed, with no core mocked:

```
run_registered_agent            → real AgentResult
agent_result_to_context_packet  → real ContextPacket (R4 binder, unchanged)
validate_context_packet / check_x108_context_boundary
sigma_bridge.run_bank_with_periphery → GuardX108.decide() → x108_gate
build_os3_ticket + run_replay   → PASS
[GATE] verified ALLOW only
CanonicalRuntimeReceiptFlow → CanonicalExecutionFlow → Orchestrator
    → MissionExecutionRouter → bounded sandbox handler
    → CanonicalExecutionEnvelope.seal() → ProviderRuntimeReceipt COMPLETED
build_memory_candidate          → readonly candidate
```

`HOLD` and `BLOCK` in the tests are genuine kernel verdicts from genuinely
degraded domain states (fraud pattern, over-commitment), never forced values.

The coordinator carries no authority: it cannot decide, cannot synthesize an
ALLOW, cannot produce consent, cannot write memory, cannot mutate the kernel,
and never changes `runtime_allowed_now` on the ContextPacket.

---

## C. STILL DRY-RUN

- `runtime_wiring/x108_admission_stub.py` — unchanged, still a dry-run stub.
  `ALLOW_CONTEXT_ONLY` is **never** an execution authorization and is not
  consulted by the governed cycle.
- `SovereignTicket` / `WorldActionBus` — `dry_run_only=True`,
  `world_action_allowed=False`.
- `ContextPacket.runtime_allowed_now` — structurally False.

---

## D. NOT INTEGRATED

**Canonical KX108 decision-record persistence for an agent cycle.**
`run_and_persist_kx108_pre_execution_decision` cannot be used here: its
binding contract (`_PRE_BINDING_CONTEXT_FIELDS`) requires remediation-rail
artefacts — `batch_execution_id`, `child_execution_id`, an
`execution_authority_hash` over file content, an `approval_id` for a
HumanApproval bound to that hash, a `pre_execution_context_id` for a Git
isolation capture, a `test_contract_hash`. An agent → provider cycle has none
of them, and fabricating them would divert a human authorization granted for
something else. Named as `KX108_DECISION_RECORD_PERSISTENCE_FOR_AGENT_CYCLE`
and left unresolved rather than bypassed.

Consequently `verify_kx108_decision_record()` is not applied to this cycle.
The verification performed is the OS3 rail's (ticket + replay), which is real
but is not the decision-record verification.

Also not integrated: external world actuation; a real proof chain with
Merkle sealing and RFC3161 anchoring on this path; the 52 declarative agent
configurations, which stay non-executable.

---

## E. BLOCKING BEFORE GLOBAL RUNTIME

1. No canonical decision-record persistence or verification for agent cycles (D).
2. No `PreExecutionContext` bound to an agent cycle.
3. Only 14 operational agents are wired; only 4 sigma domains have a canonical
   bridge (bank, trading, ecom, gps) — any other domain fails closed.
4. Mission and provider surfaces outside this cycle keep all authority flags False.

## F. BLOCKING BEFORE PRODUCTION

5. Everything in E.
6. External world actuation is not activated and is out of scope for this pass.
7. No release, deployment or freeze authorization exists, by design.
8. Pre-existing unrelated debt in `tests/api/*brody*` (10 failures, predating
   this work, untouched).

---

## Flag state — what R5 did and did not raise

| Flag | Value | Why |
|---|---|---|
| `canonical_agent_context_adapter_present` | **true** | Detected on disk; binder + flow exist and are tested |
| `governed_runtime_cycle_present` | **true** | Detected on disk; 27 E2E tests |
| `runtime_end_to_end_validated` | **false** | 3 links of the R5-L chain are missing: `REAL_PRE_EXECUTION_CONTEXT`, `REAL_DECISION_RECORD_PERSISTED`, `REAL_DECISION_RECORD_VERIFIED` |
| `runtime_globally_validated` | **false** | One internal cycle, four domains, no global coverage |
| `world_action_runtime_activated` | **false** | Untouched by this pass, by mandate |
| `runtime_allowed_now` | **false** | Structurally locked in `ContextPacket.validate_invariants()` |
| `production_ready` | **false** | See E, F |
| `release_ready` | **false** | See E, F |
| `deployment_ready` | **false** | See E, F |
| `final_freeze` | **false** | See E, F |
| `activation_authorized` | **false** | `runtime_activation_authorized` False in every release/freeze proof |

Ten of the thirteen R5-L links are proven. Three are not, so the E2E flag stays
down. A real internal governed execution is a fact; a validated runtime is not.

---

## Reproduction

```bash
# R5 governed internal runtime cycle
python -m pytest tests/integration/test_canonical_governed_runtime_e2e_v1.py -q

# binder / runtime / API
python -m pytest tests/periphery/test_agent_result_context_adapter.py \
  tests/periphery/test_agent_x108_context_flow.py \
  tests/api/test_agent_x108_context_route.py -q

# KX108 decision store and pre-execution gate
python -m pytest tests/cli/test_kx108_pre_execution_gate_v0.py \
  tests/test_kx108_decision_persistence_v0.py \
  tests/cli/test_kx108_post_pre_binding_v0.py -q

# governed execution / providers / non-sovereignty / bounded full stack
python -m pytest tests/cli/test_governed_apply_preflight_v0.py \
  tests/cli/test_governed_content_apply_c2_v0.py \
  tests/cli/test_governed_rollback_v0.py -q
python -m pytest tests/cli/providers tests/non_sovereignty -q
python -m pytest tests/integration/test_full_stack_static_bank.py \
  tests/integration/test_full_stack_static_gps.py \
  tests/integration/test_full_stack_static_trading.py \
  tests/integration/test_os3_gencoin_chain.py -q

# after any world-action test run
git restore -- audit/world_action_bus.jsonl
```
