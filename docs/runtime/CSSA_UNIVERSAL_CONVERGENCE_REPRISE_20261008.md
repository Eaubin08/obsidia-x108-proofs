# CSSA / Universel — audit de convergence et plan de reprise V0.1

Date: 2026-10-08
Branche active unique: `feat/cssa-v01-active`
Mode: REVIEW / OFFLINE / NO_MAIN_MERGE
Autorité: `KX108_ONLY`; décision ≠ permission d'exécuter.

## Objectif reconfirmé
Le CSSA constitue la référence métier complète (matchs, abonnés, billetterie, événements, communications, administration), **pas** une architecture indépendante. Les contrats réutilisables d'Obsidia doivent fonctionner aussi pour une PME et une association fictives. Ne pas reconstruire un second moteur de CRM, d'intake, de source runtime, de Binder, de Gateway ou de gouvernance.

## Matrice de convergence — preuves présentes dans la branche
| Couche | Source locale vérifiée | Décision | Vérification restante |
|---|---|---|---|
| Entreprise / rôles / outils / responsabilités | `periphery/company_model_v0.py`, `docs/runtime/V01_ENTERPRISE_C0_C1_COMPANY_MODEL_V0.md` | REUSE | instancier trois organisations avec frontières explicites |
| Sources multi-provider | `periphery/native_sources/source_runtime_v0.py`, `docs/runtime/SOURCE_RUNTIME_NATIVE_V0.md` | REUSE | contrats MAIL/DOCUMENT/CALENDAR sur jeux locaux |
| Interprétation vers intake | `periphery/native_ops/interpretation_to_intake_policy_v0.py`, `docs/runtime/INTERPRETATION_TO_INTAKE_POLICY_NATIVE_V0.md` | REUSE | délais, unknowns, contradictions, doublons, absence de propriétaire |
| CRM et tâches natifs | `periphery/native_ops/crm_native_v0.py`, `docs/runtime/NATIVE_TASKS_CRM_V0.md` | REUSE | isolation `organization_id`, refus des doubles CASE/TASK |
| Bureau complet | `periphery/native_sources/enterprise_office_full_loop_e2e_v0.py`, `docs/runtime/ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0.md` | REUSE | rejouer sur HEAD actif et hors CSSA; ne pas confondre sandbox et LIVE |
| Réservations / IPC | `periphery/enterprise_offline_storage_worker_v0.py`, `periphery/enterprise_ipc_ambiguous_commit_recovery_v0.py` | ADAPT | isolation OS, identité IPC, réponse durable, autorité d'exécution absente |
| Contrôle souverain et actions | WorldAction PRE / KX108 / activation policy / ticket documentés dans l'E2E | REUSE | conserver le gate canonique et refus sans vrai record/approval |
| Monde | Projection readonly dans contrat C0/C1 | DEFER | ne pas modifier Monde depuis la branche CSSA |

## Scénarios de calibration
CSSA: infos de match, changement horaire, tribune fermée, accès abonné, billetterie, annonce CRM, demande nécessitant CASE/TASK, incident, deadline, contradiction, doublon, pièce manquante. Une confirmation d'achat est une trace transactionnelle, pas une tâche inventée. Tous les contenus viennent de fixtures/sources autorisées, pas d'un accès interne présumé.

Généralisation: même chaîne sur une **PME fictive** (commande, facture, contrat, incident) et une **association fictive** (adhésion, événement, demande, échéance). L'adapter de domaine traduit; le kernel ne comprend pas le métier.

## Résultat CI observé avant ce commit
Sur `feat/cssa-v01-active` au commit `382812edd5654924cf8dc1a623ba46bcd3ea9582`, les workflows recensés sur la branche affichent 82 succès et 3 échecs historiques, sans job en attente. Les CI ciblées C2.28 et C2.29 *récentes* sont SUCCESS, mais la CI globale `X108 Periphery CI` sur le correctif C2.28 échoue encore (run #37816141333): **12 976 PASS, 11 FAIL, 46 SKIP, 207 deselected**.

Familles des 11 échecs:
- `tests/api/test_brody_routes_registered.py` et `tests/api/test_f67_sigma_live_smoke_api_audit.py` (2): divergences d’inventaire de routes;
- `tests/cli/test_mission_authority_conformance_v0.py` (2): exécutable `lake` absent de l'environnement;
- `tests/test_batch_execution_v0.py` (5): contrat/statut CLI et chemin batch;
- `tests/test_branching_ledger_v0.py`: résultat DISCOVERED vs ALREADY_REGISTERED;
- `tests/test_git_worktree_repository_identity_v0.py`: identité auteur Git absente sur runner;
- Total confirmé par les onze identifiants de tests en échec dans les logs.

## Gates de réparation, dans cet ordre
1. Reproduire et classer tous les 11 échecs sur une **même SHA** : défaut code, test obsolète, isolation runner ou prérequis manquant. Ne pas réécrire un test pour cacher un échec métier.
2. Restaurer la CI générale sans transformer `HOLD/BLOCK` en permission d'action ni intervenir sur les dépôts kernel ou Monde.
3. Valider E2E office sur trois domaines, avec les mêmes interfaces de sources, CRM/TASKS, KX108, receipts/replay, zéro egress.
4. Vérifier sécurité multi-organisation, responsabilité des sources, permissions et journalisation. Les politiques CSSA restent CSSA; seuls les contrats génériques remontent au cœur.
5. Présenter le Digital Twin réaliste sur semaine/mois puis décider d'un pilote réel *distinct*, explicitement approuvé.

## Décision
HOLD sur tout connecteur réel / mail send / déploiement CSSA. Poursuivre uniquement sur `feat/cssa-v01-active` par commits et tests; pas de PR par `Go`, pas de merge `main`, pas de suppression des archives.
