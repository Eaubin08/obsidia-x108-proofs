# CSSA × Universal — A0 Interface audit / LOT A readiness

Date: 2026-10-09. Audit **read-only** of Universal branch `feat/obsidia-universal-cross-domain-conformance-v0`; CSSA work branch `feat/cssa-v01-active`. No merge, no kernel/shared-code edit.

## Concrete source interfaces inspected

| Actual file on Universal branch | Public functions / contract found | CSSA mapping or gap |
|---|---|---|
| `periphery/native_ops/native_work_to_action_projection_v0.py` | `project_native_work_to_action_v0`, `verify_native_work_action_projection_v0`, `build_world_action_request_from_action_candidate_v0`; uses `ActionCandidate` | Consumes **persisted canonical** CRM CASE + TASK + FOLLOW-UP, including linked refs and date; current CSSA creates *unapplied proposals* only — **not plug-compatible** |
| `periphery/universal_enterprise_stack_adapter_v0.py` | `EnterpriseStackManifestV0`, `EnterpriseActionBindingV0`, `EnterpriseSourceBindingV0`; `build_enterprise_stack_manifest_v0`, `stable_business_intent_hash_v0`, `build_enterprise_action_binding_v0`, `build_world_action_request_from_enterprise_binding_v0`, `provider_swap_invariant_v0` | Existing provider-neutral binding and semantic intent identity. CSSA must **declare** its capabilities; it must not invent permissions |
| `periphery/native_sources/enterprise_office_full_loop_e2e_v0.py` | `run_enterprise_office_full_loop_e2e_v0` and deterministic calendar sandbox adapter | Existing sandbox E2E with real KX108 decision rail in test context; CSSA V0–V0.3 **does not** invoke it |
| `docs/runtime/NATIVE_WORK_TO_ACTION_PROJECTION_V0.md` | FOLLOW-UP exactly links to case_id, task_id and task.due_at; incident produces NO_ACTION; mail requires proven recipient/body | CSSA draft has fixture sender/body; **not sufficient** to claim a canonical MAIL action. Date absence => no calendar action |
| `docs/runtime/OBSIDIA_UNIVERSAL_CROSS_DOMAIN_CONFORMANCE_V0.md` | Previously 16 scenario matrix, domain provider-swap, sandbox tickets/receipts, 58 passed on referenced run | Provides reusable proof pattern; **not** automatic CSSA conformance |
| `docs/runtime/UNIVERSAL_ENTERPRISE_STACK_ADAPTER_V0.md` | Google/Microsoft/custom-like simulated provider swap; reported 127 tests pass | Provider labels are mock, not credentials or live access |
| `docs/runtime/ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0.md` | 12 observations → 3 committed CASE/TASK work bundles → 2 calendar actions → sovereign sandbox execution + receipts, 117 passed | Reuse as integrated reference, not as a false claim of CSSA execution |

## Exact incompatibilities before a CSSA bridge

1. **Repository drift:** Universal branch is separate and not known to be present in current CSSA checkout at the same versions. Direct imports are not safe to assume from the read-only audit.
2. **State:** CSSA currently holds native CRM/TASK mutation candidates **without apply**; Universal projector requires statefully bound CASE/TASK/FOLLOW-UP. Never replace this with invented records or fake receipts.
3. **Semantics:** seasonal conflicts, FFF/licences, roles, budgets and deadlines require a CSSA domain-state schema and explicit provenance.
4. **Approval:** fixture HOLD is not an exact HumanApproval, PRE or signed KX108 ALLOW. Integration test must use the existing rail, not mock an authorization.
5. **Source evidence:** 904-event F3F and 291-test F3G numbers are **historical references**, not re-run or traced to immutable source commits by this audit.
6. **Safety:** universal enterprise tests simulate sandbox execution; no live provider effects.

## Work package: LOT A (one integrated delivery, no micro-freezes)

### A0. Source reconciliation
- Locate original F3F/F3G proofs/receipts and the 11 role requirements with exact SHA, tests, branch and definition; mark missing files as **unverified**, not reconstructed.
- Pin Universal tree/commit and inspect the module signatures and test fixtures before bridge implementation.
- Verify all required modules are available in the CSSA branch; if not, **do not** copy global shared runtime or silently merge Universal. Explicitly record blocker.

### A1. CSSA domain-state contract
- Model season scheduling, matches and deadlines; delegates/role authority; resources; budget and stock; regulatory/club communications and provenance.
- All contradictions and unknown authority fail closed; source category and priority alone confer no permission.

### A2. Integrated campaign
- Reuse historical F3F season stress fixture **if recovered**. Otherwise declare new synthetic campaign (no relabeling as recovered 904 events).
- Scenarios: overlapping fixtures/resources, absent owner, conflicting role delegation, date change, contractual expiry, over-budget activity, false communication, supporter query and multiple simultaneous incidents.
- Produce event trace, decisions/NO_ACTION, source hashes, KPI report, receipt/replay and explicit non-dispatch proof per case.

### A3. Reuse rail without mutation
- Read-only compatibility check with native projection and enterprise universal binding.
- If interfaces match, compose a **CSSA-only adapter/test** feeding the existing immutable KX108 PRE and bounded sandbox, no real connectors.
- If interfaces differ, hold the bridge and document options rather than patching shared kernel/native modules.

### A4. Acceptance gate (single lot freeze)
- Run CSSA scoped regression (last observed 123 passed, 1 skipped) + exact integrated LOT A suite + applicable Universal tests if present; check clean worktree.
- Closure requires traceability of 11 CSSA role requirements or explicit unmet requirements; ZERO fictional approvals, sends or CRM writes.
- Only after that: LOT B matchday 12-case campaign and LOT C Universal portability.

## Operational verdict

**Interfaces identified, integration not yet implemented.** Real blocker: domain/proposal → persisted canonical work seam and source-branch compatibility. Don't multiply CSSA-only placeholder implementations to compensate for missing integration. Keep current frozen baselines untouched.
