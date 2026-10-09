# CSSA Lot A — Campagne métier intégrée 12 dossiers / 2 parcours gouvernés

Date : 2026-10-09. Branche : `feat/cssa-v01-active`. **Non gelé, tests Windows en attente**.

## Travaux livrés

- `periphery/cssa_full_lot_a_campaign_v0.py` — revue **du lot entier avant toute mutation**, puis routage sélectif vers le circuit CSSA → native CASE/TASK/FOLLOW-UP → WORLD_ACTION_PRE / KX108 → ticket souverain → sandbox déterministe → receipt/replay ; chaque dossier admissible utilise sa propre racine de test.
- `tests/test_cssa_full_lot_a_campaign_v0.py` — huit tests, dont une campagne de **12 situations synthétiques**, 2 échéances pouvant traverser le circuit gouverné en sandbox (approbations d'opérateur **simulées explicitement**), 9 dossiers bloqués pour incohérence ou données manquantes, 1 dossier HOLD sans approbation. Refus testés aussi sur autorisations de fixture erronées, absence de date canonique et mutation de receipt.

## Contrat de vérité

- Les 12 événements sont **nouvelles fixtures synthétiques**, non 12 événements observés de Sedan.
- Aucune exploitation de la preuve historique F3F 904 événements ni du dossier F3G 11 responsabilités ; éléments en attente de récupération et de couverture.
- Seuls les dossiers de type DEADLINE avec source et base réglementaire déclarées par la fixture, date UTC explicite, aucun conflit relevé dans le lot, et ID d'approbation **test-only** peuvent créer des objets natifs dans un répertoire temporaire isolé.
- Une approbation simulée ne constitue **jamais** une approbation humaine réelle. Aucun effet externe, réseau, e-mail ou calendrier réel.
- Les cas autres que DEADLINE restent HOLD/BLOCK ; aucune autorité d'action n'est accordée à la logique métier CSSA.
- Reçoit un hash de rapport local pour intégrité accidentelle / rejeu du rapport ; **pas une signature authentifiée**.

## Limites de fermeture

Cette campagne lie plusieurs événements CSSA dans une seule préanalyse, mais l'exécution autorisée se déroule indépendamment par sous-racine ; elle ne prouve **pas** la cohérence transactionnelle d'un CRM multi-dossiers partagé, l'arbitrage temps réel, les dépendances inter-événements au-delà des collisions simplifiées, ni le stress historique F3F. La preuve de bout en bout concerne exclusivement les deux dossiers échéance prévus.

Il reste à fermer : mapping des 11 fonctions du manager, données métier saison réelles validées, horaires/fuseaux/budgets et rôles formalisés, F3F/F3G traçables, campagne de charge, décision documentée de déploiement. Ne pas déclarer `LOT_A_FROZEN`.

## Vérification Windows

```powershell
Set-Location (Join-Path $env:TEMP 'cssa-eol-final')
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter 'test_cssa_*.py' -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

Régression précédente validée par l'utilisateur : **144 passed / 1 skipped**. Huit tests viennent d'être ajoutés ; **résultat attendu 152 passed / 1 skipped** sous réserve d'exécution réelle. Ne pas extrapoler à toute la CI X108.

Périmètre inchangé : aucune modification `main`, kernel, Brody, native CRM ou Universal ; uniquement modules, tests et documentation CSSA.
