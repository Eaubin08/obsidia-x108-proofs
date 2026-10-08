# V0.1 C4 — Domaines réels : conformance des preuves et limites métier

Date : 2026-10-08
Statut : **audit de référence + tests du registre de revendications, pas intégration réelle de trois stacks**
Branche : `feat/v01-c4-sector-evidence-conformance-v0`
Base : `feat/v01-c3-multiorg-multidomain-sandbox-e2e-v0` — PR #90 (DRAFT)

## Décision

**CONTRACT_COMPATIBILITY_PARTIAL / REAL_DOMAIN_EXECUTION_NOT_PROVEN**

Pas de DomainPack unique qui invente la signification de Trading, GNSS ou Administration.
Les règles métier restent dans les repos propriétaires. Le nouveau code
`periphery/enterprise_sector_claims_v0.py` ne classe ni marché, ni RF, ni
message administratif et n'accorde AUCUN droit. Il expose les revendications
**documentées** selon les limites de trois audits figés par commit.

Une revendication documentaire « compatible » ne signifie jamais
`PRODUCTION_READY`, autorisation entreprise, KX ALLOW, ou capacité d'action.

## 1. Trading — PARTIAL_REFERENCE_VALIDATED

Repository : `Eaubin08/OBSIDIA_TRADING@master`
SHA : `6dfee86778810829a2e9d89d3cc6caaaaa0996e9`.

Preuves révisées :

- `domain/contracts/canonical.py` : `to_canonical_agent_signal` est un
  point de convergence des signaux natifs/externes, avec conservation de
  `unknowns`, `contradictions`, `risk_flags` et `evidence_refs`.
- `external/adapters/base_adapter.py` : `ExternalStackAdapter` fournit
  des signaux non souverains; ne possède ni Binder, broker, ni autorité.
- `docs/F12_REAL_KERNEL_ROUND_TRIP.md` : preuve **historique** documentée
  d'un appel HTTP réel au Kernel; réponse `x108_gate=HOLD`, et non
  `verdict` selon une attente historique. Ne confondre pas cette séance
  avec l'état par défaut de l'application Trading.
- `docs/FREEZE_MANIFEST.md` : manifest actif v0.3.2, **284 passed / 1 skipped
  déclarés**, `RealKX108Client` intégrable mais **désactivé par défaut**;
  `UnavailableKX108Client` refuse fermement; `PAPER_ONLY`;
  `ProofPolicy.REQUIRED` imposée quand client réel utilisé.

Écarts : README mentionne un autre compte historique de tests; manifest
actif fait autorité pour son propre lot. Le C3 Trading actuel porte une
**tâche de revue de risque simulée** et non le chemin Trading PAPER complet.
C4 ne prétend pas qu'un broker a été joint par V0.1.

Refus absolus : trading LIVE, ordre réel, rendement financier prouvé,
kernel réel connecté par défaut.

## 2. GPS/Défense/Aviation — PARTIAL_RECORDED_PHYSICAL_EVIDENCE

Repository : `Eaubin08/obsidia-gps-defense-@main`
SHA : `db1b1777faaa598f08e314c915b274520e5f601b`.

Preuves révisées :

- `docs/CLAIM_MATRIX.md`, `docs/GPS_DEFENSE_V1_FINAL_REPORT.md` :
  RINEX enregistré réel, RF I/Q nominal réel et FGI hostile RF partiel
  avec trajectoire NAV/PVT anormale; détection `RF_ANOMALY`.
- `schemas/gps_physical_observation.schema.json` :
  `proof_level`, hashes d'entrées/config/observables, timestamps,
  `limitations` et observation physique.
- `evidence-pipeline/public_domain_bridge/gps_x108_gate.py` :
  traduction vers kernel public; `HOLD` si private kernel absent;
  **attention**, lit `verdict` du JSON, tandis que le contrat Kernel
  attesté ailleurs utilise `x108_gate`. Risque de masquage/fallback :
  audit de compatibilité obligatoire avant réemploi.
- `evidence/hostile-rf-partial/window_C_observation_envelope.json` :
  contient explicitement `proof_level=RECORDED_RF_ATTACK` et
  `eligible_for_physical_claim=true`.
  **Contradiction de terminologie** avec la matrice autorisant seulement
  une chaîne FGI NAV/PVT partielle, pas une attaque RF causalement prouvée.
  Ce label source est conservé comme **contradiction à résoudre**,
  **jamais** transformé en preuve de spoofing opérationnel.

Manques : base nominale comparable, matrice TP/TN/FP/FN, attribution
causale, IMU/radar indépendant, récepteur LIVE, certifications. C4
ne conclut ni `RECORDED_RF_ATTACK closed` ni résistance au spoofing.

## 3. CSSA Administration — CONTRACT_SHADOW_REAL_INTERNAL_BLOCKED

Repository : `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-`
Branche `feat/f3h-h-cssa-real-readonly-pilot-preflight-v0`
SHA `a3125ce211e0c55d6608b39396f1f7633dbab72c`.

Preuves révisées :

- `universal/contracts/domain_v0.py` : StateRef / GovernancePayload,
  `upstream_state_ref` facultatif et jamais de décision ni Binder.
- `docs/architecture/F3H_E_CSSA_REAL_READONLY_INTAKE_ROUTER_V0.md` :
  **8** messages réels issus d'une boîte **personnelle**, seulement
  classés READONLY/shadow ; **0 promotion interne CRM/TASK**.
- `docs/architecture/F3H_H_CSSA_REAL_READONLY_PILOT_PREFLIGHT_V0.md`
  et `organizations/cssa/intake/f3h_h_real_readonly_pilot_preflight_progress_v0.json` :
  aucune boîte ni documentation interne opérationnelle autorisée;
  `PILOT_STARTED=false`. Préflight ne fait **aucune ingestion**.

Il ne faut ni présenter la messagerie personnelle comme celle du CSSA,
ni exécuter un vrai flux opérationnel/Footclubs/FMI, ni déduire des tâches
métier internes de communications de match ou de billetterie personnelle.

## 4. Artefacts C4 ajoutés

- `docs/runtime/V01_ENTERPRISE_C4_SECTOR_EVIDENCE_PROFILES_V0.json` :
  3 profils figés avec dépôts/SHA/paths, 9 revendications documentaires,
  16 interdictions explicites, écarts et blockers.
- `periphery/enterprise_sector_claims_v0.py` :
  validation structurelle et évaluation de revendications non souveraine.
- `tests/integration/test_v01_c4_sector_evidence_conformance_v0.py` :
  toutes les revendications permises restent documentaires, toutes
  les revendications prohibées refusées, contradiction GPS quarantinée,
  refus de sortie réelle, faux statut de source CSSA refusé malgré
  le C3 Administration simulé, tests de falsification de registre.
- GitHub Actions dédié + régression ciblée C3, C2, C1, universal stack.

Le registre contient des **citations de sources et SHA Git**, pas des
signatures d'attestation ou une vérification indépendante de runtime.
Les tests C4 ne réexécutent pas les suites des trois dépôts métier;
ils vérifient les revendications transcrites, leurs frontières et
l'absence de promotion automatique. Cette frontière est explicite.

## 5. Suites de Forge proposées (pas exécutées par C4)

**C4.1 — Réconciliation des contrats réellement incompatibles**

1. Trading : adapter `x108_gate`/statut défaut et preuve du chemin
   `PROOF_REQUIRED + PAPER` raccordé au V0.1 sur fixture réelle,
   sans import des secrets/broker interne.
2. GPS : harmoniser `proof_level` brut versus niveau de preuve
   `RECORDED_RF_ATTACK` effectivement *prouvé*, puis réparer le
   lecteur de verdict côté périmètre public **sans dégrader fail-closed**;
   demande de preuve indépendante avant levée du blocage.
3. CSSA : requérir autorisation d'une source **interne**, pas les huit
   messages personnels. Tant qu'elle n'existe pas, seulement shadow.

**C2 sécurité toujours ouverte** : identité légale de l'entreprise et
délégation réelle d'un responsable, consentement durable et révocation
transactionnelle au point d'exécution. Le présent registre n'est
jamais une alternative à cette vérification.

No kernel mutation, no Monde, no source LIVE, no `main` merge.
