# FAIL_CLOSED_PRIORITY
# runtime_contracts/boundaries/FAIL_CLOSED_PRIORITY.md
# Status: CONTRACT_SKELETON_ONLY

---

## 1. Boundary Statement

```
BLOCK > HOLD > ALLOW  (priorité absolue — invariant aggregate4_fail_closed)

∀ situation ambiguë → HOLD ou BLOCK (jamais ALLOW par défaut)
∀ champ manquant critique → fail_closed
∀ conflit de décision → BLOCK
∀ source inconnue → HOLD candidat
∀ claim-scope conflit → fail_closed
∀ schema invalide → fail_closed et reject
∀ stale temporal signal → fail_closed
```

---

## 2. Applies To

Tous les modules, tous les contrats, tous les schemas.
Applicable à : IntentEnvelope, ContextPacket, PeripheralSignalPacket, DecisionTicket, OS3EvidenceTicket, BoundaryContract, RuntimeAdmissionContract.

---

## 3. Allowed

- BLOCK en réponse à tout conflit, ambiguïté, ou champ manquant critique
- HOLD en réponse à toute incertitude réversible
- ALLOW uniquement quand toutes les conditions sont satisfaites

---

## 4. Forbidden

```
❌ ALLOW par défaut (fail-open)
❌ Ignorer un champ critique manquant
❌ Continuer avec source inconnue sans flag
❌ Produire ALLOW avec claim-scope non vérifié
❌ Bypasser fail_closed par exception silencieuse
```

---

## 5. Failure Mode — Table complète

| Déclencheur | Comportement fail_closed |
|-------------|------------------------|
| `irreversibility_level` manquant | `fail_closed_candidate = true` → HOLD par défaut |
| `authority ≠ KX108_ONLY` | Reject → fail_closed |
| Conflit entre deux DecisionTickets | BLOCK |
| `tau_status` manquant pour IRREVERSIBLE | HOLD — `X108_no_act_before_tau` |
| `evidence_ticket_refs` absent pour CRITICAL | HOLD ou BLOCK |
| `hash_chain` invalide ou manquante | BLOCK |
| `replay_status = FAIL` | BLOCK |
| `source_status = UNKNOWN_SOURCE` | HOLD + flag |
| Label NPL manquant | `label_missing_flag` → X108 pénalise |
| Schema JSON invalide | Reject → fail_closed |
| `confidence = 1.0` sans LEAN_PROVEN | `overconfidence_flag` → poids réduit |
| Stale temporal signal (stale_execution_check = FAIL) | fail_closed → HOLD candidat |
| `peripheral_override` détecté | BLOCK + violation |

---

## 6. Required Contract Fields

- `decision_priority: "BLOCK > HOLD > ALLOW"` dans DecisionTicket (const)
- `fail_closed_candidate` flag dans IntentEnvelope si champ critique manquant
- `unknown_source_flag` si source_status = UNKNOWN_SOURCE

---

## 7. Required Future Tests

- `test_fail_closed_on_missing_irreversibility`
- `test_fail_closed_on_conflict`
- `test_fail_closed_on_unknown_source`
- `test_fail_closed_schema_invalid`

---

## 8. Proof Expectation

- `aggregate4_fail_closed` : Lean-proven (Consensus.lean)
- `aggregate4_unanimous` : Lean-proven
- `skew_negative_implies_hold` : Lean-proven (TemporalBridge.lean)

---

## 9. Claim-Scope

**Autorisé :** "Obsidia applique fail-closed — en cas de doute, HOLD ou BLOCK, jamais ALLOW par défaut"
**Interdit :** "Le système choisit ALLOW en cas d'incertitude" — INTERDIT ABSOLU

---

## 10. Example Violation

```python
# VIOLATION — fail-open
def evaluate(intent):
    if intent.irreversibility_level is None:
        return "ALLOW"  # ← VIOLATION : manquant → fail_closed
```

---

## 11. Correct Handling

```python
# CORRECT
def evaluate(intent):
    if intent.irreversibility_level is None:
        return DecisionTicket(
            decision="HOLD",
            reason_codes=["MISSING_IRREVERSIBILITY_LEVEL"],
            x108_gate_status="X108_FAIL_CLOSED"
        )
```
