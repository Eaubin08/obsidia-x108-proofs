# CSSA historique ↔ Universal — Matrice d'interfaces, réutilisation sans duplication

Date : 2026-10-09. Références en lecture seule ; aucun code historique importé ni modifié. Sources CSSA : `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-`, branche `feat/f3g-j-cssa-matchday-buvette-restauration-v0`. Cible : `Eaubin08/obsidia-x108-proofs`, `feat/cssa-v01-active`.

## 1. Interfaces originales contrôlées (GitHub fetch_file)

| Surface métier | Code source et SHA du blob | Interface d'entrée réelle | Type de sortie observé |
|---|---|---|---|
| Stress saison F3F | `organizations/cssa/stress/organizational_stress_v0.py` — `bcb42ab1973442867f0df3653f232c944c8e8910` | `assess_stress_scenario_v0(raw, resource_model)`, `assess_catalog_v0(catalog, resource_model)`, `detect_resource_conflicts_v0(items, resource_model)` | `StressAssessmentV0`, `ResourceConflictV0`, `StressItemV0` |
| Contrats/conformité F3G-G | `organizations/cssa/compliance/contract_compliance_v0.py` — `97a1dbd804300927785c23cfd544eff00badaae3` | `assess_contract_v0(raw, *, as_of)`, `assess_compliance_v0(raw, *, as_of)`; variantes `_catalog_v0` | `ContractAssessmentV0`, `ComplianceAssessmentV0` |
| Institutions F3G-H | `organizations/cssa/institutions/institutional_relations_v0.py` — `14a8490f953ddf28c96a5f5363fa7ce6d5f8b6e6` | `assess_institutional_case_v0(raw, *, as_of)`, `assess_institutional_catalog_v0(catalog, *, as_of)` | `InstitutionalAssessmentV0` |
| Root-cause/récidive F3G-I | `organizations/cssa/root_cause/root_cause_recurrence_v0.py` — `72c1dd9883694d2334d9cbf1df1a860930cd4be8` | `assess_root_cause_case_v0(raw, *, as_of)`, `build_recurrence_prevention_receipt_v0(raw, assessment)` | `RootCauseAssessmentV0` et reçu métier |
| Buvette/restauration F3G-J | `organizations/cssa/matchday_food/buvette_restauration_v0.py` — `64288134a553068b12871354e8680d9d17b17b32` | `assess_buvette_case_v0(raw, *, as_of)`, `build_matchday_reconciliation_receipt_v0(raw, assessment)` | `BuvetteAssessmentV0` et reçu métier |
| Onze missions | `organizations/cssa/coverage/announced_manager_role_coverage_v0.json` — `440f00cb98e48c6340eebb045d93f4b5a1fd3627` | `requirements[].id` | Liste canonique de 11 IDs issue d'une annonce publique, **pas** organigramme interne vérifié |

### Les onze IDs canoniques historiques

`ADMINISTRATION_DAILY`, `INSTITUTIONAL_RELATIONS`, `PEOPLE_MANAGEMENT_DELEGATION`, `CROSS_POLE_COORDINATION`, `MATCHDAY_TICKETING`, `MATCHDAY_SECURITY`, `MATCHDAY_WELCOME_HOSPITALITY`, `MATCHDAY_BUVETTE_RESTAURATION`, `WRITTEN_PROCESS_RESPONSIBILITY`, `ROOT_CAUSE_DURABILITY`, `DECISION_EXECUTION`.

## 2. Compatibilité effective des contrats

| Amont historique | Aval Universal existant | Classification | Motif |
|---|---|---|---|
| F3F `StressAssessmentV0` | CSSA Lot A `run_cssa_season_campaign(events)` | **ADAPTER_REQUIRED** | Modèles d'événements, capacités ressources, collision/priorité plus riches dans F3F ; le Lot A actuel ne prouve qu'une détection simplifiée |
| F3G-G/H/I/J `*AssessmentV0` | `build_native_case_task_intake_plan_v0` | **ADAPTER_REQUIRED** | Évaluation métier != dossier canonique ; il faut mapper explicitement verdict, raison, provenance, responsable, échéance. Ne jamais inventer approbations/dates |
| F3G-G/H/I/J et 11-roles | `ActionCandidate` Universal | **HOLD UNTIL MAPPING PROVEN** | L'évaluation métier ne confère aucun droit ni surface d'action. Les objets non-actionnables doivent conserver un statut `NO_ACTION`/HOLD/BLOCK |
| Native CRM CASE/TASK/FOLLOW-UP | `project_native_work_to_action_v0` | **REUSED_AND_TESTED** | Branche active : 152 tests ciblés passés (1 ignoré) sur campagne CSSA synthétique ; les seuls parcours E2E couvrent actuellement des DEADLINE |
| Universal `ActionCandidate` | WORLD_ACTION_PRE/KX108/ticket/executor/receipt/replay | **REUSED_AND_TESTED (SANDBOX)** | Deux échéances CSSA synthétiques ont traversé la chaîne, sans effet externe réel |
| Buvette / contrats / institutions / RCA | Fonction opérationnelle réelle du club | **UNVERIFIED_FIELD** | Le contrat public est distinct des faits internes (autorités, stocks, effectifs, tarifs, pièces et canaux) |

## 3. Interdiction des faux raccords

- `ALLOW` dans une **évaluation métier historique** != autorisation d'appliquer un CASE ou d'émettre une action ; l'autorité décisionnelle reste `KX108_ONLY`.
- Un `*AssessmentV0` ne devient pas un `ActionCandidate` en changeant simplement de nom ; il faut une proposition métier documentée, un target, un scope, une source et l'autorité.
- `build_recurrence_prevention_receipt_v0` et `build_matchday_reconciliation_receipt_v0` sont des reçus **métier**, pas des tickets souverains ou des receipts d'exécution externe.
- Le `as_of: date` historique est un **paramètre de contexte** à fournir explicitement, pas l'heure serveur supposée.
- Les 904 événements F3F sont la fixture de saison historique, pas le lot de 12 événements récents. Aucun rejeu croisé n'a encore été effectué.

## 4. Plan de raccordement inter-dépôts (lot complet)

**Passage R1 — Monter les sources originales en lecture seule.** Établir des SHAs HEAD exacts et conserver les fichiers originaux dans leur repo ; ne pas fusionner `main`, ni copier le noyau métier entier.

**Passage R2 — Définir le contrat d'adaptation CSSA uniquement.** Pour chacun des cinq assessors, mapping explicite `input/provenance/as_of → assessment → typed work proposal/HOLD/BLOCK/NO_ACTION`. Rejeter les champs inconnus critiques, la version ambiguë, les preuves de responsabilité manquantes.

**Passage R3 — Campagne intégrée.** Réexécuter les fixtures d'origine dans un checkout isolé ; connecter les sorties via adaptateur CSSA à l'intake natif et au rail Universal, mais seulement pour les cas ayant une surface d'action démontrée. Vérifier priorités F3F **SAFETY > REGULATORY > DEADLINE**, refus HOLD/BLOCK et aucune diffusion publique ni provider réel.

**Passage R4 — Matrice de fermeture des 11 IDs.** Une ligne par ID officiel avec fichier, SHA, test, décision, reçu, calibration terrain restante. Distinguer `STRUCTURALLY_PROVEN`, `SIMULATED_INTEGRATION_PROVEN`, `FIELD_UNVERIFIED` et `MISSING`. Ne pas faire de freeze de Lot A avant cette preuve.

## 5. Verdict

**Les fonctions métier existent et leurs signatures sont identifiées, mais elles ne sont pas directement plug-compatible avec le pipeline Universal.** Le bon prochain développement est un **adaptateur sémantique CSSA**, pas un second moteur F3F/F3G.

Status: `CROSS_REPO_SIGNATURES_VERIFIED — CSSA_SEMANTIC_ADAPTER_REQUIRED`. Pas de nouveau test dans cette étape documentaire.
