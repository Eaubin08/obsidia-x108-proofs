# OBSIDIA — CROSS-DOMAIN UNIVERSAL CONFORMANCE V0

Date: 2026-10-09. Branch: `feat/universal-cross-domain-conformance-v0`, parent `feat/cssa-v01-active`. **No main merge; CSSA freeze intact**.

## Mission

Confronter **CSSA / GPS-Défense-Aviation / Trading / Industrie-maintenance** au même contrat d'intention. Ne reconstruire ni UDIP, ni KX108, ni WORLD_ACTION, ni les domaines historiques. L'industrie est un nouveau jumeau numérique synthétique.

**Ce lot est une première livraison de conformité des adaptateurs sur fixtures, pas encore le passage des vrais moteurs GPS/Trading dans un runner inter-dépôts.** On interdit explicitement d'appeler `CONFORMANCE_FULLY_PROVEN` une campagne sans ce dernier test.

## Raccord des quatre domaines

| Domaine | Entrée spécifique | Capacité normalisée | Risque | Verdict local sain |
|---|---|---|---|---|
| CSSA | organisation / dossier / autorité | TASK.CREATE | NORMAL | REVIEW_ONLY |
| GPS/Défense | récepteur / signal / évidence RF | DEVICE.CONTROL.PROPOSE | CRITICAL | HOLD |
| Trading | portefeuille / ordre / limite risque | ORDER.PAPER.PROPOSE | HIGH | HOLD |
| Industrie | machine / mesure / procédure maintenance | MAINTENANCE.TASK.PROPOSE | HIGH | REVIEW_ONLY |

Des entrées contradictoires sont BLOCK, des inconnues ou lacunes sont HOLD. `REVIEW_ONLY` ne veut **jamais** dire KX108 ALLOW. Le composant prépare des enveloppes, une empreinte d'intention stable et la matrice de risques, mais ne simule pas un record KX108 souverain.

### Audit du patrimoine existant

- CSSA : fin des dix passes, 281 PASS/1 skip sur `feat/cssa-v01-active` commit `234ad83`, sous-périmètre simulé, vérifié par le PC de l'utilisateur.
- GPS : dépôt `Eaubin08/obsidia-gps-defense-`, branche de référence historique `feat/c41-gps-kernel-response-and-claim-boundary-v0`. Évidences GNSS / RF et frontières du récepteur à confronter; **pas de LIVE validé par ce nouveau lot**.
- Trading : dépôt `Eaubin08/OBSIDIA_TRADING`, branche de référence historique `test/c41-v01-paper-proof-convergence-v0`; PAPER only.
- Universal V0.1 : runner inter-dépôts C4.2.1 historique, 4 dépôts, contrat offline PASS ; ce nouveau lot n'a pas relancé ce runner et n'hérite pas automatiquement de son statut.

Sources de comparaison : `docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md` et contrats `periphery/native_ops/` de l'upstream. Les preuves existantes restent indépendantes ; aucun chiffre de suite de tests n'est additionné artificiellement.

## Livrables techniques

- `periphery/universal_cross_domain_conformance_v0.py` : 4 règles de traduction, contrat commun, provenance, contraintes, empreinte, fail-closed.
- `tests/test_universal_cross_domain_conformance_v0.py` : matrice structurée de tests déterministes, variations d'identité multi-organisation, falsification des faits et refus de LIVE.

## Critères pour une fermeture réellement inter-domaines

1. Tests locaux de ce lot verts et travail Git propre ;
2. Réutiliser sans modification les adapters UDIP de GPS et Trading issus de leurs branches épinglées ;
3. Runner multi-repos réellement exécuté sur les branches/HEAD épinglés : contrôler la provenance et les sorties de chaque moteur original ;
4. Le même pipeline KX108 canonique, non simulé, reçoit les propositions issues de chaque domaine ; ne pas supposer les mêmes verdicts ;
5. Matrice adversariale croisée : données contradictoires, provenance perdue, compte/organisation changé, délégation révoquée, délai dépassé, provider absent ;
6. Aucun ordre réel, commande de dispositif, e-mail, paiement ou action industrielle réelle ; replay et reçus authentiques uniquement quand le vrai rail sandbox les produit ;
7. CI globale et régressions historiques distinctes, y compris les échecs préexistants.

## Validation locale du lot de conformité

```powershell
$repo = Join-Path $env:TEMP 'obsidia-universal-cross-domain-v0'
git clone --single-branch --branch feat/universal-cross-domain-conformance-v0 https://github.com/Eaubin08/obsidia-x108-proofs.git $repo
Set-Location $repo
py -m pytest tests/test_universal_cross_domain_conformance_v0.py -q --tb=short
git status --short
```

Ce parcours clone une copie indépendante, **sans modifier la branche CSSA figée**. Résultat des tests ajouté sur GitHub : **à confirmer par exécution**, non présumé.

## Décision

`CONTRACT_SIMULATION_IMPLEMENTED / CROSS_REPO_E2E_PENDING`. Première couche pertinente pour l'universalité, mais pas une preuve d'exécution multi-domaines complète et encore moins de terrain réel.
