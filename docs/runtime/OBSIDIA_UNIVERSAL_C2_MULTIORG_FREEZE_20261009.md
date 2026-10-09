# Universalité V0.1 — Verrou C2 multi-organisations / multi-métiers

**Branche** : `feat/universal-cross-domain-conformance-v0` — ne pas fusionner dans `main` sans revue. Trading suspendu à la demande de l'utilisateur : ce lot ne dépend pas de son clone.

## Point de départ réellement présent dans le code

- `periphery/enterprise_org_stack_lifecycle_v0.py` et `tests/integration/test_v01_c2_organization_stack_lifecycle_v0.py` : scope entreprise, raccordement de sources et révocations de liens.
- `periphery/enterprise_durable_revocation_ledger_v0.py` : stockage SQLite transactionnel, refus des nonces rejoués, révocation persistante ; une vérification positive reste explicitement **sans autorité d'exécution**.
- `tests/integration/test_v01_c218_identity_delegation_chain_fixture_v0.py` : signatures locales Ed25519, identité, délégation et expiration ; une chaîne cohérente ne devient pas une autorisation réelle.
- `tests/integration/test_v01_c221_revocation_concurrency_v0.py` : concurrence et révocation du ledger local.
- `tests/integration/test_v01_c28_approval_ticket_boundary_v0.py` : un ticket local non authentifié ne vaut pas preuve de décision KX108.
- `periphery/universal_cross_domain_conformance_v0.py` : enveloppe d'intention commune, sans appel au noyau ni au connecteur.

## Nouvelle régression

`tests/integration/test_universal_c2_multi_org_authority_regression_v0.py` ajoute les mêmes vérifications C2 pour CSSA, GPS et Industrie sans recoder un système de permissions. Secteurs et capacités ne servent que de données d'entrée. Une organisation B ne peut pas reprendre la délégation de A ; un nonce rejoué est refusé ; la révocation persiste après réouverture de SQLite ; les enveloppes métier conservent `KX108_ONLY`, `NOT_INVOKED` et `real_effect=False`.

**Limite explicite** : tests hors ligne de fixtures. Ce lot ne prouve ni une autorité légale réelle, ni un transport réseau sécurisé, ni une décision KX108 de production. Les trois propriétés (cross-tenant, révocation, expiration) sont vérifiées au niveau de ces contrats et tests existants, non comme garantie universelle de déploiement.

## Commande de validation locale

```powershell
Set-Location (Join-Path $env:TEMP 'obsidia-universal-cross-domain-clean')
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'Pull échoué' }

py -m pytest `
  tests/integration/test_universal_c2_multi_org_authority_regression_v0.py `
  tests/integration/test_v01_c2_organization_stack_lifecycle_v0.py `
  tests/integration/test_v01_c218_identity_delegation_chain_fixture_v0.py `
  tests/integration/test_v01_c221_revocation_concurrency_v0.py `
  tests/integration/test_v01_c28_approval_ticket_boundary_v0.py `
  tests/test_universal_cross_domain_conformance_v0.py `
  -q --tb=short

if ($LASTEXITCODE -ne 0) { throw 'Régression C2 non validée' }
git status --short
```

## Suite après validation

Auditer les frontières `C2.42–C2.48` déjà présentes (stockage SQLite multi-processus, IPC et reprise après commit) et déterminer quelles propriétés sont réellement garanties, lesquelles ne sont que des fixtures. Ne pas faire passer une vérification ledger pour un feu vert KX108. C3/C4 régression globale puis C5 représentation dans Monde Obsidia, uniquement après preuves.
