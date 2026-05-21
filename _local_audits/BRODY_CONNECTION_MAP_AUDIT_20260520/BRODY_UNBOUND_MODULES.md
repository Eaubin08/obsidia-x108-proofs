# Brody Unbound Modules
**Audit date**: 2026-05-20

---

## A. EXISTING_AND_SHOULD_BE_BOUND_NEXT

### A1. brody_local_command_gate_readonly_v1.py
- **path**: `periphery/brody_memory_readonly/brody_local_command_gate_readonly/`
- **why it matters**: Operator loop entry point — validates incoming human commands before execution
- **current proof**: Smoke script exists; module compiles
- **current binding status**: EXISTS in periphery; NOT imported by automation_orchestrator or routes/brody.py
- **risk**: LOW — readonly gate, no write
- **recommended action**: Add to `brody_automation_orchestrator.py` operator_loop section; expose `operator_loop.status` in automation_snapshot
- **priority**: P2

### A2. brody_human_command_packet_readonly_v1.py
- **path**: `periphery/brody_memory_readonly/brody_human_command_packet_readonly/`
- **why it matters**: Structures the operator's command before Brody processes it (HumanCommandPacket)
- **current proof**: Smoke script exists
- **current binding status**: UNBOUND — not imported anywhere in API runtime
- **risk**: LOW — readonly, advisory-only
- **recommended action**: Bind after command_gate is active; emit as `human_command_packet` field in automation_snapshot
- **priority**: P2

### A3. brody_human_output_receipt_validator_readonly_v1.py
- **path**: `periphery/brody_memory_readonly/brody_human_output_receipt_validator_readonly/`
- **why it matters**: Validates the output receipt for operator handoff loop closure
- **current proof**: Smoke script exists
- **current binding status**: UNBOUND
- **risk**: LOW — readonly validator
- **recommended action**: Bind after command packet is active; emit as `execution_receipt` field
- **priority**: P2

### A4. brody_api_memory_operator_replay_readonly (smoke)
- **path**: `periphery/brody_memory_readonly/brody_api_memory_operator_replay_readonly/`
- **why it matters**: Validates operator replay path — proves the loop can replay without re-writing
- **current proof**: Smoke only
- **current binding status**: UNBOUND
- **risk**: LOW
- **recommended action**: Run as validation gate when operator_loop is activated
- **priority**: P3

---

## B. EXISTING_BUT_SHOULD_STAY_READONLY_SIDE

### B1. graphiti_candidate_prep / review / dry_run (full pipeline)
- **path**: `periphery/brody_memory_readonly/graphiti_candidate_prep_from_post_human_triage_readonly/` and related
- **why it matters**: Full 6-step memory pipeline for writing candidates to Graphiti
- **current proof**: Modules exist and compile
- **current binding status**: UNBOUND — and should REMAIN unbound until Neo4j is live and human review gate is explicit
- **risk**: MEDIUM if bound incorrectly — graphiti_write risk
- **recommended action**: Keep as manual-only operator pipeline; never auto-bind
- **priority**: P6 (after Neo4j live)

### B2. connectors/ (4 flow files)
- **path**: `connectors/brody_memory_readonly_flow.py`, `context_packet_flow.py`, `memory_feedback_candidate_flow.py`, `interface_ready_memory_flow.py`
- **why it matters**: High-level connector flows for memory pipeline orchestration
- **current binding status**: UNBOUND — standalone scripts
- **risk**: LOW (readonly) but need careful review before binding
- **recommended action**: Use as standalone operator scripts; document in operator runbook
- **priority**: P3

### B3. session_trace_ledger_readonly_v1_6_3.py
- **path**: `periphery/brody_memory_readonly/session_trace_ledger/`
- **why it matters**: Full per-session trace (more granular than session_memory_ledger)
- **current binding status**: UNBOUND
- **recommended action**: Available for operator replay / debug; not needed in real-time API path
- **priority**: P4

### B4. taxonomy_mapper_34_8_readonly_v1_6_4d.py
- **path**: `periphery/brody_memory_readonly/taxonomy_mapper_34_8_readonly/`
- **why it matters**: Maps content to 34+8 taxonomy (tree classification)
- **current binding status**: UNBOUND (tree_policy already covers basic classification)
- **recommended action**: Expose in /api/brody/chat payload if detailed taxonomy needed
- **priority**: P4

---

## C. EXISTING_BUT_STALE_OR_DUPLICATE

### C1. brody_full_runtime_orchestrator.py
- **path**: `apps/obsidia_api/brody_full_runtime_orchestrator.py`
- **why**: Role overlaps with `brody_full_runtime_reconnect.py`; name suggests older version
- **recommended action**: Verify if imported anywhere; if not, mark STALE

### C2. brody_real_response_pipeline.py
- **path**: `apps/obsidia_api/brody_real_response_pipeline.py`
- **why**: Name suggests a pipeline; `brody_memory_response_chain_adapter.py` now handles the real chain
- **recommended action**: Verify imports; if not active, mark STALE_OR_SUPERSEDED

### C3. brody_backend_response_composer.py
- **path**: `apps/obsidia_api/brody_backend_response_composer.py`
- **why**: `safe_response.py` + `safe_backend_response()` appears to handle this now
- **recommended action**: Verify; may be older composer superseded by safe_response.py

### C4. brody_v1_4_12a_final_answer_adapter.py
- **path**: `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py`
- **why**: v1.4.12a naming suggests older; `brody_true_voice_adapter.py` is current final answer source
- **recommended action**: Verify if still imported in routes/brody.py; if not, STALE

### C5. world_source_intake v1_6 and v1_6_1 (older versions)
- **path**: `periphery/brody_memory_readonly/world_source_intake/brody_world_source_intake_readonly_v1_6.py` and `v1_6_1.py`
- **why**: v1_6_2 exists — v1_6 and v1_6_1 are older versions
- **recommended action**: Keep only v1_6_2; mark others as DUPLICATE_OR_OLD

---

## D. EXISTING_BUT_PROTECTED_DO_NOT_TOUCH

| Module | Path | Reason |
|--------|------|--------|
| sigma/guard.py | sigma/ | Sigma governance — sealed |
| sigma/contracts.py | sigma/ | Sigma contracts — sealed |
| sigma/protocols.py | sigma/ | Sigma protocols — sealed |
| sigma/aggregation.py | sigma/ | Sigma aggregation — sealed |
| All Lean proofs | proofs/lean/ | Crypto-anchored |
| All TLA+ specs | formal/tla/ | Crypto-anchored |
| merkle_seal.json | root | Merkle seal anchor |
| BFCL V1 adapter | _external_benchmarks/03_bfcl/brody_adapter/ | Frozen PASS — do not modify |
| Three Foundations freeze | _local_audits/EXTERNAL_BENCHMARKS/BRODY_THREE_FOUNDATIONS_RUNTIME_STABILIZED/ | Frozen PASS |

---

## E. MISSING_BUT_REQUIRED_BY_NEXT_GOAL

### E1. tool_call_candidate readonly adapter (BLOCKING P1)
- **required by**: BFCL V2 PASS (`BFCL_BRODY_LOCAL_ADAPTER_V2_FULL_RUNTIME_PASS`)
- **description**: A readonly layer that detects BFCL-style tool-call requests in the user message, parses function schema, and emits a structured `CANDIDATE_TOOL_CALL` block in `response_md` or a dedicated `tool_call_candidate` field
- **current proof**: ABSENT — confirmed None in all 7 live API calls
- **current binding status**: DOES NOT EXIST
- **risk**: LOW — readonly, candidate only, `TOOL_CALL_IS_CANDIDATE_ONLY=true`, `BRODY_DECISION=false`
- **recommended action**: Build `apps/obsidia_api/brody_tool_call_candidate_adapter.py` — readonly, KX108_ONLY, emits candidate not decision
- **priority**: P1

### E2. operator_loop status reporter
- **description**: The `operator_loop` key exists in `automation_snapshot` but status is always empty/None — no module populates it from the live command gate state
- **current proof**: Field present in API; always empty
- **risk**: LOW
- **recommended action**: Wire `brody_local_command_gate_readonly_v1.py` status into `brody_automation_orchestrator.py`
- **priority**: P2

### E3. handoff_line module
- **description**: No dedicated handoff_line module found in any periphery subdirectory
- **current proof**: Referenced in docs (BRODY_FULL_POINTER_MAP.md); no .py file found
- **risk**: LOW
- **recommended action**: Verify if `brody_human_output_receipt_validator_readonly_v1.py` covers handoff; document
- **priority**: P3
