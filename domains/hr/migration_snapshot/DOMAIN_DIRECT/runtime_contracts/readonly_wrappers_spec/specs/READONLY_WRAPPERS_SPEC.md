# READONLY_WRAPPERS_SPEC
# runtime_contracts/readonly_wrappers_spec/specs/
# Plan 3 P6 — Spec documentaire uniquement — NO WRAPPER ACTIVE / NO WRITE / NO EXECUTION
# Date: 2026-06-02
# Status: WRAPPER_SPEC_ONLY / CONTEXT_ENRICHMENT_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

Ce document spécifie la structure documentaire des futurs wrappers readonly pour :
- Graphiti (memory/context graph — readonly uniquement)
- Brody (memory/context agent — readonly uniquement)
- NPL (Narrative Provenance Layer — advisory uniquement)

Ces wrappers produiront des ContextPackets enrichissant l'IntentEnvelope avant soumission
à X-108. Ils ne décident jamais. Ils n'écrivent jamais. Ils n'autorisent jamais.

---

## 2. Status

```
Status:                 WRAPPER_SPEC_ONLY
Wrapper actif:          NO
Memory write:           NO
Graph write:            NO
Graphiti write:         NO
Brody write:            NO
Tool call:              NO
Python files:           NO
Runtime execution:      NO
Test execution:         NO
Packages:               NO
World action:           NO
DecisionTicket réel:    NO
Commit:                 NO
Push:                   NO
```

---

## 3. Scope

| Wrapper | Source | Boundary | Status local | Output autorisé |
|---------|--------|----------|-------------|-----------------|
| Graphiti | periphery/graphiti/ (existant) | READONLY_CONTEXT_ONLY | READONLY — periphery existant | ContextPacket readonly |
| Brody | periphery/brody/ (existant) | READONLY_CONTEXT_ONLY | READONLY — periphery existant | ContextPacket readonly |
| NPL | specs/12_NARRATIVE_PROVENANCE_LAYER/ (importé F04) | NPL_ADVISORY_ONLY | SPEC_IMPORTED | ContextPacket advisory |

**Note :** Le corpus Brody est absent de Graphiti V20 (confirmé audit P0).
Graphiti et Brody sont des sources distinctes.

---

## 4. Non-executable status

P6 crée uniquement :
- Fichiers `.md` documentaires
- Zéro fichier `.py`
- Zéro wrapper Python actif
- Zéro requête DB réelle
- Zéro lecture mémoire réelle
- Zéro écriture mémoire réelle

Les futurs wrappers Python seront créés dans `periphery/` uniquement après :
1. Plan 3 P6 Readonly Wrappers Spec validé (ce run)
2. Gate humaine explicite
3. Tests anti-bypass P4 exécutables après F03/F06/F07

---

## 5. Wrapper model

```
Source readonly (Graphiti | Brody | NPL)
  ↓
Readonly Wrapper SPEC
  ↓
ContextPacket (readonly=true, advisory_only=true, emits_verdict=false)
  ↓
IntentEnvelope.context_packet_refs[]
  ↓
X108 Gateway (seul décideur)
  ↓
DecisionTicket (ALLOW/HOLD/BLOCK — X108 seul)
```

Propriétés fondamentales de tout wrapper readonly :

```yaml
wrapper_properties:
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_write_memory: false
  can_write_graph: false
  can_call_tools: false
  decision_authority: KX108_ONLY
  sovereign: false
  context_enrichment_only: true
```

---

## 6. Readonly source model

| Propriété | Graphiti | Brody | NPL |
|-----------|----------|-------|-----|
| Source type | Memory/context graph | Memory/context agent | Narrative provenance |
| Local status | periphery existant (READONLY) | periphery existant (READONLY) | specs/12/ (SPEC_IMPORTED F04) |
| Brody corpus in Graphiti V20 | N/A | ABSENT (confirmed P0 audit) | N/A |
| memory_decision | false | false | false |
| writes_allowed | false | false | false |
| advisory_only | true | true | true |
| claim_max | CONTEXT_REFERENCE | CONTEXT_REFERENCE | ADVISORY |
| can_produce | ContextPacket | ContextPacket | ContextPacket |
| cannot_produce | DecisionTicket | DecisionTicket | DecisionTicket |

---

## 7. Graphiti readonly wrapper

Voir `specs/GRAPHITI_READONLY_WRAPPER_SPEC.md` pour le détail complet.

Résumé :
- Source : periphery/graphiti/ + specs/08_MEMORY_BRODY_GRAPHITI/GRAPHITI_TO_CONTEXT_PACKET_ONLY.md
- Output : ContextPacket(source_layer=graphiti, readonly=true, advisory_only=true)
- Interdiction absolue : graph_write, memory_write, decision, ACT
- Boundary : READONLY_CONTEXT_ONLY

---

## 8. Brody readonly wrapper

Voir `specs/BRODY_READONLY_WRAPPER_SPEC.md` pour le détail complet.

Résumé :
- Source : periphery/brody/ (corpus absent de Graphiti V20)
- Output : ContextPacket(source_layer=brody, readonly=true, advisory_only=true)
- Interdiction absolue : memory_write, tool_call, decision, ACT
- Boundary : READONLY_CONTEXT_ONLY

---

## 9. NPL readonly wrapper

Voir `specs/NPL_READONLY_WRAPPER_SPEC.md` pour le détail complet.

Résumé :
- Source : specs/12_NARRATIVE_PROVENANCE_LAYER/ (34 fichiers importés F04)
- Output : ContextPacket(source_layer=npl, advisory_only=true, label=NPL_ADVISORY_NOT_SOVEREIGN)
- Interdiction absolue : proof_claim, diagnosis, moral_verdict, decision
- Boundary : NPL_ADVISORY_ONLY

---

## 10. Required contracts

| Contrat | Rôle dans P6 |
|---------|-------------|
| ContextPacket.contract.md | Output principal des wrappers |
| PeripheralSignalPacket.contract.md | Output optionnel (métriques NPL) |
| IntentEnvelope.contract.md | Destination enrichie |
| DecisionTicket.contract.md | X108 produit après enrichissement |
| OS3EvidenceTicket.contract.md | Evidence future des wrappers |
| BoundaryContract.contract.md | Droits de chaque wrapper |
| RuntimeAdmissionContract.contract.md | Admission SPEC→DRY_RUN |

---

## 11. Required schemas

| Schema | Usage |
|--------|-------|
| context_packet.schema.json | Validation ContextPacket output |
| peripheral_signal_packet.schema.json | Validation PeripheralSignalPacket optionnel |
| intent_envelope.schema.json | Destination enrichie |
| os3_evidence_ticket.schema.json | Evidence reference future |

---

## 12. Required boundaries

| Boundary | Wrapper(s) | Rôle |
|----------|-----------|------|
| READONLY_CONTEXT_ONLY | Graphiti, Brody | Lecture seule — aucune écriture |
| NPL_ADVISORY_ONLY | NPL | Advisory uniquement — jamais verdict |
| NO_ACT_FROM_PERIPHERY | Tous | Aucun ACT depuis wrapper |
| X108_GATEWAY_REQUIRED | Tous | Décision → X108 obligatoirement |
| FAIL_CLOSED_PRIORITY | Tous | Failure → fail_closed |

---

## 13. ContextPacket output model

```yaml
contextpacket_readonly_output:
  source_layer: graphiti | brody | npl
  source_module: <wrapper_id>
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_decide: false
  decision_authority: KX108_ONLY
  confidence: 0.0-0.95   # jamais 1.0 depuis périphérie
  claim_scope: CONTEXT_REFERENCE | ADVISORY  # jamais CLAIMABLE_FORMAL
  labels:
    graphiti: [GRAPHITI_CONTEXT_ONLY, READONLY]
    brody:    [BRODY_CONTEXT_ONLY, READONLY]
    npl:      [NPL_ADVISORY_NOT_SOVEREIGN, ADVISORY]
  context_payload:
    graphiti: {entities: [], relations: [], retrieval_trace: "..."}
    brody:    {memory_refs: [], advisory_labels: [], trace: "..."}
    npl:      {narrative_provenance: "...", hypothesis: "...", metric_advisory: {}}
  dry_run: true
```

---

## 14. PeripheralSignalPacket optional model

NPL peut optionnellement émettre un PeripheralSignalPacket pour ses métriques advisory :

```yaml
npl_peripheral_signal_optional:
  signal_type: NPL_ADVISORY_METRIC
  source_module: npl_wrapper
  metric_name: narrative_confidence | provenance_score | hypothesis_weight
  metric_value: 0.0-0.95
  advisory_only: true
  emits_act: false
  emits_allow_hold_block: false
  label: NPL_ADVISORY_NOT_SOVEREIGN
  boundary: NPL_ADVISORY_ONLY
  # Influence reason_codes via X108 uniquement — jamais direct
```

---

## 15. Link to IntentEnvelope

```yaml
intent_envelope_enrichment:
  context_packet_refs:
    - <graphiti_context_packet_id>  # optionnel
    - <brody_context_packet_id>     # optionnel
    - <npl_context_packet_id>       # optionnel
  
  # Les wrappers enrichissent — ils ne décident pas
  decision_authority: KX108_ONLY
  enrichment_only: true
  
  # Règle P6 :
  # ContextPacket + IntentEnvelope → X108 évalue et décide
  # Les wrappers ne peuvent pas forcer une décision via l'enrichissement
```

---

## 16. Link to OS3EvidenceTicket

```yaml
os3_evidence_future_from_wrappers:
  graphiti_trace: CONTEXT_TRACE_FUTURE (référencé P5)
  brody_trace: CONTEXT_TRACE_FUTURE (référencé P5)
  npl_trace: PROVENANCE_TRACE (référencé P5 — SPEC_IMPORTED)
  
  link_to_os3: FUTURE — post-wrapper-implementation
  evidence_type: CONTEXT_TRACE | PROVENANCE_TRACE
  claim_scope: SPEC_ONLY | SPEC_IMPORTED
  real_evidence_in_p6: false
```

---

## 17. Allowed operations (P6)

```
✅ Créer fichiers .md dans readonly_wrappers_spec/
✅ Décrire la forme théorique des wrappers readonly
✅ Documenter le mapping source → ContextPacket
✅ Documenter les boundaries par wrapper
✅ Créer exemples JSON documentaires en Markdown
✅ Lier aux contrats et boundaries existants
```

---

## 18. Forbidden operations (P6)

```
❌ Créer wrapper Python actif
❌ Créer fichier .py
❌ Lire Graphiti réel
❌ Écrire Graphiti réel
❌ Lire Brody réel
❌ Écrire Brody réel
❌ Écrire mémoire
❌ Appeler un outil
❌ Créer adapter actif
❌ Créer décision
❌ Créer ACT
❌ Modifier periphery/ / specs/ / runtime existant
❌ Committer ou pousser
```

---

## 19. Failure handling

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f : f → requires_x108_review
∀ failure mode f : f ↛ allow_by_default
```

---

## 20. Claim-scope

| Wrapper | Claim autorisé | Claim interdit |
|---------|---------------|----------------|
| Graphiti | CONTEXT_REFERENCE / READONLY | truth, decision, graph_authority |
| Brody | CONTEXT_REFERENCE / READONLY | memory_authority, tool_execution |
| NPL | ADVISORY / PROVENANCE_CANDIDATE | PROOF, DIAGNOSIS, MORAL_VERDICT |

---

## 21. Future implementation gates

| Gate | Prérequis |
|------|-----------|
| Graphiti wrapper Python | P6 Spec ✅ + gate humaine |
| Brody wrapper Python | P6 Spec ✅ + gate humaine |
| NPL wrapper Python | P6 Spec ✅ + gate humaine |
| Tests wrappers | Wrappers Python + tests/readonly_wrappers/ |
| F07 (Cognitive context) | F78B ✅ + F78C ✅ + Cognitive specs importées |
| Atlas context wrapper | F06 + P6 Spec ✅ |

---

## 22. Tests required later

```
test_graphiti_readonly_no_write
test_graphiti_no_decision
test_brody_readonly_no_write
test_brody_no_decision
test_npl_advisory_no_verdict
test_npl_no_proof_claim
test_wrapper_context_packet_advisory_only
test_wrapper_cannot_bypass_x108
test_wrapper_cannot_emit_act
test_wrapper_fail_closed_on_write_attempt
```

---

## 23. Proof expected later

```
Lean proofs attendus :
  graphiti_context_only_proof
  brody_context_only_proof
  npl_advisory_non_sovereign_proof

TLA+ specs attendues :
  ReadonlyWrapperInvariant.tla
  ContextEnrichmentOnly.tla
```
