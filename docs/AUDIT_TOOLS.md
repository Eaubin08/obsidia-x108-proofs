# Outils d'audit

## Objectif

Ce document explique comment utiliser les outils d'audit du dépôt public P1 d'Obsidia X-108.

Ces outils permettent à un auditeur indépendant de scorer, inspecter et recalculer les résultats de stabilité du kernel sans avoir accès au moteur propriétaire.

## Outils disponibles

### `RECUPE_SCORING/aggregation_stable.py`

**Rôle :** calcule le score agrégé de stabilité du kernel en sommant les résultats de toutes les catégories de preuves.

**Utilisation :**

```bash
python RECUPE_SCORING/aggregation_stable.py
```

**Ce que produit cet outil :**
- Score global agrégé (baseline P1 : 8007)
- Détail par catégorie (Lean, TLC, Python verifiers, Sigma, QA)
- Statut de stabilité du kernel

**Note :** Le compteur 8007 est la ligne de base au freeze P1 (tag `p1-freeze-2026-04-22`). Il peut augmenter sur `main` avec les ajouts P2+.

---

### `RECUPE_SCORING/contracts_stable.py`

**Rôle :** vérifie les contrats d'invariants du kernel. Définit et valide les propriétés qui doivent tenir pour que le kernel soit déclaré stable.

**Utilisation :**

```bash
python RECUPE_SCORING/contracts_stable.py
```

**Ce que produit cet outil :**
- Validation de chaque contrat d'invariant
- Rapport PASS / FAIL par invariant
- Conclusion globale de stabilité

---

## Scénarios d'utilisation types

### Scénario 1 : run d'audit complet

Lancer le runner e2e complet pour valider l'ensemble du périmètre P1 :

```powershell
.\run_all_proofs.ps1
```

Résultat attendu : `=== DONE ===` sur la dernière ligne.

---

### Scénario 2 : vérification Python uniquement

Pour une vérification rapide sans Lean ni TLC :

```bash
python proofs/verify_all.py
python proofs/verify_decision.py
```

Ces scripts n'ont pas de dépendance externe (pas de TSA, pas de Java, pas de Lean) et sont les plus reproductibles.

---

### Scénario 3 : recalcul du score de stabilité

Pour vérifier la ligne de base et l'évolution depuis le freeze P1 :

```bash
python RECUPE_SCORING/aggregation_stable.py
python RECUPE_SCORING/contracts_stable.py
```

Comparaison attendue :
- Sur le tag `p1-freeze-2026-04-22` : score = 8007
- Sur `main` après P2+ : score >= 8007

---

### Scénario 4 : audit orienté Sigma uniquement

```bash
python sigma/run_pipeline.py
python sigma/sigma_monitor.py
python -m pytest sigma/tests/
```

---

### Scénario 5 : vérification QA RFC3161

```bash
python qa/cross-platform/test_rfc3161_anchor_schema.py
python qa/cross-platform/test_rfc3161_cross_platform.py
```

**Attention :** le sondage TSA dépend d'endpoints réseau tiers. Un échec réseau ne remet pas en cause la validité des preuves locales. Voir `docs/LIMITS.md`.

---

## Interprétation des résultats

| Résultat | Signification |
|---|---|
| PASS / VALID | Le périmètre public concerné est valide dans l'environnement testé |
| FAIL sur TSA | Dépendance réseau tiers indisponible, pas une régression du kernel |
| FAIL sur Lean / TLC | À investiguer : vérifier les prérequis (Java 17+, elan, Lake) |
| FAIL sur Python verifiers | Anomalie nette : ces scripts n'ont pas de dépendance externe |
| Score < 8007 sur le tag P1 | Incohérence : recalculer et vérifier l'intégrité du checkout |

## Prérequis

- Python 3.11+
- Java 17+ (pour TLC uniquement)
- Lean 4 + Lake (pour les preuves Lean uniquement)
- `tla2tools.jar` dans `%USERPROFILE%` (Windows) ou chemin configurable
- Connexion réseau (pour les checks TSA uniquement, optionnel)

## Liens utiles

- `docs/PROOF_SCOPE.md` — taxonomie complète des catégories de preuves
- `docs/LIMITS.md` — limites structurelles du périmètre P1
- `docs/REPO_MAP.md` — carte complète du dépôt
- `docs/CI_POLICY.md` — politique CI et jobs bloquants
