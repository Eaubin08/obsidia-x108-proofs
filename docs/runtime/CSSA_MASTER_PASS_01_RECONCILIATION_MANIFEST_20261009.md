# CSSA × Obsidia Universal — PASSE 01 : Manifeste de réconciliation et verrouillage des contrats

Date : 2026-10-09. **Périmètre : audit READ_ONLY des sources, écriture documentaire uniquement sur `feat/cssa-v01-active`.** Ce manifeste constitue le référentiel de la passe 2, pas une preuve de déploiement.

## 1. Dépôts et frontières

| Usage | Dépôt | Référence de lecture / travail | Constat |
|---|---|---|---|
| Métier CSSA historique | [cssa-v01--entreprise-universelle-domaien-obsidia-](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-) | `feat/f3g-j-cssa-matchday-buvette-restauration-v0` | 296 commits devant main, 0 derrière selon comparaison au moment de l'audit; F3F/F3G présents |
| Préparation pilote historique | même dépôt | `feat/f3h-h-cssa-real-readonly-pilot-preflight-v0` | 386 commits devant main, 0 derrière ; source potentiellement plus récente, **pas présumée remplaçante sans diff** |
| Infrastructure Universal + CSSA courant | [obsidia-x108-proofs](https://github.com/Eaubin08/obsidia-x108-proofs) | `feat/cssa-v01-active` | 488 commits devant main, 0 derrière ; **branche de travail unique** |
| `main` | les deux dépôts | lecture seulement | aucune fusion/push autorisée |

**Attention :** les compteurs « commits ahead » ne constituent pas des SHA de gel et ne permettent pas de conclure que le code a été fusionné. La prochaine passe doit fixer les HEAD exacts dans un manifeste de release et vérifier les blobs utilisés.

## 2. Branches/PR historiques retrouvées

CSSA, toujours visibles en PR ouvertes/draft : [F3G-F #2](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/2), [F3G-G #4](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/4), [F3G-H #5](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/5), [F3G-I #6](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/6), [F3G-J #7](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/7), [F3H-D #11](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/11), [F3H-E #12](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/12), [F3H-F #13](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/13), [F3H-G #14](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/14), [F3H-H #15](https://github.com/Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-/pull/15).

Universal, PR références : [native projection #79](https://github.com/Eaubin08/obsidia-x108-proofs/pull/79), [full loop #80](https://github.com/Eaubin08/obsidia-x108-proofs/pull/80), [enterprise stack #81](https://github.com/Eaubin08/obsidia-x108-proofs/pull/81), [cross-domain #84](https://github.com/Eaubin08/obsidia-x108-proofs/pull/84), [company model #86](https://github.com/Eaubin08/obsidia-x108-proofs/pull/86), [organization source lifecycle #88](https://github.com/Eaubin08/obsidia-x108-proofs/pull/88), [multi-organization governed sandbox #90](https://github.com/Eaubin08/obsidia-x108-proofs/pull/90), [sector CSSA evidence boundaries #91](https://github.com/Eaubin08/obsidia-x108-proofs/pull/91), [offline pinned inter-repo composition #93](https://github.com/Eaubin08/obsidia-x108-proofs/pull/93).

Les PR ouvertes ne doivent **pas** être traitées comme des intégrations `main`. L'état des dépendances et les conflits de versions nécessitent une analyse de diff ciblée avant tout import.

## 3. Inventaire des moteurs : propriétaire unique et classification

| Capacité | Propriétaire canonique | Référence retrouvée | Décision |
|---|---|---|---|
| F3F saison 904 / priorités/ressources | dépôt CSSA historique | `organizations/cssa/stress/organizational_stress_v0.py`, `season_simulation/full_season_v0.py` | REUSE_READONLY ; pas de second moteur de capacité |
| F3G contrats/conformité | dépôt CSSA historique | `organizations/cssa/compliance/contract_compliance_v0.py` | REUSE ; adapter la sortie, pas l'algorithme |
| F3G institutions | dépôt CSSA historique | `organizations/cssa/institutions/institutional_relations_v0.py` | REUSE ; ACK ≠ APPROVED |
| F3G cause racine/récidive | dépôt CSSA historique | `organizations/cssa/root_cause/root_cause_recurrence_v0.py` | REUSE ; reçu métier ≠ receipt exécution |
| F3G buvette/restauration | dépôt CSSA historique | `organizations/cssa/matchday_food/buvette_restauration_v0.py` | REUSE au Lot B |
| Onze responsabilités manager | dépôt CSSA historique | `organizations/cssa/coverage/announced_manager_role_coverage_v0.json` | REUSE exact 11 IDs, public ≠ procédure interne |
| Source/CRM/TASK/Follow-up | infrastructure Universal | `periphery/native_ops/intake_bundle_v0.py` | SINGLE OWNER UNIVERSAL |
| ActionCandidate / KX108 / ticket/receipt/replay | infrastructure Universal | `periphery/native_ops/native_work_to_action_projection_v0.py`, `enterprise_office_full_loop_e2e_v0.py` | SINGLE OWNER UNIVERSAL ; pas de mutation kernel |
| Projection F3F/F3G → proposition | branche CSSA courante | `periphery/cssa_historical_semantic_adapter_v0.py` | REUSE, sécurité HOLD/BLOCK |
| Proposition → plan CASE/TASK/FOLLOW-UP | branche CSSA courante | `periphery/cssa_historical_native_intake_draft_v0.py` | REUSE, aucun commit de state |
| CSSA échéance → exécution sandbox | branche CSSA courante | `periphery/cssa_sovereign_sandbox_lot_a_v0.py` | preuve de fixture seulement |
| Campagne CSSA 12 dossiers | branche CSSA courante | `periphery/cssa_full_lot_a_campaign_v0.py` | **ne remplace pas** F3F 904 |

## 4. Matrice exacte des 11 missions, états de preuve

Identifiants du manifeste historique :
`ADMINISTRATION_DAILY`,
`INSTITUTIONAL_RELATIONS`,
`PEOPLE_MANAGEMENT_DELEGATION`,
`CROSS_POLE_COORDINATION`,
`MATCHDAY_TICKETING`,
`MATCHDAY_SECURITY`,
`MATCHDAY_WELCOME_HOSPITALITY`,
`MATCHDAY_BUVETTE_RESTAURATION`,
`WRITTEN_PROCESS_RESPONSIBILITY`,
`ROOT_CAUSE_DURABILITY`,
`DECISION_EXECUTION`.

- F3G-F photographie initiale : 5 structurellement couvertes, 4 partielles, 2 lacunes.
- F3G-G/H/I/J a ensuite ajouté des moteurs et des preuves sur contrats, institutions, RCA et buvette. **Ne pas réutiliser le tableau F3G-F initial comme verdict final.**
- Ces identifiants proviennent de la **description publique du poste**. Ni l'organigramme interne ni les autorisations réelles du club ne sont démontrés.
- L'état transversal `STRUCTURAL_HISTORICAL` doit être distingué de `NATIVE_SANDBOX_E2E` et `REAL_FIELD` ; pas de « 11/11 opérationnel » sans matrice d'acceptation traçable.

## 5. Régression et preuves — ce qui est effectivement vérifié

| Famille | Attestation actuellement disponible | Limite |
|---|---|---|
| Ancien F3F | receipt original `F3F_CSSA_ORGANIZATIONAL_STRESS_RECEIPT.md` : 904 événements synthétiques, run `37559251006`, 217 PASS | historique seulement ; pas de rejeu 904 sur branche active |
| Ancien F3G | receipts F3G-F/G/H/I/J, jusqu'à 368 PASS historique | ancienne CI, pas de certification de version présente actuelle |
| Adaptateurs CSSA actuels | retour utilisateur Windows `185 passed, 1 skipped` | tests ciblés dont moteurs historiques en lecture seule |
| Sandbox Universal avec cas CSSA | 2 scénarios d'échéance dans campagne 12 cas | approbations simulées ; aucune autorisation réelle CSSA |
| Pilote terrain | non réalisé | absence d'accès et d'approbation institutionnelle réelle |

Sources consolidées : `CSSA_F3F_F3G_ORIGINAL_PROOFS_RECOVERED_20261009.md`, `CSSA_F3F_F3G_UNIVERSAL_EXACT_CONTRACT_MATRIX_20261009.md`, `CSSA_REAL_HISTORICAL_ENGINES_CROSS_REPO_TEST_20261009.md` (si disponible), `CSSA_HISTORICAL_NATIVE_INTAKE_DRAFT_20261009.md`.

## 6. Verrous des interfaces — contrat Passe 2

1. **Métier n'autorise rien** : `expected_gate=ALLOW` historique ≠ KX108 ALLOW, consentement, ticket ni exécution.
2. **L'intégration F3G est aujourd'hui lecture → assessment → semantic proposal → native intake DRAFT.** Il n'y a pas de commit natif authentifié pour ces véritables évaluations ; aucun automatisme d'approbation.
3. Tout plan doit conserver source, date as_of, auteur/responsable, références documentaires, inconnues/contradictions, version du moteur, contexte et hash ; si origine/source incohérente → HOLD/BLOCK.
4. **Ne pas importer les anciens moteurs dans Universal** ni déplacer du code métier dans le kernel. Adapter seulement sur périmètre CSSA.
5. Calendrier, Gmail, CRM externe et sources CSSA réelles : **OFF** sans droits validés et protocole de confidentialité.
6. `memory_write=False`, `emits_act=False`, `kernel_mutation=False` sur les couches non souveraines ; `KX108_ONLY`, receipt/replay, refus déterministe.
7. **Aucun push/merge main** ; historiques consultés en lecture seule, nouvelles écritures restreintes à `feat/cssa-v01-active`.
8. **Le source repo F3H-D contient un ancien pont CRM/TASKS** : comparer son schéma au pont présent et classer `SAME/REUSE/ADAPTER_REQUIRED/OBSOLETE` avant nouvelle construction.
9. PR #93 de l'infrastructure concerne une composition inter-repos épinglée ; **examiner la possibilité de la réutiliser** au lieu d'inventer un troisième chargeur.
10. Si une preuve est absente, écrire `NOT_VERIFIED`, jamais `PASS` supposé.

## 7. Dépendances des passes

`P1 inventory + authority boundaries` → `P2 adapter F3F/F3G et workflow admin` → `P3 stress 904 + 11-role validation` = clôture Lot A si acceptation.

`P4 matchday` → `P5 communication` → `P6 inter-lot stress` = Lot B.

`P7 universal connectors` → `P8 governed automation` → `P9 cockpit portability` → `P10 audit / freeze / readiness pilot` = Lot C/global.

## 8. Verdict P1 et réserves

**P1: DOCUMENTARY_BASELINE_RECONCILED — CONTRACT_FREEZE_PROPOSED, NOT RELEASE-FROZEN.**

Établi : deux dépôts, fonctions propriétaires, interfaces observées, branches et PR historiques, vrais artefacts de preuve, comparaison des responsabilités, frontière de non-exécution. Non établi : HEAD SHA immuable par branche, vérification des changements entre F3G-J et F3H-H, suite exhaustive 904 actuelle, état de CI globale, pilotes réels.

Le plan de construction P2 doit commencer par vérifier l'ancienne intégration F3H-D, le code de composition PR #93 et des HEAD immuables. Ne pas déclarer la passe 1 « runtime certified ».
