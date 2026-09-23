# COGNITIVE_THERMODYNAMICS_METRICS

Status: PYTHON_SPEC
Authority: KX108_ONLY

Source Paths:
- periphery/energy_thermo.py

Source Status: PYTHON_SPEC

Scope: Définir les métriques de thermodynamique cognitive.

Allowed:
- delta_E, delta_C comme signaux Python

Forbidden:
- Ces métriques = physique thermodynamique rigoureuse

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

## DELTA_2026_06_02 — Audit Audio Entropy + NPL

Source: `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/AUDIO_ENTROPY_SOURCE_AUDIT.md`

### Clarifications ajoutées

- `delta_E` et `delta_C` (thermo_debt, computational_debt) issus de `periphery/math_core/governed_state.py`
- Thermodynamique cognitive = métaphore architecturale — NON une loi thermodynamique physique
- Aucun monitoring de "chaleur sémantique" actif — `SEMANTIC_HEAT_MONITORING_SPEC.md` couvre la spec cible

### Métriques candidates (issues de l'audio)

```yaml
delta_E:
  type: float
  status: PYTHON_SPEC_NOT_LEAN_PROVEN
  authority: ADVISORY_ONLY
  label: PYTHON_SPEC_NOT_LEAN_PROVEN

delta_C:
  type: float
  status: PYTHON_SPEC_NOT_LEAN_PROVEN
  authority: ADVISORY_ONLY

semantic_heat_estimate:
  status: SPEC_TARGET — non existant
  spec_cible: SEMANTIC_HEAT_MONITORING_SPEC.md
```

### Claim-scope renforcé

- Forbidden ajouté : "La thermodynamique cognitive est une preuve physique" — INTERDIT
- Forbidden ajouté : "Ces métriques peuvent décider" — INTERDIT
- Allowed confirmé : métriques candidates avec label `PYTHON_SPEC_NOT_LEAN_PROVEN`

### Liens

- `specs/03_ENTROPY_DISCIPLINE/P107_LYAPUNOV_FORMALIZATION_TARGET.md`
- `specs/03_ENTROPY_DISCIPLINE/P161_ENERGETIC_CALIBRATION_FORMALIZATION_TARGET.md`
- `specs/03_ENTROPY_DISCIPLINE/AUDIO_ENTROPY_SOURCE_CONSTRAINTS.md`
