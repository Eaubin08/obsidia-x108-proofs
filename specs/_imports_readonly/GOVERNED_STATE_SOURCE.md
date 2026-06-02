# GOVERNED_STATE_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/math_core/governed_state.py`
- `periphery/energy_thermo.py`
- `periphery/gencoin_debt_model.py`

Imported Facts:
- Métriques : thermo_debt, computational_debt, timeline_drift, violence_score, feasibility_score
- governed_state = état d'un objet dans l'espace de gouvernance
- energy_thermo.py : delta_E, delta_C (variations d'énergie et de cohérence)
- gencoin_debt_model.py : total_debt = thermo_debt + computational_debt + timeline_drift

What This Source Proves:
- Spécification Python des métriques d'état gouverné
- La dette totale est calculable à partir de ses composantes
- L'état gouverné est une entrée pour Gencoin et X108

What This Source Does NOT Prove:
- Stabilité Lyapunov prouvée formellement (FORMAL_PROOF_PENDING)
- Que ces métriques correspondent à une notion thermodynamique physique rigoureuse
- Preuve Lean de convergence

Boundary:
- PYTHON_SPEC — runtime approximation

Claim-Scope:
- "Obsidia calcule une dette thermodynamique en Python" — AUTORISÉ
- "Obsidia a prouvé la stabilité Lyapunov formellement" — INTERDIT

Specs Depending On This Source:
- 03_ENTROPY_DISCIPLINE/GOVERNED_STATE_SPACE_SPEC.md
- 03_ENTROPY_DISCIPLINE/THERMODYNAMIC_DEBT_BOUNDARY.md
- 10_VALUE_GENCOIN_JCOIN/VALUE_EMISSION_MODEL.md

Runtime Status: PYTHON_SPEC

Do Not Move Original Source: true
Authority: KX108_ONLY
