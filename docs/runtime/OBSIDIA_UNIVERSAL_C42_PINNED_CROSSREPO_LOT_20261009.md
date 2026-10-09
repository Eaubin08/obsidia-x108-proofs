# Universal × CSSA × GPS × Trading × Industrie — Lot E2E offline

Date : 2026-10-09. Branche : `feat/universal-cross-domain-conformance-v0`. Aucune fusion dans `main`.

## Composant existant réutilisé

`scripts/v01_c42_local_crossrepo_probe_v0.py` est la référence C4.2 : GPS et Trading sont importés et exécutés en Python depuis des dépôts locaux épinglés, CSSA est lu en lecture seule. Réseau interdit dans les sous-processus; Trading PAPER et fake broker, kernel HTTP mocké. Les repos doivent être propres et aux commits exacts. Les sorties C4.2 passent dans les vérifications C4/C4.1 existantes. Il ne s'agit ni de fonctions de production ni de décisions KX108 réelles.

Pins **du runner préexistant C4.2**, sans mise à jour arbitraire :

| Repo | SHA exact |
|---|---|
| `Eaubin08/obsidia-gps-defense-` | `d1221fce6914274f7b0c445a829739367b0c6abb` |
| `Eaubin08/OBSIDIA_TRADING` | `4c2438d97191ec780369b230e597c711471243ca` |
| `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-` | `a3125ce211e0c55d6608b39396f1f7633dbab72c` |

## Raccord livré

`scripts/run_universal_pinned_crossrepo_v0.py` appelle directement le runner C4.2, vérifie son résultat et l'associe à la même matrice d'intention de `periphery/universal_cross_domain_conformance_v0.py`. Elle ajoute une maintenance industrielle **purement fictive**, sans créer de nouveau runtime machine.

Le rapport contient les SHAs des quatre dépôts, les empreintes de C4.2 et Universal, les HOLD/BLOCK/REVIEW_ONLY ainsi que les limites réelles. Un échec C4.2, un SHA incorrect, un dossier sale ou une montée de privilège refuse la clôture.

**Ne pas confondre** :
- `OFFLINE_PINNED_CROSSREPO_CONTRACT_PASS` = code GPS/Trading exécuté localement dans C4.2, sans effet réel.
- `CONTRACT_SIMULATION_PASS` = normalisation d'intentions sur fixtures.
- `KX108 LIVE ALLOW` / contrôle matériel / courtier en ligne = **non testés et interdits** dans ce lot.

## Exécuter dans une copie de test propre

Les clones externes doivent être disponibles localement **au commit exact** ; ne pas les forcer à changer de branche s'ils contiennent du travail. Dans PowerShell, préparer au préalable trois clones de lecture isolés (par exemple `$env:TEMP\universal-pinned-gps`, `$env:TEMP\universal-pinned-trading`, `$env:TEMP\universal-pinned-cssa`) placés aux SHAs ci-dessus. Ne pas utiliser les dépôts de travail sans vérifier `git status`.

```powershell
Set-Location (Join-Path $env:TEMP 'obsidia-universal-cross-domain-clean')
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'Git pull a échoué' }
py -m pytest tests/test_universal_cross_domain_conformance_v0.py tests/test_universal_pinned_crossrepo_join_v0.py tests/integration/test_v01_c42_local_crossrepo_harness_v0.py -q --tb=short
if ($LASTEXITCODE -ne 0) { throw 'Tests ciblés en échec' }
git status --short
```

Pour le **vrai parcours C4.2** — une fois les trois clones épinglés disponibles :

```powershell
py -m scripts.run_universal_pinned_crossrepo_v0 `
  --gps-root (Join-Path $env:TEMP 'universal-pinned-gps') `
  --trading-root (Join-Path $env:TEMP 'universal-pinned-trading') `
  --cssa-root (Join-Path $env:TEMP 'universal-pinned-cssa') `
  --output (Join-Path $env:TEMP 'obsidia-universal-crossrepo-report.json')
```

**Statut** : implémentation et tests de jointure enregistrés sur GitHub ; exécution ciblée et exécution C4.2 avec les trois clones **à confirmer**. Aucun appel réel au noyau, aucune action réelle ni diffusion réseau.

## Critère de fermeture

La fermeture exige le rapport C4.2 issu des clones réels épinglés et non une fixture rédigée à la main. La vérification d'une décision canonique réellement émise par KX108 est un test distinct à construire en sandbox contrôlée, sans autoriser une exécution externe.
