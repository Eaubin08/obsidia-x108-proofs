# CSSA × Universal — Réconciliation globale et plan de fermeture par lots

Date : 2026-10-09  
Dépôt : `Eaubin08/obsidia-x108-proofs`  
Branche documentaire : `feat/cssa-v01-active`  
Statut : **AUDIT PARTIEL SOURCÉ / PLAN DE FERMETURE — PAS UN FREEZE MÉTIER**

## 0. Changement de méthode

**Arrêt du cycle micro-patch → quelques tests → freeze.** Une phase n'est close que quand un processus métier cohérent est couvert en bout-en-bout (entrées, rôles, contraintes, exceptions, propositions, autorité, reçus, rejeu et acceptation). Les anciens tests sont conservés comme régression, pas comme substitut à une preuve métier.

Contraintes : lecture seule des anciens chantiers et de l'Universal ; créations CSSA uniquement sur cette branche ; aucune fusion `main`, modification kernel, Brody, Native Memory, Monde, Sigma, ou autre domaine ; aucun compte CSSA connecté ni envoi réel ; `KX108_ONLY`, `HOLD/BLOCK` et refus explicatif.

## 1. Sources croisées et qualité de preuve

1. Historique de projet « CSSA Biweekly Review » : F3F stress organisationnel, **904 événements** simulés, conflits de ressources, responsables absents, échéances, budgets, délégations, priorité et cockpit hebdomadaire/bihebdomadaire/mensuel. C'est une **description historique**, pas une nouvelle exécution vérifiée ici.
2. Historique « Go F3G E Closure » : F3G-F annoncé terminé avec **291/291 PASS** (run `37568642321`), branche citée `feat/f3g-f-cssa-announced-role-coverage-v0`, sans merge `main`; **11 responsabilités** du manager général : 5 structurelles, 4 partielles, 2 lacunes. Preuve historique déclarée à réconcilier avec les artefacts exacts, commits et branches archivées.
3. Historique « Proposer une IA administrative » : analyse de **22 communications reçues** du club, séparant campagnes, opérationnel et transactions ; proposition de **10–15 cas matchday + communication** et neuf objets CSSA. Ce ne sont pas des e-mails internes du secrétariat.
4. Code vérifié par lecture GitHub sur `feat/cssa-v01-active` : `cssa_synthetic_intake_v0`, `cssa_admin_e2e_synthetic_v0`, `cssa_native_crm_candidate_v0`, `cssa_calendar_email_candidates_v0`, `cssa_cross_component_offline_v0`, `cssa_provider_sandbox_v01`, `cssa_sandbox_hardening_v01`, `cssa_local_checkpoint_v02`, `cssa_checkpoint_guard_v02`, `cssa_security_preflight_v03`, `cssa_guarded_sandbox_v03`.
5. L'utilisateur a exécuté une régression ciblée Windows : **123 PASS, 1 SKIPPED, 0 FAILED**, `git status --short` vide. Le cas ignoré porte sur le lien symbolique non disponible localement. Cette régression **ne valide ni Universal, ni le métier complet, ni l'exécution réelle**.
6. Recherche GitHub : branches Universal identifiées : `feat/obsidia-universal-cross-domain-conformance-v0` et `feat/universal-enterprise-stack-adapter-v0`. Leur contenu et leur état de tests ne sont **pas encore qualifiés exhaustivement** par cette passe. La recherche de branches F3F/F3G n'a pas restitué les branches anciennes : **ne pas conclure à leur inexistence ni inventer leur clôture**.

## 2. Matrice de réconciliation — ne pas confondre les niveaux

| Capacité | Héritage historique documenté | Preuve CSSA V0–V0.3 actuelle | Verdict pour une capacité métier terminée |
|---|---|---|---|
| Triage mails / demandes | Modèle campagne vs mail opérationnel vs transaction | Classification par signaux de fixtures, ambiguïtés HOLD | **PARTIEL** : pas de fils réels, pièces jointes interprétées ni source authentifiée |
| CRM et TASKS | Ancien trou `DECISION_EXECUTION` | Enveloppes natives candidates, sans apply ni état persistant | **PARTIEL** : liaison candidate, pas de cycle métier opérationnel |
| Calendrier et réponses | Besoin MAIL/CALENDAR/CRM/TASKS | Brouillons et rappels à date explicite, aucun envoi | **PARTIEL** |
| Résilience | Stress F3F, collisions multisurfaces | Checkpoint local, hash, garde de chemin, verrou exclusif local, pannes injectées | **PARTIEL** : pas de crash brutal, verrou périmé, concurrence distribuée |
| Organisation de saison | F3F mentionne 904 événements, ressources, vues par rôle | Non couvert par la simple régression des 123 cas CSSA | **PREUVE HISTORIQUE À REJOUER / RÉCONCILIER** |
| Matchday complet | 5 responsabilités structurelles déclarées F3G-F | Pas de contrat intégré terrain → communication dans V0–V0.3 | **OUVERT** |
| Administration/réglementaire | 4 responsabilités partielles F3G-F | Classification e-mail non équivalente à licences/FFF/Ligue/collectivités | **OUVERT** |
| Buvette / restauration | Lacune explicite `MATCHDAY_BUVETTE_RESTAURATION` | Pas de fermeture prouvée | **OUVERT** |
| Exécution autorisée | Lacune explicite `DECISION_EXECUTION` | HOLD, sans décision KX108 réelle ni outils externes | **VOLONTAIREMENT NON ACTIVÉ** |
| Universal multi-organisations | Deux branches Universal identifiées | Pas de matrice croisée vérifiée entre domaines au cours de cette passe | **À AUDITER** |

## 3. Inventaire des domaines CSSA à fermer — en gros lots

### LOT A — Gouvernance opérationnelle saison + administration

**Entrées :** calendrier saison, 904 événements historiques (à retrouver), licences, contrats, dossiers fédération/ligue/district/ville, délégations, ressources humaines et matérielles, budgets et contraintes temporelles.

**Un seul parcours de preuve :** `dossier/événement → conflits → priorité → responsable et délégation → décision candidate → HOLD/BLOCK → suivi rôle → rapport → receipt/replay`.

**Acceptation :** exécuter une campagne multi-événements avec collisions véhicules/créneaux/personnes, responsable absent, urgence réglementaire, budget dépassé, sources contradictoires ; montrer les refus motivés, les dépendances, le respect des rôles et la cohérence du reporting. Ne pas réécrire F3F si la campagne historique existe : la retrouver, la caractériser et seulement combler les écarts.

### LOT B — Matchday + billetterie + communication CSSA

**Objet CSSA à garder local avant généralisation :** `MatchEvent`, `VenueConfiguration`, `StandStatus`, `SubscriberAccessRule`, `TicketingStatus`, `MatchdayService`, `AudienceSegment`, `CommunicationCampaign`, `PublicationCandidate`.

**Boucle métier :** `configuration de match → contraintes/contradictions → segments publics → campagnes candidates → revue humaine → HOLD ou blocage → preuve de non-diffusion`.

**Campagne de 12 scénarios :**
1. Annonce correcte d'un match ;
2. horaire non homologué ;
3. changement d'horaire tardif ;
4. tribune fermée annoncée ouverte ;
5. espaces VIP fermés mais offre hospitalité active ;
6. accès abonné par carte contredit par consigne billetterie ;
7. ouverture des portes contradictoire ;
8. parking fermé dans un canal et ouvert dans l'autre ;
9. buvette indisponible alors que campagne la promet ;
10. guichets fermés malgré vente annoncée sur place ;
11. CRM conserve l'ancienne version de la campagne ;
12. manager absent, urgence de communication et délégation incertaine.

**Acceptation :** chaque scénario présente état terrain, écart, audience concernée, règle d'autorité, verdict, justificatif et absence d'envoi effectif ; aucune fausse information ne passe le gate de publication.

### LOT C — Suite de gestion CSSA exhaustive + transposition Universal

**CSSA d'abord :** administration/contrats/conformité, organismes et collectivités, RH/bénévoles/délégations, partenaires/hospitalités, billetterie/abonnements, accueil/sécurité, boutique, buvette/restauration, communication, calendrier, CRM/TASKS et récurrence/root cause.

**Universal ensuite :** conserver uniquement le contrat commun `intake → état du domaine → propositions → politiques/autorités → décision gouvernée → plan d'action sous contrôle → reçu/rejeu`. Garder les règles sportives, objets match, tribunes et abonnements propres au domaine CSSA. Comparer le contrat universel à un second domaine existant **en lecture seule** : aucun patch sur GPS/Défense, Trading ou e-commerce.

**Acceptation :** démontrer un même contrat invariant à travers CSSA et un domaine indépendant, sans contaminer l'architecture ni faire entrer les objets football dans le noyau.

## 4. Ordre de travail unifié (pas de micro-freeze)

| Passage | Livraison attendue | Critère d'arrêt |
|---|---|---|
| A0 — Réconciliation des sources | Catalogue F3F/F3G/Universal par fichier, branche, commit, preuve, statut | Aucune « preuve retrouvée » inventée ; lacunes explicites |
| A1 — Couverture saison/administration | LOT A entier et rapport de collisions par rôles | Toutes les collisions critiques maîtrisées ou explicitement HOLD/BLOCK |
| B1 — Exploitation matchday | LOT B entier, campagne de 12 cas connectés | Aucun envoi non autorisé ni incohérence publiable |
| C1 — Fonctions club restantes | LOT C CSSA, dont buvette et root cause | 11 responsabilités traçables au minimum |
| U1 — Conformité Universal | Matrice d'invariants sur CSSA + un autre domaine, lecture seule | Aucun couplage football au noyau |
| F — Freeze final de jalon | Regroupement preuves, régression, limites, rapports, SHA | Freeze seulement à la fermeture d'une capacité entière |

## 5. Décision immédiate

Ne pas produire de V0.4 sécurité contenant encore quelques tests isolés. **D'abord retrouver et indexer la preuve F3F/F3G/Universal et construire LOT A puis LOT B comme campagnes intégrées.** Les 123 tests courants restent une suite de non-régression utile, mais ne sont pas le KPI de fermeture métier. Maintenir `main`, kernel et les autres domaines hors périmètre.
