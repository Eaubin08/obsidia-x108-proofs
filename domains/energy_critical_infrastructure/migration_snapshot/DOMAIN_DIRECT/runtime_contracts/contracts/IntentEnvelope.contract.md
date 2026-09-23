# IntentEnvelope
# runtime_contracts/contracts/IntentEnvelope.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

L'IntentEnvelope est la structure d'intention minimale et maximalement typée
qu'un module périphérique doit produire AVANT de soumettre une demande à X-108.

Il représente une intention candidate, pas une décision. Il ne peut jamais
produire ACT, ALLOW, HOLD, ou BLOCK par lui-même.

Son rôle est de formaliser : qui demande quoi, pour quel domaine, avec quel
niveau d'irréversibilité, avec quels contextes et signaux, en déclarant
explicitement qu'X-108 est requis pour toute décision.

---

## 2. Contract Status

```
Status:             CONTRACT_SKELETON_ONLY
Runtime:            NO_RUNTIME_EXECUTION
Authority:          KX108_ONLY
Emits ACT:          false
Emits ALLOW:        false
Emits HOLD:         false
Emits BLOCK:        false
Decision authority: NONE (forwarded to KX108)
Sovereign:          false
Memory write:       false
Graphiti write:     false
Tool call:          false
```

---

## 3. Inputs

| Input | Type | Source | Required | Description |
|-------|------|--------|----------|-------------|
| Requête module source | structured | tout module périphérique | OUI | La requête brute avant structuration |
| ContextPacket(s) | ContextPacket[] | Graphiti, Brody, NPL, External Signals, Atlas (future), Cognitive (future) | OUI (≥1) | Contexte associé |
| PeripheralSignalPacket(s) | PeripheralSignalPacket[] | NPL métriques, entropy, External Signals | NON | Signaux additionnels |
| Tick ou timestamp | string/int | OS3 / system clock | OUI | Contexte temporel |

---

## 4. Outputs

| Output | Type | Description |
|--------|------|-------------|
| IntentEnvelope structuré | JSON object | Représentation de l'intention soumise à X-108 |

**Ce qui N'est PAS un output :**
- ACT, ALLOW, HOLD, BLOCK — ces sorties appartiennent au DecisionTicket
- Exécution d'action monde réel
- Écriture mémoire ou graphe
- Modification d'état machine

---

## 5. Required Fields

| Field | Type | Required | Description | Boundary |
|-------|------|----------|-------------|---------|
| `intent_id` | string (UUID) | OUI | Identifiant unique de l'intention | Immutable après création |
| `source_module` | string | OUI | Nom du module émetteur | Doit être dans le registre agents_52 ou module connu |
| `action_candidate_type` | enum | OUI | Type d'action candidate : `READ`, `WRITE`, `EXECUTE`, `SIGNAL`, `EMIT_CONTEXT` | Doit correspondre aux droits du BoundaryContract du module |
| `target_domain` | string | OUI | Domaine cible : `kernel`, `sigma`, `graphiti`, `brody`, `npl`, `atlas`, `cognitive`, `gps`, `gencoin`, `external` | Doit exister dans la matrice de droits interlayer |
| `irreversibility_level` | enum | OUI | `REVERSIBLE`, `PARTIALLY_REVERSIBLE`, `IRREVERSIBLE` | Manquant → fail_closed |
| `criticality_level` | enum | OUI | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | `CRITICAL` → X108 gate obligatoire avec tau status |
| `context_packet_refs` | string[] | OUI (≥1) | IDs des ContextPackets associés | Doit référencer des packets existants et valides |
| `peripheral_signal_refs` | string[] | NON | IDs des PeripheralSignalPackets | Optionnel — enrichit le contexte X-108 |
| `requested_operation` | string | OUI | Description structurée de l'opération demandée | Doit être lisible par X-108 — pas de bypass implicite |
| `timestamp_or_tick_context` | string | OUI | Contexte temporel (ISO8601 ou tick) | Utilisé par External Signals pour anti-replay et stale check |
| `requires_x108` | boolean | OUI | Doit toujours être `true` | `false` → reject — toute intention passe par X-108 |
| `authority` | enum | OUI | Toujours `KX108_ONLY` | Autre valeur → fail_closed |
| `emits_act` | boolean | OUI | Toujours `false` | `true` → PLAN3_BACKUP_GUARD_VIOLATION |
| `source_status` | enum | OUI | Statut de la source du module : `LEAN_PROVEN`, `PYTHON_TESTED`, `PYTHON_SPEC_NOT_LEAN_PROVEN`, `DOC_ONLY`, `SPEC_FUTURE`, `UNKNOWN_SOURCE` | Propagé dans le DecisionTicket |
| `claim_scope` | enum | OUI | `CLAIMABLE_FORMAL`, `CLAIMABLE_ADVISORY`, `CLAIMABLE_SPEC_ONLY`, `CLAIM_FORBIDDEN` | Doit correspondre au source_status |

---

## 6. Forbidden Fields

| Field | Reason forbidden | Risk |
|-------|-----------------|------|
| `decision` | L'intention ne décide jamais | CRITICAL — seul DecisionTicket peut contenir decision |
| `act_trigger` | Pas d'ACT depuis IntentEnvelope | CRITICAL |
| `allow_flag` | Pas d'ALLOW depuis IntentEnvelope | CRITICAL |
| `hold_override` | Pas de bypass HOLD | CRITICAL |
| `block_override` | Pas de bypass BLOCK | CRITICAL |
| `bypass_x108` | Bypass X-108 interdit | CRITICAL — `X108_NO_BYPASS_RULE` |
| `tool_call_execution` | Pas d'exécution de tool depuis l'intention | CRITICAL |
| `direct_memory_write` | Pas d'écriture mémoire | HIGH |
| `graphiti_write` | Pas d'écriture Graphiti | HIGH |
| `brody_write` | Pas d'écriture Brody | HIGH |
| `final_verdict` | Pas de verdict depuis une intention | HIGH |
| `sovereign_decision` | L'intention n'est pas souveraine | HIGH |
| `masked_irreversibility` | irreversibility_level masqué ou `null` | CRITICAL — fail_closed si absent |

---

## 7. Allowed Operations

- Structurer une intention en JSON valide selon le schema `intent_envelope.schema.json`
- Transporter un candidat d'action avec ses métadonnées de contexte
- Référencer des ContextPackets et PeripheralSignalPackets existants
- Déclarer explicitement `requires_x108: true`
- Déclarer le niveau d'irréversibilité et de criticité
- Déclarer la source_status du module émetteur
- Déclarer le claim_scope de l'intention

---

## 8. Forbidden Operations

- Produire ACT, ALLOW, HOLD, BLOCK — interdit absolu
- Appeler un tool, une API, un adapter
- Écrire en mémoire ou en graphe (Graphiti, Brody, Neo4j)
- Décider de l'action candidate
- Bypasser le gateway X-108
- Masquer irreversibility_level
- Prétendre être souverain
- Émettre un verdict moral, culturel, historique, ou de vérité

---

## 9. Authority

```yaml
decision_authority: KX108_ONLY
periphery_authority: NONE
runtime_authority: NONE
emits_act: false
emits_allow: false
emits_hold: false
emits_block: false
requires_x108_evaluation: true
```

---

## 10. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| `irreversibility_level` manquant | `fail_closed_candidate = true` → X108 évalue → HOLD par défaut |
| `authority ≠ KX108_ONLY` | Reject immédiat → `fail_closed` |
| `requires_x108 = false` | Reject immédiat → `fail_closed` |
| `action_candidate_type` inconnu | Reject → `fail_closed` |
| `criticality_level = CRITICAL` sans context_packet | Reject → `fail_closed` |
| `emits_act = true` dans le champ | Violation détectée → `PLAN3_BACKUP_GUARD_VIOLATION` |
| `context_packet_refs` vide | `requires_x108_review = true` → HOLD candidat |
| `source_status = UNKNOWN_SOURCE` | Flag `unknown_source_flag = true` → X108 évalue avec pénalité |
| Schema JSON invalide | Reject → `fail_closed` |
| `timestamp_or_tick_context` manquant | External Signals ne peut valider → stale_risk flag |

---

## 11. Boundary

```
IntentEnvelope ↛ ACT
IntentEnvelope ↛ ALLOW
IntentEnvelope ↛ HOLD
IntentEnvelope ↛ BLOCK
IntentEnvelope → X108 gateway (obligatoire)
IntentEnvelope ← ContextPacket (0..N)
IntentEnvelope ← PeripheralSignalPacket (0..N)
IntentEnvelope → DecisionTicket (résultat X-108)
Boundary: X108_GATEWAY_REQUIRED
Boundary: NO_ACT_FROM_PERIPHERY
Boundary: FAIL_CLOSED_PRIORITY
```

---

## 12. Claim-Scope

**Autorisé :**
- "Un IntentEnvelope structure une intention soumise à X-108"
- "L'IntentEnvelope ne décide jamais — X-108 décide"
- "L'IntentEnvelope porte le niveau d'irréversibilité et de criticité de façon explicite"

**Interdit :**
- "L'IntentEnvelope peut déclencher une action" — INTERDIT
- "L'IntentEnvelope est une décision" — INTERDIT
- "L'IntentEnvelope peut bypasser X-108" — INTERDIT

---

## 13. JSON Example

```json
{
  "intent_id": "ie-2026-06-02-001",
  "source_module": "sigma_pipeline",
  "action_candidate_type": "WRITE",
  "target_domain": "graphiti",
  "irreversibility_level": "PARTIALLY_REVERSIBLE",
  "criticality_level": "HIGH",
  "context_packet_refs": ["cp-brody-20260602-001", "cp-npl-20260602-042"],
  "peripheral_signal_refs": ["psp-external-signals-temporal-001"],
  "requested_operation": "write_memory_entry(key='session_42', value=<structured_context>)",
  "timestamp_or_tick_context": "2026-06-02T09:10:37Z",
  "requires_x108": true,
  "authority": "KX108_ONLY",
  "emits_act": false,
  "source_status": "PYTHON_TESTED",
  "claim_scope": "CLAIMABLE_ADVISORY",
  "npl_labels": ["NPL_ADVISORY_NOT_SOVEREIGN"],
  "entropy_labels": [],
  "external_signal_flags": {
    "temporal_receipt": "tsr-20260602-001",
    "anti_replay_check": "PASS",
    "stale_execution_check": "PASS"
  }
}
```

*Ce JSON est non exécutable — documentation contractuelle uniquement.*

---

## 14. Future Implementation Notes

**FUTURE_IMPLEMENTATION_NOTE — Phase P2 : External Signals adapter**
Lorsque F04 External Signals sera branché en dry-run (Phase P2), l'IntentEnvelope
devra inclure un champ `external_signal_validation_ref` pointant vers le
temporal_receipt_metadata généré par les composants C459-C482.

**FUTURE_IMPLEMENTATION_NOTE — Phase P6 : NPL enrichment**
Lorsque NPL sera branché en readonly wrapper (Phase P6), les `context_packet_refs`
devront inclure au moins un NarrativeProvenancePacket si le domaine cible implique
une logique humaine (lecture de mémoire narrative, OS Trad, Reverse OS).

**FUTURE_IMPLEMENTATION_NOTE — Phase F06/F07 : Atlas/Cognitive**
Lorsque Branchable Atlas et Cognitive Reintegration seront importés (F06/F07),
le champ `target_domain` devra être étendu pour inclure `atlas` et `cognitive`
avec leurs boundaries dédiées (à créer en P1).

---

## 15. Tests Required Later

- `test_intent_envelope_requires_x108` — vérifie que `requires_x108 = true` est obligatoire
- `test_intent_envelope_no_act` — vérifie que l'IntentEnvelope ne produit jamais ACT
- `test_intent_envelope_irreversibility_fail_closed` — manquant → fail_closed
- `test_intent_envelope_schema_valid` — JSON valide contre `intent_envelope.schema.json`
- `test_intent_envelope_unknown_source_flag` — source inconnue → flag + pénalité
- `test_intent_envelope_critical_without_context_fails` — CRITICAL sans ContextPacket → reject

---

## 16. Proof Expected Later

- Python test : chaîne de validation complète (schema + boundary + fail-closed)
- Plan 4+ : formalisation Lean possible si IntentEnvelope structure devient invariant du kernel
