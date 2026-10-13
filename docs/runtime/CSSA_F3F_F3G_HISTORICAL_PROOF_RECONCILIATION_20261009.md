# CSSA × Universal — Réconciliation historique F3F / F3G avec Lot A

Date : 2026-10-09. Audit documentaire + GitHub, **pas de nouveau test exécuté, aucun freeze**.

## 1. Correction importante de la matrice précédente

L'analyse initiale « F3G-F : 5 structurelles / 4 partielles / 2 lacunes » est un **instantané intermédiaire**, et **pas** l'état final historique de ce programme. Les archives « Go F3G E Closure » signalent explicitement des fermetures ultérieures : F3G-H (relations institutionnelles), buvette/restauration, contrats, root-cause/récidive, puis le rail Universal. Réouvrir tous ces chantiers comme s'ils n'avaient jamais existé serait une régression méthodologique.

Ces déclarations sont des **preuves documentaires historiques**, pas une preuve automatique de présence ni de fonctionnement des implémentations F3F/F3G sur la branche CSSA active.

## 2. Registre de preuves, certitudes séparées

| ID | Source | Résultat historique rapporté | Vérification dans cet audit | Décision |
|---|---|---|---|---|
| F3F-S | Archive « CSSA Biweekly Review » | Simulation de saison **904 événements** ; stress ressources/affectations/budgets/échéances/personas annoncé | Source conversationnelle retrouvée. Pas de fixture 904 ni reçu de run identifié par chemin et SHA | **HISTORIQUE_DOC / REPLAY_NON_VÉRIFIÉ** |
| F3G-F | Archive « Go F3G E Closure » | 11 missions de l'annonce de manager général ; 5/4/2 au stade initial, **291/291 PASS**, run `37568642321`, branche `feat/f3g-f-cssa-announced-role-coverage-v0`, PR #2 DRAFT, sans merge main | Source conversationnelle retrouvée. Recherche de branche F3G dans `obsidia-x108-proofs` actuellement sans résultat | **RUN_RAPPORTÉ / FICHIER_SOURCE_NON_INDEXÉ** |
| F3G-H | Archive « Go F3G E Closure » | Relations FFF/LGEF/District/Ville/collectivités structurées ; 10 cas institutionnels (2 ALLOW, 3 HOLD, 5 BLOCK), distinction `ACKNOWLEDGED != APPROVED` | Source historique retrouvée ; codes/fixtures non identifiés sur branche active | **FERMETURE_HISTORIQUE_RAPPORTÉE / NON_REJOUÉE** |
| F3G-plus | Archive « Go F3G E Closure » | Contrats, institutions, délégations, buvette/restauration, stock/fournisseurs/shifts/caisse, incidents et prévention récidive décrits comme **structurellement modélisés** | Pas de preuve physique complète rattachée à chaque fonction sur branche actuelle | **NE PAS RECONSTRUIRE AVANT RÉCUPÉRATION** |
| Universal | Branche `feat/obsidia-universal-cross-domain-conformance-v0`, docs runtime | Circuits source, native work, HumanApproval, KX108, ticket, executor, receipt/replay, conformance | Modules retrouvés, blob SHA comparés, tests d'intégration CSSA exécutés par l'utilisateur | **RÉUTILISATION TECHNIQUE VÉRIFIÉE SUR PÉRIMÈTRE CIBLÉ** |
| Lot A | Branche `feat/cssa-v01-active` | Campagne 12 événements, 2 parcours KX108 sandbox, 9 BLOCK, 1 HOLD | **152 passed / 1 skipped / 0 failed** rapporté par exécution Windows de l'utilisateur, 3.83 s | **VALIDÉ SYNTHÉTIQUE CIBLÉ** |

Limites GitHub : recherche de branches `f3f` et `f3g` dans **ce dépôt** : aucune trouvée. Cela ne prouve pas la disparition du travail : anciennes branches peuvent appartenir à une autre instance/repo, à un historique supprimé ou à des PR non présentes dans cette vue. La recherche de code sur la branche `main` n'est pas une fouille fiable des archives F3F/F3G.

## 3. Les 11 responsabilités — table de transfert prudente

L'archive F3G-F confirme le **nombre 11** et les groupes de couverture, mais sa synthèse n'énumère pas 11 identifiants métier complets et canoniques. Les lignes ci-dessous sont des **axes de vérification reconstruits à partir de la description de l'annonce**, et non le manifeste F3G originel.

| Axe métier à relier au manifeste d'origine | Statut F3G historique | Lot A actuel | Poursuite |
|---|---|---|---|
| Administration, licences, déclarations et conformité | Partiel F3G-F, extension ultérieure annoncée | Deadline synthétique avec base réglementaire fixture | Retrouver contrats F3G et réexécuter |
| Contrats et renouvellements | Fermeture ultérieure rapportée | Deadline simple | Retrouver preuve contrat/récurrence |
| Relations FFF/LGEF/District | Fermeture F3G-H rapportée | Aucune source institutionnelle réelle | Vérifier ACK ≠ APPROVED, scope et canal |
| Ville/collectivités | Fermeture F3G-H rapportée | Non observé terrain | Vérifier les compétences et délégations |
| Personnel / bénévoles / délégation | Modélisé historiquement | Absence et délégation non prouvée détectées | Lier états canoniques et preuve de mandat |
| Coordination multi-pôles | Structurelle dès F3G-F | 12 événements avec collisions simplifiées | Rejouer F3F ressources/dépendances |
| Matchday / billetterie | Structurelle dès F3G-F | Pas de circuit billetterie Lot A | Basculer en LOT B sans redévelopper |
| Sécurité / contrôle d'accès | Structurelle dès F3G-F | Contradictions génériques | Rejouer F3G matchday multi-surface |
| Accueil / hospitalités | Structurelle dès F3G-F | Non raccordé | LOT B |
| Buvette, restauration, stocks/fournisseurs | Trou initial F3G-F, **fermée ensuite selon archive** | Non raccordée au nouveau lot | Retrouver l'implémentation existante |
| Processus, responsabilité, root-cause et récidive | Structurel / partiel initial, fermeture ultérieure rapportée | Reçus sandbox et refus, pas de moteur root-cause saison | Retrouver et comparer mécanisme historique |

**La correspondance stricte 1:1 au manifeste officiel des 11 responsabilités reste à prouver** ; cette table n'en tient pas lieu.

## 4. Écart réel à traiter — pas une réimplémentation

Le cœur Universal et la chaîne technique CSSA → CASE/TASK/FOLLOW-UP → KX108 → ticket/executor/receipt/replay sont démontrés pour des échéances **synthétiques**. Les chantiers historiques CSSA supplémentaires sont rapportés fermés, mais leurs fixtures, contrats et reçus ne sont pas encore retrouvés avec identifiants immuables. Ne pas créer une nouvelle « buvette V0 » ou « institution V0 » avant cette recherche.

### Fermeture suivante en un lot

1. Identifier **le dépôt et les PR/commits de F3F/F3G** (y compris branches historiques, PR #2/#3 et preuves F3G-H) avec manifestes et fichiers exacts.
2. Comparer les interfaces de ces artefacts à la branche CSSA actuelle : `SAME / COMPATIBLE / ADAPTER_REQUIRED / MISSING / UNVERIFIED`.
3. Réutiliser sans duplication les scénarios institutionnels F3G-H et la vraie fixture F3F de 904 événements si récupérable ; sans elle, aucun « 904 rejoués ».
4. Fermer une matrice **11 responsabilités × exigences métier × source × test × receipt × état** ; ne pas inférer « couvert » d'un simple PASS global.
5. Poursuivre LOT B matchday/communication sur l'infrastructure existante ; préparer pilote réel CSSA **readonly** séparément avec approbation préalable pour toute connexion.

## 5. Frontières

Pas de merge/push `main`, pas de modification kernel/Universal/Graphiti/Native Memory/Brody ni des autres domaines, pas de vrai Gmail/Calendar/CRM CSSA connecté, `KX108_ONLY`, maintien HOLD/BLOCK, aucune autorisation ni exécution externe réelle. Régression CSSA 152/1 valide la campagne ciblée, **pas** la suite globale X108.

**Verdict : `F3F_F3G_HISTORY_RECONCILED_PARTIALLY — ORIGINAL_PROOF_ARTIFACTS_UNRESOLVED`**. La fausse lacune « buvette pas faite » est corrigée au niveau historique ; couverture actuelle non certifiée tant que les sources originales ne sont pas rattachées.
