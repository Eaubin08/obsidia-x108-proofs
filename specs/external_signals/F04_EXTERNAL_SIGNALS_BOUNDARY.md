# F04_EXTERNAL_SIGNALS_BOUNDARY

**Date :** 2026-06-02
**Pack :** OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1
**Authority :** KX108_ONLY

---

## Règle fondamentale

```
External Signals = TEMPORAL_PREFILTER_ONLY
External Signals ↛ ALLOW
External Signals ↛ HOLD
External Signals ↛ BLOCK
External Signals ↛ ACT
External Signals ↛ X108 (réautorisation)
```

---

## Ce que External Signals produit (autorisé)

| Signal | Description | Boundary |
|--------|-------------|---------|
| `temporal_context` | Contexte temporel d'une requête (timestamp, tick, corridor) | CONTEXT_ONLY |
| `anti_replay_signal` | Détection de rejeu d'une action déjà exécutée | SIGNAL_ONLY |
| `stale_execution_signal` | Détection d'exécution périmée (delai > seuil) | SIGNAL_ONLY |
| `temporal_receipt_metadata` | Métadonnées de reçu temporel pour audit | EVIDENCE_ONLY |
| `consequence_boundary_context` | Contexte de boundary de conséquence d'action | CONTEXT_ONLY |

---

## Ce que External Signals NE produit JAMAIS

- `ALLOW` — autorisation d'action
- `HOLD` — suspension d'action
- `BLOCK` — blocage d'action
- `ACT` — déclenchement d'action
- Verdict moral, verdict culturel, verdict de vérité
- Réautorisation de X-108 ou de tout composant décisionnel
- Preuve formelle de sécurité (RSSI readiness ≠ certification)

---

## Position dans le cycle d'action

```
INPUT_CAPTURED
    ↓
[External Signals = TEMPORAL_PREFILTER ici]
    ↓
ACTION_CANDIDATE_BUILT
    ↓
PERIPHERY_SCORED
    ↓
SIGMA_ROUTED
    ↓
X108_EVALUATED  ← seule autorité
    ↓
OS3_TICKETED
    ...
```

External Signals opère **avant** la construction du candidat d'action.
Son output est un signal de contexte enrichi — jamais un verdict.

---

## Composants C459-C482 — invariants

| Composant | Rôle | Invariant |
|-----------|------|-----------|
| C459 Timeverse Temporal Sidecar | Sidecar temporel | advisory_only=true |
| C460 Temporal Context Header | En-tête de contexte temporel | no_decision=true |
| C461 Tick Canonical Validation | Validation du tick canonique | signal_only=true |
| C462 No Float Temporal Math | Mathématique temporelle sans flottant | DETERMINISTIC — pas de décision |
| C463 Anti Replay Horizon | Horizon anti-rejeu | signal=replay_detected — pas BLOCK |
| C464 Temporal Challenge | Défi temporel | challenge_only — pas verdict |
| C465 Time Bounded Tool Call Check | Vérification tool-call borné temps | prefilter_only=true |
| C466 Temporal Receipt Metadata | Métadonnées reçu temporel | evidence_only=true |
| C467 TSAE Receipt Model | Modèle de reçu TSAE | receipt_only — pas décision |
| C468 Receipt Anchor Hash | Hash d'ancrage de reçu | audit_only=true |
| C469 Stale Execution Detection | Détection exécution périmée | signal_only — pas BLOCK |
| C470 Temporal Zero Trust Positioning | Positionnement zero-trust temporel | context_only=true |
| C471 Gateway Before Endpoint Prefilter | Préfiltre gateway avant endpoint | prefilter_only — pas gate finale |
| C472 Consequence Boundary Enrichment | Enrichissement boundary conséquence | enrichment_only=true |
| C473 Wrapper Non Reauthoring Law | Loi de non-réautorisation wrapper | NO_REAUTHORING absolu |
| C474 Law State Input Replay Triplet | Triplet loi/état/input pour replay | triplet_audit — pas verdict |
| C475 Corridor Packaging Registry | Registre d'emballage corridor | registry_only=true |
| C476 Refusal Preserves Structure | Refus préserve la structure | structural_only — pas décision |
| C477 Protected Consequence Could Not Bind | Conséquence protégée non liée | signal_only=true |
| C478 Executable Standing Check | Vérification standing exécutable | check_only — pas ALLOW |
| C479 Continuation Legitimacy Check | Vérification légitimité continuation | check_only — pas ALLOW |
| C480 Consequence Binding Status Extended | Statut liaison conséquence étendu | status_only=true |
| C481 Visible Enforcement Surface | Surface d'application visible | surface_only — pas décision |
| C482 Intent Effect Receipt Separation | Séparation intent/effet/reçu | separation_only=true |

---

## Règle C473 — Non-réautorisation (critique)

```
C473_wrapper_non_reauthoring_law :
Un wrapper External Signals NE PEUT PAS réautoriser X108.
Un wrapper External Signals NE PEUT PAS produire un nouveau ALLOW.
Un wrapper External Signals enrichit le contexte — jamais la décision.
```

Cette règle est la plus importante de F04. Elle protège KX108_ONLY.

---

## Claim-scope

**Autorisé :**
- "External Signals fournit un préfiltre temporel contextuel à X108"
- "Les signaux temporels détectent le rejeu et la péremption"
- "External Signals enrichit le contexte avant évaluation X108"

**Interdit :**
- "External Signals décide de l'action"
- "External Signals remplace ou réautorise X108"
- "External Signals certifie la sécurité temporelle"
- "RSSI readiness = certification de sécurité"
