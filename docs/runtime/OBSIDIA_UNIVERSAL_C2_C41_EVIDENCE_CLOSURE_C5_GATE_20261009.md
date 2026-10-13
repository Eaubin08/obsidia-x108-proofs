# OBSIDIA UNIVERSAL V0.1 — Clôture probatoire C2–C4.1 et entrée C5

Date: 2026-10-09. Branche: `feat/universal-cross-domain-conformance-v0`. Aucun push sur `main`. Trading reste exclu des **nouvelles exécutions inter-dépôts** sur décision utilisateur ; les tests documentaires historiques C4/C4.1 qui mentionnent Trading ne constituent pas une nouvelle validation de Trading.

## Verdict de clôture

**C2–C4.1: TARGETED_OFFLINE_CONTRACT_AND_SANDBOX_REGRESSIONS_PASS — SCOPE_LIMITED.**

Verdict fondé sur les sorties `pytest` fournies par l'opérateur, sans rapport machine horodaté, hashé et joint au dépôt. Il ne s'agit **pas** de `UNIVERSAL_PRODUCTION_PROVEN`, ni de `C42_CROSSREPO_PASS`, ni d'une régression globale verte.

| Lot exécuté localement | Résultat observé | Valeur probatoire |
|---|---:|---|
| C2 + Universal (gouvernance identités/délégations) | 64 PASS / 2.28 s | Fixtures multi-organisations, révocation, nonces, KX108_ONLY |
| C2.42–C2.48 (SQLite, IPC, concurrence, recovery) | 21 PASS / 6.21 s | Garde local, workers IPC et absence de retry après ambiguïté |
| C3 + C4 + C4.1 (sandbox et claims sectoriels) | 64 PASS / 0.94 s | Vraie chaîne GuardX108/WORLD_ACTION_PRE, ticket, receipt/replay *en sandbox sans réseau* + conformité documentaire |
| Universal + C4.2 harness/unit fixtures (lot précédent) | 69 PASS / 0.97 s | Tests de contrat/jointure, **pas** exécution réussie du runner réel à trois dépôts |

Les totaux (149 passages sur les trois lots C2–C4.1) ne sont pas des tests uniques garantis, et les tests n'ont pas été rejoués par une CI issue de ce freeze.

## PROUVÉ DANS LE PÉRIMÈTRE OFFLINE/SANDBOX

1. Enveloppes d'intention communes à plusieurs métiers avec `KX108_ONLY`, aucune usurpation de décision souveraine et aucune sortie externe.
2. Contrôles de scope entreprise/source/domaines ; révocation de liens, délégation et source dans les scénarios tests.
3. Ledger SQLite anti-rejeu et révocation persistante dans les scénarios reproduits ; C2.42 confirme que les protections SQLite *ne constituent pas une isolation complète de processus*.
4. C3 exerce GuardX108 et la chaîne ticket / receipt / replay pour deux organisations, deux domaines, deux providers simulés, avec adaptateurs NO-NETWORK. Ce n'est pas l'autorisation d'une entreprise réelle.
5. C4/C4.1 refusent la promotion de claims sectoriels interdits (GPS attribution causale, CSSA accès interne, Trading live), et montrent les SHAs / limites des snapshots historiques.

## PARTIEL / NON CLOTURÉ

- C4.2 vraie exécution épinglée multi-dépôts: **BLOCKED_FAIL_CLOSED**, car clone Trading déclaré dirty; abandon volontaire de ce parcours, ne pas contourner le garde-fou.
- Les tests C4/C4.1 incluent des assertions *documentaires historiques* sur Trading; ils ne signifient ni des tests moteurs Trading frais ni un green live.
- Évidence machine consolidée, CI dédiée, reproductibilité complète et audit de l'ensemble de la régression: non finalisés.
- Snapshot historique C4.1: 12 756 PASS, **11 FAIL**, 46 SKIP, 207 deselected; `per_test_identity_parity_verified=false`. Ne pas présenter la suite globale comme GREEN.
- L'assertion d'universalité «n'importe quelle organisation» reste hypothèse d'architecture et propriété de portabilité ciblée, **pas validation de tout secteur**.

## NON PROUVÉ / INTERDIT PAR LE LOT

- Identités/délégations authentifiées par des autorités réelles d'entreprises, autorisation d'accès effectif aux sources opérationnelles CSSA.
- Isolation production entre processus/hôtes, garanties distribuées du ledger, sécurité complète d'un transport IPC ou réseau.
- Décisions KX108 réelles hors sandbox autorisant des actes matériels, envois de mails, courtier live, équipement GPS réel, systèmes industriels.
- Consentement réel CSSA, conformité juridique complète, déploiement multi-client, certification défense/aviation.
- Attribution causale d'attaque RF GPS; broker réel, résultat économique.

## C5 — Préparation Monde Obsidia, PAS activation

C5 doit matérialiser le **même socle universel** dans une interface lisible, sans confondre capacités métier et autorité:

- Vues: organisations (tenants), identité/acteurs, rôles/délégations, domaines et adaptateurs, sources, capacités, intentions, décisions KX108, tickets, preuves et receipts.
- Relations obligatoires: `organization_id`, `domain_id`, `source_ref`, `capability_id`, `delegation_generation`, `decision_record_id`, `ticket_hash`, `receipt_id`, plus origine/période/état vérifié.
- Contrôles UI: tenant scoping à chaque lecture; aucun bouton «AGIR» sur preuve synthetic, `KX108_NOT_INVOKED` ou source non autorisée; refus HOLD/BLOCK visibles; source et délégation révoquées représentées comme inactives; origine des preuves affichée.
- API de lecture seule pour le premier C5. C5 n'émet pas de droits, n'invente pas d'autorisations, ne remplace ni KX108 ni les garde-fous d'exécution.
- Le test de succès initial de C5: présenter deux organisations + différents métiers sans mélange de sources/décisions/receipts, pouvoir expliquer pour chaque capacité *qui peut proposer* et *pourquoi personne ne peut exécuter sans le chemin souverain*.

## Décision après ce freeze

**GO préparation C5 READ-ONLY**, pas `GO LIVE`, pas fermeture C4.2, pas merge main. Demander un test de non-régression global différenciant les 11 échecs historiques avant une clôture plus forte.
