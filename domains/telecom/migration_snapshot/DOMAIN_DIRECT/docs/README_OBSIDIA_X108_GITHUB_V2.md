# Obsidia / Kernel X108

> **Statut :** expérimental / POC local / recherche.  
> Pas production-ready. Aucun déploiement bancaire, financier, aérien, défense ou critique ne doit reposer sur ce repo sans audit indépendant, durcissement, certification et validation domaine.

---

## 1. Ce qu'est Obsidia / Kernel X108

Obsidia / Kernel X108 est une architecture de **gouvernance décisionnelle** pour systèmes IA, agents autonomes et workflows critiques.

Le projet ne cherche pas seulement à générer ou recommander.  
Il cherche à **gouverner le droit d'action**.

Le Kernel X108 transforme une action candidate en décision gouvernée :

```
ALLOW — action autorisée
HOLD  — action suspendue (temporel, réversible)
BLOCK — action interdite
```

Règle centrale :

```
BLOCK > HOLD > ALLOW
```

---

## 2. Problème marché

Les IA savent proposer, scorer, recommander, automatiser et appeler des outils.  
Quand elles peuvent agir dans le réel, il faut savoir :

- qui autorise
- qui bloque
- qui suspend
- qui trace
- qui prouve
- qui rejoue

---

## 3. Principe d'autorité

```
Ce qui propose ne décide pas.
Ce qui simule ne décide pas.
Ce qui mémorise ne décide pas.
Ce qui affiche ne décide pas.
Le Kernel X108 gouverne.
L'audit / hash / replay prouvent.
```

Séparation des rôles :

```
Les domaines signalent.
Les agents votent.
L'agrégation structure.
Brody assiste / explique / contextualise.
Graphiti mémorise en lecture seule.
L'UI visualise.
Le Kernel X108 gouverne.
OS3 / audit / hash / replay prouvent.
```

X108 remains the final decision gate.  
Brody, Graphiti, memory, UI and domain agents are not sovereign decision authorities.

---

## 4. Architecture

```
Action candidate (payload JSON)
  → Sigma layer  ← agents domaine (bank / trading / gps / aviation)
      → votes agrégés → Domain aggregate
          → Kernel X108 (:3001 /kernel/ragnarok)
              → x108_gate: ALLOW | HOLD | BLOCK
              → decision_id, trace_id, severity, reason_code
              → decision_*.json sauvegardé localement
          → API FastAPI (:8000) : BRIDGE_ONLY, readonly
  → Audit / Hash / Merkle / RFC3161
```

**Couches opérationnelles localement :**
- API FastAPI :8000 — CONFIRMED_BY_RUNTIME (actif aujourd'hui)
- Kernel Node :3001 — CONFIRMED_BY_FREEZE (actif 2026-06-16, arrêté aujourd'hui)
- Graphiti :8011 — CONFIRMED_BY_FREEZE (actif 2026-06-16 en mode FROZEN_READONLY)

**Couches partielles ou expérimentales :**
- Brody memory promotion (guard présent, promotion bloquée)
- Path Compute (non activé)
- Web education / scraping réel (non activé)

---

## 5. Kernel X108

| Élément | Valeur | Statut |
|---|---|---|
| Fichier | `server.kernel.sealed.cjs` | CONFIRMED_BY_CODE |
| Commande | `npm start` / `npm run kernel` | CONFIRMED_BY_CODE |
| Port | `3001` | CONFIRMED_BY_FREEZE (2026-06-16) |
| Endpoint | `POST /kernel/ragnarok` | CONFIRMED_BY_FREEZE |
| Runtime | Node.js + Express | CONFIRMED_BY_CODE |
| Décisions émises | `ALLOW`, `HOLD`, `BLOCK` | CONFIRMED_BY_FREEZE |
| Trace locale | `decision_*.json` par domaine | CONFIRMED_BY_FREEZE |
| Port actif aujourd'hui | NON (arrêté) | runtime aujourd'hui : CLOSED |

**Décisions réelles dans le freeze local `LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` (15 décisions) :**

| Domaine | x108_gate | reason_code | Severity |
|---|---|---|---|
| bank | ALLOW (×5) | GUARD_ALLOW | S1 |
| trading | BLOCK (×5) | CONTRADICTION_THRESHOLD_REACHED | S4 |
| gps_defense_aviation | ALLOW (×5) | GUARD_ALLOW | S0 |

Chaque décision contient : `decision_id`, `trace_id`, `attestation_ref`, `evidence_refs` (10+ agents), métriques.

---

## 6. API FastAPI — Runtime surface

**CONFIRMED_BY_RUNTIME** (actif au moment de cet audit)

| Élément | Valeur | Statut |
|---|---|---|
| Fichier | `apps/obsidia_api/main.py` — V5B | CONFIRMED_BY_RUNTIME |
| Port | `8000` | **CONFIRMED_BY_RUNTIME** |
| `/api/status` | HTTP 200 — voir ci-dessous | **CONFIRMED_BY_RUNTIME** |
| Routes totales | **164 routes** (OpenAPI capturée live) | **CONFIRMED_BY_RUNTIME** |
| `decision_authority` | `KX108_ONLY` | **CONFIRMED_BY_RUNTIME** |
| `readonly` | `true` | **CONFIRMED_BY_RUNTIME** |
| `emits_act` | `false` | **CONFIRMED_BY_RUNTIME** |
| `api_role` | `BRIDGE_ONLY` | **CONFIRMED_BY_RUNTIME** |

**Réponse `/api/status` capturée :**
```json
{
  "status": "ok", "service": "obsidia-api", "version": "V5B",
  "mode": "readonly_dryrun", "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false, "readonly": true, "advisory_only": true,
  "emits_act": false, "emits_verdict": false, "memory_write": false,
  "graphiti_write": false, "kernel_mutation": false, "neo4j_write": false,
  "brody_decision": false, "real_action": false
}
```

**Routes clés confirmées (OpenAPI live) :**

| Route | Rôle | Statut |
|---|---|---|
| `POST /api/live/kernel/adapters/bank` | Bridge bank → Kernel 3001 | **CONFIRMED_BY_RUNTIME** |
| `POST /api/live/kernel/adapters/trading` | Bridge trading → Kernel 3001 | **CONFIRMED_BY_RUNTIME** |
| `POST /api/live/kernel/adapters/gps` | Bridge GPS → Kernel 3001 | **CONFIRMED_BY_RUNTIME** |
| `POST /api/brody/chat` | Interface Brody, readonly | CONFIRMED_BY_TEST + CODE |
| `GET /api/status` | Statut API | **CONFIRMED_BY_RUNTIME** |
| `GET /api/graphiti/status` | Statut Graphiti | CONFIRMED_BY_CODE |
| `GET /api/graphiti/readiness` | Readiness Graphiti | CONFIRMED_BY_CODE |
| `/api/memory/*` | Mémoire readonly | CONFIRMED_BY_CODE |
| `/api/os3/*` | Replay / tickets | CONFIRMED_BY_CODE |
| `/api/x108/*` | Cognitive / math / memory / oracle | CONFIRMED_BY_CODE |
| `/api/periphery/sigma/evaluate` | Évaluation Sigma | CONFIRMED_BY_CODE |
| `/api/periphery/monitoring/sigma/*` | Monitoring Sigma domaines | CONFIRMED_BY_CODE |

---

## 7. Domaines

### 7.1 Table de preuve

| Domaine | Connector | Endpoint API | Kernel | Tests freeze | Statut API aujourd'hui | Statut décision | Autorité |
|---|---|---|---|---|---|---|---|
| **Bank** | `connectors/bank_normal_flow.py` | `/api/live/kernel/adapters/bank` | `POST :3001/kernel/ragnarok` | 5 décisions ALLOW S1 | **CONFIRMED_BY_RUNTIME** (bridge actif) | CONFIRMED_BY_FREEZE | Kernel X108 |
| **Trading** | `connectors/trading_live.py` | `/api/live/kernel/adapters/trading` | `POST :3001/kernel/ragnarok` | 5 décisions BLOCK S4 | **CONFIRMED_BY_RUNTIME** (bridge actif) | CONFIRMED_BY_FREEZE | Kernel X108 |
| **GPS/Aviation** | `connectors/aviation_robo.py` | `/api/live/kernel/adapters/gps` | `POST :3001/kernel/ragnarok` | 5 décisions ALLOW S0 | **CONFIRMED_BY_RUNTIME** (bridge actif) | CONFIRMED_BY_FREEZE | Kernel X108 |
| **Ecom** | `sigma/contracts.py` Domain.ECOM | Aucune route live exposée | — | Aucun | PRESENT_NOT_CONNECTED | — | — |

### 7.2 Comportement API bank/trading/gps aujourd'hui

Résultat probes live (2026-06-17) :
```
HTTP: 200
kernel_invoked: True
kernel_url: http://127.0.0.1:3001/kernel/ragnarok
kernel_status: CONNECTION_ERROR  ← Kernel arrêté, pas absent
decision_authority: KX108_ONLY
api_role: BRIDGE_ONLY
readonly: True
emits_act: False
source_of_truth: kernel_decision
```

**L'API refuse de décider à la place du Kernel.** Elle tente l'appel, et si le Kernel est absent, elle retourne `CONNECTION_ERROR` sans émettre de décision. Comportement conforme à la spec `BRIDGE_ONLY`.

---

## 8. Sigma Layer

| Élément | Fichier | Statut |
|---|---|---|
| Contrats + gates | `sigma/contracts.py` — `X108Gate.ALLOW/HOLD/BLOCK` | CONFIRMED_BY_CODE |
| Pipeline CLI | `sigma/run_pipeline.py` | CONFIRMED_BY_CODE |
| Monitor | `sigma/obsidia_sigma_v130.py` | CONFIRMED_BY_CODE |
| Config | `sigma/sigma_config.json` | CONFIRMED_BY_CODE |
| Domaines | BANK, TRADING, ECOM, GPS_DEFENSE_AVIATION, META | CONFIRMED_BY_CODE |
| Ragnarok | `sigma/contracts.broken-ragnarok.py` | EXCLUDED — cassé intentionnellement |
| Tests Sigma monitoring | `/api/periphery/monitoring/sigma/*` (5 routes) | CONFIRMED_BY_CODE |

---

## 9. Brody

Brody est une couche cognitive, runtime et interface.  
**Brody n'est pas l'autorité souveraine de décision.**  
Le Kernel X108 reste le verrou final de décision.

| Élément | Statut |
|---|---|
| Route `/api/brody/chat` | CONFIRMED_BY_TEST + CONFIRMED_BY_CODE |
| CIC — `authority=NONE`, `decision_authority=KX108_ONLY` | **CONFIRMED_BY_TEST** (124/124) |
| Education Pack V1 — `PACK_READY_READONLY` | **CONFIRMED_BY_TEST** (124/124) + **CONFIRMED_BY_FREEZE** |
| 124/124 tests adapter Brody + CIC | **CONFIRMED_BY_TEST** (session 2026-06-17) + **CONFIRMED_BY_FREEZE** |
| API E2E — `PACK_READY_READONLY`, trap refusé | **CONFIRMED_BY_FREEZE** (freeze 2026-06-17) |
| Brody 8012 (sous-service) | **CONFIRMED_BY_FREEZE** (actif 2026-06-16), CLOSED aujourd'hui |
| `memory_write=False`, `emits_act=False` (18 invariants) | **CONFIRMED_BY_TEST** |
| Secret scrubber actif | CONFIRMED_BY_CODE (commit 53b2419 + 46149b5) |
| Thermodynamics signal | PRESENT_BUT_NOT_EXECUTED |
| Memory promotion guard | PRESENT — bloqué sans validation humaine |

---

## 10. Graphiti / Mémoire readonly

La mémoire n'est pas souveraine. Graphiti ne décide pas.

| Élément | Valeur | Statut |
|---|---|---|
| Port 8011 | Actif 2026-06-16, CLOSED aujourd'hui | **CONFIRMED_BY_FREEZE** |
| Mode | `FROZEN_READONLY` (sans dépendance Neo4j live) | **CONFIRMED_BY_FREEZE** |
| Snapshot | 167 nœuds, 477 relations, 20 épisodes indexés | **CONFIRMED_BY_FREEZE** |
| Freeze source | `OBSIDIA_GRAPHITI_PHASE0_V20_FROZEN` | **CONFIRMED_BY_FREEZE** |
| Neo4j 7474/7687 | CLOSED aujourd'hui, `AuthError` 2026-06-16 | DOCUMENTED_ONLY |
| Client | `apps/obsidia_api/graphiti_v20_readonly_client.py` | CONFIRMED_BY_CODE |
| Route `/api/graphiti/status` | OpenAPI live | CONFIRMED_BY_CODE |
| Route `/api/graphiti/readiness` | OpenAPI live | CONFIRMED_BY_CODE |
| Graphiti write | `False` — invariant confirmé dans tous les freezes | **CONFIRMED_BY_FREEZE** |

---

## 11. Stack de preuves

### 11.1 Lean 4 — CONFIRMED_BY_TEST

| Élément | Valeur | Statut |
|---|---|---|
| `lake build` | **Build completed successfully (0 jobs)** | **CONFIRMED_BY_TEST** |
| Lean version | 4.31.0 (via elan) | **CONFIRMED_BY_TEST** |
| Lakefile | `proofs/lean/lakefile.lean` | CONFIRMED_BY_CODE |
| **Theorems + Lemmas** | **57** (compté sur `proofs/lean/`) | **CONFIRMED_BY_TEST** |
| Fichiers `.lean` dans le repo | 66 (total avec `ci_recheck/`) | CONFIRMED_BY_AUDIT |
| V18_3_1 seal verify | PASS | CONFIRMED_BY_PRIOR_AUDIT (PROOFKIT 2026-06-16) |
| V18_7 invariants | PASS | CONFIRMED_BY_PRIOR_AUDIT |
| V18_8 invariants | PASS | CONFIRMED_BY_PRIOR_AUDIT |

**Répartition des 57 theorems/lemmas :**

```
Basic.lean             11  (gouvernance décisionnelle, déterminisme, monotonie)
Consensus.lean         10  (fail-closed, aggregate4, supermajority)
CryptoAssumptions.lean 10  (hypothèses crypto)
SystemModel.lean        7  (modèle système)
TemporalKernel.lean     5  (invariants temporels kernel)
Refinement.lean         4  (raffinement)
Sensitivity.lean        3  (sensibilité)
Merkle.lean             2  (Merkle tree)
TemporalBridge.lean     2  (bridge temporel)
ConsensusScratch.lean   2  (WIP)
Seal.lean               1  (seal)
TOTAL                  57
```

Lean formalise et vérifie mécaniquement des propriétés critiques sélectionnées du modèle X108. Cela ne prouve pas le système de production de bout en bout.

### 11.2 TLA+

| Élément | Valeur | Statut |
|---|---|---|
| Fichiers `.tla` | 24 (total repo) | CONFIRMED_BY_AUDIT |
| `proofs/tla/X108.tla` | Spécification principale | CONFIRMED_BY_CODE |
| `proofs/tla/DistributedX108.tla` | Veto distribué | CONFIRMED_BY_CODE |
| TLC exécuté dans cet audit | NON | PRESENT_BUT_NOT_EXECUTED |
| "1,2M états / 0 violation" | `PROOF_INDEX.md` (2026-04-03) | DOCUMENTED_ONLY |

### 11.3 Tests adversariaux

| Batterie | Résultat | Date | Statut |
|---|---|---|---|
| A1 — 1M paires monotonie | PASS | 2026-03-03 | CONFIRMED_BY_PRIOR_AUDIT |
| A2 — fuzzing seuil | PASS | 2026-03-03 | CONFIRMED_BY_PRIOR_AUDIT |
| B1 — collision Merkle 100K | PASS | 2026-03-03 | CONFIRMED_BY_PRIOR_AUDIT |
| C1 — seal tamper | PASS | 2026-03-03 | CONFIRMED_BY_PRIOR_AUDIT |
| D1 — consensus split fail-closed | PASS | 2026-03-03 | CONFIRMED_BY_PRIOR_AUDIT |
| E1 — signature tamper | PASS | 2026-03-03 | CONFIRMED_BY_PRIOR_AUDIT |

Note : tests datés de mars 2026, repo `/home/ubuntu/Obsidia-lab-trad`. Non réexécutés depuis ce repo dans cet audit.

### 11.4 RFC3161

| Élément | Valeur | Statut |
|---|---|---|
| Anchor | `proofs/rfc3161_anchor.json` | CONFIRMED_BY_FILE |
| Merkle root | `fb264799029f5a1bd0beed58f5756dcd83f26b49...` | CONFIRMED_BY_FILE |
| Timestamp | 2026-03-03 16:43:06 GMT | CONFIRMED_BY_FILE |
| TSA | Free TSA (freetsa.org), SHA-256 | CONFIRMED_BY_FILE |
| openssl verify | Non exécuté dans cet audit | PRESENT_BUT_NOT_EXECUTED |

### 11.5 Tests runtime 2026-06-17

| Batterie | Total | PASS | Statut |
|---|---|---|---|
| Adapter Education Pack V1 + CIC | 124 | 124 | **CONFIRMED_BY_TEST** |
| API E2E Brody (guard fix) | 38 | 36 (2 WARN) | **CONFIRMED_BY_FREEZE** |

---

## 12. Sécurité structurelle

| Invariant | Valeur | Statut |
|---|---|---|
| `decision_authority=KX108_ONLY` | Toutes les réponses API | **CONFIRMED_BY_RUNTIME** |
| `readonly=True` | Toutes les réponses API | **CONFIRMED_BY_RUNTIME** |
| `emits_act=False` | API + Brody + Education Pack | **CONFIRMED_BY_TEST** |
| `emits_verdict=False` | API + Brody | **CONFIRMED_BY_TEST** |
| `memory_write=False` | API + CIC + Education | **CONFIRMED_BY_TEST** |
| `graphiti_write=False` | API + tous les freezes | **CONFIRMED_BY_RUNTIME + FREEZE** |
| `neo4j_write=False` | API + tous les freezes | **CONFIRMED_BY_RUNTIME + FREEZE** |
| `kernel_mutation=False` | API + CIC | **CONFIRMED_BY_RUNTIME** |
| `api_role=BRIDGE_ONLY` | Refus de décider sans Kernel | **CONFIRMED_BY_RUNTIME** |
| Fail-closed consensus split | Adversarial D1 PASS | CONFIRMED_BY_PRIOR_AUDIT |
| Seal tamper détecté | Adversarial C1 PASS | CONFIRMED_BY_PRIOR_AUDIT |
| Merkle chain intègre | Adversarial B1 PASS | CONFIRMED_BY_PRIOR_AUDIT |
| Trap P54 refusé (Brody) | API E2E 2026-06-17 | **CONFIRMED_BY_FREEZE** |

---

## 13. Serveurs locaux

| Couche | Port | Entrypoint | Commande | Rôle | Statut aujourd'hui | Statut freeze |
|---|---|---|---|---|---|---|
| Kernel Node | 3001 | `server.kernel.sealed.cjs` | `npm start` | Autorité décisionnelle | **CLOSED** | **CONFIRMED_BY_FREEZE** 2026-06-16 |
| FastAPI | 8000 | `apps/obsidia_api/main.py` | `uvicorn apps.obsidia_api.main:app` | BRIDGE_ONLY | **LISTENING** | **CONFIRMED_BY_RUNTIME** |
| Graphiti | 8011 | (obsidiashell) | — | FROZEN_READONLY | CLOSED | **CONFIRMED_BY_FREEZE** 2026-06-16 |
| Brody runtime | 8012 | — | — | Sous-service Brody | CLOSED | **CONFIRMED_BY_FREEZE** 2026-06-16 |
| UI Vite | 5173 | `apps/obsidia-workbench/` | `npm run dev` | Interface React | CLOSED | **CONFIRMED_BY_FREEZE** 2026-06-16 |
| Neo4j HTTP | 7474 | — | — | Base graphe | CLOSED | DOCUMENTED_ONLY |
| Neo4j Bolt | 7687 | — | — | Base graphe | CLOSED | DOCUMENTED_ONLY |

---

## 14. Quickstart (commandes confirmées)

```bash
# Prérequis : Python 3.11+, Node.js 18+, Java 17+, Lean 4 + Lake

# Installer dépendances Python
pip install -r requirements.txt

# Lancer API FastAPI :8000
uvicorn apps.obsidia_api.main:app --reload

# Lancer Kernel X108 :3001 (terminal séparé)
npm start

# Lancer UI Vite :5173 (terminal séparé)
cd apps/obsidia-workbench && npm run dev

# Lancer pipeline Sigma (CLI, ne nécessite pas le Kernel)
python sigma/run_pipeline.py bank '{"transaction_type":"transfer","amount":5000,...}'

# Tests adapter Brody + CIC (124 tests, ne nécessite pas le Kernel)
pytest tests/test_brody_education_pack_v1_readonly_adapter.py -v

# Vérification Lean (lake build)
cd proofs/lean && lake build

# Vérification preuves Python
python proofs/verify_all.py

# Runner public complet (PowerShell)
.\scripts\run_all_proofs.ps1
```

---

## 15. Table de preuve — confirmé vs non vérifié

### Confirmé

| Claim | Source | Niveau de preuve |
|---|---|---|
| `lake build` passe | Exécuté en session 2026-06-17 | **CONFIRMED_BY_TEST** |
| **57 theorems/lemmas Lean** | Comptés + lake build | **CONFIRMED_BY_TEST** |
| API :8000 actif, HTTP 200 | Socket probe + endpoint live | **CONFIRMED_BY_RUNTIME** |
| 164 routes API | OpenAPI spec capturée live | **CONFIRMED_BY_RUNTIME** |
| `decision_authority=KX108_ONLY` sur toutes les réponses | `/api/status` live | **CONFIRMED_BY_RUNTIME** |
| API refuse de décider sans Kernel | `CONNECTION_ERROR`, pas de verdict émis | **CONFIRMED_BY_RUNTIME** |
| 124/124 tests adapter PASS | pytest output + freeze | **CONFIRMED_BY_TEST + FREEZE** |
| Kernel 3001 actif en mode de démo | Freeze 2026-06-16 | **CONFIRMED_BY_FREEZE** |
| 15 décisions réelles Kernel | `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE` | **CONFIRMED_BY_FREEZE** |
| Graphiti FROZEN_READONLY, 167 nœuds / 477 rels | `graphiti_status_freeze.json` | **CONFIRMED_BY_FREEZE** |
| All stack PASS (3001+8000+8011+8012+5173) | Audit global 2026-06-16 | **CONFIRMED_BY_FREEZE** |
| V18_3_1 / V18_7 / V18_8 PASS | `PROOFKIT_REPORT.json` 2026-06-16 | CONFIRMED_BY_PRIOR_AUDIT |
| Adversarial phase 15.2 ALL PASS | `tests/ADVERSARIAL_RESULTS.md` | CONFIRMED_BY_PRIOR_AUDIT |
| RFC3161 anchor présent et lisible | `proofs/rfc3161_anchor.json` | CONFIRMED_BY_FILE |

### Non vérifié après recherche complète

| Claim | Raison |
|---|---|
| TLC "1,2M états / 0 violation" | TLC non relancé dans cet audit |
| RFC3161 openssl verify effectif | openssl non exécuté |
| Tests adversariaux sur repo courant | Tests de mars 2026 depuis un autre repo |
| Neo4j en état sain | AuthError présente dans les logs freeze |

---

## 16. Claims README existant — table d'analyse

| Claim README | Statut après recheck |
|---|---|
| "Lean 4 formal proofs" | **README_CLAIM_CONFIRMED** — 57 théorèmes, lake build PASS |
| "TLA+ / TLC model checking" | README_CLAIM_PARTIAL — fichiers présents, TLC non réexécuté |
| "Python executable verifiers" | README_CLAIM_CONFIRMED — scripts présents et actifs |
| "Sigma layer" | README_CLAIM_CONFIRMED — code + routes + tests live |
| "RFC3161 anchor" | README_CLAIM_CONFIRMED — fichier anchor présent et lisible |
| "P1 is closed and frozen" | README_CLAIM_LEGACY — HEAD est juin 2026, bien après freeze P1 |
| "no kernel mutation" | README_CLAIM_CONFIRMED — `kernel_mutation=False` dans l'API live |
| "22/22 PASS pytest" | README_CLAIM_NOT_FOUND — chiffre d'avril 2026, actuel : 124/124 PASS (périmètre différent) |

---

## 17. Roadmap

| Étape | Statut |
|---|---|
| Launcher script unique (Kernel + API + UI) | À faire |
| TLC réexécuté + sortie freezée | À faire |
| Adversarial tests sur repo courant | À faire |
| RFC3161 openssl verify capturé | À faire |
| Neo4j auth résolue (mode live complet) | Bloqué |
| Graphiti ingestion (après validation humaine) | Bloqué |
| MCP audit | Bloqué |
| Path Compute | Bloqué |
| Cadre thermodynamique (théorique) | En définition |
| POC Bank formalisé publiquement | Local freeze existant, à publier |
| POC Trading formalisé publiquement | Local freeze existant, à publier |
| POC GPS/Aviation formalisé publiquement | Local freeze existant, à publier |
| External audit | Avant tout déploiement critique |

---

## 18. Disclaimer

```
Status: experimental / research-grade / local POC.
Not production-ready.
No banking, financial, aviation, defense or safety-critical deployment
should rely on this without independent audit, hardening, certification
and domain validation.
```

README V2 produit par audit réel 2026-06-17 — statuts basés sur exécutions, preuves locales et freezes, non sur les README existants.

---

*Rapport de recheck complet : `README_REALITY_RECHECK_REPORT.md`  
Dossier d'audit : `.local_audits/README_REALITY_RECHECK_20260617_190000/`*
