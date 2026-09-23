# BRODY_READONLY_WRAPPER_SPEC
# runtime_contracts/readonly_wrappers_spec/specs/
# Plan 3 P6 — Spec documentaire — NO BRODY WRITE / NO EXECUTION
# Date: 2026-06-02
# Status: WRAPPER_SPEC_ONLY / READONLY_CONTEXT_ONLY

---

## Sources locales

```
periphery/brody/ — runtime existant (READONLY)
specs/08_MEMORY_BRODY_GRAPHITI/BRODY_RESPONSE_AUTHORITY_SPEC.md
specs/08_MEMORY_BRODY_GRAPHITI/CONTEXT_PACKET_READONLY_CONTRACT.md
specs/08_MEMORY_BRODY_GRAPHITI/MEMORY_DECISION_FORBIDDEN_SPEC.md
specs/08_MEMORY_BRODY_GRAPHITI/WRITABLE_MEMORY_ADMISSION_SPEC.md
```

---

## Identité Brody

```
Brody = readonly memory/context agent
Role = fournir du contexte mémoire readonly sur les interactions, traces, et mémoire épisodique
Boundary = READONLY_CONTEXT_ONLY
Decision authority = NONE (forwarded to KX108)
```

**Note critique :** Le corpus Brody est **absent de Graphiti V20** (confirmé audit P0).
Les données Brody et les données Graphiti sont dans des sources distinctes.
Brody ne peut pas alimenter Graphiti de son propre chef.

---

## Contract status

```yaml
brody_wrapper_contract:
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
  source_layer: brody
  spec_status: WRAPPER_SPEC_ONLY
  brody_in_graphiti_v20: false   # corpus absent confirmé
```

---

## Inputs du wrapper (documentaires)

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| interaction_context | string | IntentEnvelope candidate | Contexte de l'interaction |
| memory_refs | string[] | Brody memory store | Références mémoire à récupérer |
| trace_depth | int (1-2) | BoundaryContract | Profondeur de la trace |
| advisory_scope | string | BoundaryContract | Périmètre advisory |

---

## Outputs admis

### ContextPacket Brody

```yaml
brody_context_packet_output:
  context_id: "CP-BRODY-<uuid>-READONLY"
  source_layer: brody
  source_module: brody_readonly_wrapper
  readonly: true
  advisory_only: true
  confidence: 0.0-0.85
  claim_scope: CONTEXT_REFERENCE
  labels: [BRODY_CONTEXT_ONLY, READONLY]
  emits_act: false
  emits_verdict: false
  source_status: READONLY
  context_payload:
    memory_refs: [<memory_id>]
    advisory_labels: [<label>]
    interaction_trace: "<trace_ADVISORY_ONLY>"
    episodic_summary: "<summary_ADVISORY_ONLY>"
    brody_in_graphiti_v20: false   # toujours false en V20
  dry_run: true
```

---

## Règle WRITABLE_MEMORY_ADMISSION

```
specs/08_MEMORY_BRODY_GRAPHITI/WRITABLE_MEMORY_ADMISSION_SPEC.md

→ Écriture mémoire Brody = gate X108 obligatoire
→ En P6 : aucune écriture admise
→ Futur : WRITE_REQUEST doit passer par IntentEnvelope → X108 → ALLOW avant écriture

Brody readonly wrapper P6 :
  memory_write = false TOUJOURS en P6
  memory_write_gate = X108_REVIEW_REQUIRED (futur)
```

---

## Allowed operations

```
✅ Lire des références mémoire Brody (futur — lecture uniquement)
✅ Extraire traces épisodiques en ContextPacket readonly
✅ Produire un advisory_label basé sur l'historique d'interaction
✅ Enrichir IntentEnvelope.context_packet_refs
✅ Référencer comme CONTEXT_TRACE dans OS3EvidenceTicket futur
```

## Forbidden operations

```
❌ Écrire dans la mémoire Brody
❌ Mettre à jour une mémoire existante
❌ Alimenter Graphiti directement
❌ Déclencher ACT
❌ Émettre ALLOW/HOLD/BLOCK
❌ Appeler un outil
❌ Modifier X108 kernel
❌ Réautoriser décision X108
❌ Prétendre que Brody = autorité
❌ Prétendre que corpus Brody est dans Graphiti V20
```

---

## Brody → X108 chain (documentaire)

```
Brody memory (READONLY)
  ↓ query (future wrapper Python)
ContextPacket(source_layer=brody, readonly=true)
  ↓ enriches
IntentEnvelope.context_packet_refs[]
  ↓ submitted to
X108 Gateway (seul décideur)
  ↓ produces
DecisionTicket (ALLOW/HOLD/BLOCK — X108 seul)
```

**Futur (post-P6 + gate X108) :**
```
X108 produit ALLOW pour WRITE_MEMORY →
  Brody memory write autorisée (après ticket X108 ALLOW seulement)
```

---

## Invariants applicables

| Invariant | Application Brody |
|-----------|------------------|
| READONLY_CONTEXT_ONLY | Brody = lecture seule toujours en P6 |
| E2_NO_ACT | Aucun ACT depuis Brody |
| MEMORY_WRITE_X108_REVIEW_GATE | Écriture future gérée par X108 |
| NO_BRODY_WRITE | Aucune mutation en P6 |
