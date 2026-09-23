# P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY
# runtime_contracts/boundaries/P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY.md
# Status: CONTRACT_SKELETON_ONLY
# Source: specs/03_ENTROPY_DISCIPLINE/P107_LYAPUNOV_FORMALIZATION_TARGET.md
# Source: specs/03_ENTROPY_DISCIPLINE/P161_ENERGETIC_CALIBRATION_FORMALIZATION_TARGET.md

---

## 1. Boundary Statement

```
P107 = FUTURE_FORMAL_TARGET / DOC_ONLY / LEAN_SKELETON_ONLY
P161 = FUTURE_FORMAL_TARGET / DOC_ONLY / LEAN_SKELETON_ONLY

P107 ↛ runtime authority
P107 ↛ Lean-proven claim
P107 ↛ HOLD trigger direct
P107 ↛ BLOCK trigger direct
P107 ↛ production safety guarantee

P161 ↛ runtime authority
P161 ↛ loi formelle prouvée
P161 ↛ HOLD trigger direct
P161 ↛ BLOCK trigger direct
P161 ↛ production safety guarantee

L_value (P107) → signal advisory uniquement (label: PYTHON_SPEC_NOT_LEAN_PROVEN)
thermo_debt (P161) → signal advisory uniquement (label: PYTHON_SPEC_NOT_LEAN_PROVEN)
```

---

## 2. Applies To

- P107 : `periphery/math_core/lyapunov.py` — L(x) = α·ΔE + β·ΔC + γ·V_inst + δ·Δτ + η·I_ctrl
- P161 : `periphery/math_core/governed_state.py` (delta_E, delta_C) + `periphery/energy_thermo.py` (thermo_debt)
- `periphery/.../P107.lean` : squelette trivial `by rfl` — hors lakefile
- `periphery/.../P161.lean` : squelette identique à P107 — hors lakefile

---

## 3. Statut formel

| Propriété | Statut | Gate impactée |
|-----------|--------|--------------|
| P107 Lean proof | LEAN_SKELETON_ONLY / DOC_ONLY | Gate G1 = PARTIAL |
| P161 Lean proof | LEAN_SKELETON_ONLY / DOC_ONLY | Gate G1 = PARTIAL |
| Gate G1 (P36+P107+P161) | PARTIAL | Gate G5 non franchissable |
| Python spec (lyapunov.py) | PYTHON_SPEC_NOT_LEAN_PROVEN | Signal advisory |
| Python spec (energy_thermo.py) | PYTHON_SPEC_NOT_LEAN_PROVEN | Signal advisory |
| P107 dans lakefile | ABSENT | Non compilé par `lake build` |

---

## 4. Allowed

- Utiliser `L_value` comme signal advisory dans ContextPacket/PeripheralSignalPacket avec label `PYTHON_SPEC_NOT_LEAN_PROVEN`
- Utiliser `thermo_debt` comme signal advisory avec label `PYTHON_SPEC_NOT_LEAN_PROVEN`
- "P107/P161 sont des cibles de formalisation Lean Plan 4+"
- "Gate G1 est PARTIAL en raison de P107/P161"
- Référencer P107/P161 comme `FUTURE_FORMAL_TARGET` dans les specs Plan 3

---

## 5. Forbidden

```
❌ "P107 est Lean-prouvé"
❌ "La stabilité Lyapunov est formellement vérifiée"
❌ "P107 garantit la sécurité en production"
❌ "P107 est équivalent à X108_no_act_before_tau"
❌ "thermo_debt > θ déclenche HOLD directement"
❌ "P161 constitue une loi formelle de l'espace d'état"
❌ Intégrer P107.lean / P161.lean dans le lakefile avant preuve complète
❌ Utiliser L_value ou thermo_debt comme autorité décisionnelle
```

---

## 6. Failure Mode

- `L_value` utilisé comme trigger HOLD sans label → `overauthority_flag`
- `thermo_debt > θ` → HOLD direct sans X108 → violation boundary
- P107/P161 présentés comme Lean-proven dans un rapport public → CLAIM_FORBIDDEN

---

## 7. Required Contract Fields

- `label: "PYTHON_SPEC_NOT_LEAN_PROVEN"` obligatoire si signal P107/P161
- `authority: "ADVISORY_ONLY"` sur les champs L_value / thermo_debt
- `source_status: "DOC_ONLY"` ou `"FUTURE_FORMAL_TARGET"` pour P107/P161

---

## 8. Required Future Tests (Plan 4+)

- `test_lyapunov_lean_compiles` — P107Proofs.lean sans sorry
- `test_p161_lean_compiles` — P161Proofs.lean sans sorry
- `test_thermo_debt_no_hold_without_x108`

---

## 9. Proof Expectation

- Plan 4+ : P107Proofs.lean avec `stability_exists`, `delta_eps_bound`, `lyapunov_convergent`
- Plan 4+ : P161Proofs.lean avec `cost_exists`, `cost_positive`, `calibration_bounded`
- Actuellement : Python spec uniquement (PYTHON_SPEC_NOT_LEAN_PROVEN)

---

## 10. Claim-Scope

**Autorisé :** "P107/P161 sont des cibles de formalisation Lean Plan 4+ — signaux advisory Python uniquement"
**Interdit :** Tout claim Lean-proven sur P107/P161 — `CLAIM_FORBIDDEN` jusqu'à Plan 4+

---

## 10. Example Violation

```python
# VIOLATION
if lyapunov_value < 0.05:
    return "ALLOW"  # ← P107 ne peut pas émettre ALLOW
```

---

## 11. Correct Handling

```python
# CORRECT
signal = PeripheralSignalPacket(
    signal_type="LYAPUNOV_ADVISORY",
    metric_name="L_value",
    metric_value=lyapunov_value,
    label="PYTHON_SPEC_NOT_LEAN_PROVEN",
    emits_act=False, emits_allow_hold_block=False
)
# → X108 reçoit L_value comme signal advisory et décide
```
