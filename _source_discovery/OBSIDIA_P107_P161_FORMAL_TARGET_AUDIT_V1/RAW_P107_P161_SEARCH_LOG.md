# RAW_P107_P161_SEARCH_LOG
# OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1
# Date: 2026-06-02
# Mode: READ_ONLY — aucune modification

---

## Commandes grep exécutées

| # | Terme | Options | Résultats |
|---|-------|---------|-----------|
| 1 | `P107` | insensible à la casse, récursif | 200+ occurrences |
| 2 | `Lyapunov` | insensible à la casse, récursif | 360+ occurrences |
| 3 | `lyapunov` | insensible à la casse, récursif | inclus dans #2 |
| 4 | `stability` | insensible à la casse, récursif | 500+ occurrences |
| 5 | `stabilité` | insensible à la casse, récursif | 200+ occurrences |
| 6 | `P161` | insensible à la casse, récursif | 452+ occurrences |
| 7 | `energetic calibration` | insensible à la casse, récursif | 2 occurrences |
| 8 | `energetic` | insensible à la casse, récursif | 2 occurrences pertinentes |
| 9 | `thermodynamic` | insensible à la casse, récursif | 1654+ occurrences |
| 10 | `calibration` | insensible à la casse, récursif | 997+ occurrences |
| 11 | `temporal calibration` | insensible à la casse, récursif | 0 occurrences |
| 12 | `cognitive thermodynamics` | insensible à la casse, récursif | 0 occurrences |
| 13 | `sorry` | fichiers .lean uniquement | 0 dans P107.lean, 0 dans P161.lean |
| 14 | `TODO V4` | récursif | 2 occurrences (P107.lean ligne 3, P161.lean ligne 3) |
| 15 | `FORMAL_PROOF_PENDING` | récursif | dans PROOF_INDEX.md, SOURCE_TO_SPEC_MAPPING.md |
| 16 | `DOC_ONLY` | récursif | nombreuses occurrences dans docs/, external_pack/ |
| 17 | `FUTURE_FORMAL_TARGET` | récursif | dans F74_F77_FINALIZATION_AUDIT.md |

---

## Glob patterns exécutés

| # | Pattern | Résultats |
|---|---------|-----------|
| 1 | `**/P107*.lean` | 2 fichiers (P107.lean, copie dans GROUPE_02) |
| 2 | `**/*P107*` | 18 fichiers documentaires |
| 3 | `**/P161*.lean` | 2 fichiers (P161.lean, copie dans GROUPE_02) |
| 4 | `**/*P161*` | 18 fichiers documentaires |
| 5 | `**/*.lean` | 33 fichiers Lean au total dans le dépôt |

---

## Fichiers ouverts et lus

### Fichiers Lean P107

| Fichier | Lignes | Contenu notable |
|---------|--------|-----------------|
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/08_PREUVES_LEAN_TLA/P107__Stabilite_Lyapunov_delta_epsilon/P107.lean` | 19 | Squelette trivial, `by rfl`, `-- TODO V4` |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/14_REGROUPEMENTS_COHERENCE/GROUPE_02__Temps_X_108_Non_contournement/09_PREUVE__P107__Stabilite_Lyapunov_delta_epsilon__P107.lean` | 19 | Copie identique |

### Fichiers Lean P161

| Fichier | Lignes | Contenu notable |
|---------|--------|-----------------|
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/08_PREUVES_LEAN_TLA/P161__Calibration_energetique_temporelle/P161.lean` | 19 | Squelette identique à P107, `by rfl` |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/14_REGROUPEMENTS_COHERENCE/GROUPE_02__Temps_X_108_Non_contournement/09_PREUVE__P161__Calibration_energetique_temporelle__P161.lean` | 19 | Copie identique |

### Sources Python P107

| Fichier | Contenu notable |
|---------|-----------------|
| `periphery/math_core/lyapunov.py` | L(x) = α·ΔE + β·ΔC + γ·V_inst + δ·Δτ + η·I_ctrl — marqué "NOT Lean-proven" |

### Sources Python P161

| Fichier | Contenu notable |
|---------|-----------------|
| `periphery/math_core/governed_state.py` | `delta_E`, `delta_C` (thermo_debt, computational_debt) |
| `periphery/energy_thermo.py` | `thermo_debt > theta_thermo_debt` → recommande HOLD |

### Fichiers d'audit lus

| Fichier | Contenu notable |
|---------|-----------------|
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/INVARIANT_GRAPH_REPORT.md` | Lyapunov/PoG = PYTHON_SPEC, gap critique Plan 3+ |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/FORMAL_GAPS_AND_CLAIM_SCOPE_WARNINGS.md` | Claims autorisés/interdits sur Lyapunov |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX.md` | Ligne 37 : P107 ❌Lean ❌test ✅Python — Ligne 39 : P161 ❌Lean |
| `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` | P107/P161 = DOC_ONLY, risque HIGH |
| `docs/architecture/OBSIDIA_X108_V4_GATE_STATUS.md` | Gate G1 = PARTIAL |
| `docs/architecture/OBSIDIA_X108_V4_CHECKLIST_AUDIT.md` | P161 = ÉCART MAJEUR |
| `external_pack/PROOF_INDEX.md` | "P107 DOC_ONLY (no tests)", "P161 DOC_ONLY (no tests)" |
| `external_pack/KNOWN_LIMITS.md` | P107 et P161 = "No tests, no Lean proof" |
| `external_pack/RELEASE_NOTES_F77.md` | "P107 Lyapunov, P161 Calibration — DOC_ONLY" |

---

## Fichiers absents confirmés

| Fichier recherché | Statut |
|-------------------|--------|
| `proofs/lean/P107.lean` | ABSENT — P107.lean est uniquement dans `periphery/` |
| `proofs/lean/P161.lean` | ABSENT — P161.lean est uniquement dans `periphery/` |
| `proofs/lean/lakefile.lean` (référençant P107) | P107/P161 non importés dans lakefile |
| `proofs/lean/lakefile.lean` (référençant P161) | P107/P161 non importés dans lakefile |
| Tout fichier de test Python dédié à P107 | ABSENT |
| Tout fichier de test Python dédié à P161 | ABSENT |

---

## Occurrences notables par fichier

### P107 — Occurrences dans les registres

| Fichier | Ligne | Contenu |
|---------|-------|---------|
| `external_pack/PROOF_INDEX.md` | 104 | "P107 Lyapunov stability - DOC_ONLY (no tests)" |
| `external_pack/KNOWN_LIMITS.md` | ligne ~38 | "P107 Lyapunov stability | DOC_ONLY | No tests, no Lean proof" |
| `external_pack/RELEASE_NOTES_F77.md` | 49 | "P107 Lyapunov, P161 Calibration | DOC_ONLY - no proof, no tests" |
| `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` | 164 | "P107 Lyapunov stability | DOC_ONLY | NONE | HIGH" |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX.md` | 37 | "P107 | ❌ Lean | ❌ test direct | ✅ Python spec | PRIORITAIRE" |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/INVARIANT_GRAPH_REPORT.md` | 148 | "Lyapunov / PoG | PYTHON_SPEC | FORMAL_PROOF_PENDING" |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/FORMAL_GAPS_AND_CLAIM_SCOPE_WARNINGS.md` | 86 | "Lean proof Lyapunov | HAUTE | FORMAL_PROOF_PENDING" |
| `P107.lean` | 3 | `-- TODO V4: remplacer par preuve complète sans sorry.` |

### P161 — Occurrences dans les registres

| Fichier | Ligne | Contenu |
|---------|-------|---------|
| `external_pack/PROOF_INDEX.md` | 105 | "P161 Calibration energetique - DOC_ONLY (no tests)" |
| `external_pack/KNOWN_LIMITS.md` | ligne ~38 | "P161 Calibration energetique | DOC_ONLY | No tests, no Lean proof" |
| `external_pack/RELEASE_NOTES_F77.md` | 49 | (commun avec P107) |
| `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` | 165 | "P161 Calibration energetique | DOC_ONLY | NONE | HIGH" |
| `docs/architecture/OBSIDIA_X108_V4_GATE_STATUS.md` | 48 | "P161 | Squelette trivial (rfl), marqué TODO V4 | DOC_ONLY" |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX.md` | 39 | "P161 energetic calibration | ❌ | — | — | ✅ | ✅ | docs/ — à localiser" |
| `P161.lean` | 3 | `-- TODO V4: remplacer par preuve complète sans sorry.` |

---

## Erreurs rencontrées

| Erreur | Description | Impact |
|--------|-------------|--------|
| API timeout (session précédente) | Interruption lors de l'écriture du fichier P107_P161_TO_PLAN3_CONSTRAINTS.md | Fichier créé malgré tout (123 lignes) |
| Aucune autre erreur | — | — |

---

## Verdict de périmètre

```
SCOPE CHECK — git status -sb :
  ?? _source_discovery/   ← SEUL répertoire non tracké

Aucun fichier modifié dans :
  proofs/        ✓
  formal/        ✓
  specs/         ✓
  docs/          ✓
  periphery/     ✓
  sigma/         ✓

Aucun commit créé.
Aucun push effectué.
Aucun code patché.
Aucun théorème modifié.
Aucun sorry remplacé.
```

---

## Verdict final de l'audit

```
P107_P161_AUDIT_READY_FOR_PLAN3

P107 = P107_LEAN_SKELETON_ONLY
P161 = P161_LEAN_SKELETON_ONLY

Les deux sont DOC_ONLY dans tous les registres officiels.
Gate G1 = PARTIAL.
Plan 3 peut démarrer avec signaux Python advisory uniquement.
Formalisation Lean = Plan 4+.
```
