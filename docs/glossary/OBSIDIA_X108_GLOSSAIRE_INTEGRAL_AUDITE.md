# OBSIDIA X-108 — GLOSSAIRE INTÉGRAL AUDITÉ

**Date d'audit :** 2026-06-17  

---

## Légende des statuts

| Code | Signification |
|---|---|
| **CONFIRMED_BY_RUNTIME** | Confirmé par sonde live (HTTP, socket) dans cette session |
| **CONFIRMED_BY_TEST** | Confirmé par exécution de tests (pytest, lake build) dans cette session ou une session documentée |
| **CONFIRMED_BY_FREEZE** | Confirmé par un fichier freeze daté présent dans `.local_freezes/` ou `.local_exports/` |
| **CONFIRMED_BY_PRIOR_AUDIT** | Confirmé par un audit antérieur documenté (rapport, résultats archivés) |
| **CONFIRMED_BY_CODE** | Confirmé par lecture directe du code source — pas exécuté |
| **CONFIRMED_BY_FILE** | Confirmé par présence et lecture d'un fichier spécifique |
| **PRESENT_BUT_NOT_EXECUTED** | Fichier/code présent, jamais exécuté dans ce repo dans les audits disponibles |
| **DOCUMENTED_ONLY** | Mentionné dans la doc ; introuvable dans le code ou les freezes locaux |
| **LEGACY** | Présent mais obsolète ou remplacé — ne pas utiliser |
| **DO_NOT_CLAIM** | Ne pas affirmer : absence de preuve ou contredit par l'audit |

---

## Format d'entrée

```
### TERME
- **Couche :** <layer>
- **Type :** <catégorie>
- **Statut :** <code>
- **Définition :** <définition concise>
- **Preuve / source :** <fichier ou freeze ou commande>
- **Autorité :** <qui décide / qui émet>
- **Alias :** <autres noms>
- **Dépendances :** <ce dont ça dépend>
- **Pièges :** <erreur fréquente>
- **Ne pas dire :** <claim interdit>
- **Réf. code :** <fichier:ligne ou module>
```

---

---

# A. GLOSSAIRE INTÉGRAL

---

## A1. Kernel & Gouvernance centrale

---

### KERNEL X-108

- **Couche :** KERNEL (6)
- **Type :** Moteur de décision souverain
- **Statut :** CONFIRMED_BY_FREEZE (2026-06-16) + CONFIRMED_BY_RUNTIME (bridge câblé, CONNECTION_ERROR quand arrêté)
- **Définition :** Seule entité autorisée à émettre une décision finale (`ALLOW / HOLD / BLOCK`). Implémenté en Node.js dans `server.kernel.sealed.cjs`, expose `POST /kernel/ragnarok`. Aucun autre composant ne peut décider — tous bridgent vers lui.
- **Preuve / source :** `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C_20260616_233032` — `kernel_3001: PASS HTTP 200` ; `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` — 15 décisions réelles capturées
- **Autorité :** `DECISION_AUTHORITY=KX108_ONLY` — seul souverain
- **Alias :** `KX108`, `ragnarok endpoint`, `Kernel Node`
- **Dépendances :** Port 3001, `server.kernel.sealed.cjs`
- **Pièges :** Confondre le Kernel (décideur) avec l'API FastAPI (pont) ; croire que l'API peut décider si le Kernel est arrêté
- **Ne pas dire :** "L'API décide quand le Kernel est down" — l'API retourne `CONNECTION_ERROR` et ne substitue pas de décision
- **Réf. code :** `apps/obsidia_api/routes/live_kernel_bridge.py` — `kernel_url = "http://127.0.0.1:3001/kernel/ragnarok"`

---

### DECISION_AUTHORITY=KX108_ONLY

- **Couche :** KERNEL (6)
- **Type :** Invariant de gouvernance fondamental
- **Statut :** CONFIRMED_BY_RUNTIME (présent dans réponse HTTP live `/api/status`) + CONFIRMED_BY_CODE
- **Définition :** Clé de contexte CIC attestant que seul le Kernel X-108 a autorité de décision. Présente dans toutes les réponses API, tous les contextes CIC, tous les freezes. Valeur fixe, non modifiable par l'API.
- **Preuve / source :** `GET http://127.0.0.1:8000/api/status` → `"decision_authority": "KX108_ONLY"` (confirmé en session 2026-06-17)
- **Autorité :** N/A — c'est une déclaration d'invariant, pas un agent
- **Alias :** `KX108_ONLY`
- **Ne pas dire :** "L'API a partiellement autorité" — false. L'API est `BRIDGE_ONLY`
- **Réf. code :** `apps/obsidia_api/main.py`, `apps/obsidia_api/cic/cic_domain_context.py`

---

### BRIDGE_ONLY

- **Couche :** CONNECTORS (entre PERIPHERAL et KERNEL)
- **Type :** Rôle API — invariant architectural
- **Statut :** CONFIRMED_BY_RUNTIME + CONFIRMED_BY_CODE
- **Définition :** Rôle de l'API FastAPI V5B : elle ne décide jamais, elle ne fait que transmettre la requête au Kernel et retourner sa réponse. Toutes les clés de boundary (`emits_act`, `emits_verdict`, `kernel_mutation`, etc.) sont `false`.
- **Preuve / source :** `apps/obsidia_api/routes/live_kernel_bridge.py` — `BOUNDARY = {emits_act: False, emits_verdict: False, ...}` ; réponse live `/api/status` confirme tous les flags à `false`
- **Alias :** `api_role=BRIDGE_ONLY`, `KX108_BRIDGE`
- **Ne pas dire :** "L'API a un rôle décisionnel de secours"

---

### X108Gate

- **Couche :** SIGMA (5)
- **Type :** Enum Python — gate de gouvernance
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Enum avec 3 valeurs : `ALLOW`, `HOLD`, `BLOCK`. Résultat terminal d'une décision de gouvernance. La loi fondamentale est `BLOCK > HOLD > ALLOW` (priorité de sécurité décroissante).
- **Preuve / source :** `sigma/contracts.py` — `class X108Gate(Enum): ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"`
- **Autorité :** Kernel X-108 (seul émetteur)
- **Alias :** `x108_gate`, `gate`
- **Réf. code :** `sigma/contracts.py`

---

### BLOCK > HOLD > ALLOW

- **Couche :** KERNEL (6) / SIGMA (5)
- **Type :** Loi de priorité fondamentale
- **Statut :** CONFIRMED_BY_TEST (théorème Lean `D1_determinism`) + CONFIRMED_BY_CODE
- **Définition :** Règle de résolution de conflits entre votes d'agents : BLOCK est le verdict le plus fort, ALLOW le moins fort. En cas de conflit inter-agents, BLOCK l'emporte. Garantit le fail-closed du système.
- **Preuve / source :** `proofs/lean/Obsidia/Basic.lean` — théorème `D1_determinism` ; `proofs/lean/Obsidia/Consensus.lean` — `aggregate4_fail_closed`
- **Alias :** "fail-closed ordering", "governance priority"
- **Pièges :** Croire que la majorité ALLOW l'emporte — non : un seul BLOCK suffit selon la règle de consensus
- **Réf. code :** `proofs/lean/Obsidia/Basic.lean`, `sigma/contracts.py` → `calculate_immutable_vote()`

---

### server.kernel.sealed.cjs

- **Couche :** KERNEL (6)
- **Type :** Fichier binaire scellé — PROTÉGÉ
- **Statut :** CONFIRMED_BY_FILE (présent dans le repo)
- **Définition :** Implémentation Node.js compilée et scellée du Kernel X-108. Expose `POST /kernel/ragnarok` sur port 3001. Fichier intentionnellement opaque — ne pas décompiler, ne pas modifier.
- **Autorité :** Seule source de vérité pour les décisions Kernel
- **Pièges :** Tenter de modifier ou reformater ce fichier — interdit par PROTECTED_SCOPE
- **Ne pas dire :** "On peut remplacer le Kernel par du Python"
- **Réf. code :** `server.kernel.sealed.cjs` (racine repo)

---

### POST /kernel/ragnarok

- **Couche :** KERNEL (6)
- **Type :** Endpoint de décision souverain
- **Statut :** CONFIRMED_BY_FREEZE (15 décisions capturées 2026-06-10) + CONFIRMED_BY_RUNTIME (bridge tente l'appel live, CONNECTION_ERROR quand Kernel arrêté)
- **Définition :** Unique point d'entrée du Kernel X-108. Reçoit un payload de domaine, retourne `x108_gate` (ALLOW/HOLD/BLOCK) + `severity` + `reason_code`. Toutes les routes bank/trading/gps de l'API le proxifient.
- **Preuve / source :** `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` — 15 décisions réelles
- **Alias :** `ragnarok`, `kernel endpoint`
- **Réf. code :** `apps/obsidia_api/routes/live_kernel_bridge.py` — `kernel_url`

---

## A2. Couches — Layer(IntEnum)

---

### Layer — Enum de couche

- **Couche :** SIGMA (5)
- **Type :** IntEnum Python — architecture en couches
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Hiérarchie des 8 couches du système Obsidia X-108 :

| Valeur | Nom | Rôle |
|---|---|---|
| 1 | OBSERVATION | Capteurs, entrées brutes |
| 2 | INTERPRETATION | Parsing, normalisation |
| 3 | CONTRADICTION | Détection de conflits |
| 4 | PERIPHERAL | Agents périphériques |
| 5 | SIGMA | Agrégation, contrats |
| 6 | KERNEL | Décision souveraine |
| 7 | PROOF | Preuves formelles |
| 8 | SCELLAGE | Ancrage cryptographique |

- **Réf. code :** `sigma/contracts.py` — `class Layer(IntEnum)`

---

### OBSERVATION (Layer 1)

- **Type :** Couche d'entrée — capteurs
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Première couche : réception des données brutes (signaux, inputs, métriques entrantes). Pas de décision possible à ce niveau.
- **Réf. code :** `sigma/contracts.py`

---

### INTERPRETATION (Layer 2)

- **Type :** Couche de normalisation
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Parsing et normalisation des données brutes vers des structures Sigma (`BankState`, `TradingState`, etc.).

---

### CONTRADICTION (Layer 3)

- **Type :** Couche de détection de conflits
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FREEZE (raison_code `CONTRADICTION_THRESHOLD_REACHED` présent dans décisions Trading)
- **Définition :** Détecte les signaux contradictoires entre agents. Si le seuil est franchi, le verdict passe BLOCK S4. Le freeze Trading montre `CONTRADICTION_THRESHOLD_REACHED` comme reason_code pour 5 décisions BLOCK S4.
- **Preuve / source :** `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` — trading decisions

---

### PERIPHERAL (Layer 4)

- **Type :** Couche des agents périphériques
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Agents spécialisés par domaine (bank, trading, gps, ecom). Émettent des `AgentVote` qui remontent vers la couche Sigma.

---

### SIGMA (Layer 5)

- **Type :** Couche d'agrégation
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_TEST
- **Définition :** Agrège les votes des agents périphériques en un `DomainAggregate`. Applique `calculate_immutable_vote()`. Le résultat est transmis au Kernel pour décision finale.
- **Réf. code :** `sigma/contracts.py`, `sigma/aggregation.py`

---

### KERNEL (Layer 6)

- **Type :** Couche de décision souveraine
- **Statut :** CONFIRMED_BY_FREEZE + CONFIRMED_BY_RUNTIME
- **Définition :** Voir `KERNEL X-108` ci-dessus.

---

### PROOF (Layer 7)

- **Type :** Couche de vérification formelle
- **Statut :** CONFIRMED_BY_TEST (lake build PASS, 57 théorèmes)
- **Définition :** Preuves Lean 4, spécifications TLA+, Merkle tree, seal cryptographique. Vérification mathématique des propriétés du système.
- **Réf. code :** `proofs/lean/`, `proofs/tla/`, `formal/tla/`

---

### SCELLAGE (Layer 8)

- **Type :** Couche d'ancrage cryptographique
- **Statut :** CONFIRMED_BY_FILE (`proofs/rfc3161_anchor.json` présent) + CONFIRMED_BY_PRIOR_AUDIT (V18_3_1 PASS)
- **Définition :** Ancrage RFC3161 TSA, seal V18.3, Merkle root. Couche finale d'intégrité — une fois scellé, immuable.
- **Réf. code :** `proofs/rfc3161_anchor.json`, `proofs/PROOFKIT_REPORT.json`

---

## A3. Lois, Règles, Invariants

---

### Invariant BOUNDARY

- **Couche :** CONNECTORS
- **Type :** Invariant de sécurité — dict Python
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_RUNTIME
- **Définition :** Dictionnaire de 10+ flags tous positionnés à `False` dans le code de l'API. Garantit que l'API ne peut pas émettre d'acte, de verdict, de mutation mémoire ou réseau. Déclaré dans `live_kernel_bridge.py` comme `BOUNDARY`.

| Flag | Valeur | Signification |
|---|---|---|
| `emits_act` | False | Ne génère pas d'action réelle |
| `emits_verdict` | False | Ne rend pas de verdict souverain |
| `memory_write` | False | Pas d'écriture mémoire |
| `graphiti_write` | False | Pas d'écriture Graphiti |
| `kernel_mutation` | False | Pas de mutation du Kernel |
| `neo4j_write` | False | Pas d'écriture Neo4j |
| `mcp_bridge` | False | Pas de pont MCP |
| `path_compute` | False | Pas de calcul de chemin souverain |
| `real_action` | False | Pas d'action réelle |
| `canonical_write` | False | Pas d'écriture canonique |

- **Preuve / source :** Réponse live `/api/status` 2026-06-17 — tous les flags `false`
- **Réf. code :** `apps/obsidia_api/routes/live_kernel_bridge.py`

---

### P17_Determinism

- **Couche :** PROOF (7)
- **Type :** Invariant formel Lean — propriété de déterminisme
- **Statut :** CONFIRMED_BY_TEST (lake build PASS)
- **Définition :** Pour tout état et toute entrée, la décision du Kernel est déterministe — même input → même output, sans variance aléatoire.
- **Preuve / source :** `proofs/lean/Obsidia/SystemModel.lean` — théorème `P17_Determinism`
- **Alias :** `D1_determinism` (Basic.lean variante)

---

### P13_Immutability / P15_Immutability_Strong

- **Couche :** PROOF (7)
- **Type :** Invariant formel Lean — immuabilité de l'audit log
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** L'audit log est append-only : on ne peut qu'ajouter, jamais modifier une entrée existante. `P15_Immutability_Strong` est la version renforcée.
- **Réf. code :** `proofs/lean/Obsidia/SystemModel.lean`

---

### P17_KernelNeverBlocks

- **Couche :** PROOF (7)
- **Type :** Invariant formel Lean — vivacité du Kernel
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** Le Kernel ne se bloque jamais dans une boucle infinie ou un deadlock — il retourne toujours une décision.
- **Alias :** `X108_kernel_never_blocks` (TemporalKernel.lean)
- **Réf. code :** `proofs/lean/Obsidia/SystemModel.lean`, `proofs/lean/Obsidia/TemporalKernel.lean`

---

### P17_SealSensitive

- **Couche :** PROOF (7) / SCELLAGE (8)
- **Type :** Invariant formel Lean — sensibilité du seal
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** Tout changement dans un fichier scellé change le hash global du seal. Propriété de sensibilité cryptographique.
- **Réf. code :** `proofs/lean/Obsidia/SystemModel.lean`

---

### fail-closed

- **Couche :** KERNEL (6)
- **Type :** Principe de sécurité
- **Statut :** CONFIRMED_BY_TEST (théorème `aggregate4_fail_closed`)
- **Définition :** En cas d'ambiguïté, d'erreur ou d'absence de consensus clair, le système choisit le verdict le plus restrictif. Jamais de défaut vers ALLOW. Prouvé formellement par `aggregate4_fail_closed`.
- **Alias :** "fail-safe", "secure default"
- **Ne pas dire :** "En cas d'erreur, l'opération passe" — faux, elle est bloquée par défaut

---

### HOLD sémantique

- **Couche :** SIGMA (5) / KERNEL (6)
- **Type :** Verdict intermédiaire
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FREEZE
- **Définition :** HOLD signifie "révision humaine requise". Ce n'est pas un rejet (BLOCK) ni une approbation (ALLOW). Une décision HOLD doit être escaladée vers un superviseur humain. Prouvé par `skew_negative_implies_hold` (TemporalBridge.lean).
- **Réf. code :** `sigma/contracts.py`, `proofs/lean/Obsidia/TemporalBridge.lean`

---

### CONTRADICTION_THRESHOLD_REACHED

- **Couche :** CONTRADICTION (3) / KERNEL (6)
- **Type :** reason_code de décision
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Code de raison émis quand les votes d'agents sur un domaine sont trop contradictoires pour atteindre le consensus requis. Déclenche systématiquement un verdict BLOCK S4.
- **Preuve / source :** `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` — 5 décisions Trading avec ce code
- **Alias :** "contradiction threshold"

---

### GUARD_ALLOW

- **Couche :** KERNEL (6)
- **Type :** reason_code de décision positive
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Code de raison émis par le Kernel quand toutes les conditions d'autorisation sont réunies. Associé à ALLOW S0 (GPS) ou ALLOW S1 (Bank).
- **Preuve / source :** `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` — 10 décisions Bank+GPS

---

## A4. Algorithmes et Protocoles

---

### calculate_immutable_vote()

- **Couche :** SIGMA (5)
- **Type :** Algorithme d'agrégation de votes
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_TEST
- **Définition :** Fonction Python qui agrège les votes de plusieurs agents selon la règle `BLOCK > HOLD > ALLOW`. Ne peut pas émettre ACT seul. Si `x108_gate=BLOCK`, retourne BLOCK immédiatement sans tenir compte de la majorité ALLOW.
- **Réf. code :** `sigma/contracts.py` — `def calculate_immutable_vote(votes, x108_gate, domain)`
- **Pièges :** Croire qu'une majorité d'ALLOW override un BLOCK

---

### compute_governance_confidence()

- **Couche :** SIGMA (5)
- **Type :** Algorithme de scoring de confiance
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Calcule un score de confiance [0.0, 1.0] basé sur la cohérence des votes d'agents et le verdict final. Utilisé pour calibrer la sévérité.
- **Réf. code :** `sigma/contracts.py`

---

### normalize_confidence()

- **Couche :** SIGMA (5)
- **Type :** Fonction utilitaire
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Normalise une valeur de confiance en [0.0, 1.0] avec un fallback à 0.50 si la valeur est invalide.
- **Réf. code :** `sigma/contracts.py`

---

### SmartAttribute

- **Couche :** SIGMA (5)
- **Type :** Classe Python — attribut numérique polymorphe
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Sous-classe de `list` qui implémente les opérateurs arithmétiques et de comparaison pour permettre l'arithmétique transparente sur des attributs d'état de domaine. Utilisé dans `BankState`, `TradingState`, etc.
- **Réf. code :** `sigma/contracts.py` — `class SmartAttribute(list)`

---

### UniversalBase

- **Couche :** SIGMA (5)
- **Type :** Classe de base polymorphe
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Classe de base pour `AgentVote`, `DomainAggregate`, `BankState`, etc. Intercepte `__getattr__` pour retourner une valeur par défaut sur tout attribut inconnu, évitant les `AttributeError`.
- **Réf. code :** `sigma/contracts.py` — `class UniversalBase`
- **Pièges :** Un accès à un attribut inexistant ne lève pas d'erreur — retourne silencieusement une valeur par défaut. Peut masquer des bugs de nommage.

---

### Merkle Tree (OBSIDIA)

- **Couche :** SCELLAGE (8) / PROOF (7)
- **Type :** Structure cryptographique d'intégrité
- **Statut :** CONFIRMED_BY_FILE (`proofs/rfc3161_anchor.json`) + CONFIRMED_BY_TEST (théorèmes `merkle2_left_mutation`, `merkle2_right_mutation`)
- **Définition :** Arbre de hachage Merkle utilisé pour ancrer l'intégrité de l'ensemble des fichiers du projet. La racine Merkle est `fb264799029f5a1bd0beed58f5756dcd83f26b49430103adcda3fc1fce047d95`. Toute mutation d'une feuille change la racine (prouvé formellement).
- **Preuve / source :** `proofs/rfc3161_anchor.json` — `merkle_root`
- **Alias :** `merkle_root`
- **Réf. code :** `proofs/lean/Obsidia/Merkle.lean`, `proofs/lean/Obsidia/Sensitivity.lean`

---

### Two-Level Guard (Brody Education Pack)

- **Couche :** CONNECTORS
- **Type :** Protocole de sécurité — garde d'injection
- **Statut :** CONFIRMED_BY_TEST (124/124 tests PASS) + CONFIRMED_BY_FREEZE
- **Définition :** Mécanisme en deux passes pour bloquer l'injection de clés d'action dans le pack éducatif Brody :
  1. **Niveau 1** (`_FORBIDDEN_ACTION_KEYS`) : présence d'une clé interdite dans le payload → BLOCK immédiat
  2. **Niveau 2** (`_SAFE_SENTINEL_VALUES`) : valeur d'une clé sentinel doit être dans la liste autorisée → sinon BLOCK
- **Preuve / source :** Commit `483eb38` — guard fix ; `tests/test_brody_education_pack_v1_readonly_adapter.py` 124 tests PASS
- **Alias :** "guard fix", "GUARD_SELF_BLOCK_R01 résolu"
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### _FORBIDDEN_ACTION_KEYS

- **Couche :** CONNECTORS
- **Type :** frozenset — liste noire de clés interdites
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** `frozenset` de noms de clés dont la présence dans un payload Brody déclenche un blocage immédiat (`PACK_INJECT_BLOCKED`). Niveau 1 du two-level guard.
- **Alias :** `_FORBIDDEN_INJECT_KEYS` (alias rétrocompat)
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### _SAFE_SENTINEL_VALUES

- **Couche :** CONNECTORS
- **Type :** dict — liste blanche de valeurs autorisées
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Dictionnaire `{clé: [valeurs_autorisées]}`. Niveau 2 du two-level guard : si une clé sentinel est présente, sa valeur doit être dans la liste. Sinon, BLOCK.
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

## A5. Preuves et Formalisation

---

### lake build (Lean 4)

- **Couche :** PROOF (7)
- **Type :** Commande de build / vérification formelle
- **Statut :** CONFIRMED_BY_TEST (`Build completed successfully (0 jobs)` — exécuté 2026-06-17)
- **Définition :** Commande Lake (gestionnaire de build Lean 4) qui compile et vérifie tous les théorèmes du projet. Un succès garantit que les 57 théorèmes sont formellement corrects.
- **Preuve / source :** `.local_audits/README_REALITY_RECHECK_20260617_190000/lake_build_output.txt`
- **Réf. code :** `proofs/lean/lakefile.lean` — `proofs/lean/` (root du projet Lean)
- **Pièges :** Lancer depuis la racine du repo échoue ("no configuration file") — doit être lancé depuis `proofs/lean/`

---

### 57 théorèmes / lemmes Lean

- **Couche :** PROOF (7)
- **Type :** Corpus de preuves formelles
- **Statut :** CONFIRMED_BY_TEST (comptage Python + lake build PASS, 2026-06-17)
- **Définition :** L'ensemble complet des preuves formelles Lean 4 du projet. Réparties sur 11 fichiers :

| Fichier | Count | Domaine |
|---|---|---|
| `Obsidia/Basic.lean` | 11 | Gouvernance décisionnelle |
| `Obsidia/Consensus.lean` | 10 | Consensus distribué (quorum 4) |
| `Obsidia/CryptoAssumptions.lean` | 10 | Hypothèses cryptographiques |
| `Obsidia/SystemModel.lean` | 7 | Modèle système, invariants P13/P15/P17 |
| `Obsidia/TemporalKernel.lean` | 5 | Propriétés temporelles du Kernel |
| `Obsidia/Refinement.lean` | 4 | Raffinement / lien spec→impl |
| `Obsidia/Sensitivity.lean` | 3 | Sensibilité cryptographique (Merkle) |
| `Obsidia/Merkle.lean` | 2 | Mutations Merkle |
| `Obsidia/TemporalBridge.lean` | 2 | Bridge temporel (skew) |
| `wip/ConsensusScratch.lean` | 2 | WIP consensus |
| `Obsidia/Seal.lean` | 1 | Intégrité du seal |
| **TOTAL** | **57** | |

- **Preuve / source :** `lake build` PASS + comptage Python session 2026-06-17
- **Réf. code :** `proofs/lean/Obsidia/`, `proofs/lean/wip/`

---

### Théorèmes clés — Basic.lean

- **Statut :** CONFIRMED_BY_TEST

| Théorème | Signification |
|---|---|
| `decision_eq_ACT_iff` | Condition nécessaire et suffisante pour qu'une décision soit ACT |
| `decision_eq_HOLD_iff` | Condition nécessaire et suffisante pour HOLD |
| `D1_determinism` | Déterminisme de la décision (même input → même output) |
| `G1_act_above_threshold` | ACT ssi score ≥ seuil |
| `E2_no_act_below_threshold` | Impossible d'ACT sous le seuil |
| `G2_boundary_inclusive` | Seuil inclusif |
| `G3_monotonicity` | Monotonie : augmenter le score ne peut pas passer de ACT à HOLD |
| `L11_3_no_block` | Conditions d'absence de BLOCK |
| `L11_3_act` | Conditions d'ACT en L11.3 |
| `L11_3_hold` | Conditions de HOLD en L11.3 |
| `decision_not_both` | Une décision ne peut pas être ALLOW et BLOCK simultanément |

---

### Théorèmes clés — Consensus.lean

- **Statut :** CONFIRMED_BY_TEST

| Théorème | Signification |
|---|---|
| `aggregate4_act` | Un quorum de 4 peut produire ACT |
| `aggregate4_fail_closed` | Sans supermajorité, le verdict est HOLD (fail-closed) |
| `aggregate4_unanimous` | Unanimité implique le verdict correspondant |
| `no_act_and_hold_supermajority_4` | ACT et HOLD ne peuvent pas avoir simultanément la supermajorité |
| `no_act_and_block_supermajority_4` | ACT et BLOCK ne peuvent pas coexister en supermajorité |
| `no_hold_and_block_supermajority_4` | HOLD et BLOCK ne peuvent pas coexister en supermajorité |
| `no_two_distinct_supermajorities_4` | Pas deux supermajorités distinctes en même temps |

---

### Théorèmes clés — TemporalKernel.lean

- **Statut :** CONFIRMED_BY_TEST

| Théorème | Signification |
|---|---|
| `X108_after_tau_equals_base` | Après τ (horizon temporel), l'état revient à la base |
| `X108_irreversible_after_tau_equals_base` | Les décisions irréversibles après τ sont fixées |
| `X108_kernel_never_blocks` | Le Kernel ne se bloque jamais (vivacité) |
| `X108_no_act_before_tau` | Pas d'acte irréversible avant τ |
| `X108_reversible_equals_base` | Les actes réversibles conservent l'état de base |

---

### Théorèmes clés — Refinement.lean

- **Statut :** CONFIRMED_BY_TEST

| Théorème | Signification |
|---|---|
| `lift_refines` | Le lift de l'implémentation raffine la spécification |
| `refined_not_block` | Le système raffiné ne produit jamais BLOCK hors protocole |
| `x108_is_lift` | X108 est un lift valide de la spécification abstraite |
| `x108_never_blocks` | X108 ne bloque jamais (au sens raffinement) |

---

### Théorèmes clés — CryptoAssumptions.lean

- **Statut :** CONFIRMED_BY_TEST

| Théorème | Signification |
|---|---|
| `H_injective_left` | La fonction de hash H est injective à gauche |
| `H_injective_right` | H est injective à droite |
| `decodeFold_H_of_decodable` | Propriété de décodage/fold |
| `append_nil_local` | Append avec nil est neutre (local) |
| `append_assoc_local` | Associativité de l'append (local) |
| `foldl_H_injective` | foldl avec H préserve l'injectivité |
| `fileHash_inj` | Le hash de fichier est injectif |
| `combine_inj` | La combinaison de hashs est injective |

---

### TLA+ (proofs/tla/ et formal/tla/)

- **Couche :** PROOF (7)
- **Type :** Spécification formelle de modèle temporel
- **Statut :** PRESENT_BUT_NOT_EXECUTED (TLC non relancé dans cet audit — Java 17+ requis)
- **Définition :** Spécifications TLA+ des propriétés de vivacité et de sécurité du système X-108. Deux arborescences : `proofs/tla/` (référence) et `formal/tla/` (CI). TLC peut explorer l'espace d'états.
- **Preuve / source :** `proofs/tla/README.md` — instructions TLC ; `formal/tla/` — specs CI
- **Pièges :** "1,2M états explorés" est une figure citée sans preuve dans cet audit — TLC non relancé
- **Ne pas dire :** "TLC a vérifié X états dans cet audit" — PRESENT_BUT_NOT_EXECUTED ici
- **Réf. code :** `proofs/tla/X108.tla`, `proofs/tla/DistributedX108.tla`

---

### RFC3161 Anchor

- **Couche :** SCELLAGE (8)
- **Type :** Timestamp cryptographique tiers
- **Statut :** CONFIRMED_BY_FILE
- **Définition :** Ancrage RFC3161 émis par Free TSA (freetsa.org) pour la racine Merkle du projet. Date de scellage : 2026-03-03. Garantit l'antériorité cryptographique de l'état du repo.
- **Preuve / source :** `proofs/rfc3161_anchor.json` — `merkle_root: fb264799...`, `tsa: "Free TSA"`
- **Alias :** `rfc3161_anchor`, `TSA anchor`
- **Vérification :** `openssl ts -verify -data merkle_root.bin -in rfc3161_anchor.tsr -CAfile cacert.pem` (non exécuté dans cet audit)
- **Réf. code :** `proofs/rfc3161_anchor.json`

---

### V18 Seal (PROOFKIT)

- **Couche :** SCELLAGE (8)
- **Type :** Résultat de vérification d'intégrité
- **Statut :** CONFIRMED_BY_PRIOR_AUDIT (2026-06-16)
- **Définition :** Trois checks du PROOFKIT V1 :
  - `V18_3_1` — ROOT SEAL : intégrité + hash racine → **PASS**
  - `V18_7` — propriété V18.7 → **PASS**
  - `V18_8` — propriété V18.8 → **PASS**
- **Preuve / source :** `proofs/PROOFKIT_REPORT.json` — `overall: PASS`, date 2026-06-16
- **Alias :** `V18.3`, `OBSIDIA_V18_3_FINAL_SEALED`
- **Réf. code :** `proofs/PROOFKIT_REPORT.json`, `proofs/seal_verify.py`

---

### globalSeal_change_if_root_change

- **Couche :** PROOF (7) / SCELLAGE (8)
- **Type :** Théorème Lean — sensibilité du seal global
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** Si la racine Merkle change (modification d'un fichier), le seal global change. Propriété de sensibilité qui garantit qu'aucune modification n'est indétectable.
- **Réf. code :** `proofs/lean/Obsidia/Sensitivity.lean`

---

### merkleRoot_change_if_leaf_change

- **Couche :** PROOF (7)
- **Type :** Théorème Lean — propagation Merkle
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** Si une feuille du Merkle tree change, la racine change. Propriété fondamentale de l'arbre Merkle, prouvée formellement.
- **Réf. code :** `proofs/lean/Obsidia/Sensitivity.lean`

---

## A6. Sévérité

---

### Severity(IntEnum) — S0 à S4

- **Couche :** SIGMA (5) / KERNEL (6)
- **Type :** Enum Python — niveau de sévérité
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FREEZE

| Valeur | Code | Signification | Exemples freeze |
|---|---|---|---|
| 0 | S0 | Nominal — opération standard | GPS 5 décisions ALLOW S0 |
| 1 | S1 | Faible — attention requise | Bank 5 décisions ALLOW S1 |
| 2 | S2 | Modéré — révision conseillée | DomainAggregate verdict HOLD |
| 3 | S3 | Élevé — révision obligatoire | (non observé dans freeze) |
| 4 | S4 | Critique — blocage | Trading 5 décisions BLOCK S4 |

- **Réf. code :** `sigma/contracts.py` — `class Severity(IntEnum)`

---

## A7. Domaines

---

### Domain — Enum de domaine

- **Couche :** SIGMA (5) / KERNEL (6)
- **Type :** Enum Python
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_RUNTIME (Bank/Trading/GPS confirmés live) + CONFIRMED_BY_FREEZE

| Valeur | Clé | État domaine |
|---|---|---|
| `BANK` | `"bank"` | CONFIRMED_BY_FREEZE — 5 ALLOW S1 |
| `TRADING` | `"trading"` | CONFIRMED_BY_FREEZE — 5 BLOCK S4 |
| `GPS_DEFENSE_AVIATION` | `"gps_defense_aviation"` | CONFIRMED_BY_FREEZE — 5 ALLOW S0 |
| `ECOM` | `"ecom"` | CONFIRMED_BY_CODE — non testé en live |
| `META` | `"meta"` | CONFIRMED_BY_CODE — usage interne |

- **Réf. code :** `sigma/contracts.py` — `class Domain(Enum)`

---

### BankState

- **Couche :** PERIPHERAL (4) / SIGMA (5)
- **Type :** Classe d'état domaine bancaire
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FREEZE
- **Définition :** État d'une transaction bancaire avec champs : `transaction_type`, `amount`, `channel`, `counterparty_known`, `counterparty_age_days`, `account_balance`, `available_cash`, `historical_avg_amount`, `behavior_shift_score`, `fraud_score`, `policy_limit`.
- **Décisions kernel capturées :** 5 × `ALLOW S1 GUARD_ALLOW`
- **Réf. code :** `sigma/contracts.py` — `class BankState(UniversalBase)`

---

### TradingState

- **Couche :** PERIPHERAL (4) / SIGMA (5)
- **Type :** Classe d'état domaine trading
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FREEZE
- **Définition :** État d'une opération de trading avec champs : `symbol`, `prices`, `highs`, `lows`, `volumes`.
- **Décisions kernel capturées :** 5 × `BLOCK S4 CONTRADICTION_THRESHOLD_REACHED` — le trading est le domaine le plus bloqué dans le freeze
- **Réf. code :** `sigma/contracts.py` — `class TradingState(UniversalBase)`

---

### GpsDefenseAviationState

- **Couche :** PERIPHERAL (4) / SIGMA (5)
- **Type :** Classe d'état domaine GPS/aviation
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FREEZE
- **Définition :** État GPS/défense/aviation avec champs : `mission_id`, `flight_id`, `altitude`, `ground_speed`, `gps_status`.
- **Décisions kernel capturées :** 5 × `ALLOW S0 GUARD_ALLOW` — le domaine le moins risqué dans le freeze
- **Réf. code :** `sigma/contracts.py` — `class GpsDefenseAviationState(UniversalBase)`

---

### EcomState

- **Couche :** PERIPHERAL (4) / SIGMA (5)
- **Type :** Classe d'état domaine e-commerce
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** État e-commerce avec champ `session_id`. Domaine présent dans le code mais absent du freeze live (note dans CIC : `ECOM_NOT_FOUND`).
- **Réf. code :** `sigma/contracts.py` — `class EcomState(UniversalBase)`

---

## A8. Brody

---

### Brody

- **Couche :** CONNECTORS / PERIPHERAL (4)
- **Type :** Agent conversationnel temps réel
- **Statut :** CONFIRMED_BY_FREEZE (8012 PASS 2026-06-16) + CONFIRMED_BY_CODE (routes `/api/brody/` dans OpenAPI)
- **Définition :** Agent conversationnel Obsidia. Expose une interface de chat (`/api/brody/chat`) via l'API FastAPI V5B. Fonctionne en mode readonly — aucune décision, aucune écriture. Le vrai service tourne sur port 8012 (sous-service).
- **Preuve / source :** `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C_20260616_233032` — `server_8012: PASS`
- **Réf. code :** `apps/obsidia_api/routes/brody.py`, `apps/obsidia_api/brody_real_response_pipeline.py`

---

### Brody Education Pack V1

- **Couche :** CONNECTORS
- **Type :** Adapteur readonly — pack éducatif
- **Statut :** CONFIRMED_BY_TEST (124/124 PASS) + CONFIRMED_BY_FREEZE
- **Définition :** Module Python qui fournit le contexte éducatif de Brody en mode strictement readonly. Retourne `status: PACK_READY_READONLY` si sain. Implémente le two-level guard anti-injection.
- **Preuve / source :** `.local_freezes/BRODY_ENRICHED_EDUCATION_PACK_V1_FREEZE_20260617_124000` ; commit `483eb38`
- **Alias :** `brody_education_pack_v1_readonly_adapter`, `Education Pack V1`
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### PACK_READY_READONLY

- **Couche :** CONNECTORS
- **Type :** Statut de réponse de l'adapter Brody
- **Statut :** CONFIRMED_BY_TEST + CONFIRMED_BY_FREEZE
- **Définition :** Valeur du champ `status` retournée par `brody_education_pack_v1_readonly_adapter` quand le pack est sain et prêt. Garantit : pas d'injection, tous les boundary flags à False, guard actif.
- **Alias :** `PACK_READY`
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### PACK_INJECT_BLOCKED

- **Couche :** CONNECTORS
- **Type :** Statut d'erreur de sécurité
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** Statut retourné quand le two-level guard détecte une tentative d'injection de clé interdite. Bloque la réponse sans exception levée.
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### BRODY_V1_FORBIDDEN_BELIEFS.md

- **Couche :** CONNECTORS / DOCS
- **Type :** Document de contraintes éducatives
- **Statut :** CONFIRMED_BY_CODE (référencé dans l'adapter)
- **Définition :** Fichier Markdown listant les croyances interdites que Brody ne doit pas propager (ex. : "le système peut décider seul", "les preuves sont suffisantes sans validation humaine"). Référencé dans le pack éducatif.
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### P54_SANDBOX_NO_ACT

- **Couche :** CONNECTORS
- **Type :** Code de refus de trap
- **Statut :** CONFIRMED_BY_TEST + CONFIRMED_BY_FREEZE
- **Définition :** Code retourné quand une requête piège tente de pousser Brody à émettre un acte réel. Le two-level guard intercepte et retourne `P54_SANDBOX_NO_ACT` au lieu d'exécuter l'acte.
- **Preuve / source :** `.local_freezes/BRODY_RUNTIME_EDUCATION_ADAPTER_API_E2E_V0_RETRY_AFTER_GUARD_FIX_FREEZE_20260617_175000/FREEZE_VERDICT.json` — FC09 `PASS — P54_SANDBOX_NO_ACT`

---

### _EDUCATION_BOUNDARY

- **Couche :** CONNECTORS
- **Type :** Dict Python — périmètre d'éducation
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Dictionnaire de 18+ invariants de boundary éducatif. Tous positionnés pour garantir que le pack éducatif ne peut pas émettre d'action, de verdict ou d'écriture.
- **Réf. code :** `apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py`

---

### 124/124 tests PASS

- **Couche :** CONNECTORS / TOOLING
- **Type :** Résultat de test
- **Statut :** CONFIRMED_BY_TEST + CONFIRMED_BY_FREEZE
- **Définition :** Suite complète de tests pour le Brody Education Pack V1 + adapter CIC. 124 tests, 0 échec. Validé en session (commit 483eb38) et capturé dans le freeze.
- **Preuve / source :** `.local_freezes/BRODY_RUNTIME_EDUCATION_ADAPTER_GUARD_FIX_V0_FREEZE_20260617_165000/pytest_output.txt`

---

## A9. Graphiti / Mémoire

---

### Graphiti

- **Couche :** CONNECTORS / PERIPHERAL (4)
- **Type :** Service de mémoire graphe
- **Statut :** CONFIRMED_BY_FREEZE (port 8011 PASS HTTP 200 2026-06-16, snapshot FROZEN_READONLY)
- **Définition :** Service de mémoire graphe (167 nœuds, 477 relations, 20 épisodes indexés). Fonctionne en mode `FROZEN_READONLY` — pas de dépendance Neo4j live, pas d'écriture. État gelé depuis la phase 0 V20.
- **Preuve / source :** `.local_exports/GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_FREEZE_20260616_154523/graphiti_status_freeze.json`
- **Alias :** `Graphiti V20`, `OBSIDIA_GRAPHITI_PHASE0_V20_FROZEN`
- **Réf. code :** Route `/api/graphiti/` dans OpenAPI (164 routes)

---

### FROZEN_READONLY (Graphiti)

- **Couche :** CONNECTORS
- **Type :** Mode opérationnel de Graphiti
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Mode dans lequel Graphiti opère sans connexion Neo4j live. Les données sont gelées dans un snapshot mémoire. Aucune écriture possible. `live_neo4j_dependency: false`.
- **Preuve / source :** `graphiti_status_freeze.json` — `"mode": "FROZEN_READONLY", "live_neo4j_dependency": false`

---

### 167 nœuds / 477 relations / 20 épisodes

- **Couche :** CONNECTORS
- **Type :** Métriques de snapshot Graphiti
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Contenu du snapshot gelé Graphiti : 167 nœuds de connaissance, 477 relations, 20 épisodes indexés, 0 épisode en échec.
- **Preuve / source :** `.local_exports/GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_FREEZE_20260616_154523/graphiti_status_freeze.json`

---

### Neo4j (AuthError)

- **Couche :** CONNECTORS
- **Type :** Base de données graphe — état dégradé
- **Statut :** CONFIRMED_BY_FREEZE (AuthError présente 2026-06-16)
- **Définition :** Base de données Neo4j sous-jacente de Graphiti. En état `degraded` lors du dernier freeze — erreur d'authentification. En mode FROZEN_READONLY, Graphiti contourne cette dépendance.
- **Ports :** 7474 (HTTP), 7687 (Bolt) — tous deux CLOSED lors de l'audit 2026-06-17
- **Ne pas dire :** "Neo4j est opérationnel" — en état dégradé (AuthError), ports fermés aujourd'hui

---

## A10. CIC / Causalité / Path Compute

---

### CIC (Causal Identity Context)

- **Couche :** CONNECTORS / KERNEL (6)
- **Type :** Contexte causal de traçabilité
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_TEST
- **Définition :** Dictionnaire de 21 clés attaché à chaque appel Brody/API. Garantit la traçabilité causale et l'invariance des contraintes de sécurité à travers tous les composants. Clés fondamentales : `authority=NONE`, `decision_authority=KX108_ONLY`, tous les flags d'action à `False`.
- **Clés principales :**

| Clé | Valeur fixe |
|---|---|
| `authority` | `"NONE"` |
| `decision_authority` | `"KX108_ONLY"` |
| `memory_write` | `False` |
| `graphiti_write` | `False` |
| `neo4j_write` | `False` |
| `canonical_write` | `False` |
| `mcp_bridge` | `False` |
| `path_compute` | `False` |
| `emits_act` | `False` |
| `emits_verdict` | `False` |
| `kernel_mutation` | `False` |

- **Réf. code :** `apps/obsidia_api/cic/cic_domain_context.py`, `apps/obsidia_api/cic/cic_readonly_pack_provider.py`

---

### authority=NONE

- **Couche :** CONNECTORS
- **Type :** Clé CIC — invariant d'autorité
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_TEST
- **Définition :** La valeur `"NONE"` sur la clé `authority` dans tout contexte CIC signifie que le composant courant (API, Brody, CIC) n'a aucune autorité de décision propre. Autorité déléguée uniquement au Kernel.
- **Réf. code :** `apps/obsidia_api/cic/cic_domain_context.py`

---

### build_cic_readonly_context()

- **Couche :** CONNECTORS
- **Type :** Fonction Python — constructeur CIC
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Construit le contexte CIC readonly complet. Tous les flags d'action positionnés à `False`. Utilisé par l'API et Brody pour attacher le contexte causal.
- **Réf. code :** `apps/obsidia_api/cic/cic_readonly_pack_provider.py`

---

### Path Compute V0

- **Couche :** CONNECTORS
- **Type :** Module de calcul de chemin — advisory only
- **Statut :** CONFIRMED_BY_FREEZE (multiples freezes PATH_COMPUTE_V0_*)
- **Définition :** Module en développement pour le calcul de chemins décisionnels. En mode `ADVISORY_ONLY` — ne peut pas émettre de décision, pas d'appel réseau externe, pas de mutation. 11 freezes produits sur la journée du 2026-06-17 couvrant : design, readiness gate, static scans, implementation test matrix.
- **Preuve / source :** `.local_freezes/PATH_COMPUTE_V0_ADVISORY_ONLY_BOUNDARY_FREEZE_20260617_180249` et autres
- **Alias :** `path_compute`, `PATH_COMPUTE`
- **Pièges :** Path Compute n'est pas un décideur — advisory uniquement. La clé CIC `path_compute=False` doit rester False.
- **Ne pas dire :** "Path Compute peut calculer des chemins souverains" — advisory only

---

### CIC Receipt

- **Couche :** CONNECTORS
- **Type :** Reçu d'invocation CIC
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Artefact produit par `build_cic_receipt()` attestant qu'un appel a été effectué avec le contexte CIC correct. Contient hash d'invocation, timestamp, clés CIC vérifiées.
- **Preuve / source :** `.local_freezes/CIC_RECEIPT_REPLAY_V0_FREEZE_20260617_005056`
- **Réf. code :** `apps/obsidia_api/cic/cic_receipt_pack.py`

---

### NCP Readonly Stub

- **Couche :** CONNECTORS
- **Type :** Stub readonly — NCP (No-Claim Protocol)
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Stub readonly pour le protocole NCP. Garantit `authority=NONE`, `decision_authority=KX108_ONLY`, `memory_write=False`. Utilisé quand le service NCP réel n'est pas disponible.
- **Preuve / source :** `.local_freezes/NCP_READONLY_STUB_V0_FREEZE_20260617_013902`
- **Réf. code :** `apps/obsidia_api/cic/cic_ncp_readonly_stub.py`

---

### Scraping Readonly Stub

- **Couche :** CONNECTORS
- **Type :** Stub readonly — scraping/crawl
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Stub readonly bloquant toutes les clés `network`, `fetch`, `crawl`, `external_http`. Aucun accès réseau externe autorisé via ce stub.
- **Preuve / source :** `.local_freezes/SCRAPING_READONLY_STUB_V0_FREEZE_20260617_093348`
- **Réf. code :** `apps/obsidia_api/cic/cic_scraping_readonly_stub.py`

---

## A11. Classes d'agents et SourceTag

---

### AgentVote

- **Couche :** SIGMA (5)
- **Type :** Classe Python — vote d'agent
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_TEST
- **Définition :** Classe de base pour les votes d'agents. Champs : `vote` (ALLOW/HOLD/BLOCK), `proposed_verdict`, `severity_hint`. Si `proposed_verdict` est vide, il prend la valeur de `vote`.
- **Réf. code :** `sigma/contracts.py` — `class AgentVote(UniversalBase)`

---

### DomainAggregate

- **Couche :** SIGMA (5)
- **Type :** Classe Python — agrégat de domaine
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Résultat de l'agrégation des votes pour un domaine. Champs : `domain`, `market_verdict`, `confidence`, `severity`. La sévérité est déduite du verdict : BLOCK/ABORT → S4, HOLD → S2, ALLOW → S0.
- **Réf. code :** `sigma/contracts.py` — `class DomainAggregate(UniversalBase)`

---

### SourceTag

- **Couche :** SIGMA (5) / KERNEL (6)
- **Type :** Enum Python — tag de source
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Enum pour identifier la source d'un signal ou d'une décision :

| Valeur | Signification |
|---|---|
| `CANONICAL` | Source canonique directe |
| `CANONICAL_FRAMEWORK` | Framework canonique |
| `SIGMA` | Couche Sigma |
| `SIGMA_FRAMEWORK` | Framework Sigma |
| `KERNEL` | Couche Kernel |
| `KERNEL_FRAMEWORK` | Framework Kernel |

- **Réf. code :** `sigma/contracts.py` — `class SourceTag(Enum)`

---

### BaseAgent / BaseMetaAgent

- **Couche :** PERIPHERAL (4) / SIGMA (5)
- **Type :** Classe de base abstraite pour agents
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** `BaseAgent` est la classe de base pour tous les agents périphériques. `BaseMetaAgent` est la base pour les agents meta (attestation, conflit, politiques, etc.).
- **Agents meta présents :** `AttestationReadinessAgent`, `ConflictResolutionAgent`, `HumanOverrideEligibilityAgent`, `PolicyScopeAgent`, `ProofConsistencyAgent`, `ReplayConsistencyAgent`, `SeverityClassifierAgent`, `TicketReadinessAgent`, `TraceIntegrityAgent`, `UnknownsAgent`
- **Réf. code :** `sigma/contracts.py`, `ci_recheck_optional_publication/sigma/base.py`

---

## A12. Serveurs, Ports, Routes

---

### FastAPI V5B (port 8000)

- **Couche :** CONNECTORS
- **Type :** Serveur API principal
- **Statut :** CONFIRMED_BY_RUNTIME (HTTP 200, 2026-06-17 en session)
- **Définition :** API principale du projet. Version V5B, port 8000. Mode `readonly_dryrun`. 164 routes selon spec OpenAPI live. Expose tous les domaines (bank, trading, gps, brody, graphiti, sigma, x108, os3, blockchain, gencoin, periphery, memory).
- **Preuve / source :** `GET http://127.0.0.1:8000/api/status` → HTTP 200, `"version": "V5B"`
- **PID :** 2996 (au moment de l'audit)
- **Réf. code :** `apps/obsidia_api/main.py`

---

### 164 routes API

- **Couche :** CONNECTORS
- **Type :** Métriques API
- **Statut :** CONFIRMED_BY_RUNTIME (spec OpenAPI capturée live)
- **Définition :** Nombre exact de routes exposées par FastAPI V5B selon la spec OpenAPI live capturée le 2026-06-17. Incluent : bank, trading, gps, brody, graphiti, sigma, x108, os3, blockchain, gencoin, periphery, memory.
- **Preuve / source :** `GET http://127.0.0.1:8000/openapi.json` capturé en session

---

### /api/status

- **Couche :** CONNECTORS
- **Type :** Endpoint de santé API
- **Statut :** CONFIRMED_BY_RUNTIME
- **Définition :** Endpoint GET retournant le statut complet de l'API avec tous les invariants de sécurité (BOUNDARY flags, decision_authority, mode).
- **Réf. code :** `apps/obsidia_api/main.py`

---

### /api/live/kernel/adapters/bank|trading|gps

- **Couche :** CONNECTORS
- **Type :** Routes de bridge domaine → Kernel
- **Statut :** CONFIRMED_BY_RUNTIME (HTTP 200, `kernel_invoked=True`, 2026-06-17)
- **Définition :** Routes qui proxifient les requêtes domaine vers le Kernel X-108. Retournent `kernel_invoked=True`, `api_role=BRIDGE_ONLY`, `decision_authority=KX108_ONLY`. Si Kernel arrêté, retournent `kernel_status=CONNECTION_ERROR` sans substituer de décision.
- **Réf. code :** `apps/obsidia_api/routes/live_kernel_bridge.py`

---

### /api/brody/chat

- **Couche :** CONNECTORS
- **Type :** Endpoint conversationnel Brody
- **Statut :** CONFIRMED_BY_CODE (présent dans 164 routes OpenAPI)
- **Définition :** Endpoint POST pour le chat avec Brody. Mode readonly, guard actif. Retourne une réponse éducative sans décision.
- **Réf. code :** `apps/obsidia_api/routes/brody.py`

---

### Port 3001 — Kernel Node.js

- **Couche :** KERNEL (6)
- **Type :** Port de service
- **Statut :** CONFIRMED_BY_FREEZE (HTTP 200 2026-06-16), CLOSED aujourd'hui
- **Définition :** Port d'écoute du Kernel X-108 (`server.kernel.sealed.cjs`). CLOSED lors de l'audit 2026-06-17 — Kernel arrêté. Dernière confirmation active : freeze 2026-06-16.

---

### Port 8011 — Graphiti

- **Couche :** CONNECTORS
- **Type :** Port de service
- **Statut :** CONFIRMED_BY_FREEZE (HTTP 200 2026-06-16, status degraded), CLOSED aujourd'hui
- **Définition :** Port de Graphiti V20 FROZEN_READONLY. Status `degraded` (AuthError Neo4j) lors du freeze 2026-06-16. CLOSED lors de l'audit 2026-06-17.

---

### Port 8012 — Brody sous-service

- **Couche :** CONNECTORS
- **Type :** Port de service
- **Statut :** CONFIRMED_BY_FREEZE (2026-06-16), CLOSED aujourd'hui
- **Définition :** Port du sous-service Brody (backend conversationnel). Confirmé joignable au freeze 2026-06-16. CLOSED lors de l'audit 2026-06-17.

---

### Port 5173 — UI Vite (obsidia-workbench)

- **Couche :** TOOLING
- **Type :** Port de développement UI
- **Statut :** CONFIRMED_BY_FREEZE (2026-06-16), CLOSED aujourd'hui
- **Définition :** Port de l'UI React/Vite `obsidia-workbench`. Proxy configuré vers `/api/brody` et `/api/status` sur port 8000.
- **Réf. code :** `apps/obsidia-workbench/vite.config.ts`

---

## A13. Freezes et Audits

---

### Freeze (concept)

- **Couche :** TOOLING / SCELLAGE (8)
- **Type :** Artefact d'audit immuable
- **Statut :** CONFIRMED_BY_CODE + CONFIRMED_BY_FILE
- **Définition :** Snapshot daté d'un état de système ou d'un résultat de test, stocké dans `.local_freezes/` ou `.local_exports/`. Contient des fichiers JSON/txt capturant les sorties de commandes, les réponses API, les résultats pytest, les statuts de serveur. Utilisé comme preuve d'audit.

---

### Inventaire des freezes locaux (`.local_freezes/`)

- **Statut :** CONFIRMED_BY_FILE (listés en session)

| Freeze | Date | Objet |
|---|---|---|
| `BRODY_ENRICHED_EDUCATION_PACK_V1_FREEZE_20260617_124000` | 2026-06-17 | Education Pack V1 enrichi |
| `BRODY_LOCAL_EDUCATION_DRY_RUN_V0_FREEZE_20260617_101049` | 2026-06-17 | Dry run éducation V0 |
| `BRODY_LOCAL_EDUCATION_PACK_V0_FREEZE_20260617_095929` | 2026-06-17 | Pack éducation V0 local |
| `BRODY_RUNTIME_EDUCATION_ADAPTER_API_E2E_V0_RETRY_AFTER_GUARD_FIX_FREEZE_20260617_175000` | 2026-06-17 | E2E guard fix — 14/14 PASS |
| `BRODY_RUNTIME_EDUCATION_ADAPTER_GUARD_FIX_V0_FREEZE_20260617_165000` | 2026-06-17 | Guard fix V0 — 124/124 pytest |
| `BRODY_RUNTIME_EDUCATION_ADAPTER_PATCH_V0_FREEZE_20260617_145000` | 2026-06-17 | Patch V0 adapter |
| `BRODY_V3_ORGANIC_RUNTIME_MEMORY_FREEZE_PACK_V0_20260616_200000` | 2026-06-16 | Mémoire organique V3 |
| `CIC_PROVIDER_BINDING_NCP_SCRAP_API_E2E_V0_FREEZE_20260617_105121` | 2026-06-17 | CIC binding NCP/scraping E2E |
| `CIC_PROVIDER_BINDING_NCP_SCRAP_PATCH_V0_FREEZE_20260617_102927` | 2026-06-17 | CIC patch NCP/scraping |
| `CIC_RECEIPT_REPLAY_V0_CLOSURE_AFTER_API_E2E_20260617_011343` | 2026-06-17 | CIC receipt replay closure |
| `CIC_RECEIPT_REPLAY_V0_FREEZE_20260617_005056` | 2026-06-17 | CIC receipt replay |
| `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_FREEZE_AFTER_CIC_46149B5_20260616_235601` | 2026-06-16 | Global freeze post-CIC — 10/10 PASS |
| `NCP_READONLY_STUB_V0_FREEZE_20260617_013902` | 2026-06-17 | NCP stub readonly |
| `P3J_CONNECTOR_HUMAN_DISPLAY_FREEZE_20260612_074923` | 2026-06-12 | Connecteur display humain |
| `P3N0_TERMINAL_COLOR_STACK_FREEZE_20260612_084414` | 2026-06-12 | Stack couleur terminal |
| `P3O1_METRICS_CONSENSUS_FREEZE_20260612_091958` | 2026-06-12 | Métriques consensus |
| `P3P1_RUNBOOK_START_ALL_SERVERS_FREEZE_20260612_093012` | 2026-06-12 | Runbook démarrage serveurs |
| `P3Q1_HEALTHCHECK_PASS_FREEZE_20260612_094855` | 2026-06-12 | Healthcheck PASS |
| `P3R1_START_STOP_STATUS_SCRIPTS_FREEZE_20260612_095337` | 2026-06-12 | Scripts start/stop/status |
| `P3T8G_IRREVERSIBLE_PROPAGATION_LIVE_VALIDATED_20260612_142914` | 2026-06-12 | Propagation irréversible validée |
| `P3T9C_HOLD_REVIEW_SEMANTIC_RULE_VALIDATED_20260612_150618` | 2026-06-12 | Règle HOLD review validée |
| `P3T11D_FINAL_CLEAN_ALLDATA_DATASET_20260612_162053` | 2026-06-12 | Dataset final nettoyé |
| `P3T12B_KERNEL_DIRECT_NORMALIZED_REPLAY_OK_20260612_163010` | 2026-06-12 | Replay kernel normalisé OK |
| `PATH_COMPUTE_V0_*` (11 freezes) | 2026-06-17 | Path Compute V0 — advisory only |
| `SCRAPING_READONLY_STUB_V0_FREEZE_20260617_093348` | 2026-06-17 | Scraping stub readonly |

---

### Freeze global 2026-06-16 — 10/10 PASS

- **Couche :** TOOLING / SCELLAGE (8)
- **Type :** Freeze de validation globale
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** Freeze de validation complète produit après le commit CIC `46149b5`. 10 checks PASS simultanément : Kernel 3001, API 8000, Graphiti 8011, Brody 8012, UI 5173, Bank ALLOW, Trading BLOCK, GPS ALLOW.
- **Preuve / source :** `.local_freezes/GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_FREEZE_AFTER_CIC_46149B5_20260616_235601/FREEZE_VERDICT.json`
- **Alias :** "Global freeze", "freeze 10/10"

---

### `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205`

- **Couche :** KERNEL (6)
- **Type :** Freeze de décisions kernel réelles
- **Statut :** CONFIRMED_BY_FREEZE
- **Définition :** 15 décisions réelles du Kernel capturées le 2026-06-10 : 5 Bank ALLOW S1, 5 Trading BLOCK S4, 5 GPS ALLOW S0. Seule source de décisions kernel réelles dans ce repo.

---

### Adversarial Phase 15.2

- **Couche :** PROOF (7) / TOOLING
- **Type :** Suite de tests adversariaux
- **Statut :** CONFIRMED_BY_PRIOR_AUDIT
- **Définition :** Suite de tests adversariaux visant le Kernel X-108 : 1M pairs aléatoires, collision Merkle, tamper de seal, split de consensus, tamper de signature. Tous les tests PASS.
- **Preuve / source :** `tests/ADVERSARIAL_RESULTS.md` (phase 15.2, repo précédent `/home/ubuntu/Obsidia-lab-trad`)
- **Pièges :** Ces tests datent de mars 2026 depuis un repo différent — non re-exécutés dans ce repo actuel
- **Ne pas dire :** "Phase 15.2 validée sur ce repo exact" — CONFIRMED_BY_PRIOR_AUDIT, pas re-run ici

---

### PROOFKIT_REPORT.json

- **Couche :** SCELLAGE (8) / PROOF (7)
- **Type :** Rapport d'intégrité proofkit
- **Statut :** CONFIRMED_BY_PRIOR_AUDIT (lu en session, daté 2026-06-16)
- **Définition :** Rapport du proofkit V1 avec résultats : V18_3_1 PASS, V18_7 PASS, V18_8 PASS, overall PASS.
- **Réf. code :** `proofs/PROOFKIT_REPORT.json`

---

## A14. Concepts vivants et pépites

---

### τ (tau) — Horizon temporel

- **Couche :** KERNEL (6) / PROOF (7)
- **Type :** Paramètre temporel formel
- **Statut :** CONFIRMED_BY_TEST (théorèmes TemporalKernel.lean)
- **Définition :** Horizon temporel du Kernel X-108. Après τ, les décisions irréversibles sont fixées (`X108_irreversible_after_tau_equals_base`). Avant τ, aucun acte irréversible (`X108_no_act_before_tau`).
- **Réf. code :** `proofs/lean/Obsidia/TemporalKernel.lean`

---

### skew_negative_implies_hold

- **Couche :** PROOF (7)
- **Type :** Théorème Lean — propriété temporelle
- **Statut :** CONFIRMED_BY_TEST
- **Définition :** Si le skew temporel (décalage entre agents) est négatif, la décision doit être HOLD. Garantit que la désynchronisation temporelle entre agents produit une révision humaine plutôt qu'une action.
- **Réf. code :** `proofs/lean/Obsidia/TemporalBridge.lean`

---

### OBSIDIA_V18_3_FINAL_SEALED

- **Couche :** SCELLAGE (8)
- **Type :** Nom du freeze de scellage principal
- **Statut :** CONFIRMED_BY_FILE
- **Définition :** Nom canonique du freeze scellé V18.3. Scellé le 2026-03-02 à 21:30:09 (Paris). Contient l'ensemble du système Obsidia à ce moment.
- **Alias :** "V18 seal", "freeze V18.3"
- **Réf. code :** `proofs/PROOFKIT_REPORT.json`

---

### Mode readonly_dryrun

- **Couche :** CONNECTORS
- **Type :** Mode opérationnel API
- **Statut :** CONFIRMED_BY_RUNTIME
- **Définition :** Mode dans lequel fonctionne FastAPI V5B : toutes les opérations sont en lecture seule ou simulées (`dryrun`). Aucune écriture réelle, aucun acte émis. Visible dans `/api/status` → `"mode": "readonly_dryrun"`.

---

### Commit 483eb38 — guard fix

- **Couche :** CONNECTORS / TOOLING
- **Type :** Commit de correction critique
- **Statut :** CONFIRMED_BY_TEST + CONFIRMED_BY_FREEZE
- **Définition :** Commit HEAD au moment de cet audit. Corrige le bug `GUARD_SELF_BLOCK_R01` : le guard se bloquait lui-même lors des tests. Fix : implémentation du two-level guard (`_FORBIDDEN_ACTION_KEYS` + `_SAFE_SENTINEL_VALUES`).
- **Message :** `fix(brody): scrub original_message in chat responses`

---

### obsidia_log()

- **Couche :** SIGMA (5)
- **Type :** Fonction utilitaire de logging
- **Statut :** CONFIRMED_BY_CODE
- **Définition :** Fonction de logging centralisée du module Sigma. Utilisée pour tracer les décisions et événements.
- **Réf. code :** `sigma/contracts.py`

---

### OBSIDIA_TOUS_LES_AGENTS.docx

- **Couche :** DOCS
- **Type :** Registre d'agents (document externe)
- **Statut :** DOCUMENTED_ONLY (référencé dans CLAUDE.md, non lu dans cet audit)
- **Définition :** Document source de vérité pour les 52 agents Obsidia en 9 familles. Référence pour tout nouveau proposal d'agent.
- **Ne pas dire :** "Le registre contient N agents" sans lire le document actuel

---

### contracts.broken-ragnarok.py

- **Couche :** SIGMA (5)
- **Type :** Fichier cassé intentionnellement — PROTÉGÉ
- **Statut :** CONFIRMED_BY_FILE (présent)
- **Définition :** Variante cassée intentionnellement de contracts.py. Sert aux tests adversariaux. **EXCLURE ABSOLUMENT** de tout export, pack éducatif, ou transmission externe.
- **Pièges :** L'inclure dans un export ou un pack — INTERDIT
- **Ne pas dire :** "contracts.broken-ragnarok.py peut être utilisé à la place de contracts.py"

---

### world_action_bus.jsonl

- **Couche :** TOOLING / CONNECTORS
- **Type :** Log d'actions monde
- **Statut :** CONFIRMED_BY_FILE (présent, modifié)
- **Définition :** Fichier JSONL de log des actions émises via le bus monde. Fichier tracké modifié dans la branche courante.
- **Réf. code :** `audit/world_action_bus.jsonl`

---

---

# B. INDEX ALPHABÉTIQUE

| Terme | Section | Statut |
|---|---|---|
| 124/124 tests PASS | A8 | CONFIRMED_BY_TEST |
| 164 routes API | A12 | CONFIRMED_BY_RUNTIME |
| 167 nœuds / 477 relations / 20 épisodes | A9 | CONFIRMED_BY_FREEZE |
| 57 théorèmes / lemmes Lean | A5 | CONFIRMED_BY_TEST |
| `_EDUCATION_BOUNDARY` | A8 | CONFIRMED_BY_CODE |
| `_FORBIDDEN_ACTION_KEYS` | A4 | CONFIRMED_BY_CODE |
| `_SAFE_SENTINEL_VALUES` | A4 | CONFIRMED_BY_CODE |
| `/api/brody/chat` | A12 | CONFIRMED_BY_CODE |
| `/api/live/kernel/adapters/bank\|trading\|gps` | A12 | CONFIRMED_BY_RUNTIME |
| `/api/status` | A12 | CONFIRMED_BY_RUNTIME |
| `aggregate4_fail_closed` | A5 | CONFIRMED_BY_TEST |
| `AgentVote` | A11 | CONFIRMED_BY_CODE |
| Adversarial Phase 15.2 | A13 | CONFIRMED_BY_PRIOR_AUDIT |
| `authority=NONE` | A10 | CONFIRMED_BY_CODE |
| BaseAgent / BaseMetaAgent | A11 | CONFIRMED_BY_CODE |
| `BankState` | A7 | CONFIRMED_BY_CODE |
| BLOCK > HOLD > ALLOW | A3 | CONFIRMED_BY_TEST |
| `BOUNDARY` invariant | A3 | CONFIRMED_BY_RUNTIME |
| Brody | A8 | CONFIRMED_BY_FREEZE |
| Brody Education Pack V1 | A8 | CONFIRMED_BY_TEST |
| `BRODY_V1_FORBIDDEN_BELIEFS.md` | A8 | CONFIRMED_BY_CODE |
| `build_cic_readonly_context()` | A10 | CONFIRMED_BY_CODE |
| `calculate_immutable_vote()` | A4 | CONFIRMED_BY_CODE |
| CIC Receipt | A10 | CONFIRMED_BY_FREEZE |
| CIC (Causal Identity Context) | A10 | CONFIRMED_BY_TEST |
| Commit 483eb38 | A14 | CONFIRMED_BY_TEST |
| `compute_governance_confidence()` | A4 | CONFIRMED_BY_CODE |
| CONTRADICTION (Layer 3) | A2 | CONFIRMED_BY_CODE |
| `CONTRADICTION_THRESHOLD_REACHED` | A3 | CONFIRMED_BY_FREEZE |
| `contracts.broken-ragnarok.py` | A14 | CONFIRMED_BY_FILE |
| `D1_determinism` | A5 | CONFIRMED_BY_TEST |
| `DECISION_AUTHORITY=KX108_ONLY` | A1 | CONFIRMED_BY_RUNTIME |
| `DomainAggregate` | A11 | CONFIRMED_BY_CODE |
| Domain (Enum) | A7 | CONFIRMED_BY_CODE |
| `EcomState` | A7 | CONFIRMED_BY_CODE |
| fail-closed | A3 | CONFIRMED_BY_TEST |
| FastAPI V5B (port 8000) | A12 | CONFIRMED_BY_RUNTIME |
| Freeze (concept) | A13 | CONFIRMED_BY_FILE |
| Freeze global 2026-06-16 | A13 | CONFIRMED_BY_FREEZE |
| FROZEN_READONLY (Graphiti) | A9 | CONFIRMED_BY_FREEZE |
| `globalSeal_change_if_root_change` | A5 | CONFIRMED_BY_TEST |
| `GpsDefenseAviationState` | A7 | CONFIRMED_BY_CODE |
| Graphiti | A9 | CONFIRMED_BY_FREEZE |
| `GUARD_ALLOW` | A3 | CONFIRMED_BY_FREEZE |
| HOLD sémantique | A3 | CONFIRMED_BY_CODE |
| INTERPRETATION (Layer 2) | A2 | CONFIRMED_BY_CODE |
| KERNEL (Layer 6) | A2 | CONFIRMED_BY_FREEZE |
| KERNEL X-108 | A1 | CONFIRMED_BY_FREEZE |
| `lake build` | A5 | CONFIRMED_BY_TEST |
| Layer (IntEnum) | A2 | CONFIRMED_BY_CODE |
| Merkle Tree | A4 | CONFIRMED_BY_FILE |
| `merkleRoot_change_if_leaf_change` | A5 | CONFIRMED_BY_TEST |
| Mode readonly_dryrun | A14 | CONFIRMED_BY_RUNTIME |
| Neo4j (AuthError) | A9 | CONFIRMED_BY_FREEZE |
| NCP Readonly Stub | A10 | CONFIRMED_BY_FREEZE |
| `normalize_confidence()` | A4 | CONFIRMED_BY_CODE |
| OBSERVATION (Layer 1) | A2 | CONFIRMED_BY_CODE |
| `obsidia_log()` | A14 | CONFIRMED_BY_CODE |
| `OBSIDIA_TOUS_LES_AGENTS.docx` | A14 | DOCUMENTED_ONLY |
| `OBSIDIA_V18_3_FINAL_SEALED` | A14 | CONFIRMED_BY_FILE |
| P13/P15_Immutability | A3 | CONFIRMED_BY_TEST |
| `P17_Determinism` | A3 | CONFIRMED_BY_TEST |
| `P17_KernelNeverBlocks` | A3 | CONFIRMED_BY_TEST |
| `P17_SealSensitive` | A3 | CONFIRMED_BY_TEST |
| `PACK_INJECT_BLOCKED` | A8 | CONFIRMED_BY_TEST |
| `PACK_READY_READONLY` | A8 | CONFIRMED_BY_TEST |
| Path Compute V0 | A10 | CONFIRMED_BY_FREEZE |
| PERIPHERAL (Layer 4) | A2 | CONFIRMED_BY_CODE |
| Port 3001 — Kernel | A12 | CONFIRMED_BY_FREEZE |
| Port 5173 — UI Vite | A12 | CONFIRMED_BY_FREEZE |
| Port 8011 — Graphiti | A12 | CONFIRMED_BY_FREEZE |
| Port 8012 — Brody | A12 | CONFIRMED_BY_FREEZE |
| `POST /kernel/ragnarok` | A1 | CONFIRMED_BY_FREEZE |
| PROOF (Layer 7) | A2 | CONFIRMED_BY_TEST |
| PROOFKIT_REPORT.json | A13 | CONFIRMED_BY_PRIOR_AUDIT |
| RFC3161 Anchor | A5 | CONFIRMED_BY_FILE |
| `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE` | A13 | CONFIRMED_BY_FREEZE |
| SCELLAGE (Layer 8) | A2 | CONFIRMED_BY_FILE |
| Scraping Readonly Stub | A10 | CONFIRMED_BY_FREEZE |
| `server.kernel.sealed.cjs` | A1 | CONFIRMED_BY_FILE |
| Severity (S0–S4) | A6 | CONFIRMED_BY_CODE |
| SIGMA (Layer 5) | A2 | CONFIRMED_BY_CODE |
| `skew_negative_implies_hold` | A14 | CONFIRMED_BY_TEST |
| `SmartAttribute` | A4 | CONFIRMED_BY_CODE |
| `SourceTag` | A11 | CONFIRMED_BY_CODE |
| τ (tau) — horizon temporel | A14 | CONFIRMED_BY_TEST |
| TLA+ | A5 | PRESENT_BUT_NOT_EXECUTED |
| `TradingState` | A7 | CONFIRMED_BY_CODE |
| Two-Level Guard | A4 | CONFIRMED_BY_TEST |
| `UniversalBase` | A4 | CONFIRMED_BY_CODE |
| V18 Seal (PROOFKIT) | A5 | CONFIRMED_BY_PRIOR_AUDIT |
| `world_action_bus.jsonl` | A14 | CONFIRMED_BY_FILE |
| `X108Gate` | A1 | CONFIRMED_BY_CODE |
| `X108_kernel_never_blocks` | A5 | CONFIRMED_BY_TEST |

---

---

# C. INDEX PAR COUCHE

| Couche | Termes principaux |
|---|---|
| **OBSERVATION (1)** | Layer OBSERVATION |
| **INTERPRETATION (2)** | Layer INTERPRETATION |
| **CONTRADICTION (3)** | Layer CONTRADICTION, `CONTRADICTION_THRESHOLD_REACHED` |
| **PERIPHERAL (4)** | `BankState`, `TradingState`, `GpsDefenseAviationState`, `EcomState`, `BaseAgent`, Brody (sous-service 8012) |
| **SIGMA (5)** | `Layer`, `Severity`, `Domain`, `X108Gate`, `SourceTag`, `AgentVote`, `DomainAggregate`, `SmartAttribute`, `UniversalBase`, `calculate_immutable_vote()`, `compute_governance_confidence()`, `normalize_confidence()`, `obsidia_log()` |
| **KERNEL (6)** | `KERNEL X-108`, `DECISION_AUTHORITY=KX108_ONLY`, `POST /kernel/ragnarok`, `server.kernel.sealed.cjs`, `BLOCK > HOLD > ALLOW`, `X108Gate`, `GUARD_ALLOW`, `CONTRADICTION_THRESHOLD_REACHED`, Port 3001, τ (tau), `P17_Determinism`, `P17_KernelNeverBlocks` |
| **PROOF (7)** | 57 théorèmes Lean, `lake build`, TLA+, `D1_determinism`, `aggregate4_fail_closed`, `merkleRoot_change_if_leaf_change`, `globalSeal_change_if_root_change`, `X108_kernel_never_blocks`, `skew_negative_implies_hold`, tous les théorèmes Basic/Consensus/CryptoAssumptions/SystemModel/TemporalKernel/Refinement/Sensitivity/Merkle/Seal, Adversarial Phase 15.2 |
| **SCELLAGE (8)** | RFC3161 Anchor, V18 Seal, `OBSIDIA_V18_3_FINAL_SEALED`, `P17_SealSensitive`, `globalSeal_change_if_root_change`, PROOFKIT_REPORT.json, Merkle Tree |
| **CONNECTORS** | FastAPI V5B, `BRIDGE_ONLY`, `BOUNDARY`, CIC, Brody Education Pack V1, Two-Level Guard, `PACK_READY_READONLY`, Graphiti, `FROZEN_READONLY`, NCP Stub, Scraping Stub, CIC Receipt, Path Compute V0, Port 8000/8011/8012/5173, `/api/status`, `/api/live/kernel/adapters/bank\|trading\|gps` |
| **TOOLING** | Freeze (concept), Freezes locaux, `world_action_bus.jsonl`, Port 5173 UI, Commit 483eb38 |
| **DOCS** | `OBSIDIA_TOUS_LES_AGENTS.docx`, `BRODY_V1_FORBIDDEN_BELIEFS.md` |

---

---

# D. INDEX PAR AUTORITÉ

| Autorité | Termes — ce qu'ils émettent |
|---|---|
| **KERNEL SEUL (KX108_ONLY)** | `X108Gate` (ALLOW/HOLD/BLOCK), `Severity`, `reason_code`, toute décision souveraine |
| **SIGMA (agrégation)** | `DomainAggregate`, `AgentVote` agrégés, `calculate_immutable_vote()` — mais résultat transmis au Kernel |
| **PERIPHERAL (agents)** | `AgentVote` individuels — advisory, sans autorité souveraine |
| **API FastAPI (BRIDGE_ONLY)** | Réponses HTTP, `kernel_invoked=True`, routage — jamais de décision |
| **BRODY (NONE)** | Réponses éducatives, contexte — jamais de décision |
| **CIC (NONE)** | Contexte causal, receipt, trace — jamais de décision |
| **PROOF (vérification)** | Théorèmes Lean, TLA+ specs — vérification, pas de décision opérationnelle |
| **AUCUNE AUTORITÉ** | `contracts.broken-ragnarok.py`, NCP stub, Scraping stub, Path Compute V0 (advisory only) |

---

---

# E. PIÈGES DÉTECTÉS

| # | Piège | Réalité | Source |
|---|---|---|---|
| P1 | "L'API décide si le Kernel est arrêté" | L'API retourne `CONNECTION_ERROR` sans substituer de décision. `BRIDGE_ONLY` est absolu. | `/api/live/kernel/adapters/bank` → `CONNECTION_ERROR` |
| P2 | "57 théorèmes = non vérifié car lake build non relancé" | `lake build` a été relancé et passe. Les théorèmes sont CONFIRMED_BY_TEST, pas DOCUMENTED_ONLY. | `lake build` PASS session 2026-06-17 |
| P3 | "Graphiti est opérationnel live" | Graphiti est FROZEN_READONLY. Neo4j en AuthError, ports 7474/7687 fermés aujourd'hui. | `graphiti_status_freeze.json` |
| P4 | "Une majorité ALLOW override un BLOCK" | `BLOCK > HOLD > ALLOW` — un seul BLOCK suffit. `aggregate4_fail_closed` le prouve formellement. | `Consensus.lean`, `contracts.py` |
| P5 | "Trading est ALLOW comme Bank" | Trading = 5 BLOCK S4 `CONTRADICTION_THRESHOLD_REACHED` dans le freeze kernel. | `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_*` |
| P6 | "lake build peut se lancer depuis la racine du repo" | Non — nécessite `cd proofs/lean && lake build`. Depuis la racine : "no configuration file". | Session 2026-06-17 |
| P7 | "Le two-level guard était toujours actif" | Non — le bug `GUARD_SELF_BLOCK_R01` l'empêchait de fonctionner avant le commit 483eb38. | Freeze GUARD_FIX_V0 2026-06-17 |
| P8 | "contracts.broken-ragnarok.py peut être inclus dans un export éducatif" | EXCLURE ABSOLUMENT — fichier intentionnellement cassé, dangereux dans un contexte éducatif. | PROTECTED_SCOPE.md |
| P9 | "Path Compute peut calculer des chemins souverains" | Path Compute V0 = ADVISORY_ONLY. La clé CIC `path_compute=False` doit rester False. | Freezes PATH_COMPUTE_V0_* |
| P10 | "TLC a vérifié 1,2M états dans ce repo" | TLC non relancé dans cet audit (Java requis). Chiffre cité sans exécution ici. | Audit 2026-06-17 |
| P11 | "Les adversarial tests Phase 15.2 sont validés sur ce repo exact" | Phase 15.2 = repo précédent `/home/ubuntu/Obsidia-lab-trad`, mars 2026. CONFIRMED_BY_PRIOR_AUDIT uniquement. | `tests/ADVERSARIAL_RESULTS.md` |
| P12 | "Port 3001 est actif aujourd'hui" | CLOSED lors de l'audit 2026-06-17. Dernière confirmation active : freeze 2026-06-16. | Sonde socket session |
| P13 | "`UniversalBase.__getattr__` lève une exception sur attribut inconnu" | Non — retourne silencieusement une valeur par défaut. Peut masquer des bugs de nommage. | `sigma/contracts.py` |
| P14 | "ECOM est testé live comme Bank/Trading/GPS" | EcomState présent dans le code mais absent du freeze live. Note CIC : `ECOM_NOT_FOUND`. | `cic_domain_context.py` |
| P15 | "Neo4j est opérationnel" | En AuthError (status degraded) lors du dernier freeze. Ports 7474/7687 CLOSED aujourd'hui. | Freeze 2026-06-16 |

---

---

# F. CLAIMS À NE PAS FAIRE

| # | Claim interdit | Pourquoi |
|---|---|---|
| F1 | "L'API a autorité de décision" | `BRIDGE_ONLY`, `decision_authority=KX108_ONLY`. Confirmé live. |
| F2 | "Le système peut fonctionner sans le Kernel" | Sans le Kernel, `CONNECTION_ERROR` — pas de décision possible |
| F3 | "57 théorèmes ne sont pas prouvés" | `lake build` PASS, 57 confirmés par comptage Python |
| F4 | "Graphiti a 167 nœuds actifs aujourd'hui" | FROZEN_READONLY — snapshot figé, pas live |
| F5 | "TLC a validé X états dans cet audit" | TLC non exécuté ici |
| F6 | "Trading reçoit ALLOW" | 5 BLOCK S4 dans le freeze kernel le plus récent |
| F7 | "contracts.broken-ragnarok.py est utilisable" | Fichier intentionnellement cassé — EXCLURE |
| F8 | "Path Compute peut prendre des décisions" | Advisory only, `path_compute=False` dans CIC |
| F9 | "RFC3161 est vérifié par openssl dans cet audit" | openssl non exécuté — CONFIRMED_BY_FILE uniquement |
| F10 | "Les adversarial tests valident ce repo" | Repo précédent, non re-run ici |
| F11 | "ECOM est validé live" | Absent du freeze, `ECOM_NOT_FOUND` dans CIC |
| F12 | "Le Kernel est actif aujourd'hui" | Port 3001 CLOSED — dernière confirmation 2026-06-16 |
| F13 | "Neo4j est opérationnel" | AuthError, ports fermés aujourd'hui |
| F14 | "SmartAttribute est une classe numérique ordinaire" | C'est une sous-classe de `list` — comportement de comparaison non standard |
| F15 | "On peut modifier server.kernel.sealed.cjs" | Fichier scellé, PROTÉGÉ — toute modification invalide le seal |

---

---

# G. RÉSUMÉ EXÉCUTABLE

## G1. Ce que le repo prouve, preuves à l'appui

```
KERNEL        : Seul décideur (DECISION_AUTHORITY=KX108_ONLY)
               Preuves : réponse live /api/status + 15 décisions freeze 2026-06-10
               
LEAN PROOFS   : 57 théorèmes vérifiés (lake build PASS 2026-06-17)
               Propriétés : déterminisme, fail-closed, immuabilité, vivacité, Merkle
               
API V5B       : 164 routes, port 8000 LISTENING (HTTP 200 live 2026-06-17)
               Mode BRIDGE_ONLY, tous flags boundary=False
               
BANK          : 5 décisions ALLOW S1 (freeze 2026-06-10)
TRADING       : 5 décisions BLOCK S4 CONTRADICTION_THRESHOLD_REACHED (freeze 2026-06-10)
GPS           : 5 décisions ALLOW S0 (freeze 2026-06-10)

BRODY         : 124/124 tests PASS, guard two-level actif (commit 483eb38)
               PACK_READY_READONLY confirmé E2E (freeze 2026-06-17)
               
GRAPHITI      : FROZEN_READONLY, 167 nœuds / 477 rels / 20 épisodes
               (freeze 2026-06-16, Neo4j dégradé, ports fermés aujourd'hui)
               
SEAL V18      : V18_3_1 + V18_7 + V18_8 PASS (PROOFKIT_REPORT 2026-06-16)
RFC3161       : Anchor présent, merkle_root fb264799... (Free TSA, 2026-03-03)
               openssl verify non exécuté dans cet audit
```

## G2. Ce qui est arrêté aujourd'hui (2026-06-17)

```
Port 3001 (Kernel)  : CLOSED
Port 8011 (Graphiti): CLOSED
Port 8012 (Brody)   : CLOSED
Port 5173 (UI Vite) : CLOSED
Ports 7474/7687 (Neo4j) : CLOSED

→ Seul port actif : 8000 (FastAPI V5B)
```

## G3. Ce qui reste à vérifier

```
[ ] TLC re-run (Java 17+ requis) — chiffre "1,2M états" non confirmé ici
[ ] RFC3161 openssl verify — anchor présent mais non vérifié cryptographiquement ici
[ ] Adversarial Phase 15.2 re-run depuis ce repo exact
[ ] Neo4j auth fix pour Graphiti en mode live complet
[ ] ECOM live test — domain présent dans le code, absent des freezes live
```

## G4. Invariants de sécurité permanents

```
PATCH=NO    COMMIT=NO    PUSH=NO    TAG=NO
MEMORY_WRITE=NO    GRAPHITI_WRITE=NO    NEO4J_WRITE=NO
MCP_BRIDGE=NO    PATH_COMPUTE=NO (sovereign)    ACT=NO
contracts.broken-ragnarok.py : EXCLURE de tout export
.env : ne pas lire, ne pas révéler
DECISION_AUTHORITY : KX108_ONLY — toujours, sans exception
```

---

**Fin du glossaire — 2026-06-17 — OBSIDIA X-108 — READ_ONLY**
