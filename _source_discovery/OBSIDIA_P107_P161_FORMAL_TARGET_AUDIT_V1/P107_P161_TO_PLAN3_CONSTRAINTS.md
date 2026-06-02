# P107_P161_TO_PLAN3_CONSTRAINTS
# OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1
# Date: 2026-06-02

---

## Statuts entrant dans Plan 3

| Propriété | Statut | Impact Plan 3 |
|-----------|--------|--------------|
| P107 Lyapunov δ-ε | `P107_LEAN_SKELETON_ONLY` | Signal Python advisory — pas d'autorité décisionnelle |
| P161 Calibration énergétique | `P161_LEAN_SKELETON_ONLY` | Signal Python advisory — pas d'autorité décisionnelle |

---

## Ce que Plan 3 PEUT faire avec P107 / P161

```
FUTURE_FORMAL_TARGET
    → Marquer explicitement dans specs/ runtime contracts
    → Exposer comme signal advisory avec label PYTHON_SPEC_NOT_LEAN_PROVEN
    → Intégrer les métriques Python dans les context packets
    → Planifier la formalisation Lean pour Plan 4+

STABILIZATION_TARGET
    → P107 peut alimenter un score de "stabilité perçue" dans le ContextPacket
    → P161 peut alimenter le champ thermo_debt dans GovernedStateVector
    → Les deux influencent HOLD si seuil dépassé (signal Python)

DOC_ONLY_CONSTRAINT
    → Toute référence à P107/P161 dans la documentation Plan 3
      doit porter la mention : "PYTHON_SPEC — NOT Lean-proven"

METRICS_CANDIDATE
    → L_value (Lyapunov) : float — signal candidat pour Plan 3 context packets
    → thermo_debt : float — signal candidat pour Plan 3 governed_state packets
    → partition (X_A/X_B/X_H/X_UNKNOWN) : candidat pour enrichissement X108 context

FORMAL_GAP_MARKER
    → P107 et P161 doivent être marqués FORMAL_PROOF_PENDING dans tout registre Plan 3
    → Gate G1 = PARTIAL (connu et documenté)
```

---

## Ce que Plan 3 NE PEUT PAS faire avec P107 / P161

```
RUNTIME_AUTHORITY
    → P107 et P161 ne peuvent pas décider de l'action
    → L_value=0 ne signifie pas "ACT autorisé" — X108 décide

DECISION_AUTHORITY
    → partition="X_A" ne peut pas déclencher ALLOW
    → partition="X_B" ne peut pas déclencher BLOCK à lui seul
    → thermo_debt > θ ne peut pas déclencher HOLD directement
      (il doit passer par X108_EVALUATED dans le cycle)

PROOF_CLAIM
    → "P107 est prouvé" — INTERDIT
    → "P161 est une loi formelle" — INTERDIT
    → "La stabilité Lyapunov garantit la sécurité" — INTERDIT
    → Préfixer par "Lean 4" tout théorème P107/P161 — INTERDIT

X108_LEVEL_INVARIANT_CLAIM
    → P107/P161 ne sont PAS équivalents à X108_no_act_before_tau
    → P107/P161 ne protègent PAS la gate temporelle
    → P107/P161 ne peuvent PAS remplacer les 28 théorèmes Lean-proven

ACT_HOLD_BLOCK_LOGIC
    → Aucun composant Plan 3 ne peut émettre ALLOW/HOLD/BLOCK
      sur la seule base de L_value ou de thermo_debt
    → Ces métriques sont des signaux d'entrée pour X108

PRODUCTION_SAFETY_GUARANTEE
    → "P107 garantit la sécurité en production" — INTERDIT
    → "P161 certifie la calibration énergétique" — INTERDIT
```

---

## Règles d'usage dans les runtime contracts Plan 3

### Règle 1 — Label obligatoire

Tout champ P107/P161 dans un runtime contract Plan 3 doit porter :

```yaml
lyapunov_L_value:
  type: float
  status: PYTHON_SPEC_NOT_LEAN_PROVEN
  authority: ADVISORY_ONLY
  can_emit_act: false
  can_emit_allow: false
  requires_x108: true

thermo_debt:
  type: float
  status: PYTHON_SPEC_NOT_LEAN_PROVEN
  authority: ADVISORY_ONLY
  influences: HOLD_SIGNAL_ONLY
  requires_x108: true
```

### Règle 2 — Position dans le cycle

P107/P161 alimentent le cycle AVANT X108_EVALUATED :
```
INPUT_CAPTURED
    ↓
PERIPHERY_SCORED  ← P107 L_value + P161 thermo_debt alimentent ici
    ↓
SIGMA_ROUTED
    ↓
X108_EVALUATED    ← seule autorité — KX108_ONLY
```

### Règle 3 — Test Plan 3 requis

Avant tout déploiement Plan 3 utilisant P107/P161 :
- `test_lyapunov_no_act_emission` — vérifier que L_value ne déclenche pas ACT
- `test_thermo_debt_no_block_alone` — vérifier que thermo_debt seul ne déclenche pas BLOCK
- `test_p107_p161_requires_x108` — vérifier que toute action passe par X108_EVALUATED
