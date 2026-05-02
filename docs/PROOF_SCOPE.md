# Proof Scope

## Objectif

Ce document définit comment lire le périmètre public de preuves de `obsidia-x108-proofs` après le freeze P1.

## Règle fondamentale

Tous les résultats PASS ne décrivent pas le même type d'objet.

Le périmètre public P1 contient plusieurs catégories qui doivent être lues séparément.

## Catégories canoniques

### 1. Preuves formelles Lean 4

Il s'agit de preuves formelles vérifiées par machine à l'intérieur du périmètre Lean public.

- Répertoire : `proofs/lean/`
- Outil : Lean 4 + Lake
- Ce que PASS signifie : le périmètre de preuves formelles publiques compile et vérifie sans erreur

### 2. Model-checking TLA+ / TLC

Il s'agit de runs de model-checking borné sur les spécifications TLA+ publiques.

- Répertoire : `formal/tla/`
- Outil : TLC via `tla2tools.jar` (Java 17+)
- Ce que PASS signifie : aucune violation détectée dans l'ensemble de runs validés

### 3. Vérification exécutable Python

Il s'agit de scripts de vérification publics tels que :

- `verify_all.py`
- `verify_decision.py`
- Répertoire : `proofs/`
- Ce que PASS signifie : les scénarios canoniques publics valident

### 4. Couche Sigma minimale publique

Il s'agit des points d'entrée Sigma publics, des exemples et des smoke tests.

- Répertoires : `sigma/run_pipeline.py`, `sigma/sigma_monitor.py`, `sigma/examples/`, `sigma/tests/`
- Ce que PASS signifie : les smoke tests et la structure publique Sigma passent

### 5. QA et sondage réseau

Il s'agit de vérifications QA publiques telles que :

- Vérification du schéma d'ancre RFC3161 (`qa/cross-platform/test_rfc3161_anchor_schema.py`)
- QA multi-plateforme (`qa/cross-platform/test_rfc3161_cross_platform.py`)
- Sondage des endpoints TSA
- Ce que PASS signifie : le QA public passe dans l'environnement validé (pas de garantie de disponibilité permanente des TSA tiers)

## Décomposition du compteur de stabilité kernel

Le commit `feat: stabilize kernel at 8007 proofs` correspond au score agrégé calculé par `RECUPE_SCORING/aggregation_stable.py`.

Ce compteur couvre l'ensemble des cinq catégories ci-dessus. Pour recalculer localement :

```
python RECUPE_SCORING/aggregation_stable.py
```

Lecture recommandée :

- `RECUPE_SCORING/aggregation_stable.py` — calcul du score agrégé
- `RECUPE_SCORING/contracts_stable.py` — contrats d'invariants du kernel
- `docs/AUDIT_TOOLS.md` — guide d'utilisation des outils d'audit

> Note : le compteur 8007 est une ligne de base de stabilité, pas un absolu.
> Il peut augmenter sur `main` au fil des ajouts P2+.
> La cible d'audit P1 reste le tag `p1-freeze-2026-04-22`.

## Ce qu'est le repo public

Ce repo est :

- une couche publique de preuves
- une couche publique de vérification
- une couche publique d'exécution pour P1

## Ce que n'est pas le repo public

Ce repo n'est pas :

- le moteur propriétaire de production complet
- la couche Sigma de production complète
- le cockpit opérateur final
- une affirmation que tous les adaptateurs métier de production sont publiés ici

## Hiérarchie d'interprétation

En cas de doute, lire dans cet ordre :

1. `P1_FREEZE_NOTE.md`
2. `PUBLIC_STATUS.md`
3. `README.md`
4. ce fichier
5. `docs/AUDIT_TOOLS.md`
6. les scripts et tests effectifs

## Affirmation publique autorisée

L'affirmation publique autorisée est :

Le périmètre public de preuves / vérification / exécution P1 d'Obsidia X-108 est fermé, reproductible et publiquement gelé.

## Sur-affirmation publique interdite

Les sur-affirmations suivantes sont à éviter :

- "le moteur de production complet est public"
- "tous les adaptateurs métier de production sont publics"
- "la disponibilité des TSA externes est garantie"
- "P1 équivaut au déploiement final en production"
