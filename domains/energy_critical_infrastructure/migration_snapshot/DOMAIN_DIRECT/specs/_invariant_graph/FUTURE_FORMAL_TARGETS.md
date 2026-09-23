# FUTURE_FORMAL_TARGETS

Status: DOCUMENTATION
Authority: KX108_ONLY
Runtime Status: DOC_ONLY
Date: 2026-06-02

---

## Source

Audits :
- `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/INVARIANT_GRAPH_REPORT.md`
- `_source_discovery/OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1/P107_P161_FORMAL_TARGET_REPORT.md`
- `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/AUDIO_ENTROPY_TO_PLAN3_CONSTRAINTS.md`

---

## Scope

Registre des propriétés NON encore prouvées en Lean, destinées à une formalisation future.
Ces propriétés ne peuvent pas être présentées comme des invariants Lean-proven.

---

## Rappel — Kernel X108 Lean-proven (28 théorèmes)

Le kernel X-108 dispose de **28 théorèmes Lean 4 prouvés** (voir `LEAN_PROVEN_VS_FUTURE_TARGETS_DELTA.md`).
Ces 28 théorèmes sont les seuls invariants formellement vérifiés.
Toute autre propriété est soit PYTHON_SPEC, soit DOC_ONLY, soit FUTURE_FORMAL_TARGET.

---

## Cibles formelles Plan 4+

### P107 — Stabilité Lyapunov (δ-ε)

| Champ | Valeur |
|-------|--------|
| Identifiant | P107 |
| Nom | Stabilité Lyapunov δ-ε |
| Fichier Lean actuel | `periphery/.../P107.lean` (squelette trivial) |
| Statut | LEAN_SKELETON_ONLY / DOC_ONLY |
| Python spec | `periphery/math_core/lyapunov.py` |
| Python testé | NON |
| Gate bloquée | Gate G1 → Gate G5 |
| Plan de formalisation | Plan 4+ |
| Spec | `specs/03_ENTROPY_DISCIPLINE/P107_LYAPUNOV_FORMALIZATION_TARGET.md` |

**Claim autorisé :** "P107 est une cible de formalisation Lean Plan 4+"
**Claim interdit :** "P107 est Lean-prouvé"

---

### P161 — Calibration énergétique temporelle

| Champ | Valeur |
|-------|--------|
| Identifiant | P161 |
| Nom | Calibration énergétique temporelle |
| Fichier Lean actuel | `periphery/.../P161.lean` (squelette trivial, identique à P107) |
| Statut | LEAN_SKELETON_ONLY / DOC_ONLY |
| Python spec | `periphery/math_core/governed_state.py`, `periphery/energy_thermo.py` |
| Python testé | NON |
| Gate bloquée | Gate G1 → Gate G5 |
| Plan de formalisation | Plan 4+ |
| Spec | `specs/03_ENTROPY_DISCIPLINE/P161_ENERGETIC_CALIBRATION_FORMALIZATION_TARGET.md` |

**Claim autorisé :** "P161 est une cible de formalisation Lean Plan 4+"
**Claim interdit :** "P161 est Lean-prouvé" / "P161 constitue une loi formelle"

---

### NPL — Narrative Provenance Layer

| Champ | Valeur |
|-------|--------|
| Identifiant | NPL |
| Nom | Narrative Provenance Layer |
| Statut | SPEC_FUTURE / PYTHON_SPEC_NOT_LEAN_PROVEN |
| Python runtime | NON |
| Plan | Plan 2 specs → Plan 3 tests → Plan 4 éventuelle formalisation |
| Spec maîtresse | `specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_CANONICAL_SPEC.md` |

**Claim autorisé :** "NPL est une couche de contexte readonly en cours de spécification"
**Claim interdit :** "NPL est prouvé" / "NPL décide"

---

### Thermodynamique Cognitive / Entropie

| Champ | Valeur |
|-------|--------|
| Identifiant | THERMO_COGNITIVE |
| Nom | Thermodynamique cognitive / Chaleur sémantique |
| Statut | THEORY_ONLY — aucun runtime |
| Plan | Plan 2 specs → Plan 4 éventuelle formalisation |
| Spec | `specs/03_ENTROPY_DISCIPLINE/AUDIO_ENTROPY_SOURCE_CONSTRAINTS.md` |

**Claim autorisé :** "La thermodynamique cognitive est une métaphore architecturale en cours de formalisation"
**Claim interdit :** "L'entropie cognitive est une loi prouvée"

---

### Gate G1 / Gate G5

| Gate | Condition | Statut actuel |
|------|-----------|--------------|
| Gate G1 | P36 + P107 + P161 Lean sans sorry | PARTIAL — P107/P161 = DOC_ONLY |
| Gate G5 | Gate G1 requis | NON FRANCHISSABLE avant Plan 4+ |

---

## Invariants

- P107 et P161 ∉ 28 théorèmes Lean-proven
- P107 et P161 ∈ cibles formelles Plan 4+
- Gate G1 = PARTIAL jusqu'à formalisation complète
- NPL = SPEC_FUTURE jusqu'à Plan 2 complet
- X-108 kernel = seul socle de 28 théorèmes prouvés

## X108 Boundary

KX108_ONLY — toute décision passe par X-108

## Claim-Scope Notes

Ce fichier est la référence pour les claims sur les propriétés non encore formalisées.
Mettre à jour quand un FUTURE_FORMAL_TARGET devient LEAN_PROVEN.
