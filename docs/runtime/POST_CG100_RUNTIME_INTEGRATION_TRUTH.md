# Post-CG100 Runtime Integration — Truth Report

Branch: `feat/r5-governed-runtime-e2e-20260903`

Progression, each stage building on the previous one:

| Stage | What it closed |
|---|---|
| R4 | Agent bound to a canonical ContextPacket, wired to the X108 dry-run path |
| R5 | A real sovereign verdict gating a real bounded provider execution |
| R6 | Frozen pre-execution context, persisted and verified KX108 decision record, feedback re-entry inheriting nothing |
| R7 | Several real domains and several real internal providers coexisting on the one canonical cycle, isolated from each other |

CG100 closes the numbered sequence. No CG101+ layer was created.

Two claims are kept strictly apart everywhere in this document:

| Claim | Value |
|---|---|
| `INTERNAL_PROVIDER_EXECUTION` | **real** — governed, gated, verified, multi-domain |
| `EXTERNAL_WORLD_ACTUATION` | **false / dry-run** — untouched |

---

## A. CLOSED / PROVEN

| Item | Evidence |
|---|---|
| `AgentResult -> ContextPacket` binder | `periphery/context/agent_result_context_adapter.py`; 9 tests |
| Agent -> context -> X108 dry-run flow | `periphery/context/agent_x108_context_flow.py`; 21 tests |
| API caller | `POST /api/periphery/governance/agent-x108-context`; 11 tests |
| Receipt lifecycle | `.complete()` only on a real sealed result, `.fail()` otherwise; 8 tests |
| Governed runtime cycle (single owner) | `scripts/obsidia_governed_runtime_cycle_v1.py`; 28 tests |
| Agent pre-execution context | `scripts/obsidia_agent_pre_execution_context_v1.py`; immutable, append-only, self-verifying |
| Execution-plan digest (anti-TOCTOU) | Substituting context, provider, capability, mission, payload or domain breaks the binding |
| KX108 agent decision record | `decision_phase=AGENT_PRE_EXECUTION`; `kxagent-*`; persisted, then `verify_kx108_decision_record` passes; 31 tests |
| Feedback re-entry | `periphery/context/feedback_result_context_adapter.py`; 15 tests |
| Multi-domain coexistence | `tests/integration/test_canonical_governed_runtime_multidomain_v1.py`; 17 tests |
| Cross-domain isolation | `tests/integration/test_canonical_governed_runtime_cross_domain_isolation_v1.py`; 18 tests |
| Real internal provider surface | `tests/integration/test_canonical_governed_runtime_provider_surface_v1.py`; 9 tests |
| Runtime link facts | `scripts/kernel/kx108_runtime_link_facts_v1.py`; 10 tests |

---

## B. REAL INTERNAL GOVERNED RUNTIME

The chain actually traversed, with no core component mocked:

```
run_registered_agent                -> real AgentResult
agent_result_to_context_packet      -> real ContextPacket
validate_context_packet / check_x108_context_boundary
is_supported_domain                 -> real canonical bridge, or refusal
create_agent_pre_execution_context  -> frozen facts + execution_plan_digest
  store -> reload -> verify_agent_pre_execution_context_record
sigma_bridge.run_<domain>_with_periphery -> GuardX108.decide() -> x108_gate
persist_kx108_agent_pre_execution_decision
  store -> reload -> verify_kx108_decision_record          [ALL VERIFIED]
build_os3_ticket + run_replay       -> PASS
[GATE] verified record + ALLOW + context binding + plan binding
CanonicalRuntimeReceiptFlow -> CanonicalExecutionFlow -> Orchestrator
  -> MissionExecutionRouter -> bounded provider
  -> CanonicalExecutionEnvelope.seal() -> ProviderRuntimeReceipt COMPLETED
build_memory_candidate              -> readonly candidate
compute_gencoin                     -> post-proof observation only
feedback_result_to_context_packet   -> next ContextPacket
  -> fresh GuardX108 verdict, fresh record, fresh gate at t1
```

Properties proven by test, not asserted:

- The gate reads the verdict from the **verified record on disk**, never from
  the in-memory object.
- An unsupported domain is refused **before any verdict is requested**:
  `decision_rendered` stays False, no record exists, the provider is untouched.
- Tampering the gate, `decision_id`, `trace_id` or either binding hash breaks
  verification. A HOLD record cannot be rewritten into an ALLOW.
- A previous ALLOW is transported as `previous_x108_gate`, a historical fact.
- A real failed execution raises a real `BLOCK_CANDIDATE`; on a state already
  carrying one contradiction the kernel really flips ALLOW to BLOCK.
- Gencoin observes the rendered gate and can never change it; a HOLD or BLOCK
  yields no mint and no execution.

Scope: `INTERNAL_BOUNDED_PROVIDER_EXECUTION`.

---

## C. GLOBAL INTERNAL COVERAGE

**Domains carried by the one canonical cycle**, with the gates each can
actually reach through its real agents — observed, not engineered:

| Domain | Bridge | Reachable gates | Note |
|---|---|---|---|
| `bank` | `run_bank_with_periphery` | ALLOW / HOLD / BLOCK | the only domain whose agents emit contradictions |
| `gps_defense_aviation` | `run_gps_with_periphery` | ALLOW / HOLD | BLOCK unreachable: no GPS agent emits a contradiction |
| `trading` | `run_trading_with_periphery` | ALLOW / HOLD | BLOCK unreachable, same reason |
| `ecom` | `run_ecom_with_periphery` | HOLD only | `EcomState` carries only `session_id` while `EcomProofAgent` reads `x108_compliance_rate` and `order_value` — the contract cannot be satisfied, so the domain fails closed |

**Agents**: the 14 operational agents are domain-agnostic and carry the domain
of the action; `DATA_PURITY_AGENT` is the one exercised end to end per domain.

**Providers actually traversed**: local sandbox handlers (SANDBOX_ONLY), plus
the real `brody_runtime_flow_adapter_v1` and `obsidure_runtime_flow_adapter_v1`
(INTERNAL_SAFE_EXECUTABLE) — both pure, both refused on BLOCK, both declaring
no authority. The world-action surface stays EXTERNAL_CONSENT_REQUIRED and is
not activated.

**Coexistence proven in one scenario**: bank ALLOW executes, gps HOLD does not,
trading ALLOW executes, and a bank feedback cycle BLOCKs — four distinct
decisions, contexts, records and traces on one runtime, exactly two authorized
executions, no identity or provider leak.

---

## D. STILL DRY-RUN

- `runtime_wiring/x108_admission_stub.py` — unchanged. `ALLOW_CONTEXT_ONLY` is
  never an execution authorization and is not consulted by the governed cycle.
- `SovereignTicket` / `WorldActionBus` — `dry_run_only=True`,
  `world_action_allowed=False`.
- `ContextPacket.runtime_allowed_now` — structurally False, including on the
  feedback re-entry packet.

---

## E. NOT INTEGRATED

- **External world actuation.** No world action is executed. The internal rail
  says nothing about it and must not be generalized to it.
- **The remediation rail remains inapplicable to an agent cycle**, by design
  and untouched: it still requires `batch_execution_id`, `child_execution_id`,
  an `execution_authority_hash` over file content, an `approval_id` bound to
  it, a Git `pre_execution_context_id` and a `test_contract_hash`. None are
  fabricated, none were made optional.
- **Human consent for irreversible operations.** The agent rail proves KX108
  authority over bounded internal execution only.
- **ECOM as a decidable domain.** Its state contract cannot express what its
  own proof agent reads; it is carried but can only HOLD.
- No RFC3161 anchoring or Merkle sealing on the agent path beyond the OS3
  ticket and its replay.
- The 52 declarative agent configurations stay non-executable.

---

## F. BLOCKING EXTERNAL RUNTIME

1. External world actuation is not activated, and is out of scope by mandate.
2. No consent rail exists for external or irreversible execution.
3. `SovereignTicket` and the world-action bus remain dry-run by construction.
4. No provider in the EXTERNAL_CONSENT_REQUIRED class is wired to the cycle.

## G. BLOCKING PRODUCTION

5. Everything in F.
6. Only 4 canonical domains exist, one of which (ecom) cannot leave HOLD, and
   two of which cannot reach BLOCK from their own agents.
7. Mission and provider surfaces outside this cycle keep all authority flags
   False; no rail exists for an irreversible internal operation.
8. No release, deployment or freeze authorization exists, by design.
9. Pre-existing unrelated debt: `tests/api/*brody*` (10 failures) and
   `tests/integration/test_f23a4_8_connectors_alignment.py` (1 failure), both
   predating this work and untouched by it.

---

## H. FLAG STATE

| Flag | Value | Why |
|---|---|---|
| `canonical_agent_context_adapter_present` | **true** | Detected on disk; binder + flow exist and are tested |
| `governed_runtime_cycle_present` | **true** | Detected on disk |
| `agent_decision_record_rail_present` | **true** | Frozen context + feedback adapter + `AGENT_PRE_EXECUTION` phase in the canonical store |
| `multi_domain_runtime_present` | **true** | The four real bridges plus the multidomain, isolation and provider-surface suites |
| `runtime_internal_end_to_end_validated` | **true** | All 14 links of `INTERNAL_E2E_REQUIRED_LINKS` proven on one continuous chain |
| `runtime_internal_globally_validated` | **true** | All 12 links of `REQUIRED_GLOBAL_RUNTIME_LINKS` proven across domains and providers |
| `runtime_end_to_end_validated` | **false** | Historical flag, wider meaning than an internal runtime; its consumers (CG97) are unchanged |
| `runtime_globally_validated` | **false** | Historical flag, wider meaning than an internal runtime; not redefined |
| `world_action_runtime_activated` | **false** | Untouched by this pass, by mandate |
| `runtime_allowed_now` | **false** | Structurally locked in `ContextPacket.validate_invariants()` |
| `production_ready` | **false** | See F, G |
| `release_ready` | **false** | See F, G |
| `deployment_ready` | **false** | See F, G |
| `final_freeze` | **false** | See F, G |
| `activation_authorized` | **false** | `runtime_activation_authorized` False in every release/freeze proof |

A governed internal runtime carrying several domains is a fact. A globally
validated runtime is not, and an actuated world is not.

---

## Reproduction

```bash
# R7 - multi-domain, isolation, real provider surface
python -m pytest tests/integration/test_canonical_governed_runtime_multidomain_v1.py \
  tests/integration/test_canonical_governed_runtime_cross_domain_isolation_v1.py \
  tests/integration/test_canonical_governed_runtime_provider_surface_v1.py -q

# R6 - decision record rail and feedback re-entry
python -m pytest tests/integration/test_canonical_governed_runtime_decision_record_v1.py \
  tests/integration/test_canonical_governed_runtime_feedback_reentry_v1.py -q

# R5 - governed internal cycle
python -m pytest tests/integration/test_canonical_governed_runtime_e2e_v1.py -q

# runtime facts
python -m pytest tests/cli/kernel/test_kx108_runtime_link_facts_v1.py -q

# binder / runtime / API
python -m pytest tests/periphery tests/api/test_agent_x108_context_route.py -q

# KX108 decision store and remediation gate (unchanged), governed execution
python -m pytest tests/cli/test_kx108_pre_execution_gate_v0.py \
  tests/test_kx108_decision_persistence_v0.py \
  tests/cli/test_kx108_post_pre_binding_v0.py \
  tests/cli/test_governed_apply_preflight_v0.py \
  tests/cli/test_governed_content_apply_c2_v0.py \
  tests/cli/test_governed_rollback_v0.py -q

# providers / non-sovereignty / full integration
python -m pytest tests/cli/providers tests/non_sovereignty tests/integration -q

# after any world-action test run
git restore -- audit/world_action_bus.jsonl
```

---

## Correction to the R6 report

The R6 summary announced `Files touched: 8` while listing ten files. The
correct R6 count is **10**: four created (`obsidia_agent_pre_execution_context_v1.py`,
`feedback_result_context_adapter.py`, and the two R6 integration suites) and
six modified (`obsidia_kx108_decision_store.py`,
`obsidia_governed_runtime_cycle_v1.py`, `kx108_runtime_link_facts_v1.py`,
`test_kx108_runtime_link_facts_v1.py`,
`test_canonical_governed_runtime_e2e_v1.py`, and this report).
