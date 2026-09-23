# DecisionTicket
# runtime_contracts/contracts/DecisionTicket.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

Le DecisionTicket est le SEUL artefact du système Obsidia X-108 admis à contenir
ALLOW, HOLD, ou BLOCK comme valeur de décision.

Il représente la sortie du gateway X-108 après évaluation complète d'un
IntentEnvelope avec ses ContextPackets et PeripheralSignalPackets associés.

Aucune périphérie, aucun LLM, aucune couche NPL, Graphiti, Brody, External
Signals, Atlas, Cognitive, Balance, P107/P161, Audio/Entropy, RSSI, ou RGPD
ne peut produire un DecisionTicket ou les champs `decision = ALLOW/HOLD/BLOCK`.

Ce contrat s'appuie directement sur `periphery/os3_ticket.py` (OS3ProofTicket)
et les 28 théorèmes Lean-proven du kernel X-108.

---

## 2. Contract Status

```
Status:             CONTRACT_SKELETON_ONLY
Runtime:            NO_RUNTIME_EXECUTION
Authority:          KX108_ONLY — seul producteur de DecisionTicket
Emits ACT:          false (via ALLOW → action possible après gate)
Decision values:    ALLOW | HOLD | BLOCK
Priority:           BLOCK > HOLD > ALLOW
Peripheral override: FORBIDDEN
```

---

## 3. Inputs

| Input | Type | Source | Required |
|-------|------|--------|----------|
| IntentEnvelope | IntentEnvelope | Module périphérique | OUI |
| ContextPacket(s) | ContextPacket[] | Graphiti, Brody, NPL, External Signals, etc. | OUI (≥1) |
| PeripheralSignalPacket(s) | PeripheralSignalPacket[] | NPL, External Signals, P107/P161, etc. | NON |
| Tau status | string | X108 temporal kernel | OUI pour irréversible |
| OS3 evidence refs | string[] | OS3EvidenceTicket | OUI pour CRITICAL |

---

## 4. Outputs

| Output | Type | Description |
|--------|------|-------------|
| DecisionTicket structuré | JSON object | Artefact de décision X-108 complet |
| `decision` | enum | `ALLOW` / `HOLD` / `BLOCK` |
| `reason_codes` | string[] | Codes de raison structurés |
| `x108_gate_status` | string | Statut du gateway |

---

## 5. Required Fields

| Field | Type | Required | Description | Boundary |
|-------|------|----------|-------------|---------|
| `ticket_id` | string (UUID) | OUI | Identifiant unique | Immutable — inclus dans hash chain |
| `intent_envelope_ref` | string (UUID) | OUI | Référence à l'IntentEnvelope source | Doit exister |
| `decision` | enum | OUI | `ALLOW`, `HOLD`, `BLOCK` | Seuls ces 3 valeurs admises |
| `decision_priority` | string | OUI | Toujours `BLOCK > HOLD > ALLOW` | Invariant `aggregate4_fail_closed` |
| `reason_codes` | string[] | OUI (≥1) | Codes structurés expliquant la décision | Auditable |
| `x108_gate_status` | string | OUI | `X108_EVALUATED`, `X108_PENDING`, `X108_FAIL_CLOSED` | |
| `tau_status` | string | OUI pour irréversible | `TAU_ELAPSED`, `TAU_PENDING`, `TAU_NOT_APPLICABLE` | `X108_no_act_before_tau` |
| `irreversibility_status` | string | OUI | `REVERSIBLE`, `PARTIALLY_REVERSIBLE`, `IRREVERSIBLE` | Doit correspondre à l'IntentEnvelope |
| `evidence_ticket_refs` | string[] | OUI si CRITICAL | Références aux OS3EvidenceTickets | `test_os3_ticket_hash_chain` |
| `replay_refs` | string[] | NON | Références aux replays vérifiés | `P17_AuditGrowth` |
| `timestamp_or_tick` | string | OUI | Contexte temporel de la décision | Anti-replay C463 |
| `hash_or_seal_ref` | string | OUI | Hash sha256 ou seal merkle de ce ticket | `P13_Immutability`, `merkleRoot_change_if_leaf_change` |
| `input_hash` | string | OUI | sha256(action_candidate) | Chaîne de preuves OS3ProofTicket |
| `output_hash` | string | OUI | sha256(envelope) | Chaîne de preuves |
| `trace_hash` | string | OUI | sha256({input+output+packet}) | Chaîne de preuves |
| `merkle_root` | string | OUI | sha256([input_hash, output_hash, trace_hash]) | `merkle2_right_mutation` |
| `replay_status` | string | OUI | `NOT_RUN`, `PASS`, `FAIL`, `PENDING` | Default `NOT_RUN` |
| `context_packet_refs` | string[] | OUI | IDs des ContextPackets utilisés | Traçabilité |
| `source_status_summary` | object | OUI | Résumé des source_status des inputs | Claim-scope |

---

## 6. Forbidden Fields

| Field | Reason | Risk |
|-------|--------|------|
| `peripheral_override` | Aucune périphérie ne peut override X-108 | CRITICAL |
| `llm_override` | LLM ne peut pas override X-108 | CRITICAL |
| `npl_override` | NPL ne peut pas changer la décision | CRITICAL |
| `graphiti_override` | Graphiti readonly — ne décide pas | CRITICAL |
| `brody_override` | Brody readonly — ne décide pas | CRITICAL |
| `external_signal_override` | External Signals = signal temporel seulement | CRITICAL |
| `p107_p161_override` | P107/P161 = DOC_ONLY — ne décident pas | CRITICAL |
| `atlas_override` | Atlas future — ne décide pas | CRITICAL |
| `cognitive_override` | Cognitive future — ne décide pas | CRITICAL |
| `rssi_override` | RSSI evidence — ne décide pas | HIGH |
| `rgpd_override` | RGPD compliance — ne décide pas | HIGH |
| `bypass_flag` | Bypass X-108 interdit absolu | CRITICAL |
| `decision = ACT` | ACT n'est pas une valeur de decision | CRITICAL |
| `decision = null` | Décision doit être explicite | HIGH |

---

## 7. Allowed Operations

- Encoder ALLOW, HOLD, ou BLOCK comme décision finale de X-108
- Attacher la chaîne de hash (input_hash, output_hash, trace_hash, merkle_root)
- Référencer les ContextPackets et PeripheralSignalPackets qui ont informé la décision
- Indiquer le tau_status et irreversibility_status
- Référencer les OS3EvidenceTickets pour les actions CRITICAL
- Propager le source_status_summary pour la traçabilité du claim-scope

---

## 8. Forbidden Operations

- Produire ALLOW/HOLD/BLOCK depuis toute source autre que X-108
- Bypasser le gateway X-108
- Permettre à une périphérie de modifier la décision
- Prétendre qu'une preuve Lean est présente sans vérification (hors 28 théorèmes)
- Masquer les reason_codes
- Produire un ticket sans chaîne de hash complète

---

## 9. Authority

```yaml
decision_authority: KX108_ONLY
peripheral_authority: NONE
llm_authority: NONE
npl_authority: NONE
emits_decision: true  # seul contrat autorisé
decision_values: [ALLOW, HOLD, BLOCK]
priority: BLOCK > HOLD > ALLOW  # aggregate4_fail_closed
```

---

## 10. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| `decision` manquant | `fail_closed` → BLOCK |
| `tau_status` manquant pour irréversible | `HOLD` — `X108_no_act_before_tau` |
| `evidence_ticket_refs` manquant pour CRITICAL | `HOLD` ou `BLOCK` |
| `input_hash` ou `merkle_root` invalide | `fail_closed` → BLOCK |
| `peripheral_override` détecté | `fail_closed` → BLOCK + PLAN3_BACKUP_GUARD_VIOLATION |
| Conflit entre deux decisions | `BLOCK` — `aggregate4_fail_closed` |
| `source_status = UNKNOWN_SOURCE` dans input | `HOLD` — inconnu = prudence |
| Schema JSON invalide | `fail_closed` → BLOCK |
| `replay_status = FAIL` | `BLOCK` — replay échoué = action compromise |

---

## 11. Boundary

```
DecisionTicket ← KX108_ONLY (seul producteur)
DecisionTicket → OS3EvidenceTicket (attaché)
DecisionTicket ← IntentEnvelope (référence source)
DecisionTicket → Module action (si ALLOW + action)
Invariants :
  D1_determinism         → décision déterministe
  E2_no_act_below_threshold → seuil θ respecté
  X108_no_act_before_tau → gate temporelle
  aggregate4_fail_closed → BLOCK > HOLD > ALLOW
  P13_Immutability       → hash_or_seal_ref immuable
  merkleRoot_change_if_leaf_change → merkle_root détecte modification
  aggregate4_unanimous   → consensus requis pour ALLOW critique
```

---

## 12. Claim-Scope

**Autorisé :**
- "Le DecisionTicket est la seule sortie décisionnelle de X-108"
- "ALLOW, HOLD, BLOCK sont produits uniquement par X-108 dans un DecisionTicket"
- "La chaîne de hash (OS3ProofTicket) prouve l'intégrité de la décision"
- "BLOCK > HOLD > ALLOW est l'invariant `aggregate4_fail_closed`"

**Interdit :**
- "NPL a contribué à la décision" — NPL contribue au ContextPacket, X-108 décide
- "P107/P161 ont déclenché HOLD" — INTERDIT (signaux advisory seulement)
- "External Signals ont autorisé ACT" — INTERDIT
- "La décision est une preuve Lean formelle" — Lean-proven = 28 théorèmes, pas ce ticket

---

## 13. JSON Example

```json
{
  "ticket_id": "dt-2026-06-02-001",
  "intent_envelope_ref": "ie-2026-06-02-001",
  "decision": "ALLOW",
  "decision_priority": "BLOCK > HOLD > ALLOW",
  "reason_codes": ["TAU_ELAPSED", "CONTEXT_SUFFICIENT", "REVERSIBILITY_CONFIRMED"],
  "x108_gate_status": "X108_EVALUATED",
  "tau_status": "TAU_ELAPSED",
  "irreversibility_status": "REVERSIBLE",
  "evidence_ticket_refs": ["os3-2026-06-02-001"],
  "replay_refs": [],
  "timestamp_or_tick": "2026-06-02T09:10:40Z",
  "hash_or_seal_ref": "seal-merkle-abc123",
  "input_hash": "sha256:abc123...",
  "output_hash": "sha256:def456...",
  "trace_hash": "sha256:ghi789...",
  "merkle_root": "sha256:jkl012...",
  "replay_status": "NOT_RUN",
  "context_packet_refs": ["cp-brody-001", "cp-npl-001"],
  "source_status_summary": {
    "brody": "PYTHON_TESTED",
    "npl": "SPEC_FUTURE",
    "external_signals": "SPEC_IMPORTED",
    "p107_advisory": "DOC_ONLY"
  }
}
```

---

## 14. Future Implementation Notes

**FUTURE_IMPLEMENTATION_NOTE — Phase P3 : X108 Gateway Dry-Run Harness**
La première implémentation dry-run produira des DecisionTickets avec
`replay_status = "NOT_RUN"` et `x108_gate_status = "X108_EVALUATED"` (simulé).
Aucune action réelle ne sera déclenchée.

**FUTURE_IMPLEMENTATION_NOTE — Phase P5 : OS3 Evidence Ticket dry-run**
`evidence_ticket_refs` sera systématiquement rempli lors de P5.
La validation de la chaîne merkle deviendra un test automatique.

---

## 15. Tests Required Later

- `test_decision_ticket_only_from_x108` — aucune périphérie ne produit DecisionTicket
- `test_decision_ticket_fail_closed_on_conflict` — conflit → BLOCK
- `test_decision_ticket_hash_chain_valid` — sha256 chain complète
- `test_decision_ticket_tau_hold_on_irreversible` — sans tau → HOLD
- `test_decision_ticket_peripheral_override_forbidden` — override → BLOCK + violation

---

## 16. Proof Expected Later

- Python test : chaîne sha256 (OS3ProofTicket pattern existant dans periphery/os3_ticket.py)
- Plan 4+ : formalisation Lean possible pour DecisionTicket structure invariante
