# Politique CI/CD

## Objectif

Ce document décrit la politique de CI/CD du dépôt `obsidia-x108-proofs`.
Il explique quels jobs sont bloquants, lesquels ne le sont pas, et pourquoi.

## Workflow principal

Fichier : `.github/workflows/verify-proofs.yml`

Déclenchement : push et pull request vers `main`.

## Jobs et politique de blocage

| Job | Bloquant | Raison |
|---|---|---|
| `verify-python-strict` | OUI | Pas de dépendance externe. Un échec = vraie régression du kernel. |
| `verify-lean` | NON | Installation elan/Lake peut échouer en CI selon l'environnement. |
| `verify-sigma-and-qa` | NON | Tests Sigma et RFC3161 dépendent de services tiers (TSA). |
| `verify-tla` | NON | Téléchargement de `tla2tools.jar` peut échouer selon le réseau. |

## Job bloquant : `verify-python-strict`

Ce job est le seul job bloquant. Il couvre :

- `proofs/verify_all.py` — vérificateur général public
- `proofs/verify_decision.py` — validation des scénarios canoniques
- `RECUPE_SCORING/aggregation_stable.py` — calcul du score de stabilité (si présent)

Pourquoi il est bloquant :
- Ces scripts n'ont aucune dépendance réseau ni dépendance de runtime spéciale.
- Un échec sur ces scripts indique une régression réelle dans le périmètre public de preuves.
- Tout commit qui fait échouer ce job ne doit pas être mergé sur `main`.

## Jobs non bloquants

### `verify-lean`

- `continue-on-error: true` sur le build Lean.
- Raison : l'installation de `elan` et `lake` peut prendre du temps ou échouer en CI selon la version disponible ou la bande passante.
- Un échec ne remet pas en cause la validité des preuves si elles passent localement.
- Ce job DOIT passer dans un environnement local avec Lean 4 + Lake installés.

### `verify-sigma-and-qa`

- `continue-on-error: true` sur les tests Sigma et les checks RFC3161.
- Raison :
  - Les smoke tests Sigma dépendent de la structure locale Sigma (correcte en local, pas toujours en CI).
  - Les checks RFC3161 sondent des endpoints TSA tiers dont la disponibilité n'est pas garantie.
- Un échec TSA ne signifie pas une régression du kernel.

### `verify-tla`

- `continue-on-error: true` sur le run TLC.
- Raison : le téléchargement de `tla2tools.jar` dépend du réseau GitHub Releases.
- Ce job DOIT passer dans un environnement local avec Java 17+ et `tla2tools.jar` disponibles.

## Règle d'acceptation d'une PR vers `main`

Une PR est acceptable si :

1. Le job `verify-python-strict` passe (OBLIGATOIRE).
2. Les jobs non bloquants peuvent être jaunes sans bloquer le merge, mais doivent être investigués si la cause est inhabituelle.

## Cible d'audit P1

La cible d'audit canonique P1 est le tag `p1-freeze-2026-04-22`, pas `main`.

`main` peut avoir des jobs CI jaunes dus aux dépendances extérieures sans que cela invalide le périmètre P1 gelé.

Pour reproduire le périmètre P1 en local : `.\\run_all_proofs.ps1`

## Liens utiles

- `docs/AUDIT_TOOLS.md` — guide des outils d'audit
- `docs/LIMITS.md` — limites structurelles (TSA, Lean, TLA)
- `docs/PROOF_SCOPE.md` — taxonomie des catégories de preuves
