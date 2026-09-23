# NO_ACT_FROM_PERIPHERY
# runtime_contracts/boundaries/NO_ACT_FROM_PERIPHERY.md
# Status: CONTRACT_SKELETON_ONLY

---

## 1. Boundary Statement

```
∀ module périphérique m : m ↛ ACT
∀ module périphérique m : m ↛ ALLOW
∀ module périphérique m : m ↛ HOLD
∀ module périphérique m : m ↛ BLOCK
∀ module périphérique m : output(m) ∈ {ContextPacket, PeripheralSignalPacket, IntentEnvelope}
```

Toute périphérie produit uniquement du contexte, des signaux, ou des intentions structurées.
Jamais une décision souveraine.

---

## 2. Applies To

| Module | Statut | Autorisé à émettre |
|--------|--------|-------------------|
| Graphiti | PYTHON_TESTED | ContextPacket readonly uniquement |
| Brody | PYTHON_TESTED | ContextPacket readonly uniquement |
| NPL | SPEC_FUTURE | ContextPacket / NarrativeProvenancePacket advisory |
| External Signals | SPEC_IMPORTED | PeripheralSignalPacket (temporal) |
| Atlas | COPIED_READONLY | ContextPacket (future F06) |
| Cognitive | COPIED_READONLY | ContextPacket advisory (future F07) |
| RSSI Security | COPIED_READONLY | OS3EvidenceTicket / BoundaryContract (future F03) |
| RGPD ISO | COPIED_READONLY | OS3EvidenceTicket / BoundaryContract (future F03/F10) |
| Balance/BUV | RUNTIME_CODE (sandbox) | PeripheralSignalPacket (admissibility_score) |
| GPS | PYTHON_TESTED | PeripheralSignalPacket (proposed_verdict) |
| Gencoin | RUNTIME_CODE | PeripheralSignalPacket (candidate) si X108_ALLOW |
| Agents 52 | SOURCE_CANON | ContextPacket uniquement |
| LLM | ADVISORY | ContextPacket / advisory signal |
| P107 (Lyapunov) | DOC_ONLY | PeripheralSignalPacket (L_value advisory) |
| P161 (calibration) | DOC_ONLY | PeripheralSignalPacket (thermo_debt advisory) |
| Audio/Entropy | SOURCE_PARTIAL | PeripheralSignalPacket (entropy advisory) |

---

## 3. Allowed

- Produire ContextPacket avec `readonly=true`, `advisory_only=true`
- Produire PeripheralSignalPacket avec `emits_act=false`, `emits_allow_hold_block=false`
- Référencer des IntentEnvelopes dans les champs `context_packet_refs`
- Fournir du contexte enrichi à X-108 via ces structures

---

## 4. Forbidden

```
❌ Produire ACT depuis un module périphérique
❌ Produire ALLOW / HOLD / BLOCK depuis un module périphérique
❌ Modifier l'état machine sans DecisionTicket ALLOW
❌ Bypasser le gateway X-108
❌ Prétendre être souverain
❌ Appeler un tool external sans gate X-108
❌ Émettre un verdict final (moral, historique, culturel, de vérité)
```

---

## 5. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| Module émet `emits_act=true` | PLAN3_BACKUP_GUARD_VIOLATION → `fail_closed` |
| Module émet ALLOW/HOLD/BLOCK directement | Reject + `fail_closed` |
| ContextPacket avec `advisory_only=false` | Reject |
| Module bypass X-108 | Detected → BLOCK |
| Source inconnue | `unknown_source_flag=true` → X108 pénalise |

---

## 6. Required Contract Fields

- `emits_act: false` dans ContextPacket, PeripheralSignalPacket, IntentEnvelope
- `advisory_only: true` dans ContextPacket, PeripheralSignalPacket
- `decision_authority: KX108_ONLY` dans tous les packets

---

## 7. Required Future Tests

- `test_no_act_from_sigma` (650+ existants — étendre pattern)
- `test_no_act_from_brody`
- `test_no_act_from_npl`
- `test_no_act_from_external_signals`
- `test_no_act_from_atlas_cognitive_future`

---

## 8. Proof Expectation

- Python tests : pattern existant (tests/sigma/test_f62_*.py, tests/api/test_brody_authority_escalation_no_act.py)
- `Refinement.x108_never_blocks` : invariant Lean-proven garantissant l'extensibilité

---

## 9. Claim-Scope

**Autorisé :**
- "Aucune périphérie ne produit ACT ou ALLOW/HOLD/BLOCK — X-108 seul décide"
- "Les 650+ tests Sigma confirment KX108_ONLY pour les périphéries existantes"

**Interdit :**
- "Les périphéries peuvent décider dans certains cas" — INTERDIT ABSOLU
- "Balance/BUV peut émettre BLOCK" — INTERDIT

---

## 10. Example Violation

```python
# VIOLATION — ne jamais faire
class NPLEngine:
    def evaluate(self, claim):
        if claim.cultural_matrix_score > 0.8:
            return "BLOCK"  # ← VIOLATION : NPL ne peut pas émettre BLOCK
```

---

## 11. Correct Handling

```python
# CORRECT
class NPLEngine:
    def evaluate(self, claim):
        return ContextPacket(
            advisory_only=True,
            emits_act=False,
            emits_verdict=False,
            decision_authority="KX108_ONLY",
            labels=["NPL_ADVISORY_NOT_SOVEREIGN"],
            context_payload={"cultural_matrix_score": claim.cultural_matrix_score}
        )
# → X108 reçoit le ContextPacket et décide
```
