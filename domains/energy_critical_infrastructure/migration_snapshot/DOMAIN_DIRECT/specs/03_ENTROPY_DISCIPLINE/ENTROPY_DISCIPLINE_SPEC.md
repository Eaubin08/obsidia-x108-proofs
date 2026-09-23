# ENTROPY_DISCIPLINE_SPEC

Status: PYTHON_SPEC
Authority: KX108_ONLY

Source Paths:
- `periphery/math_core/governed_state.py`
- `periphery/energy_thermo.py`
- `periphery/gencoin_debt_model.py`
- `periphery/math_core/lyapunov.py`

Source Status: PYTHON_SPEC + FORMAL_PROOF_PENDING

Scope: Définir les métriques d'entropie et leur rôle dans la gouvernance Obsidia.

Allowed:
- "Obsidia calcule thermo_debt, computational_debt, timeline_drift, violence_score, feasibility_score en Python"
- "Ces métriques sont des signaux — entrées pour X108, pas des décisions"

Forbidden:
- "Les métriques d'entropie prouvent la stabilité formellement"
- "thermo_debt = température physique"
- "ces métriques = Lean-prouvées"

Inputs: État du système (scores périphériques)
Outputs: Métriques d'entropie → contexte X108

Metrics:
- thermo_debt ∈ [0,∞) — dette thermodynamique
- computational_debt ∈ [0,∞) — dette computationnelle
- timeline_drift ∈ [0,1] — dérive temporelle
- violence_score ∈ [0,1] — risque de violence de transition
- feasibility_score ∈ [0,1] — faisabilité estimée

Invariants:
- total_debt = thermo_debt + computational_debt + timeline_drift
- Toutes les métriques = Python runtime — FORMAL_PROOF_PENDING

X108 Boundary: Ces métriques alimentent X108 — KX108 décide

Tests Required: test_entropy_metrics_range
Proof Expected: FORMAL_PROOF_PENDING (Lean pour Plan 3+)
Runtime Status: PYTHON_SPEC

Claim-Scope Notes:
"Lyapunov Python spec ≠ Lean proof" — ne jamais présenter ces métriques comme formellement prouvées.

Open Questions: Plan de formalisation Lean de math_core/ ?
