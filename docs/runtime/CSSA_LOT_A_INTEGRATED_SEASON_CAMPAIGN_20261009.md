# CSSA LOT A — Campagne saison / administration, tranche intégrée initiale

Date : 2026-10-09. Branche : `feat/cssa-v01-active`. Code nouveau : `periphery/cssa_season_campaign_lot_a_v0.py`; tests : `tests/test_cssa_season_campaign_lot_a_v0.py`.

## Constat de compatibilité technique

Comparaison par `fetch_file` sur CSSA vs `feat/obsidia-universal-cross-domain-conformance-v0` :

| Module | Blob SHA identique dans les deux branches |
|---|---|
| `periphery/native_ops/native_work_to_action_projection_v0.py` | `920071927c6f10705f89169e8a62c1a1d178d063` |
| `periphery/universal_enterprise_stack_adapter_v0.py` | `ed4cd654f03fece264b96de0f073cb2bb4d15838` |
| `periphery/native_sources/enterprise_office_full_loop_e2e_v0.py` | `82f2fe668e113d5bff74233b07ef68a88d88965a` |

**Le problème de présence de fichiers est levé sur ces trois interfaces précises** ; la compatibilité sémantique, les états persistés, les contrats de versions et le raccord de bout en bout ne sont pas encore prouvés.

Signatures observées :
- `project_native_work_to_action_v0(*, store, case_id, task_id, followup_id)` exige des objets CASE, TASK et FOLLOW-UP réellement liés dans `NativeEntityStoreV0`.
- `build_enterprise_action_binding_v0(*, candidate, capability_id, manifest, connector_args, target_ref, target_prestate_hash)` exige un `ActionCandidate` valide et la capacité déclarée.
- `run_enterprise_office_full_loop_e2e_v0(*, paths, runtime_root, native_store_root, governance_root, execution_root)` demande un jeu de sources et des répertoires sandbox explicites.

**Ne jamais faire passer une proposition CSSA non appliquée pour un état canonique persisté.**

## Tranche métier livrée pour campagne intégrée

La campagne CSSA Lot A prépare une inspection déterministe et un reçu de cohérence sur des événements synthétiques saison/administration :

- Ressource et créneau partagés par deux événements ; responsable déjà occupé.
- Responsable absent, délégation non prouvée.
- Dépassement budgétaire ou budget incomplet.
- Date/échéance inconnue, base réglementaire non établie.
- Communication sans faits vérifiés, contradiction de sources.
- Provenance manquante et identifiants dupliqués.

L'exemple de test réunit **12 événements de métiers différents dans un même lot**. Il ne remplace pas la campagne F3F historique de 904 événements, qui reste à retrouver/rejouer avec ses preuves originales.

Résultat possible : `HOLD` si l'événement est seulement candidat et nécessite une revue, `BLOCK` en présence de manques/conflits. Aucun `ALLOW` ne peut émaner de ce modèle CSSA. Les hashes servent uniquement de receipts locaux, non de signatures d'autorisation ou de preuve d'exécution.

## Critères de fermeture du LOT A encore ouverts

1. Traçabilité des 11 missions du manager général et des sources F3F/F3G exactes (commits/fixtures).
2. Modèle métier validé des événements : fuseaux horaires, fenêtres temporelles, rôles, délégations, budgets, pièces et organismes ; les règles de cette campagne sont pour l'instant simplifiées.
3. Dossier de preuve multi-acteurs et traitement des contradictions selon les contrats propres au club.
4. **Raccord réel en sandbox isolée aux CASE/TASK/FOLLOW-UP natifs et au rail Universal**, avec source de vérité testée, jamais simulée sous de faux objets commités.
5. Tests d'intégration et de non-régression ciblés, plus preuve de non-dispatch, collecte des receipts de sandbox et replay.
6. Un seul freeze Lot A après couverture complète. Aucun freeze prématuré sur cette tranche.

## Commande Windows de vérification

```powershell
Set-Location (Join-Path $env:TEMP "cssa-eol-final")
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter "test_cssa_*.py" -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

Dernier résultat Windows confirmé **avant le nouveau Lot A** : 123 passed, 1 skipped, répertoire propre. **La nouvelle campagne et ses tests n'ont pas encore été rejoués sur Windows.**

## Contraintes invariantes

`KX108_ONLY`, CSSA uniquement, lecture seule Universal, aucun changement `main`, kernel, Brody, Native Memory, Monde, Sigma, pas de CRM réel, pas de services externes. Tous les événements de campagne restent des fixtures synthétiques.
