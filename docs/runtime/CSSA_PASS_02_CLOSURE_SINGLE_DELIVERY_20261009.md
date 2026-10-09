# CSSA — PASSE 02/10, fermeture fonctionnelle de simulation

2026-10-09. Branche `feat/cssa-v01-active`. Aucune modification main ou composants Universal partagés.

## Périmètre livré en une passe (synthèse, pas nouveau programme de passes)

1. Moteurs originaux F3F/F3G G/H/I/J consultés et acceptés via `cssa_historical_semantic_adapter_v0.py`, puis plans natifs via `cssa_historical_native_intake_draft_v0.py`.
2. Lot administratif F3G G/H/I dans `cssa_administrative_batch_pass2_v0.py` ; couplage avec F3F et matrice exacte 11 missions du manager dans `cssa_role_work_register_pass2_v0.py`.
3. Six parcours complémentaires (LICENCE, OFFICIAL_REGISTRATION, STAFF_AVAILABILITY, VOLUNTEER_ABSENCE, DELEGATION, SUBSTITUTION) via `cssa_admin_licence_people_closure_pass2_v0.py`, distincts des moteurs historique non modifiés. Tous aboutissent au mieux à un plan `DRAFT_REVIEW_ONLY` et non une création CRM.
4. Les anciennes fonctions F3H-D de mutation native (CASE, TASK, INTERACTION, FOLLOW-UP) et leur gouvernance KX108 existent déjà dans le dépôt CSSA historique ; leur duplication a été évitée. Les anciens F3H-E à H assurent déjà un router read-only et des préflights opérationnels, sans preuve que les autorisations terrain soient disponibles aujourd'hui.

## Tests et acceptation

Baseline avant dernière livraison: **191 PASS, 1 SKIP**, confirmés par l'utilisateur, Git propre. Le nouveau fichier `tests/test_cssa_admin_licence_people_closure_pass2_v0.py` ajoute **17 tests** : quatre familles, deux délégations sans autorité, une délégation avec référence mais toujours sans permission, six champs/provenances manquants, contradiction, revendication d'accès réel refusée, campagne six cas, et doublons.

Attendu après pull: **208 PASS, 1 SKIP** si tous passent. CE CHIFFRE N'EST PAS ENCORE OBSERVÉ. Les tests des moteurs historiques requièrent `CSSA_HISTORICAL_REPO` dans la session.

```powershell
Set-Location (Join-Path $env:TEMP 'cssa-eol-final')
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter 'test_cssa_*.py' -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

## Verdict et limite de revendication

**PASS_02_SIMULATED_FUNCTIONAL_SCOPE_DELIVERED — TEST_ACCEPTANCE_PENDING.** Passe 2 close dans le périmètre structurel simulé uniquement après validation de la régression. Les vraies licences internes, les identités/mandats d'employés, les chaînes de délégation réelles, les droits d'actions et les intégrations réelles FFF/CSSA demeurent **NOT_VERIFIED**. Aucune preuve d'opérationnalité réelle ni d'exécution du batch historique complet n'est revendiquée.

Le traitement de la saison 904 événements et la clôture du lot A sont strictement la **passe 03/10** du plan original. Le reste du plan ne change pas : passes 04–06 lot B, 07–09 lot C, passe 10 audit global. Pas de sous-passe additionnelle.