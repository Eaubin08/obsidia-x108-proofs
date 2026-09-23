# Statut public

## Statut global

P1 FERMÉ

## Références canoniques

- Commit de clôture technique : `bd87e15`
- Commit de gel public : `99e966a`
- Tag de gel officiel : `p1-freeze-2026-04-22`

## Tags de version

| Tag | Signification |
|---|---|
| `p1-freeze-2026-04-22` | Cible canonique d'audit P1 |
| `v1.0.0-stable-kernel` | Release GitHub officielle (vérifiée) — même périmètre que le freeze P1 |
| `v1.0-sovereign-kernel` | Tag supplémentaire de souveraineté — même commit que `v1.0.0-stable-kernel` (`ac2b56a`) |

> `v1.0-sovereign-kernel` et `v1.0.0-stable-kernel` pointent vers le même commit.
> Ils représentent deux dimensions de la même clôture : stabilité technique et souveraineté publique.

## Matrice de vérification

| Domaine | Statut | Signification en P1 |
|---|---|---|
| Preuves formelles Lean 4 | PASS | Le périmètre de preuves formelles publiques compile avec succès |
| Model-checking TLC | PASS | Les runs de model-checking publics se terminent sans violation détectée dans l'ensemble de runs validés |
| `verify_all.py` | PASS | La vérification exécutable publique passe |
| `verify_decision.py` | PASS | Les scénarios canoniques publics valident |
| Couche Sigma minimale publique | PASS | Les points d'entrée, exemples et smoke tests Sigma publics passent |
| Schéma d'ancre RFC3161 | PASS | Les vérifications du schéma d'ancre public passent |
| QA multi-plateforme | PASS | La QA RFC3161 / TLC / Sigma passe dans l'environnement validé |
| Sondage endpoints TSA | PASS | Le sondage QA public est robuste et valide actuellement la joignabilité dans l'environnement validé |
| Runner public | PASS | `run_all_proofs.ps1` se termine de bout en bout |

## Tableau P1 public vs production

> Ce tableau clarifie ce que PASS signifie dans ce dépôt vs ce que cela implique en production.

| Ce qui est PASS en P1 | Ce que cela garantit | Ce que cela ne garantit PAS |
|---|---|---|
| Lean build | Preuves formelles publiques compilent | Moteur propriétaire complet publié |
| TLC no error | Aucune violation dans le modèle public TLA+ | Spécifications de production complètes publiques |
| verify_all.py PASS | Vérificateurs exécutables publics valident | Tous les adaptateurs métier de production |
| Sigma smoke tests PASS | Couche Sigma minimale publique fonctionnelle | Couche Sigma de production complète |
| TSA probing PASS | Joignabilité TSA dans l'env validé | Disponibilité permanente des TSA tiers |
| Runner `=== DONE ===` | Périmètre P1 reproductible localement | Déploiement de production opérationnel |

## Règle d'interprétation

Un PASS dans ce dépôt signifie :

- le périmètre public de vérification P1 est reproductible et fermé

Un PASS dans ce dépôt ne signifie PAS automatiquement :

- une disponibilité complète en production
- la publication du moteur propriétaire complet
- la complétude du déploiement métier complet
- un contrôle souverain sur les fournisseurs TSA externes

## Hors périmètre

Hors périmètre pour P1 :

- disponibilité en production
- publication du moteur propriétaire complet
- systèmes de production final banque / trading / e-commerce
- cockpit opérateur final / surface institutionnelle
- disponibilité permanente des fournisseurs TSA externes

## Discipline de lecture

Utiliser l'ordre suivant :

1. `P1_FREEZE_NOTE.md`
2. `PUBLIC_STATUS.md` (ce fichier)
3. `README.md`
4. `docs/PROOF_SCOPE.md`
5. `docs/SIGMA.md`
6. `docs/RFC3161.md`
7. les scripts et tests effectifs
