# PROOF_SCOPE_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `docs/PROOF_SCOPE.md`

Imported Facts:
- 4 catégories de preuves publiques :
  1. Preuves formelles Lean 4 — répertoire `proofs/lean/` — LEAN_PROVEN
  2. Model-checking TLA+ / TLC — répertoire `formal/tla/` — FORMAL_TLA
  3. Vérification exécutable Python — `verify_all.py`, `verify_decision.py` — PYTHON_TEST_ONLY
  4. Couche Sigma minimale publique — sigma/ — SIGMA_PUBLIC
- "PASS" a une signification différente selon la catégorie
- SOURCE_CANON — fichier gelé

What This Source Proves:
- Le périmètre public P1 est défini avec précision
- Les 4 types de preuve sont clairement distingués
- Un PASS Python ≠ preuve formelle Lean

What This Source Does NOT Prove:
- Que toutes les fonctionnalités d'Obsidia sont Lean-prouvées
- Que Python PASS = sécurité formelle

Boundary:
- SOURCE_CANON — NE PAS MODIFIER sans protocole freeze

Claim-Scope:
- "Le périmètre public P1 est défini en 4 catégories de preuve" — AUTORISÉ
- "Tout Obsidia est formellement prouvé" — INTERDIT

Specs Depending On This Source:
- 00_SCOPE_DISCIPLINE/P1_PUBLIC_PROOF_SCOPE_LIMITS.md
- 00_SCOPE_DISCIPLINE/FORMAL_PROOF_VS_RUNTIME_APPROXIMATION.md
- 11_PROOF_REPLAY_OS3/PROOF_READINESS_GATE_SPEC.md

Runtime Status: SOURCE_CANON

Do Not Move Original Source: true
Authority: KX108_ONLY
