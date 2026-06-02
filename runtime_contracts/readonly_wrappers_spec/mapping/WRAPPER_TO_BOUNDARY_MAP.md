# WRAPPER_TO_BOUNDARY_MAP
# runtime_contracts/readonly_wrappers_spec/mapping/
# Plan 3 P6 — Mapping boundaries par wrapper
# Date: 2026-06-02

---

## Table principale

| Wrapper | Boundary | Contract | Emits act? | Emits verdict? | Can write memory? | Can write graph? | Can call tools? | Decision authority |
|---------|----------|---------|-----------|----------------|------------------|-----------------|-----------------|-------------------|
| Graphiti | READONLY_CONTEXT_ONLY | ContextPacket + BoundaryContract | false | false | false | false | false | KX108_ONLY |
| Brody | READONLY_CONTEXT_ONLY | ContextPacket + BoundaryContract | false | false | false | false | false | KX108_ONLY |
| NPL | NPL_ADVISORY_ONLY | ContextPacket + PeripheralSignalPacket(opt) + BoundaryContract | false | false | false | false | false | KX108_ONLY |
| Graphiti+NPL combined | READONLY_CONTEXT_ONLY + NPL_ADVISORY_ONLY | Multiple ContextPackets | false | false | false | false | false | KX108_ONLY |
| Brody+NPL combined | READONLY_CONTEXT_ONLY + NPL_ADVISORY_ONLY | Multiple ContextPackets | false | false | false | false | false | KX108_ONLY |

---

## BoundaryContract par wrapper (forme documentaire)

### Graphiti BoundaryContract

```yaml
graphiti_boundary_contract:
  module_name: graphiti_readonly_wrapper
  module_type: READONLY_CONTEXT_SOURCE
  os_layer: OS2
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_write_memory: false
  can_write_graph: false
  can_call_tools: false
  can_produce_decision_ticket: false
  decision_authority: KX108_ONLY
  sovereign: false
  required_boundary: READONLY_CONTEXT_ONLY
  max_confidence: 0.88
  claim_scope_max: CONTEXT_REFERENCE
```

### Brody BoundaryContract

```yaml
brody_boundary_contract:
  module_name: brody_readonly_wrapper
  module_type: READONLY_MEMORY_SOURCE
  os_layer: OS2
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_write_memory: false
  can_write_graph: false
  can_call_tools: false
  can_produce_decision_ticket: false
  decision_authority: KX108_ONLY
  sovereign: false
  required_boundary: READONLY_CONTEXT_ONLY
  brody_in_graphiti_v20: false
  max_confidence: 0.85
  claim_scope_max: CONTEXT_REFERENCE
  write_admission_required: X108_ALLOW + gate humaine (futur)
```

### NPL BoundaryContract

```yaml
npl_boundary_contract:
  module_name: npl_readonly_wrapper
  module_type: NARRATIVE_ADVISORY_SOURCE
  os_layer: OS1
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_write_memory: false
  can_write_graph: false
  can_call_tools: false
  can_produce_decision_ticket: false
  can_produce_proof: false
  can_produce_diagnosis: false
  can_produce_moral_verdict: false
  decision_authority: KX108_ONLY
  sovereign: false
  required_boundary: NPL_ADVISORY_ONLY
  max_confidence: 0.80
  claim_scope_max: ADVISORY
  spec_status: SPEC_IMPORTED (F04)
```

---

## Boundaries secondaires appliquées

| Boundary | Graphiti | Brody | NPL |
|----------|---------|-------|-----|
| NO_ACT_FROM_PERIPHERY | ✅ | ✅ | ✅ |
| X108_GATEWAY_REQUIRED | ✅ | ✅ | ✅ |
| FAIL_CLOSED_PRIORITY | ✅ | ✅ | ✅ |
| NO_PACKAGES_RUNTIME_BOUNDARY | ✅ | ✅ | ✅ |

---

## Failures si boundary violée

| Boundary | Violation | Failure mode | Outcome |
|----------|-----------|-------------|---------|
| READONLY_CONTEXT_ONLY | graph_write depuis Graphiti | FM-1 | fail_closed → BLOCK |
| READONLY_CONTEXT_ONLY | memory_write depuis Brody | FM-5 | fail_closed → BLOCK |
| NPL_ADVISORY_ONLY | proof_claim depuis NPL | FM-9 | fail_closed → BLOCK |
| NO_ACT_FROM_PERIPHERY | ACT depuis tout wrapper | FM-14 | fail_closed → BLOCK absolu |
| X108_GATEWAY_REQUIRED | X108 skipped via wrapper | FM-16 | fail_closed → BLOCK absolu |
