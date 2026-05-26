# Carte du dépôt (Repo Map)

## Objectif

Ce fichier aide un lecteur externe à naviguer dans le dépôt public P1.

## Facade racine

- `README.md` — page d'accueil du dépôt public
- `docs/status/PUBLIC_STATUS.md` — matrice publique PASS / périmètre
- `docs/status/P1_FREEZE_NOTE.md` — référence de gel P1

## Périmètre de preuves public

- `proofs/lean/` — périmètre de preuves formelles Lean 4
- `formal/tla/` — spécifications TLA+ et runs TLC
- `proofs/` — vérificateurs exécutables publics et rapport de preuves public

## Périmètre Sigma public

- `sigma/run_pipeline.py` — entrée du pipeline Sigma public
- `sigma/sigma_monitor.py` — entrée du moniteur Sigma public
- `sigma/examples/` — exemples d'entrées publics
- `sigma/tests/` — smoke tests et tests de structure Sigma publics

## Périmètre QA public

- `qa/cross-platform/test_rfc3161_cross_platform.py` — QA publique RFC3161 / TLC / Sigma multi-plateforme
- `qa/cross-platform/test_rfc3161_anchor_schema.py` — vérifications publiques du schéma d'ancre RFC3161

## Périmètre outils d'audit (RECUPE_SCORING)

> Ajouté dans le commit `feat: stabilize kernel at 8007 proofs and deploy audit tools`

- `RECUPE_SCORING/aggregation_stable.py` — calcul du score agrégé de stabilité kernel
  - Agrège les résultats de toutes les catégories (Lean, TLC, Python, Sigma, QA)
  - Produit le compteur de stabilité (baseline : 8007 au freeze P1)
  - Commande de recalcul : `python RECUPE_SCORING/aggregation_stable.py`
- `RECUPE_SCORING/contracts_stable.py` — contrats d'invariants du kernel
  - Définit les invariants qui doivent tenir pour que le kernel soit déclaré stable
  - Utilisé pour valider la cohérence des preuves lors des mises à jour

Voir aussi : `docs/AUDIT_TOOLS.md` pour le guide d'utilisation.

## Périmètre de documentation

- `docs/SIGMA.md` — périmètre Sigma public P1 vs production
- `docs/LIMITS.md` — limites structurelles de P1
- `docs/PROOF_SCOPE.md` — taxonomie du scope de preuves
- `docs/RFC3161.md` — guide d'interprétation RFC3161
- `docs/REPO_MAP.md` — ce fichier
- `docs/AUDIT_TOOLS.md` — guide d'utilisation des outils d'audit
- `docs/CI_POLICY.md` — politique CI/CD et jobs bloquants vs non-bloquants
- `docs/P2_ROADMAP.md` — trajectoire P2-bank et suite (stub)

## Points d'entrée clés

| Point d'entrée | Rôle |
|---|---|
| `README.md` | Landing page auditeur |
| `docs/status/PUBLIC_STATUS.md` | Matrice de statut P1 |
| `run_all_proofs.ps1` | Runner e2e public |
| `sigma/run_pipeline.py` | Entrée Sigma publique |
| `proofs/verify_all.py` | Vérificateur Python principal |
| `RECUPE_SCORING/aggregation_stable.py` | Score agrégé de stabilité |

## Chemins de lecture recommandés

**Lecteur rapide :**
1. `docs/status/PUBLIC_STATUS.md`
2. `docs/status/P1_FREEZE_NOTE.md`
3. `README.md`

**Chemin auditeur :**
1. `docs/status/PUBLIC_STATUS.md`
2. `docs/PROOF_SCOPE.md`
3. `docs/REPO_MAP.md` (ce fichier)
4. `docs/AUDIT_TOOLS.md`
5. `run_all_proofs.ps1`

**Chemin orienté Sigma :**
1. `docs/SIGMA.md`
2. `sigma/run_pipeline.py`
3. `sigma/sigma_monitor.py`
4. `sigma/tests/`

**Chemin orienté RFC3161 :**
1. `docs/RFC3161.md`
2. `qa/cross-platform/test_rfc3161_cross_platform.py`
3. `qa/cross-platform/test_rfc3161_anchor_schema.py`

**Chemin orienté outils d'audit :**
1. `docs/AUDIT_TOOLS.md`
2. `RECUPE_SCORING/aggregation_stable.py`
3. `RECUPE_SCORING/contracts_stable.py`
