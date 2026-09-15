# BRODY_V1_MACHINATION_OBSIDIA_X108.md
# Pack: BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Statut : VALIDATED_BY_REPO
# Sources : docs/architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md,
#            docs/KERNEL_OVERVIEW.md, periphery/world_calls/, apps/obsidia_api/cic/

---

## L'architecture complète : du signal à l'audit

Ce document décrit la machination complète d'Obsidia X-108 telle qu'elle est
documentée dans les sources canoniques du repo.

---

## Étape 0 — Le signal entrant

Toute interaction commence par un **signal** : une question, une intention,
un ordre, une requête. Le signal entre dans le Control Plane.

```
[Signal / Intention / Agent]
         |
         v
[Control Plane]  — orchestre les gates, fusionne les signaux, ne décide pas
```

---

## Étapes 1 à 12 — Le stack constitutionnel

**Source :** `docs/architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md`

```
[1]  INPUT
[2]  Control Plane          — orchestration, pas de décision
[3]  Data Gate              — pureté des données entrantes
[4]  Provenance             — traçabilité de l'origine
[5]  Memory                 — mémoire stabilisée (Mémoire Fractale)
[6]  Sigma Engine           — agrégation des agents domaine
[7]  EML                    — Énergie / Mémoire / Langage (couche symbolique)
[8]  Energy / Thermo        — thermodynamique informationnelle
[9]  Timeverse              — contexte temporel, constance
[10] OCS                    — Operational Constance System
[11] Operational Constance  — agent de constance opérationnelle
[12] Permission / Economic  — gates de permission + couche économique (Gencoin)
```

---

## Étape 13 — X-108 KERNEL (décision souveraine)

**Source :** `docs/KERNEL_OVERVIEW.md`, `proofs/lean/`

```
[13] X-108 KERNEL
     — évalue les invariants mathématiques D1, E2, G1, G2, G3
     — produit un verdict : ACT | HOLD | BLOCK
     — aucune exception possible
     — aucune IA générative impliquée dans la décision
```

**Les 3 verdicts :**
- `ACT` : Tous les invariants respectés → exécution immédiate
- `HOLD` : Certitude insuffisante → attente de clarification
- `BLOCK` : Invariant violé → blocage immédiat + trace

---

## Étapes 14 à 16 — Preuve, valeur, mémoire

```
[14] OS3                    — preuve cryptographique de la décision
[15] Gencoin                — valeur / récompense / ancrage économique
[16] Feedback               — boucle de retour vers mémoire candidate
```

**Note :** Gencoin n'est pas un token crypto.
Source : `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`

---

## Le CIC dans la machination

**Source :** `apps/obsidia_api/cic/cic_readonly_pack_provider.py` (commit 783e664)

Brody assemble un **Causal Identity Context** (CIC) avant d'entrer dans
le pipeline. Le CIC est readonly :

```
build_cic_readonly_context()
  → source_zip_sha256          (empreinte du corpus source)
  → confirmed_metric_families  (familles de métriques validées)
  → domain_relevance           (pertinence du domaine)
  → forbidden_capabilities     (liste d'interdictions)
  → cic_receipt                (traçabilité — voir ci-dessous)
  → ncp_context                (stub NCP readonly SIDE_LOAD)
  → scraping_context           (stub Scraping readonly QUARANTINED)
```

---

## Le CIC Receipt — replay et audit

**Source :** `apps/obsidia_api/cic/cic_receipt_pack.py`

```
invocation_hash = SHA256(domain + source_zip_sha256 + confirmed_metric_families)
receipt_id      = "CIC_RCP_" + invocation_hash[:16].upper()
```

Le receipt permet :
- La **traçabilité** : chaque appel Brody a un identifiant unique
- Le **replay** : rejouer exactement le même contexte à tout moment
- L'**audit** : comparer deux réponses Brody avec le même hash

---

## World Call Gateway — frontière monde

**Source :** `periphery/world_calls/`

```
[ActionCandidate]
       |
  classify_action_risk()       → ActionRiskClass
       |
  classify_world_call()        → WorldCallClass
       |
  compute_autonomy_level()     → AutonomyLevel (0-5)
       |
  issue_sovereign_ticket()     → SovereignTicket (dry_run_only=True TOUJOURS)
       |
  ObsidiaGateway.check()       → GatewayDecision (egress_allowed=False TOUJOURS)
       |
  WorldActionBus.publish()     → journal local append-only (AUCUN egress réel)
```

**Invariants absolus :**
- `egress_allowed = False` — TOUJOURS
- `dry_run_only = True` — TOUJOURS
- Pas de ticket → BLOCK immédiat
- `WorldActionBus` = journal local, pas une sortie réseau
- `assert_no_secret_in_agent_payload()` avant tout gateway pass

---

## La traçabilité cryptographique

Chaque décision X-108 est ancrée cryptographiquement :

```
Décision
  → Decision ID + Trace ID
  → Merkle Root (immuabilité)
  → RFC3161 timestamp (preuve temporelle)
  → CIC Receipt (contexte causal)
```

La combinaison Decision ID + Trace ID + Merkle Root + RFC3161 forme
une **preuve immuable** que la décision a été prise à un instant donné,
dans un contexte donné, avec un résultat donné.

---

## Ce que Brody voit dans cette machination

Brody est situé dans la couche PERIPHERY. Il reçoit :
- Le CIC (contexte causal readonly)
- La langue de la requête (routing)
- Le message utilisateur (sanitisé — `brody_response_sanitizer.py`)

Il produit :
- Une `BrodyResponse` structurée
- Avec tous les invariants du contrat (`advisory_only=True`, etc.)
- Et renvoie le CIC enrichi au pipeline

Brody ne voit jamais les verdicts finaux X-108. Il ne participe pas
à la décision. Il fournit du contexte à la chaîne, rien de plus.
