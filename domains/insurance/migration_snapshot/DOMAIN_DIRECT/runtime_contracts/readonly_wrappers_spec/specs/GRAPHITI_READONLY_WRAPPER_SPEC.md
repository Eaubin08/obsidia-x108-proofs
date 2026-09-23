# GRAPHITI_READONLY_WRAPPER_SPEC
# runtime_contracts/readonly_wrappers_spec/specs/
# Plan 3 P6 — Spec documentaire — NO GRAPHITI WRITE / NO EXECUTION
# Date: 2026-06-02
# Status: WRAPPER_SPEC_ONLY / READONLY_CONTEXT_ONLY

---

## Sources locales

```
periphery/graphiti/ — runtime existant (READONLY)
specs/08_MEMORY_BRODY_GRAPHITI/GRAPHITI_TO_CONTEXT_PACKET_ONLY.md
specs/08_MEMORY_BRODY_GRAPHITI/MEMORY_DECISION_FORBIDDEN_SPEC.md
specs/08_MEMORY_BRODY_GRAPHITI/NEO4J_WRITE_BOUNDARY_SPEC.md
```

---

## Identité Graphiti

```
Graphiti = memory/context graph sidecar
Role = fournir du contexte readonly sur les entités, relations, et mémoire
Boundary = READONLY_CONTEXT_ONLY
Decision authority = NONE (forwarded to KX108)
```

**Note critique :** Le corpus Brody est **absent de Graphiti V20** (confirmé audit P0).
Graphiti et Brody sont des sources distinctes. Ne pas les confondre.

---

## Contract status

```yaml
graphiti_wrapper_contract:
  readonly: true
  advisory_only: true
  emits_act: false
  emits_verdict: false
  can_decide: false
  can_write_graph: false
  can_write_memory: false
  can_call_tools: false
  decision_authority: KX108_ONLY
  sovereign: false
  source_layer: graphiti
  spec_status: WRAPPER_SPEC_ONLY
```

---

## Inputs du wrapper (documentaires)

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| query_context | string | IntentEnvelope candidate | Contexte de la requête |
| entity_refs | string[] | Graphiti graph | Entités à récupérer |
| relation_scope | string | BoundaryContract | Périmètre des relations |
| retrieval_depth | int (1-3) | Config readonly | Profondeur de traversée |

---

## Outputs admis

### ContextPacket Graphiti

```yaml
graphiti_context_packet_output:
  context_id: "CP-GRAPHITI-<uuid>-READONLY"
  source_layer: graphiti
  source_module: graphiti_readonly_wrapper
  readonly: true
  advisory_only: true
  confidence: 0.0-0.88   # jamais 1.0 — Graphiti = contexte probabiliste
  claim_scope: CONTEXT_REFERENCE
  labels: [GRAPHITI_CONTEXT_ONLY, READONLY]
  emits_act: false
  emits_verdict: false
  source_status: READONLY
  context_payload:
    entities: [<entity_id>, <entity_type>]
    relations: [<relation_id>, <relation_type>]
    retrieval_trace: "<query_hash_PLACEHOLDER>"
    memory_summary: "<summary_ADVISORY_ONLY>"
    graphiti_version: "V20"
    brody_corpus_present: false   # confirmé absent V20
  dry_run: true
```

---

## Allowed operations

```
✅ Lire des nœuds/relations Graphiti (futur — lecture uniquement)
✅ Extraire des entités en ContextPacket readonly
✅ Produire un retrieval_trace advisory
✅ Enrichir IntentEnvelope.context_packet_refs
✅ Référencer comme CONTEXT_TRACE dans OS3EvidenceTicket futur
```

## Forbidden operations

```
❌ Écrire dans le graph Graphiti
❌ Créer des nœuds/relations
❌ Modifier des entités existantes
❌ Déclencher ACT
❌ Émettre ALLOW/HOLD/BLOCK
❌ Modifier X108 kernel
❌ Réautoriser une décision X108
❌ Contourner IntentEnvelope
❌ Contourner RuntimeAdmissionContract
❌ Prétendre que le contexte graphiti = vérité absolue
❌ Prétendre que graphiti V20 contient le corpus Brody
```

---

## Graphiti → X108 chain (documentaire)

```
Graphiti graph (READONLY)
  ↓ query (future wrapper Python)
ContextPacket(source_layer=graphiti, readonly=true)
  ↓ enriches
IntentEnvelope.context_packet_refs[]
  ↓ submitted to
X108 Gateway (seul décideur)
  ↓ produces
DecisionTicket (ALLOW/HOLD/BLOCK — X108 seul)
```

---

## Invariants applicables

| Invariant | Application Graphiti |
|-----------|---------------------|
| READONLY_CONTEXT_ONLY | Graphiti = lecture seule toujours |
| E2_NO_ACT | Aucun ACT depuis Graphiti |
| D1_DETERMINISM | Même query → même ContextPacket shape |
| NO_GRAPHITI_WRITE | Aucune mutation dans P6 |

---

## Future implementation requirements

```
1. Graphiti readonly query adapter Python (periphery/graphiti/)
2. BoundaryContract pour le module graphiti_wrapper
3. RuntimeAdmissionContract : SPEC → DRY_RUN gate
4. Tests : test_graphiti_readonly_no_write + test_graphiti_no_decision
5. Lean proof : graphiti_context_only_proof
```
