# CSSA — LOT B : LIVRAISON CONSOLIDÉE ET FERMETURE SIMULÉE — PASSES 4 À 6

2026-10-09. Branche `feat/cssa-v01-active`. Préservation de `main`, F3G-J original et Universal partagé.

## Regroupement sans micro-passes

Passe 4 (validée 220 PASS + 1 SKIP) : onze flux stade, sûreté, accès, billetterie, abonnements, accueil, hospitalités, buvette, stocks, fournisseurs, bénévoles, caisse ; moteur F3G-J original. Passe 5 (validée 240 PASS + 1 SKIP) : onze familles supporters, partenaires, communications, messages transactionnels vs demandes internes, aucun envoi. Passe 6 (livrée maintenant) : campagne de cascades croisée A+B, évaluation déterministe et verdict unique.

## Passe 6 — analyse de cascade

`periphery/cssa_cross_lot_ab_closure_pass6_v0.py` reçoit le verdict Lot A, les 11 signaux matchday, les 11 communications, les évaluations originales F3G-J du même match, sept incidents simultanément couverts : report, alerte sécurité, absence bénévole, défaillance fournisseur, dépassement budgétaire, remboursement et collision d'échéance administrative.

Le rapport relie chaque incident à ses flux impactés, vérifie les dépendances, refuse une source F3G-J absente, un lot A incomplet, les flux critiques absents, les notifications non couvertes, les tentatives d'escalade d'autorité. Il ne pousse aucune communication, n'écrit pas en CRM et ne prend aucune décision d'ouverture du stade. Verdict `LOT_B_CLOSED_SIMULATION` ou `LOT_B_BLOCKED`, avec diagnostic SHA-256 (non receipt souverain).

`tests/test_cssa_cross_lot_ab_closure_pass6_v0.py` : six tests sur les vrais objets historiques F3G-J et scénarios de refus de clôture.

## Qualification honnête

Ancien résultat confirmé par utilisateur : 240 PASS, 1 SKIP ; Git propre. Après six nouveaux tests, attente 246 PASS, 1 SKIP **si** les validations réussissent, dépôt CSSA original fourni via `CSSA_HISTORICAL_REPO`. Pas de validation présumée. La chaîne testée est synthétique, pas un véritable match ni un ordre aux services externes. La campagne A+B utilise le verdict synthétique Lot A en entrée et ne relance pas elle-même le moteur 904 événements (ce dernier a été vérifié au passage 3).

## Validation unique du Lot B

```powershell
Set-Location (Join-Path $env:TEMP 'cssa-eol-final')
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter 'test_cssa_*.py' -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

Après acceptation, LOT B est clos uniquement au périmètre simulé. Les passes 7–9 de Lot C seront développées et livrées autant que possible dans **un seul grand lot** plutôt que trois cycles de validations. La passe 10 reste l'audit final du plan initial à dix jalons.