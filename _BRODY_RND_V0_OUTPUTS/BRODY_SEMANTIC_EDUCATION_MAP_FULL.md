# BRODY_SEMANTIC_EDUCATION_MAP_FULL.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Carte sémantique éducative complète — Obsidia X-108

Ce document mappe les concepts du repo par domaine éducatif, avec niveau de maîtrise cible et sources.

---

## Niveau 1 : Fondements — Qu'est-ce qu'Obsidia X-108 ?

### Concept A : Gouvernance déterministe ex ante

**Message clé :** Obsidia X-108 juge les actions *avant* qu'elles s'exécutent. C'est un disjoncteur mathématique, pas une IA générative.

**Sources :**
- `docs/KERNEL_OVERVIEW.md` §I-II
- `README.md`
- `USE_CASES.md`

**Concept central :**
```
Intention / Agent → [KERNEL X-108] → ACT / HOLD / BLOCK → Trace / Preuve
```

**Ce que ça enseigne :** La différence entre gouvernance ex ante (avant) et ex post (après). Pourquoi le post est insuffisant en haute fréquence (trading, fraude).

---

### Concept B : Dual Obsidia

**Message clé :** L'architecture sépare strictement l'exploration (Espace Latent) de la décision (Noyau Déterministe).

**Sources :**
- `docs/GLOSSAIRE.md`

**Schéma :**
```
Espace Latent    → exploration libre, hypothèses, simulation
Noyau Déterministe → invariants mathématiques, pas d'hallucination
```

**Ce que ça enseigne :** Comment combiner la flexibilité d'une IA avec la rigueur d'un système déterministe.

---

### Concept C : La Chaîne Canonique

**Message clé :** L'information traverse 5 étapes obligatoires : Sens → Organisation → Cohérence → Temps (Constance) → Mémoire (Stabilisation).

**Source :** `docs/GLOSSAIRE.md`

**Ce que ça enseigne :** Pourquoi la mémoire d'Obsidia ne peut pas être effacée par une simple commande — elle survit à l'épreuve du temps et de la cohérence.

---

## Niveau 2 : Architecture — Comment ça fonctionne ?

### Concept D : Le vote d'agents et l'agrégation Sigma

**Message clé :** Plusieurs agents spécialisés votent sur une action. Sigma agrège leurs scores. X-108 prend la décision finale.

**Source :** `docs/KERNEL_OVERVIEW.md` §III, `USE_CASES.md` §Cas 1

**Exemple :**
```
FraudDetectionAgent    : 0.95 (BLOCK)
BehaviorAnalysisAgent  : 0.80 (BLOCK)
TransactionValidation  : 0.30 (ALLOW)
→ Agrégation pondérée  : 0.68 → seuil BLOCK
→ Verdict              : BLOCK
```

**Ce que ça enseigne :** Le principe de consensus distribué pour la prise de décision critique. Aucun agent seul ne peut forcer un verdict.

---

### Concept E : La traçabilité immuable

**Message clé :** Chaque décision X-108 est scellée cryptographiquement et ne peut jamais être modifiée.

**Source :** `docs/KERNEL_OVERVIEW.md` §IV, `USE_CASES.md` §Cas 5

**Pipeline de traçabilité :**
```
Decision ID  → DEC-{DOMAIN}-{TIMESTAMP}-{HASH}
Trace ID     → TRACE-{DECISION_ID}-{MERKLE_ROOT}
Merkle Root  → Merkle(decision_1, ..., decision_n)
RFC 3161     → Signature immuable par TSA (Trusted Stamp Authority)
```

**Ce que ça enseigne :** Comment prouver à un régulateur que la décision était correcte, 3 ans après les faits.

---

### Concept F : La couche Sigma

**Message clé :** Sigma est le pipeline d'agrégation entre les agents et le kernel. Il a une couche publique minimale (P1) et une couche production privée.

**Source :** `docs/SIGMA.md`, `sigma/run_pipeline.py`

**Ce que ça enseigne :** La différence entre périmètre public auditableRobotique et production propriétaire. Pourquoi le public ne contient pas tout.

---

### Concept G : Le protocole X-108 (TLA+)

**Message clé :** Le protocole X-108 a été formellement vérifié sur 1,2M états sans violation. Le veto distribué est prouvé sans deadlock.

**Source :** `formal/tla/X108.tla`, `formal/tla/DistributedX108.tla`, `PROOF_INDEX.md`

**Ce que ça enseigne :** Ce que signifie une vérification formelle de modèle (model checking). Pourquoi TLA+ est utilisé pour prouver les systèmes distribués.

---

## Niveau 3 : BRODY — Qui parle dans le système ?

### Concept H : BRODY comme surface conversationnelle

**Message clé :** BRODY est le module qui "parle" — mais il ne décide jamais. Chaque réponse porte le contrat de souveraineté.

**Sources :** `docs/brody/` (5 fichiers)

**Règle :**
```
Brody répond. X108 décide.
Contexte ≠ Décision.
```

**Ce que ça enseigne :** Comment séparer interface utilisateur (conversationnelle) et autorité (déterministe) dans un système critique.

---

### Concept I : Le BRODY_RESPONSE_CONTRACT

**Message clé :** Chaque sortie BRODY est contractualisée par 8 champs invariants. Violation → exception levée.

**Source :** `docs/brody/BRODY_RESPONSE_CONTRACT_V1.md`

**Ce que ça enseigne :** Le pattern "contract-first" pour les systèmes multi-agents critiques. Comment éviter que la couche conversationnelle ne dérive vers l'autorité.

---

## Niveau 4 : Preuves formelles — Comment c'est prouvé ?

### Concept J : Lean 4 et les invariants

**Message clé :** 5 invariants sont prouvés en Lean 4 avec 0 sorry (0 axiome non prouvé).

**Source :** `PROOF_INDEX.md`, `proofs/lean/Obsidia.lean`

| Invariant | Ce qu'il prouve |
|---|---|
| D1 | Les règles de gouvernance ne se contredisent pas |
| E2 | Le même input donne toujours le même vote (déterminisme) |
| G1 | La trace ne peut pas être modifiée après scellement |
| G2 | L'arbre de Merkle est cohérent |
| G3 | Aucune règle ne crée de contradiction circulaire |

**Ce que ça enseigne :** Ce que signifie "prouvé formellement" en mathématiques. La différence entre "testé" et "prouvé".

---

### Concept K : RFC3161 — L'ancrage temporel

**Message clé :** RFC3161 est le standard international de timestamp cryptographique. Il ancre la Merkle Root dans le temps de façon immuable et vérifiable par des tiers.

**Source :** `docs/RFC3161.md`

**Ce que ça enseigne :** La notion de "trusted timestamp". Pourquoi une signature seule ne suffit pas — il faut aussi prouver *quand* elle a été émise.

---

## Niveau 5 : Frontières et limites

### Concept L : P1 public vs production

**Message clé :** Ce repo est un périmètre de preuve public. PASS ici ≠ déploiement production complet.

**Source :** `PUBLIC_STATUS.md`, `docs/LIMITS.md`

**Ce que ça enseigne :** La différence entre un "audit perimeter" et un "production system". Pourquoi publier les preuves sans publier le moteur propriétaire.

---

### Concept M : World Call Gateway — Aucune sortie vers le monde réel

**Message clé :** En V4, egress_allowed=False et dry_run_only=True pour tous les appels monde. Le système ne peut pas agir dans le monde réel sans ticket souverain validé.

**Source :** `docs/WORLD_CALL_GATEWAY_INTEGRATION_REPORT.md`

**Ce que ça enseigne :** Le principe de "containment" — un agent IA ne peut pas agir dans le monde sans autorisation cryptographique explicite et tracée.

---

## Carte des connexions entre concepts

```
KERNEL X-108 ←[prouvé par]← Lean 4 (D1,E2,G1,G2,G3)
     ↑                      TLA+ (X108.tla, DistributedX108.tla)
SIGMA (agrège)
     ↑
Agents domaine (Bank/Trading/GPS/Ecom)
     ↑
BRODY (contexte advisory) ←[contrainte par]← BRODY_RESPONSE_CONTRACT
     ↑
Utilisateur
     
Décision → scellée par → Merkle Root → ancrée par → RFC3161
```

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
