# BRODY_V1_RND_CONTEXTUAL_MEMORY.md
# Pack: BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Statut de ce fichier : HISTORIC_USEFUL + SYNTHESIS_ONLY + RND_TO_CONFIRM
# IMPORTANT : Aucun élément de ce fichier n'est une vérité canonique d'autorité.
# Source principale : ZIP Cowork education brody.zip (BRODY_WIDE_RND_DISCOVERY_V0)

---

## Préambule — Règle de lecture

Ce fichier contient la R&D Cowork utile pour la compréhension contextualisée de Brody.
Chaque élément porte un statut explicite. Brody peut s'en nourrir pour comprendre
le projet, mais ne doit jamais les présenter comme des vérités canoniques.

**Hiérarchie de confiance de ce fichier :**
```
VALIDATED_BY_REPO       → Ne figure PAS ici (voir BRODY_V1_CANONICAL_CORE.md)
HISTORIC_USEFUL         → Utile pour contextualisation, sources partiellement vérifiables
SYNTHESIS_ONLY          → Construit par Cowork depuis lectures — non source directe
RND_TO_CONFIRM          → À confirmer avant toute citation comme fait
SCAN_INDICATIVE_ONLY    → Chiffres de scan, indicatifs uniquement
```

---

## Section A — Historique du projet (HISTORIC_USEFUL)

**Source :** `BRODY_PROJECT_HISTORY.md` (ZIP Cowork, HISTORIC_USEFUL)
**Note :** Éléments observés via audits locaux et git — vérifiables mais non tous relus directement.

### Audits locaux observés (historique)

Des audits récurrents sur le module BRODY ont été identifiés dans `_local_audits/` :

| Date obs. | Audit | Thème |
|---|---|---|
| 2026-05-14 | BRODY_X108_FULL_STABILIZED_SYSTEM_FINAL_SMOKE_READONLY | Smoke test complet |
| 2026-05-14 | BRODY_NON_ACTIVATED_LAYERS_INTEGRITY_TEST_READONLY | Couches non activées |
| 2026-05-14 | BRODY_RUNTIME_REAL_FILES_AUDIT_READONLY | Fichiers runtime |

Ces audits documentent une pratique régulière de vérification des invariants Brody.

### Phase P2 Banking observée (HISTORIC_USEFUL)

Sous-phases observées dans git et docs locaux :
- `P2_BANK_ADVERSARIAL_SCOPE` — scénarios adversariaux
- `P2_BANK_SECURITY_FUZZ_SCOPE` — fuzzing sécurité
- `P2_BANK_REGULATORY_PROXY_SCOPE` — proxy réglementaire
- `P2_BANK_REPLAY_RESULTS` — replay transactions

Un test de replay bancaire à grande échelle est référencé
(`sigma/tests/test_bank_replay_pack_10k.py`). Le volume exact de cas
exécutés en CI est à vérifier directement dans le fichier.

---

## Section B — Carte sémantique Obsidia X-108 (SYNTHESIS_ONLY)

**Source :** `BRODY_SEMANTIC_EDUCATION_MAP_FULL.md` (ZIP Cowork, SYNTHESIS_ONLY)
**Avertissement :** Synthèse Cowork — utile comme trame, non comme source d'autorité.

### Dual Obsidia (à croiser avec docs/GLOSSAIRE.md)

```
Espace Latent      → exploration libre, hypothèses, simulation
Noyau Déterministe → invariants mathématiques, pas d'hallucination
```

Le Dual Obsidia sépare l'exploration (où l'IA peut être créative et probabiliste)
de la décision (où seuls les invariants mathématiques s'appliquent).

### Chaîne canonique (SYNTHESIS_ONLY — à vérifier contre docs/GLOSSAIRE.md)

```
Sens → Organisation → Cohérence → Temps (Constance) → Mémoire (Stabilisation)
```

Cette chaîne décrit le parcours d'une information dans le système.
Elle est citée dans le GLOSSAIRE mais la formulation exacte est à vérifier.

### Niveaux sémantiques Cowork (SYNTHESIS_ONLY)

| Niveau | Thème | Sources citées par Cowork |
|---|---|---|
| 1 | Gouvernance déterministe ex ante | docs/KERNEL_OVERVIEW.md |
| 2 | Dual Obsidia | docs/GLOSSAIRE.md |
| 3 | Vote d'agents + agrégation Sigma | sigma/contracts.py |
| 4 | World Call Gateway | periphery/world_calls/ |
| 5 | Mémoire Fractale + Graphiti | (non lue directement) |
| 6 | Preuves formelles | proofs/lean/, formal/tla/ |

---

## Section C — Architecture étendue (SYNTHESIS_ONLY)

**Source :** `OBSIDIA_X108_MACHINATION_FULL.md` (ZIP Cowork, SYNTHESIS_ONLY)

### Double Brain (SYNTHESIS_ONLY — à vérifier contre periphery/bdf/)

```
Double Brain = deux cerveaux parallèles
Cerveau 1 : réponse rapide (pattern matching)
Cerveau 2 : réponse profonde (raisonnement structuré)
```

Source repo possible : `periphery/bdf/double_brain_router.py` (non lu dans cette session).
Statut : RND_TO_CONFIRM avant citation.

### EML — Énergie / Mémoire / Langage (SYNTHESIS_ONLY)

Couche symbolique positionnée entre Sigma et Energy dans le stack.
Le contenu exact de cette couche est à vérifier dans les sources repo.
Statut : RND_TO_CONFIRM.

---

## Section D — Registre d'agents étendu (RND_TO_CONFIRM)

**Source :** `agents/registry.md` (top 5) + ZIP Cowork (synthèse)

### Confirmés (VALIDATED_BY_REPO) :
5 agents fondateurs documentés dans `agents/registry.md` :
1. `OBSIDIA_ATLAS_INGESTOR` — Analyse multi-couches + cartes mémoire JSON
2. `CANON_GUARDIAN` — Verdict statut canonique + alertes contradictions
3. `GRAPH_BUILDER` — Graphe noeuds/liens avec force et type de relation
4. `TERMINAL_BUILDER` — Blocs commandes + preuves d'exécution attendues
5. `PROOF_SENTINEL` — Rapport preuve : invariant touché, cause, niveau de rupture

### 9 familles (VALIDATED_BY_REPO via agents/registry.md) :
1. À créer en premier / Top 5 founders
2. Code / Repo / CI
3. Documentation / Théorie / Freeze
4. Données / Logs / Audit
5. Sécurité / Pare-feu
6. Terrain / Produit / Communication
7. Frise / Arbres / Monde humain
8. Atlas Obsidia
9. Pour Étienne directement

### Agents supplémentaires (RND_TO_CONFIRM) :
Un registre interne (non committé — `OBSIDIA_TOUS_LES_AGENTS.docx`) référencerait
des agents supplémentaires dans ces 9 familles. Ni leur nombre exact ni leurs
détails ne peuvent être vérifiés depuis le repo. Statut : TO_CONFIRM_EXTERNAL_DOCX.

---

## Section E — Modules éducatifs Cowork V0 (SYNTHESIS_ONLY)

**Source :** `BRODY_EDUCATION_MODULES_V0.md` (ZIP Cowork, SYNTHESIS_ONLY)

Cowork a produit 7 modules pédagogiques lors de sa mission de découverte.
Ces modules sont des **synthèses** construites à partir des lectures —
non des copies de sources repo.

| Module | Thème | Niveau Cowork |
|---|---|---|
| MODULE 01 | Qu'est-ce qu'Obsidia X-108 ? | Débutant |
| MODULE 02 | Le Kernel X-108 | Intermédiaire |
| MODULE 03 | BRODY : le moteur de contexte | Intermédiaire |
| MODULE 04 | Sigma : l'agrégateur | Avancé |
| MODULE 05 | Preuves formelles Lean 4 + TLA+ | Expert |
| MODULE 06 | Domaines réels | Intermédiaire |
| MODULE 07 | World Call Gateway | Avancé |

Ces modules peuvent servir de **trame pédagogique** pour la rédaction
des modules V1 (voir `BRODY_V1_EDUCATION_MODULES.md`), mais chaque
affirmation doit être vérifiée contre la source repo avant usage.

---

## Section F — Limites de la R&D Cowork (SCAN_INDICATIVE_ONLY)

**Source :** `EXTRACTION_LIMITS_AND_DEFERRED_SCOPE.md` (ZIP Cowork)

Cowork a identifié ses propres limites :
- Volume de fichiers repo (indicatif — scan 2026-06-17)
- Timeout bash 45s — opérations larges impossible en un seul appel
- Production propriétaire hors scope par conception
- `OBSIDIA_TOUS_LES_AGENTS.docx` non disponible dans ce repo
- Contrainte mission READ_ONLY — pas d'exécution des verifiers

Les modules Python de `periphery/` (~50+ non lus) et `apps/obsidia_api/` (~25 brody_*.py)
restent un scope déféré pour un audit ciblé ultérieur.

Ces chiffres sont **SCAN_INDICATIVE_ONLY** — ne pas les citer comme vérité absolue.
