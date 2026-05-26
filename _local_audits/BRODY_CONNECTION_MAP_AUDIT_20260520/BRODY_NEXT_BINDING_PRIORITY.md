# Brody Next Binding Priority
**Audit date**: 2026-05-20
**Based on**: BRODY_CONNECTION_MAP_AUDIT_20260520

Maximum 7 priorities. Do not execute — this is a map only.

---

## P0 — DO NOT TOUCH / PROTECTED

**Objective**: Never modify these during any binding work.

**Files**:
- `sigma/guard.py`, `sigma/contracts.py`, `sigma/protocols.py`, `sigma/aggregation.py`
- `proofs/lean/` (all)
- `formal/tla/` (all)
- `merkle_seal.json`
- `_external_benchmarks/03_bfcl/brody_adapter/` (BFCL V1 frozen)
- `_local_audits/EXTERNAL_BENCHMARKS/BRODY_THREE_FOUNDATIONS_RUNTIME_STABILIZED/` (Three Foundations freeze)

**Must not touch**: Everything above.
**Validation**: `git diff -- sigma/ proofs/lean/ formal/tla/ merkle_seal.json` must return empty.
**Expected status**: PROTECTED_UNCHANGED

---

## P1 — MISSING LAYER BLOCKING CURRENT GOAL

**Objective**: Build `tool_call_candidate` readonly adapter so BFCL V2 can reach PASS.

**Problem confirmed**: All 7 live API calls return `tool_call_candidate=None`. BFCL V2 smoke is `BLOCKED_NO_CANDIDATE_FROM_FULL_RUNTIME`.

**Files likely involved**:
- NEW: `apps/obsidia_api/brody_tool_call_candidate_adapter.py`
- MODIFY: `apps/obsidia_api/routes/brody.py` — add `tool_call_candidate_snapshot` to response
- MODIFY: `apps/obsidia-workbench/src/components/RightPanel.tsx` — display field

**Must not touch**: sigma, proofs, BFCL V1, Three Foundations freeze.

**Constraints**:
- `TOOL_CALL_IS_CANDIDATE_ONLY=true`
- `BRODY_DECISION=false`
- `BRODY_TOOL_AUTHORITY=false`
- `DECISION_AUTHORITY=KX108_ONLY`
- `EMITS_ACT=false`
- `MEMORY_WRITE=false`

**Validation command**:
```
python _external_benchmarks/03_bfcl/brody_adapter_v2_full_runtime/run_bfcl_brody_full_runtime_simple_python_smoke_v2.py
```

**Expected status**: `BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_PASS`

**Reason**: BFCL V2 has been live and callable for 2 sessions; only missing piece is the candidate-emission layer. Low risk — readonly, no write, no act.

---

## P2 — EXISTING MODULE TO BIND

**Objective**: Activate operator_loop status in `automation_snapshot`.

**Problem confirmed**: `automation_snapshot.operator_loop.status` is empty in all live API calls, even though `brody_local_command_gate_readonly_v1.py` exists and compiles.

**Files likely involved**:
- MODIFY: `apps/obsidia_api/brody_automation_orchestrator.py` — call command_gate status check
- READ: `periphery/brody_memory_readonly/brody_local_command_gate_readonly/brody_local_command_gate_readonly_v1.py`

**Must not touch**: sigma, proofs, kernel X108.

**Validation command**:
```
python -m pytest tests/api/test_brody_operator_loop_automation.py -v --tb=short
```

**Expected status**: `automation_snapshot.operator_loop.status` non-empty

**Reason**: Operator loop docs and modules exist; status field is wired but unpopulated. One adapter call away from being active.

---

## P3 — EXISTING MODULE TO EXPOSE IN API PAYLOAD

**Objective**: Expose `Mmonde/world_source_intake` status and `ActionCandidate` in API payload.

**Problem**: `ir_candidate` is present in API but `ActionCandidate` is not structured/typed. WorldActionBus and 34-arbres tree policy are partly bound but `mmonde_status` is not a dedicated API field.

**Files likely involved**:
- READ: `periphery/brody_memory_readonly/world_source_intake/brody_world_source_intake_readonly_v1_6_2.py`
- MODIFY: `apps/obsidia_api/brody_automation_orchestrator.py` or new adapter
- MODIFY: `apps/obsidia_api/routes/brody.py` — add `mmonde_snapshot` or `world_source_snapshot`

**Validation command**:
```
python -m pytest tests/api/ -q --tb=short
```

**Expected status**: `mmonde_snapshot` present in /api/brody/chat response

---

## P4 — EXISTING MODULE TO EXPOSE IN UI PANEL

**Objective**: Add dedicated `tool_call_candidate` panel and `operator_loop` status in RightPanel.tsx.

**Dependency**: P1 (tool_call_candidate) must exist first.

**Files likely involved**:
- MODIFY: `apps/obsidia-workbench/src/components/RightPanel.tsx`
- MODIFY: `apps/obsidia-workbench/src/api/contracts.ts` — add ToolCallCandidateSnapshot interface

**Validation command**:
```
cd apps/obsidia-workbench && npm run build
```

**Expected status**: No TypeScript errors; panel renders tool_call_candidate fields

---

## P5 — BENCHMARK INTEGRATION

**Objective**: Run BFCL on more cases once P1 is done; assess SWE-Bench and Terminal-Bench Brody integration.

**Files likely involved**:
- `_external_benchmarks/03_bfcl/brody_adapter_v2_full_runtime/`
- `_local_audits/EXTERNAL_BENCHMARKS/freezes/SWE_BENCH_WSL_GOLD_SMOKE/`
- `_local_audits/EXTERNAL_BENCHMARKS/freezes/TERMINAL_BENCH_LOCAL_ORACLE_SMOKE_V7/`

**Dependency**: P1 done; Neo4j optional (SWE-Bench / Terminal-Bench are independent of Brody memory).

**Expected status**: BFCL V2 extended smoke PASS; SWE-Bench Brody integration plan documented

---

## P6 — LATER / DEFERRED

**Objective**: Full Graphiti live write pipeline — memory candidate prep → review → import → verify.

**Dependency**: Neo4j live (NEO4J_PASSWORD set + port 7688 open). None of this should happen automatically.

**Files**:
- Full `periphery/brody_memory_readonly/graphiti_candidate_prep_*` pipeline
- `graphiti_import_apply_guarded_manual_only_v1.py`
- `post_graphiti_apply_verify_readonly_v1.py`

**Must not touch**: Until NEO4J_PASSWORD is explicitly set by operator and human review gate is confirmed.

**Risk**: MEDIUM — graphiti_write=true only at manual_apply step, but full pipeline must be audited before any binding.

**Expected status**: GRAPHITI_CANDIDATE_PREP_READY when Neo4j live — currently DEFERRED

---

## Summary

| Priority | Name | Blocking Goal | Effort | Risk |
|----------|------|---------------|--------|------|
| P0 | Protected | Always | None | ZERO |
| P1 | tool_call_candidate adapter | BFCL V2 PASS | 1 session | LOW |
| P2 | operator_loop activation | Operator visibility | 0.5 session | LOW |
| P3 | Mmonde/ActionCandidate API | Completeness | 0.5 session | LOW |
| P4 | UI panels for P1+P2 | Workbench | 0.5 session | LOW |
| P5 | Benchmark integration | BFCL extended smoke | 1 session | LOW |
| P6 | Graphiti live pipeline | Memory writes | 2+ sessions | MEDIUM |
