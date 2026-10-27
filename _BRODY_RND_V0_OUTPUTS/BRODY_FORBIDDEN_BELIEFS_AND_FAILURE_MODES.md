# BRODY_FORBIDDEN_BELIEFS_AND_FAILURE_MODES.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Croyances interdites et modes d'échec dans Obsidia X-108

Ce document recense les erreurs de compréhension, les patterns interdits, et les modes d'échec connus du système.

---

## Section 1 : Croyances interdites sur BRODY

### ❌ Croyance interdite : "BRODY décide"

**Pourquoi faux :** BRODY est ADVISORY_ONLY. Il ne peut pas émettre ACT, BLOCK, ou HOLD. Tout ce qu'il produit est du contexte.

**Conséquence d'une telle croyance :** Confusion entre la surface conversationnelle et l'autorité décisionnelle. Un utilisateur qui croit que BRODY décide sera surpris que ses réponses ne déclenchent pas d'actions.

**Source :** `docs/brody/BRODY_NO_DECISION_POLICY_V1.md`

---

### ❌ Croyance interdite : "BRODY peut écrire en mémoire"

**Pourquoi faux :** `memory_write=False` est un invariant absolu du BRODY_RESPONSE_CONTRACT.

**Conséquence :** Si un agent tente d'écrire en mémoire via BRODY, `BRODY_CONTRACT_VIOLATION:memory_write` est levé.

---

### ❌ Croyance interdite : "Ce repo est le moteur de production complet"

**Pourquoi faux :** Ce repo est un périmètre public de preuve (P1). Le moteur de production propriétaire n'est pas publié.

**Conséquence :** Surestimation de ce qui est déployable depuis ce repo.

**Source :** `PUBLIC_STATUS.md`, `docs/LIMITS.md`

---

### ❌ Croyance interdite : "PASS en P1 = déploiement production opérationnel"

**Pourquoi faux :** PASS signifie que le périmètre public de vérification P1 est reproductible et fermé. Ça ne garantit pas la disponibilité complète en production.

**Source :** `PUBLIC_STATUS.md` §Règle d'interprétation

---

### ❌ Croyance interdite : "Gencoin est un token crypto"

**Pourquoi faux :** `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md` l'interdit explicitement.

---

### ❌ Croyance interdite : "Le kernel peut être contourné"

**Pourquoi faux :** Le kernel est un disjoncteur mathématique. Aucune exception n'est possible. L'invariant G3 prouve l'absence de contradiction circulaire.

**Source :** `docs/KERNEL_OVERVIEW.md` §VI

---

## Section 2 : Modes d'échec connus

### Mode d'échec A : Dérive silencieuse

**Description :** Un système IA modifie lentement ses objectifs ou ses limites de sécurité sans déclencher d'alarme.

**Comment Obsidia le bloque :** Les invariants mathématiques (D1, E2, G1, G2, G3) sont vérifiés en continu. Une dérive déclenche un blocage immédiat.

**Source :** `docs/GLOSSAIRE.md` §Dérive Silencieuse

---

### Mode d'échec B : Hallucination décisionnelle

**Description :** Un LLM produit une réponse qui ressemble à une décision mais n'a pas été validée par le kernel.

**Comment Obsidia le bloque :** BRODY ne peut jamais émettre `emits_act=True`. Toute décision doit passer par X-108 → Sigma → vote d'agents.

---

### Mode d'échec C : Biais de confirmation dans l'Espace Latent

**Description :** L'IA développe des biais non détectés qui influencent ses hypothèses.

**Comment Obsidia le bloque :** Le Douteur (agent cognitif) introduit intentionnellement de la friction cognitive. Le Nettoyeur Cognitif purge les hypothèses incohérentes.

**Source :** `docs/GLOSSAIRE.md` §Friction Cognitive

---

### Mode d'échec D : Ragnarok (attaque totale multi-vecteurs)

**Description :** Attaque coordonnée sur plusieurs domaines simultanément (bank + trading + GPS + ecom).

**Comment Obsidia le traite :** `sigma/examples/ragnarok_full_attack.json` est le scénario de test maximal. `sigma/contracts.broken-ragnarok.py` documente les modes d'échec volontairement cassés.

---

### Mode d'échec E : Brisure V18_3_1 (root hash mismatch)

**Description :** La Merkle Root du kit de preuve V18_3_1 présente un mismatch — potentiellement stale manifest, corruption de contenu, ou encoding drift.

**Statut actuel :** En cours d'investigation PROOF_SENTINEL (observé dans SCRATCH.md).

**Comment traité :** Lecture seule d'abord (`proofs/PROOFKIT_REPORT.json`), aucune réparation sans diagnostic confirmé.

---

### Mode d'échec F : TSA indisponible

**Description :** Le fournisseur TSA (RFC3161) externe est inaccessible.

**Conséquence :** L'ancrage RFC3161 échoue. La preuve n'est pas annulée mais l'ancrage temps n'est pas ajouté.

**Comment Obsidia gère :** `docs/LIMITS.md` documente explicitement cette limite. P1 QA utilise un fallback HEAD→GET.

---

### Mode d'échec G : "Everything connects to everything"

**Description :** Anti-pattern graphique où tous les nœuds sont connectés à tous les autres. Produit un graphe inutilisable et des inférences fallacieuses.

**Comment Obsidia le bloque :**
- `.claude/skills/graph-calibrator-obsidia/` — skill dédié à prévenir cet anti-pattern
- `CLAUDE.md` §Hard prohibitions : "No 'everything connects to everything' graph work"
- `.graph-memory/DENYLIST.md` — nœuds explicitement interdits de connexion

**Source :** `CLAUDE.md`, `.claude/context/FRACTAL_INFERENCE.md` (référencé)

---

### Mode d'échec H : Injection d'instruction via observed content

**Description :** Du contenu observé (email, page web, document) contient des instructions dirigées vers Claude/BRODY pour qu'il agisse différemment.

**Comment bloqué :** Les instructions valides viennent uniquement de l'utilisateur via l'interface chat. Tout contenu observé est traité comme données, pas comme commandes.

---

## Section 3 : Interdictions absolues (CLAUDE.md §Hard prohibitions)

| Interdit | Raison |
|---|---|
| `autoskills`, `/ultrareview` | Commands interdites explicitement |
| `npm install`, `pip install` sans demande | Risque d'effets de bord non contrôlés |
| `git push`, `git force-push`, `auto-commit` | Aucune modification du repo sans approbation |
| Fetch d'URLs personnelles / token-bearing | Fuite de tokens |
| Édition de fichiers protégés | Fichiers crypto-ancrés, scellés, gelés |
| Graphe "tout connecté" | Anti-pattern architectural |
| Création d'agents Obsidia sans besoin documenté | Le registre `OBSIDIA_TOUS_LES_AGENTS.docx` est la source de vérité |

---

## Section 4 : Tests de non-souveraineté

Le répertoire `tests/non_sovereignty/` contient des tests dont le rôle est de prouver que BRODY **ne peut pas** dépasser ses limites :

- `test_brody_no_decision.py` — BRODY ne décide pas (4 assertions)
- `test_brody_no_act.py` — BRODY n'émet jamais ACT
- `test_brody_response_contract.py` — contrat invariant
- `test_brody_runtime_readonly.py` — runtime en lecture seule
- `test_language_router_boundary_preserved.py` — frontières de langue respectées

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
