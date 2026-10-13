# CSSA — Passe 04/10 : exploitation matchday, construction unifiée

2026-10-09. Branche `feat/cssa-v01-active`. Aucun merge/push main, aucune mutation des moteurs historiques ni d'Universal partagé.

## Acceptation de la passe 3

Validation utilisateur : 212 PASS, 1 SKIP en 104,77 secondes, Git propre. Le verdict de la passe 3 peut être `LOT_A_CLOSED_SIMULATION` pour le périmètre synthétique, sans accréditer un pilote réel.

## Livrable consolidé de la passe 4

`periphery/cssa_matchday_full_pass4_v0.py` regroupe 11 flux : TICKETING, SUBSCRIPTIONS, ACCESS, SAFETY, WELCOME, HOSPITALITY, BUVETTE, STOCK, SUPPLIERS, VOLUNTEERS et CASH. Les entrées sont des signaux structurés explicitement reliés à une référence de match ; leurs propriétaires, sources, preuves, dates, readiness, contradictions et statut d'autorité restent visibles.

Les signaux de sûreté ou d'accès non prêts sont BLOCK; les contradictions sont BLOCK; l'absence de preuve, responsable, réviseur ou autorité reste HOLD. Aucune autorisation d'ouvrir le stade, vendre un billet ou envoyer une communication ne peut découler de ce cockpit. Le rapport est déterministe et doté d'un hash de diagnostic, non d'un reçu d'exécution.

L'ancien moteur `organizations/cssa/matchday_food/buvette_restauration_v0.py` (F3G-J) n'a pas été recopié. Le rapport peut consommer ses vrais `BuvetteAssessmentV0` pour le même `match_ref`, et les passer via l'adaptateur existant dans le constructeur natif CASE/TASK **en revue seulement**. Une divergence de match_ref échoue explicitement.

## Preuves et limites

Tests `tests/test_cssa_matchday_full_pass4_v0.py`: 8 tests ajoutés; 5 principaux et 3 opt-in sur les vraies données F3G-J. Vérification attendue de 16 cas synthétiques, parmi lesquels stock, fournisseurs, équipes, readiness et rapprochement de caisse. Ce n'est pas une certification des systèmes de billetterie, paiement, sécurité ou personnel réels du CSSA.

Baseline confirmée : 212 PASS, 1 SKIP. Si `CSSA_HISTORICAL_REPO` reste configuré, total attendu : **220 PASS, 1 SKIP**, sous réserve de validation. Si non configuré, les tests historiques additionnels seront SKIP.

```powershell
Set-Location (Join-Path $env:TEMP 'cssa-eol-final')
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter 'test_cssa_*.py' -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

## Découpage fidèle du plan dix passes

Passe 4 livre le circuit structurel matchday et les vérifications de non-escalade. Passe 5 couvre les supporters/partenaires et communications. Passe 6 teste la saison croisée A+B et clôt le Lot B si critères satisfaits. Il n'y a aucune passe additionnelle. Aucune opération réelle CSSA n'est autorisée.