# PeripheralSignalPacket
# runtime_contracts/contracts/PeripheralSignalPacket.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

Le PeripheralSignalPacket représente un signal individuel non souverain émis
par une couche périphérique. Là où le ContextPacket agrège plusieurs contextes,
le PeripheralSignalPacket encode UNE métrique ou UN signal, avec son type,
sa valeur, sa plage admissible, son statut de source, et sa boundary.

Tous les signaux NPL, P107/P161 advisory, External Signals, Cognitive, Atlas,
RSSI, RGPD, et entropy peuvent être représentés dans ce format.

Un PeripheralSignalPacket ne décide jamais. Il ne produit jamais
ALLOW, HOLD, BLOCK, ou ACT. Il alimente le ContextPacket ou
l'IntentEnvelope en tant que référence additionnelle.

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
Advisory:           true
Sovereign:          false
Decision authority: NONE
```

---

## 3. Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Valeur métrique | float/int/string | module source | La valeur du signal |
| Métadonnées source | object | module source | Statut, label, timestamp |
| Référence ContextPacket | string (ID) | parent packet | Optionnel — lie le signal au contexte |

---

## 4. Outputs

| Output | Type |
|--------|------|
| PeripheralSignalPacket JSON | JSON object |

**Non-outputs :** ACT, ALLOW, HOLD, BLOCK, verdict, écriture mémoire.

---

## 5. Required Fields

| Field | Type | Required | Description | Boundary |
|-------|------|----------|-------------|---------|
| `signal_id` | string (UUID) | OUI | Identifiant unique | Immutable |
| `signal_type` | enum | OUI | `NPL_METRIC`, `ENTROPY_METRIC`, `LYAPUNOV_ADVISORY`, `THERMO_DEBT`, `EXTERNAL_TEMPORAL`, `COGNITIVE_ADVISORY`, `ATLAS_SIGNAL`, `RSSI_EVIDENCE`, `RGPD_COMPLIANCE`, `GRAPH_SIGNAL`, `RISK_SIGNAL`, `UNKNOWN` | Détermine boundary applicable |
| `source_module` | string | OUI | Module émetteur | Doit être dans le registre connu |
| `source_status` | enum | OUI | `LEAN_PROVEN`, `PYTHON_TESTED`, `PYTHON_SPEC_NOT_LEAN_PROVEN`, `DOC_ONLY`, `FUTURE_FORMAL_TARGET`, `SPEC_FUTURE`, `SOURCE_PARTIAL`, `COPIED_READONLY`, `AUDITED_ONLY`, `UNKNOWN_SOURCE` | Propagé vers X-108 |
| `metric_name` | string | OUI | Nom de la métrique (ex: `cultural_matrix_score`) | Doit correspondre à signal_type |
| `metric_value` | float/int/string | OUI | Valeur du signal | Doit être dans metric_range |
| `metric_range` | object `{min, max}` | OUI | Plage admissible | Violation → flag |
| `advisory_only` | boolean | OUI | Toujours `true` | `false` → reject |
| `decision_authority` | enum | OUI | Toujours `KX108_ONLY` | Autre → reject |
| `emits_act` | boolean | OUI | Toujours `false` | `true` → violation |
| `emits_allow_hold_block` | boolean | OUI | Toujours `false` | `true` → violation |
| `label` | string | OUI | Label de claim-scope obligatoire | Voir table labels |
| `timestamp_or_tick` | string | OUI | Contexte temporel | Anti-replay |

### Labels requis par signal_type

| signal_type | Label obligatoire |
|-------------|-----------------|
| `NPL_METRIC` | `NPL_ADVISORY_NOT_SOVEREIGN` |
| `LYAPUNOV_ADVISORY` | `PYTHON_SPEC_NOT_LEAN_PROVEN` |
| `THERMO_DEBT` | `PYTHON_SPEC_NOT_LEAN_PROVEN` |
| `ENTROPY_METRIC` | `ENTROPY_ADVISORY_NOT_RUNTIME_AUTHORITY` |
| `EXTERNAL_TEMPORAL` | `EXTERNAL_SIGNAL_ONLY` |
| `COGNITIVE_ADVISORY` | `COGNITIVE_ADVISORY_FUTURE` |
| `ATLAS_SIGNAL` | `ATLAS_READONLY_FUTURE` |
| `RSSI_EVIDENCE` | `RSSI_EVIDENCE_ONLY_FUTURE` |
| `RGPD_COMPLIANCE` | `RGPD_SCOPE_GUARD_FUTURE` |

---

## 6. Forbidden Fields

| Field | Reason | Risk |
|-------|--------|------|
| `allow_signal` | Signal ne peut émettre ALLOW | CRITICAL |
| `hold_signal` | Signal ne peut émettre HOLD seul | CRITICAL |
| `block_signal` | Signal ne peut émettre BLOCK | CRITICAL |
| `act_trigger` | Signal ne peut déclencher ACT | CRITICAL |
| `direct_decision` | Signal n'est pas souverain | HIGH |
| `proof_claim_without_source` | Claim de preuve sans source vérifiée | HIGH |
| `confidence = 1.0` sans LEAN_PROVEN | Fausse certitude | MEDIUM |

---

## 7. Allowed Operations

- Encoder une valeur métrique scalaire [0,1] ou autre plage documentée
- Étiqueter le signal avec son type, label, et source_status
- Référencer un ContextPacket parent
- Transporter des signaux NPL (37 métriques), P107 (L_value), P161 (thermo_debt)
- Transporter des signaux External Signals (anti-replay, stale, temporal_receipt)
- Transporter des signaux Cognitive, Atlas, RSSI, RGPD (future)

---

## 8. Forbidden Operations

- Décider : ALLOW, HOLD, BLOCK, ACT
- Écrire en mémoire ou graphe
- Émettre un verdict de vérité, culturel, moral
- Prétendre être souverain
- Bypasser X-108

---

## 9. Authority

```yaml
decision_authority: KX108_ONLY
advisory_only: true
emits_act: false
emits_allow_hold_block: false
sovereign: false
```

---

## 10. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| `metric_value` hors `metric_range` | `out_of_range_flag = true` → X108 ignore ou pénalise |
| `advisory_only = false` | Reject → fail_closed |
| `emits_act = true` | PLAN3_BACKUP_GUARD_VIOLATION |
| Label manquant | `label_missing_flag = true` → X108 pénalise |
| `source_status = UNKNOWN_SOURCE` | `unknown_source_flag = true` → HOLD candidat |
| Schema invalide | Reject → fail_closed |

---

## 11. Boundary

```
PeripheralSignalPacket ↛ ACT
PeripheralSignalPacket ↛ ALLOW / HOLD / BLOCK
PeripheralSignalPacket → ContextPacket (agrégation)
PeripheralSignalPacket → IntentEnvelope (référence)
Boundary: NO_ACT_FROM_PERIPHERY
Boundary: variable selon signal_type (NPL_ADVISORY_ONLY, EXTERNAL_SIGNALS_SIGNAL_ONLY, etc.)
```

---

## 12. Claim-Scope

**Autorisé :**
- "Un PeripheralSignalPacket encode un signal non souverain advisory"
- "Les métriques NPL encodées dans ce packet sont ADVISORY_ONLY [0,1]"
- "L_value (P107) et thermo_debt (P161) sont PYTHON_SPEC_NOT_LEAN_PROVEN"

**Interdit :**
- "Ce signal déclenche HOLD ou BLOCK" — INTERDIT
- "Ce signal est une décision" — INTERDIT
- "La valeur de ce signal prouve quoi que ce soit formellement" — INTERDIT sauf LEAN_PROVEN

---

## 13. JSON Example

```json
{
  "signal_id": "psp-20260602-042",
  "signal_type": "NPL_METRIC",
  "source_module": "npl_engine",
  "source_status": "SPEC_FUTURE",
  "metric_name": "cultural_matrix_score",
  "metric_value": 0.63,
  "metric_range": {"min": 0.0, "max": 1.0},
  "advisory_only": true,
  "decision_authority": "KX108_ONLY",
  "emits_act": false,
  "emits_allow_hold_block": false,
  "label": "NPL_ADVISORY_NOT_SOVEREIGN",
  "timestamp_or_tick": "2026-06-02T09:10:37Z",
  "context_packet_ref": "cp-20260602-001"
}
```

---

## 14. Future Implementation Notes

**FUTURE_IMPLEMENTATION_NOTE — P1 :** Boundary `COGNITIVE_REINTEGRATION_ADVISORY_ONLY`
permettra de valider les `COGNITIVE_ADVISORY` signal packets de F07.

**FUTURE_IMPLEMENTATION_NOTE — F06 :** Les signaux Atlas (`ATLAS_SIGNAL`) nécessiteront
la boundary `ATLAS_READONLY_ADVISORY_ONLY` et une résolution des 92 duplicats internes.

**FUTURE_IMPLEMENTATION_NOTE — F03 :** RSSI/RGPD enrichiront ce format avec des champs
`evidence_ref` et `compliance_confidence` spécifiques.

---

## 15. Tests Required Later

- `test_peripheral_signal_no_act` — advisory_only=true + emits_act=false
- `test_peripheral_signal_range_check` — valeur dans range obligatoire
- `test_peripheral_signal_label_required` — label obligatoire selon signal_type
- `test_peripheral_signal_schema_valid` — JSON valide contre le schema

---

## 16. Proof Expected Later

Python test : validation schema + boundary enforcement.
