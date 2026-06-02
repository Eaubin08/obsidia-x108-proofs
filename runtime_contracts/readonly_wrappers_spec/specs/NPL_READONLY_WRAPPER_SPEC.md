# NPL_READONLY_WRAPPER_SPEC
# runtime_contracts/readonly_wrappers_spec/specs/
# Plan 3 P6 — Spec documentaire — NO NPL WRITE / NO NPL DECISION / NO EXECUTION
# Date: 2026-06-02
# Status: WRAPPER_SPEC_ONLY / NPL_ADVISORY_ONLY

---

## Sources locales

```
specs/12_NARRATIVE_PROVENANCE_LAYER/ — 34 fichiers importés F04
specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_TO_PLAN3_CONSTRAINTS.md
specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_CLAIM_SCOPE_LOCKS.md
specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_METRICS_ADVISORY_ONLY.md
```

**Status NPL :** SPEC_FUTURE / SPEC_IMPORTED (F04) / KX108_ONLY / NON_SOVEREIGN /
Memory Write: FORBIDDEN / Graphiti Write: FORBIDDEN

---

## Identité NPL

```
NPL = Narrative Provenance Layer
Role = fournir de la provenance narrative, des hypothèses contextuelles,
       et des métriques advisory sur la logique humaine
Boundary = NPL_ADVISORY_ONLY
Decision authority = NONE — NON_SOVEREIGN
```

---

## Contract status

```yaml
npl_wrapper_contract:
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_decide: false
  can_write_memory: false
  can_write_graph: false
  can_call_tools: false
  decision_authority: KX108_ONLY
  sovereign: false
  source_layer: npl
  spec_status: WRAPPER_SPEC_ONLY
  memory_write_status: FORBIDDEN
  graphiti_write_status: FORBIDDEN
```

---

## Claim-scope locks NPL (depuis specs/12/)

```yaml
npl_claim_scope_locks:
  # Autorisés
  narrative_provenance_candidate: true
  hypothesis: true
  advisory_metric: true
  human_logic_packet_as_non_sovereign: true
  signal_context: true
  
  # Interdits
  proof_claim: false
  diagnosis: false
  moral_verdict: false
  final_truth: false
  lean_proven_claim: false
  autonomous_decision: false
  override_x108: false
  
  # Formulations interdites :
  forbidden_phrases:
    - "NPL prouve que..."
    - "NPL diagnostique..."
    - "NPL valide juridiquement..."
    - "la logique narrative est vraie"
    - "NPL autorise X108"
    - "NPL certifie"
  
  # Formulations autorisées :
  allowed_phrases:
    - "NPL fournit une hypothèse narrative advisory"
    - "NPL enrichit le contexte de l'IntentEnvelope"
    - "NPL metric = signal advisory uniquement"
    - "NPL ne décide pas"
```

---

## Outputs admis

### ContextPacket NPL

```yaml
npl_context_packet_output:
  context_id: "CP-NPL-<uuid>-ADVISORY"
  source_layer: npl
  source_module: npl_readonly_wrapper
  readonly: true
  advisory_only: true
  confidence: 0.0-0.80   # NPL = hypothèse narrative, confiance limitée
  claim_scope: ADVISORY
  labels: [NPL_ADVISORY_NOT_SOVEREIGN, ADVISORY]
  emits_act: false
  emits_verdict: false
  source_status: SPEC_IMPORTED
  context_payload:
    narrative_provenance: "<provenance_candidate_ADVISORY>"
    hypothesis: "<hypothesis_ADVISORY_ONLY>"
    metric_advisory:
      narrative_confidence: 0.0-0.80
      provenance_score: 0.0-0.80
      hypothesis_weight: 0.0-0.80
    claim_scope: ADVISORY
    sovereign: false
    can_decide: false
  dry_run: true
```

### PeripheralSignalPacket NPL (optionnel)

```yaml
npl_peripheral_signal_optional:
  signal_type: NPL_ADVISORY_METRIC
  source_module: npl_wrapper
  source_status: SPEC_IMPORTED
  metric_name: narrative_confidence | provenance_score
  metric_value: 0.0-0.80
  metric_range: {min: 0.0, max: 0.80}
  advisory_only: true
  emits_act: false
  emits_allow_hold_block: false
  label: NPL_ADVISORY_NOT_SOVEREIGN
  boundary: NPL_ADVISORY_ONLY
  # Influence reason_codes via X108 uniquement
```

---

## Allowed operations

```
✅ Extraire provenance narrative depuis specs/12/ (futur — lecture uniquement)
✅ Produire hypothesis advisory en ContextPacket
✅ Produire métrique advisory (confiance 0-0.80)
✅ Enrichir IntentEnvelope avec label NPL_ADVISORY_NOT_SOVEREIGN
✅ Référencer comme PROVENANCE_TRACE dans OS3EvidenceTicket futur
```

## Forbidden operations

```
❌ Émettre un verdict moral
❌ Diagnostiquer une situation
❌ Prétendre à la vérité finale
❌ Prétendre que NPL = preuve Lean
❌ Écrire dans mémoire / Graphiti / Brody
❌ Déclencher ACT
❌ Émettre ALLOW/HOLD/BLOCK
❌ Modifier X108 kernel
❌ Réautoriser décision X108
❌ Confidence > 0.80 depuis NPL
```

---

## NPL → X108 chain (documentaire)

```
NPL specs/12/ (READONLY)
  ↓ extraction (future wrapper Python)
ContextPacket(source_layer=npl, advisory_only=true, label=NPL_ADVISORY_NOT_SOVEREIGN)
  +
PeripheralSignalPacket(signal_type=NPL_ADVISORY_METRIC) [optionnel]
  ↓ enriches
IntentEnvelope.context_packet_refs[]
  ↓ submitted to
X108 Gateway (seul décideur)
  ↓ X108 évalue avec le contexte NPL advisory
DecisionTicket (ALLOW/HOLD/BLOCK — X108 seul)
```
