# LYAPUNOV_POG_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/math_core/lyapunov.py`
- `periphery/math_core/proof_of_governance.py`
- `periphery/math_core/governance_partition.py`
- `periphery/math_core/__init__.py`
- `periphery/memory_governor.py`

Imported Facts:
- lyapunov.py : calcul de stabilité basé sur delta_E et delta_C — Python uniquement
- proof_of_governance.py : validation Python de conditions de gouvernance
- governance_partition.py : partition de l'espace de gouvernance
- Tous les fichiers dans `periphery/math_core/` : PYTHON_SPEC, pas Lean

What This Source Proves:
- Une spécification Python pour évaluer la stabilité et la gouvernance
- Ces métriques sont intégrées dans le pipeline de décision (entrée pour Gencoin)
- Le concept de ProofOfGovernance existe comme vérification Python

What This Source Does NOT Prove:
- Preuve formelle Lean (FORMAL_PROOF_PENDING pour tous)
- Stabilité mathématique au sens Lyapunov strict
- Convergence garantie

Boundary:
- PYTHON_SPEC — runtime approximation — pas Lean proof

Claim-Scope:
- "Obsidia implémente un scoring de gouvernance en Python" — AUTORISÉ
- "Obsidia a prouvé Lyapunov formellement" — INTERDIT
- "ProofOfGovernance = preuve formelle" — INTERDIT

Specs Depending On This Source:
- 03_ENTROPY_DISCIPLINE/LYAPUNOV_RUNTIME_TO_FORMAL_PROOF_PLAN.md
- 03_ENTROPY_DISCIPLINE/PROOF_OF_GOVERNANCE_LIMITS.md

Runtime Status: PYTHON_SPEC + FORMAL_PROOF_PENDING

Do Not Move Original Source: true
Authority: KX108_ONLY
