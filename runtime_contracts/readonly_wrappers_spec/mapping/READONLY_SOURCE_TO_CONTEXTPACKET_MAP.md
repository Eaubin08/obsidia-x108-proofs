# READONLY_SOURCE_TO_CONTEXTPACKET_MAP
# runtime_contracts/readonly_wrappers_spec/mapping/
# Plan 3 P6 — Mapping documentaire Source → ContextPacket
# Date: 2026-06-02
# Status: WRAPPER_SPEC_ONLY

---

## Règle globale

```
∀ source readonly s : output(s) = ContextPacket(readonly=true, advisory_only=true)
∀ source readonly s : output(s) ↛ DecisionTicket
∀ source readonly s : output(s) ↛ ACT
∀ source readonly s : output(s) → IntentEnvelope.context_packet_refs (enrichissement)
```

---

## Table de mapping principale

| Source | Current status | Allowed output | Required ContextPacket fields | Forbidden output | Boundary | Failure mode |
|--------|---------------|----------------|-------------------------------|------------------|----------|-------------|
| Graphiti | READONLY periphery existant | ContextPacket(source_layer=graphiti) | readonly=true, advisory_only=true, labels=[GRAPHITI_CONTEXT_ONLY] | graph_write, decision, ACT, memory_write | READONLY_CONTEXT_ONLY | FM-1,FM-2,FM-3,FM-4 |
| Brody | READONLY periphery existant (corpus absent Graphiti V20) | ContextPacket(source_layer=brody) | readonly=true, advisory_only=true, labels=[BRODY_CONTEXT_ONLY] | memory_write, tool_call, decision, ACT | READONLY_CONTEXT_ONLY | FM-5,FM-6,FM-7,FM-8 |
| NPL | SPEC_IMPORTED (F04) — specs/12/ | ContextPacket(source_layer=npl) + PeripheralSignalPacket(NPL_ADVISORY) optionnel | advisory_only=true, labels=[NPL_ADVISORY_NOT_SOVEREIGN], confidence≤0.80 | proof_claim, diagnosis, moral_verdict, decision | NPL_ADVISORY_ONLY | FM-9,FM-10,FM-11,FM-12,FM-13 |
| Graphiti + NPL combined | READONLY + SPEC_IMPORTED | ContextPacket[] (2 packets distincts) | chaque packet = ses propres labels + boundaries | confondre les deux sources, merger sans distinction | READONLY_CONTEXT_ONLY + NPL_ADVISORY_ONLY | FM-17 |
| Brody + NPL combined | READONLY + SPEC_IMPORTED | ContextPacket[] (2 packets distincts) | chaque packet = ses propres labels + boundaries | confondre les deux sources | READONLY_CONTEXT_ONLY + NPL_ADVISORY_ONLY | FM-17 |
| Future Graphiti/Brody/NPL OS3 evidence | FUTURE — post-implementation | OS3EvidenceTicket reference (CONTEXT_TRACE / PROVENANCE_TRACE) | evidence_type, source_status, claim_scope=SPEC_ONLY | real evidence claim in P6 | READONLY_CONTEXT_ONLY | FM-19 |

---

## Mapping détaillé — Graphiti → ContextPacket

```yaml
graphiti_to_context_packet:
  input_query:
    entity_refs: [<entity_id>]
    relation_scope: <scope>
    retrieval_depth: 1-3
  
  output_context_packet:
    source_layer: graphiti
    source_module: graphiti_readonly_wrapper
    readonly: true
    advisory_only: true
    confidence: 0.0-0.88
    claim_scope: CONTEXT_REFERENCE
    labels: [GRAPHITI_CONTEXT_ONLY, READONLY]
    context_payload:
      entities: [<entity_summary>]
      relations: [<relation_summary>]
      retrieval_trace: ADVISORY_ONLY
      brody_corpus_present: false  # confirmé V20
  
  intent_enrichment:
    target: IntentEnvelope.context_packet_refs[]
    method: APPEND_CONTEXT_REFERENCE
    override_decision: false
```

---

## Mapping détaillé — Brody → ContextPacket

```yaml
brody_to_context_packet:
  input_query:
    memory_refs: [<memory_id>]
    trace_depth: 1-2
    advisory_scope: <scope>
  
  output_context_packet:
    source_layer: brody
    source_module: brody_readonly_wrapper
    readonly: true
    advisory_only: true
    confidence: 0.0-0.85
    claim_scope: CONTEXT_REFERENCE
    labels: [BRODY_CONTEXT_ONLY, READONLY]
    context_payload:
      memory_refs: [<summary>]
      advisory_labels: [<label>]
      interaction_trace: ADVISORY_ONLY
      brody_in_graphiti_v20: false  # toujours false
  
  memory_write_gate:
    write_allowed_in_p6: false
    write_requires: X108_ALLOW + gate humaine
```

---

## Mapping détaillé — NPL → ContextPacket + PeripheralSignalPacket

```yaml
npl_to_context_packet:
  input_spec:
    source: specs/12_NARRATIVE_PROVENANCE_LAYER/
    files_count: 34
    source_status: SPEC_IMPORTED
  
  output_context_packet:
    source_layer: npl
    source_module: npl_readonly_wrapper
    advisory_only: true
    confidence: 0.0-0.80   # jamais > 0.80
    claim_scope: ADVISORY
    labels: [NPL_ADVISORY_NOT_SOVEREIGN, ADVISORY]
    context_payload:
      narrative_provenance: ADVISORY_CANDIDATE
      hypothesis: ADVISORY_ONLY
      metric_advisory: {confidence: 0.0-0.80}
    sovereign: false
    can_decide: false
  
  output_peripheral_signal_optional:
    signal_type: NPL_ADVISORY_METRIC
    metric_name: narrative_confidence | provenance_score
    metric_value: 0.0-0.80
    advisory_only: true
    emits_allow_hold_block: false
```
