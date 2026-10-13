# CSSA — LOT C, livraison consolidée des passes 07–09 / 10

**Branche :** `feat/cssa-v01-active`. **Date :** 2026-10-09.
**Contrat :** CSSA-only, aucune modification de main, du noyau KX108, de Brody ou de Native Memory. Source historique CSSA non modifiée.

## Réutilisation de l'existant

Ce lot n'implémente pas un nouveau moteur CRM ou un nouveau KX108. Il réutilise :
- `periphery/native_ops/intake_bundle_v0.py` : assemblage + vérification du CASE/TASK/INTERACTION/FOLLOW-UP natif ;
- `periphery/cssa_calendar_email_candidates_v0.py` : modèles mail/calendrier en HOLD et sans envoi ;
- `periphery/native_sources/calendar_connector_v0.py` : connecteur calendrier READONLY de référence ;
- `periphery/native_ops/monde_native_read_model_v0.py` : contrat de projection Monde à partir de sources persistées ;
- `periphery/cssa_sovereign_sandbox_lot_a_v0.py` et `periphery/native_sources/enterprise_office_full_loop_e2e_v0.py` : rail sandbox KX108/approbation fictive/ticket/receipt/replay, aucun effet externe réel.

## Livraison en un bloc

**Passe 7 — CRM natif, sources, mail, calendrier.** Un seul routeur CSSA reçoit MAIL, CALENDAR, DOCUMENT et CRM. Un plan natif de revue est créé uniquement depuis une fixture synthétique explicite avec source, provenance, propriétaire, dates avec fuseau et relecteur humain. Les messages personnels ne deviennent jamais automatiquement un dossier club. Les sources de vraie boîte CSSA non attestées restent HOLD. Les propositions de suivi/calendrier et de réponse mail ne sont pas exécutables et ne contiennent aucun destinataire réel.

**Passe 8 — gouvernance.** Réutilisation de la preuve du rail sandbox Universal existant avec KX108, approbation opérateur simulée, contrôle de non-répétition et replay. Le résultat doit confirmer qu'aucun réseau ni effet réel n'a été produit. Jamais de faux KX108 ALLOW injecté dans le routeur CSSA. Une preuve manquante ou non conforme bloque la fermeture du lot.

**Passe 9 — cockpit et portabilité.** Projection pure en nœuds CSSA `source`, états de revue, nombre de plans natifs, propositions calendrier et modèles mail. Profil portable **OFFLINE_READONLY** explicitement lié à la branche CSSA, réseau désactivé, aucun identifiant de club, aucun noyau partagé mutable. Le rapport inclut un SHA-256 de diagnostic : il **n'est pas** un reçu souverain et ne donne aucune autorité.

Livraison : `periphery/cssa_lot_c_universal_passes7_9_v0.py`.
Tests : `tests/test_cssa_lot_c_universal_passes7_9_v0.py` avec 22 nouveaux tests : 4 connecteurs, abstentions sur données personnelles, 9 refus pour données incomplètes/autorité, contradictions, absence d'une preuve, configuration de portabilité incorrecte, falsification de la preuve sandbox et doublons.

## Limites

Cette fermeture est **une preuve structurelle en simulation**. Elle ne constitue ni une intégration des véritables comptes Gmail/Outlook/Google Calendar/CSSA, ni un serveur cockpit déployé, ni une preuve de traitement des données personnelles en conditions réelles. Aucun push main, aucune migration de schéma Universal ni création d'identifiants réels.

## Validation consolidée unique du Lot C

Dernier résultat utilisateur vérifié : **246 PASS, 1 SKIP, Git propre**.
Après ce lot, **268 PASS, 1 SKIP** sont attendus, **non encore exécutés**. Ne pas déclarer la passe 9 ni le Lot C fermés avant cette régression.

```powershell
Set-Location (Join-Path $env:TEMP "cssa-eol-final")
git pull --ff-only
$cssaTests = @(Get-ChildItem tests -Filter "test_cssa_*.py" -File | ForEach-Object { $_.FullName })
py -m pytest @cssaTests tests/integration/test_native_tasks_crm_v0.py -q --tb=short
git status --short
```

Critère : tous les tests du lot passent avec uniquement le skip historique ; le statut devient `LOT_C_CLOSED_SIMULATION` si le verdict passe sur la véritable preuve sandbox ; sinon `LOT_C_BLOCKED`.

**Prochaine et dernière étape du programme : passe 10/10**, audit des lots A+B+C, dérives d'architecture, tests/receipts, non-régression et freeze commenté sans push main.
