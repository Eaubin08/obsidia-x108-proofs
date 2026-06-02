# P107_P161_FORMAL_TARGET_REPORT
# OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1
# Date: 2026-06-02
# Audit: MODE INVARIANT ADDENDUM AUDIT V1

---

## Résumé exécutif

Deux propriétés formelles du kernel Obsidia X-108 — P107 (Stabilité Lyapunov δ-ε) et P161
(Calibration énergétique temporelle) — ont été auditées comme cibles formelles dans le graphe
d'invariants. Les deux présentent un fichier Lean dans `periphery/` mais sans substance
mathématique (squelette trivial par `rfl`). Aucun des deux n'est intégré au lakefile principal.
Les deux sont officiellement classés `DOC_ONLY` dans tous les registres du dépôt.

Ce rapport documente leur statut précis, leur placement dans le graphe d'invariants, leurs
claim-scope autorisés/interdits, et leurs contraintes pour Plan 3.

---

## Statut final P107 — Lyapunov Stability (δ-ε)

```
VERDICT: P107_LEAN_SKELETON_ONLY
```

| Dimension | Valeur |
|-----------|--------|
| Fichier Lean | `periphery/OBSIDIA_V4_STRUCTURED_FULL/08_PREUVES_LEAN_TLA/P107__Stabilite_Lyapunov_delta_epsilon/P107.lean` |
| Contenu Lean | Squelette 19 lignes — structure `Evidence {label, valid}`, théorème trivial `by rfl` |
| Substance mathématique | ABSENTE — aucune modélisation de stabilité Lyapunov δ-ε |
| Dans lakefile principal | NON — hors `proofs/lean/lakefile.lean` |
| `sorry` présent | NON (mais inutile — pas de contenu) |
| Tag dans code | `-- TODO V4: remplacer par preuve complète sans sorry.` |
| Python spec | `periphery/math_core/lyapunov.py` — L(x) = α·ΔE + β·ΔC + γ·V_inst + δ·Δτ + η·I_ctrl |
| Tests Python | AUCUN — PROOF_INDEX.md : "DOC_ONLY (no tests)" |
| Registres officiels | DOC_ONLY : PROOF_INDEX.md, KNOWN_LIMITS.md, RELEASE_NOTES_F77.md, F74_F77_FINALIZATION_AUDIT.md |
| Gate impactée | Gate G1 = PARTIAL (P36/P107/P161 squelettes DOC_ONLY) → bloque G5 |

---

## Statut final P161 — Calibration énergétique temporelle

```
VERDICT: P161_LEAN_SKELETON_ONLY
```

| Dimension | Valeur |
|-----------|--------|
| Fichier Lean | `periphery/OBSIDIA_V4_STRUCTURED_FULL/08_PREUVES_LEAN_TLA/P161__Calibration_energetique_temporelle/P161.lean` |
| Contenu Lean | Squelette structurellement identique à P107 — même `Evidence`, même `gate_ready`, même tautologie `by rfl` |
| Substance mathématique | ABSENTE — aucune modélisation de calibration énergétique |
| Dans lakefile principal | NON — hors `proofs/lean/lakefile.lean` |
| `sorry` présent | NON (mais inutile — pas de contenu) |
| Tag dans code | `-- TODO V4: remplacer par preuve complète sans sorry.` |
| Python spec | `periphery/math_core/governed_state.py` (delta_E, delta_C) + `periphery/energy_thermo.py` (thermo_debt) |
| Tests Python | AUCUN — KNOWN_LIMITS.md : "No tests, no Lean proof" |
| Registres officiels | DOC_ONLY : PROOF_INDEX.md, KNOWN_LIMITS.md, RELEASE_NOTES_F77.md, OBSIDIA_X108_V4_GATE_STATUS.md |
| Gate impactée | Gate G1 = PARTIAL (même condition que P107) → bloque G5 |

---

## Comparaison avec les invariants Lean-proven

Le kernel X-108 compte **28 théorèmes Lean 4 prouvés** couvrant :

| Groupe | Théorèmes | Fichiers |
|--------|-----------|---------|
| Temporal kernel | L5–L9 (X108_no_act_before_tau, etc.) | `TemporalKernel.lean` |
| Determinisme | D1, E2, L3–L4 | `Basic.lean` |
| Immutabilité Merkle/Seal | L13–L17 | `Seal.lean`, `Merkle.lean`, `Sensitivity.lean` |
| Consensus | L18–L21 | `Consensus.lean` |
| Temporal bridge | L22–L23 | `TemporalBridge.lean` |
| Système | L24–L27 | `SystemModel.lean` |
| Crypto axiome | L28 | `CryptoAssumptions.lean` |
| Refinement | L10–L12 | `Refinement.lean` |

**P107 et P161 n'apparaissent dans aucun de ces 28 théorèmes.**

Ils sont dans la catégorie `DOC_ONLY` avec D1 (Tree34), D2 (NPL specs) — périphérie
documentaire, hors périmètre kernel prouvé.

---

## Placement dans le graphe d'invariants

```
KERNEL (28 théorèmes Lean-proven)
  └── Gate G1 (P36 + P107 + P161 Lean sans sorry)
        └── Gate G5 (déploiement)

P107 → Gate G1 → Gate G5
P161 → Gate G1 → Gate G5

Statut actuel de Gate G1 : PARTIAL
  - P36 : squelette DOC_ONLY
  - P107 : squelette DOC_ONLY ← ce rapport
  - P161 : squelette DOC_ONLY ← ce rapport

Impact : Gate G1 et Gate G5 non franchissables avant formalisation Lean complète.
```

P107 et P161 sont des **nœuds périphériques** du graphe d'invariants. Ils ne font pas partie
du noyau déterministe X108 prouvé, mais bloquent le palier de gate G1 requis pour la
qualification formelle complète.

---

## Claim-scope warnings

### P107 — Claims autorisés

- "P107 est une cible de formalisation future (FUTURE_FORMAL_TARGET)"
- "Une spécification Python de la stabilité Lyapunov existe dans `periphery/math_core/lyapunov.py`"
- "P107.lean est un squelette documentaire sans substance mathématique"
- "Le signal Lyapunov L(x) est une approximation Python advisory, label PYTHON_SPEC_NOT_LEAN_PROVEN"
- "Gate G1 est PARTIAL en raison de P107"

### P107 — Claims interdits

- ❌ "P107 est Lean-prouvé"
- ❌ "La stabilité Lyapunov δ-ε est formellement vérifiée"
- ❌ "P107 garantit la sécurité en production"
- ❌ "P107 est équivalent à X108_no_act_before_tau"
- ❌ "P107 peut décider ACT / HOLD / BLOCK"

### P161 — Claims autorisés

- "P161 est une cible de formalisation future (FUTURE_FORMAL_TARGET)"
- "Une approximation Python de la calibration énergétique existe via `governed_state.py` et `energy_thermo.py`"
- "P161.lean est un squelette documentaire sans substance mathématique"
- "Le signal thermo_debt peut influencer un signal HOLD advisory, label PYTHON_SPEC_NOT_LEAN_PROVEN"
- "Gate G1 est PARTIAL en raison de P161"

### P161 — Claims interdits

- ❌ "P161 est Lean-prouvé"
- ❌ "La calibration énergétique temporelle est formellement vérifiée"
- ❌ "P161 constitue une loi formelle de l'espace d'état"
- ❌ "thermo_debt > θ peut déclencher HOLD à lui seul"
- ❌ "P161 est une loi X108-level"

---

## Impact sur Plan 3

Plan 3 (Runtime Contract Skeleton) peut consommer P107 et P161 **uniquement** comme signaux
Python advisory, avec les règles suivantes :

### Autorisé dans Plan 3

```yaml
lyapunov_L_value:
  type: float
  status: PYTHON_SPEC_NOT_LEAN_PROVEN     # label OBLIGATOIRE
  authority: ADVISORY_ONLY
  can_emit_act: false
  can_emit_allow: false
  requires_x108_decision: true

thermo_debt:
  type: float
  status: PYTHON_SPEC_NOT_LEAN_PROVEN     # label OBLIGATOIRE
  authority: ADVISORY_ONLY
  influence: HOLD_SIGNAL_CANDIDATE        # signal seulement — X108 décide
  requires_x108_decision: true
```

### Interdit dans Plan 3

- Utiliser P107/P161 comme **runtime authority** (autorité décisionnelle)
- Générer des events ACT / ALLOW / BLOCK sur base de P107/P161 seuls
- Clamer que P107/P161 sont des invariants X108-level
- Intégrer P107.lean / P161.lean dans le lakefile Plan 3
- Présenter les signaux Python Lyapunov / thermo_debt sans le label `PYTHON_SPEC_NOT_LEAN_PROVEN`

### Chemin de formalisation (Plan 4+)

1. Créer `P107Proofs.lean` avec axiomes : `stability_exists`, `delta_eps_bound`, `lyapunov_convergent`
2. Créer `P161Proofs.lean` avec axiomes : `cost_exists`, `cost_positive`, `calibration_bounded`
3. Compiler sans `sorry` → Gate G1 franchissable
4. Intégrer au `lakefile.lean` principal
5. Relancer `lake build` — Gate G1 → FULL

---

## Recommandation finale

```
P107_P161_AUDIT_READY_FOR_PLAN3

Les deux propriétés sont des cibles formelles légitimes, correctement documentées,
sans preuve Lean substantielle à ce jour.

Plan 3 peut démarrer en traitant P107 et P161 comme :
  - signaux Python advisory avec label PYTHON_SPEC_NOT_LEAN_PROVEN
  - formal gap markers documentés
  - stabilization targets pour Plan 4+

Aucun blocage pour Plan 3. Gate G1 reste PARTIAL jusqu'à Plan 4+.
```
