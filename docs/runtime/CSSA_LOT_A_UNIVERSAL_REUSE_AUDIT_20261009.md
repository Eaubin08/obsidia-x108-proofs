# CSSA × Universal — Audit de réutilisation et ouverture du LOT A

Date : 2026-10-09. Branche CSSA seule : `feat/cssa-v01-active`. Ce document corrige la priorité d'intégration sans altérer les artefacts Universal.

## Découverte vérifiée par lecture des branches

Branche `feat/obsidia-universal-cross-domain-conformance-v0` :
- `docs/runtime/OBSIDIA_UNIVERSAL_CROSS_DOMAIN_CONFORMANCE_V0.md` (2026-10-08). Le contrat compose ActionCandidate, capacité provider-neutre, binding, WorldActionRequest, HumanApproval exact, WORLD_ACTION_PRE, KX108, policy, ticket, exécuteur sandbox, receipt et replay. Rapport : 58 tests passés, workflow 37706027327 ; simulation uniquement, global X108 non vert.
- `docs/runtime/ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0.md` (2026-10-07). Digital twin 12 observations → 12 packets → 12 interprétations → 3 bundles CRM/TASKS → 2 ActionCandidates → 2 sandbox executions, 2 receipts/replays, 2 duplicate blocks, réseau = 0. Rapport : 117 tests passés, workflow 37639234164.
- `docs/runtime/UNIVERSAL_ENTERPRISE_STACK_ADAPTER_V0.md` (2026-10-07). Manifest canonique de capacités, intention stable malgré changement provider ; Google-like/Microsoft-like/CalDAV-like simulés et CRM non-calendar. Rapport : 127 tests passés, workflow 37643201046.

Comparaison GitHub `main..feat/obsidia-universal-cross-domain-conformance-v0` : branche en avance (185 commits indiqués), comprenant workflows et artefacts enterprise/native CRM-TASKS/intake/source/capability/conformance. La comparaison `main..feat/universal-enterprise-stack-adapter-v0` indique 180 commits d'avance. Ces chiffres correspondent à l'API de comparaison consultée, **pas** à une certification de contenu complet ni une instruction de fusion.

L'inventaire F3F/F3G ancien reste à lier à des fichiers/SHAs exacts : ses totaux historiques ne sont pas requalifiés par la présente passe.

## Conséquence essentielle

**Le cœur universel et un circuit administratif sandbox jusqu'à l'exécution gouvernée existent déjà sur une branche distincte.** Ne pas ajouter dans CSSA un second moteur de décision, d'approbation, de tickets ou d'exécution. Conserver les 123 tests CSSA V0–V0.3 comme régression de la **préparation** et non preuve de l'exécution intégrée. L'intégration doit se faire par **adaptation CSSA-only**, sans modifier ni cherry-pick aveuglément des composants partagés.

## LOT A — lot métier complet à fermer

1. **Catalogue / mapping en lecture seule** : récupérer les chemins exacts de contrats Universal sur la branche active ainsi que preuves F3F/F3G ; relever champs obligatoires et compatibilités des candidats CSSA.
2. **Adaptateur métier CSSA** : définir DomainState saison/match/dossiers/rôles/échéances, provenance et contraintes ; émettre uniquement le format canonique attendu par Universal, sans attribuer de droit d'action.
3. **Campagne intégrée** : partir de la logique 904 événements historiques si l'artefact est retrouvable et rejouable ; sinon conserver le chiffre en référence historique et créer un jeu de scénarios synthétiques déclaré distinct. Couvrir conflits ressources, absence responsable, échéances, budget, contradiction, doublon et délégation.
4. **Contrat de preuves** : produire pour chaque cas décision attendue, résultats observés, receipts, refus explicatifs, non-envoi et rejeu ; distinguer autorisation KX108 simulée/gouvernée des simples `HOLD` CSSA.
5. **Acceptation unique LOT A** : un parcours métier complet sur une branche de travail CSSA avec tests de régression CSSA + pertinents Universal **sans** modifier Universal, kernel, main ni autres domaines. Un seul freeze du lot après preuve complète.

## LOT B suivant

Raccorder les neuf objets matchday définis dans le plan général et la campagne des douze scénarios ; **ne pas dupliquer** intake/source, CRM/TASKS, provider binding, exécuteur, reçus ou replay Universal.

## Risques et points ouverts

- Les branches Universal avancent séparément ; compatibilité d'import, base Git et API exactes **non encore démontrées** sur `feat/cssa-v01-active`.
- Les reports Universal déclarent eux-mêmes limites : pas de SaaS réel, pas de vraie source opérationnelle CSSA, pas de sémantique métier garantie, pas de CI globalement vert.
- Les F3F/F3G 904 événements / 291 tests cités dans l'historique doivent être rattachés aux artefacts exacts avant toute réutilisation ou conclusion de couverture.
- Aucun accès aux comptes du club, aucune écriture externe, aucun `main` push ni modification des modules non-CSSA.

**Décision :** avant de coder un nouveau moteur, faire l'inventaire précis d'interface Universal puis ouvrir en un seul lot la campagne A. Ne pas dériver en micro-patchs.
