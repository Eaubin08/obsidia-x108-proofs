# dry_run_machination_check.md
# DRY_RUN : Test B — Compréhension machination Obsidia X-108
# Pack : BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Source lue : BRODY_V1_MACHINATION_OBSIDIA_X108.md, BRODY_V1_CANONICAL_CORE.md

---

## Question simulée

> "Explique la machination Obsidia/X108."

---

## Réponse Brody simulée (depuis le pack)

La machination Obsidia X-108 suit un pipeline strictement ordonné,
de l'entrée du signal jusqu'à la preuve cryptographique de la décision.

### 1. Signal entrant

Tout commence par un **signal** : une question, une intention, un ordre, une requête.
Le signal entre dans le **Control Plane** qui orchestre les gates et fusionne
les signaux sans décider.

### 2. Le stack constitutionnel (16 étapes)

*Source : `docs/architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md`*

```
[1]  INPUT
[2]  Control Plane          — orchestration, pas de décision
[3]  Data Gate              — pureté des données
[4]  Provenance             — traçabilité de l'origine
[5]  Memory                 — mémoire stabilisée (Mémoire Fractale)
[6]  Sigma Engine           — agrégation des agents domaine
[7]  EML                    — Énergie / Mémoire / Langage
[8]  Energy / Thermo        — thermodynamique informationnelle
[9]  Timeverse              — contexte temporel, constance
[10] OCS                    — Operational Constance System
[11] Operational Constance  — constance opérationnelle
[12] Permission / Economic  — gates permission + Gencoin
[13] X-108 KERNEL           — évalue D1, E2, G1, G2, G3 → ACT|HOLD|BLOCK
[14] OS3                    — preuve cryptographique de la décision
[15] Gencoin                — ancrage économique (non-token)
[16] Feedback               — boucle retour mémoire candidate
```

### 3. Le rôle du CIC dans ce pipeline

Brody assemble le **CIC (Causal Identity Context)** avant d'entrer dans le pipeline.
Le CIC est readonly : il contient le contexte du domaine, les métriques confirmées,
les capacités interdites, et le `cic_receipt` (traçabilité).

Le `cic_receipt` permet le **replay** : toute décision peut être rejouée et auditée
avec exactement le même contexte causal.

### 4. X-108 KERNEL — le seul décideur

À l'étape 13, le Kernel X-108 évalue les 5 invariants formels (D1, E2, G1, G2, G3)
et produit **un seul** verdict : `ACT`, `HOLD`, ou `BLOCK`.

Ce verdict est déterministe : même entrée = même verdict. Toujours.
Aucune IA générative n'est impliquée dans cette décision.

### 5. La frontière monde — World Call Gateway

Avant toute sortie vers le monde réel, chaque action candidate passe par le
World Call Gateway :

```
ActionCandidate
  → classify_action_risk()
  → classify_world_call()
  → compute_autonomy_level()
  → issue_sovereign_ticket()       [dry_run_only=True TOUJOURS]
  → ObsidiaGateway.check()         [egress_allowed=False TOUJOURS]
  → WorldActionBus.publish()       [journal local, pas de réseau]
```

### 6. Preuve cryptographique

Chaque décision est ancrée :
```
Décision → Decision ID + Trace ID → Merkle Root → RFC3161 timestamp → CIC Receipt
```

---

## Vérification de la séquence attendue

| Étape attendue | Présente | Source citée |
|---|---|---|
| signal → contexte (CIC) | ✓ | `cic_readonly_pack_provider.py` |
| contexte → agents Sigma | ✓ | `sigma/contracts.py` |
| agents → Guard/X-108 | ✓ | `docs/KERNEL_OVERVIEW.md` |
| X-108 → décision (ACT/HOLD/BLOCK) | ✓ | prouvé Lean 4 D1, E2 |
| décision → preuve (Merkle, RFC3161) | ✓ | `proofs/rfc3161/`, `sigma/merkle_root_generator.py` |
| preuve → replay/audit (CIC Receipt) | ✓ | `cic_receipt_pack.py` |

---

## Contrôle des pièges latents

| Piège potentiel | Détecté | Action |
|---|---|---|
| Brody prétendu décideur dans le pipeline | NON | OK — "X-108 est le seul décideur" |
| 15 couches citées | NON | OK — "16 étapes" correctement cité |
| Egress réseau décrit comme possible | NON | OK — "egress_allowed=False TOUJOURS" |
| WorldActionBus décrit comme réseau | NON | OK — "journal local" |
| Gencoin décrit comme token crypto | NON | OK — "(non-token)" |

---

## Verdict du test B

**PASS**
La séquence pipeline est correcte, complète (signal → preuve → replay),
et ne prétend à aucun moment que Brody, Sigma ou un autre composant décide.
16 étapes correctement citées (correction C14 intégrée).
Aucun invariant violé.
