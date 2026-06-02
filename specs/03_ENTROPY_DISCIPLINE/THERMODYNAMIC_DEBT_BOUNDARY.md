# THERMODYNAMIC_DEBT_BOUNDARY

Status: PYTHON_SPEC
Authority: KX108_ONLY

Source Paths:
- periphery/gencoin_debt_model.py

Source Status: PYTHON_SPEC

Scope: Frontière de la dette thermodynamique.

Allowed:
- total_debt = signal d'alerte

Forbidden:
- La dette = certitude d'échec

Inputs: Sources domain
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: PYTHON_SPEC
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/ pour limites publiques
Open Questions: À préciser en Plan 3

---

## DELTA_2026_06_02 — Audit P107/P161 + Audio Entropy

Source: `_source_discovery/OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1/P161_ENERGETIC_CALIBRATION_STATUS.md`

### Clarifications ajoutées

- `total_debt` et `thermo_debt` proviennent de `periphery/energy_thermo.py` et `periphery/math_core/governed_state.py`
- Ces signaux sont `PYTHON_SPEC_NOT_LEAN_PROVEN` — aucune preuve Lean formelle
- P161 (Calibration énergétique) = DOC_ONLY / LEAN_SKELETON_ONLY — voir `P161_ENERGETIC_CALIBRATION_FORMALIZATION_TARGET.md`

### Claim-scope renforcé

- Forbidden ajouté : "La dette thermodynamique prouve un état d'échec" — INTERDIT
- Forbidden ajouté : "thermo_debt déclenche HOLD directement" — INTERDIT (seul X-108 décide)
- Allowed confirmé : `thermo_debt` comme signal advisory avec label `PYTHON_SPEC_NOT_LEAN_PROVEN`

### Lien P161

Spec complète : `specs/03_ENTROPY_DISCIPLINE/P161_ENERGETIC_CALIBRATION_FORMALIZATION_TARGET.md`
Audit source : `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/AUDIO_ENTROPY_SOURCE_AUDIT.md`
