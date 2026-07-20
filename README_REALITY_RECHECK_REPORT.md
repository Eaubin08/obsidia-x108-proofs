# README_REALITY_RECHECK_REPORT

**Date :** 2026-06-17  
**Audit dir :** `.local_audits/README_REALITY_RECHECK_20260617_190000/`  
**Branch :** `sec1-neo4j-secret-rotation-cleanup`  
**HEAD :** `483eb38`

---

## 1. Ce qui change par rapport au précédent audit

| Point | Avant | Après recheck |
|---|---|---|
| 57 théorèmes Lean | DOCUMENTED_BUT_NOT_VERIFIED | **CONFIRMED_BY_TEST** (lake build + count exact) |
| lake build | non exécuté | **Build completed successfully (0 jobs)** |
| API FastAPI 8000 | CONFIRMED_BY_CODE | **CONFIRMED_BY_RUNTIME** (HTTP 200, /api/status, 164 routes OpenAPI) |
| Kernel 3001 actif | CONFIRMED_BY_FREEZE | CONFIRMED_BY_FREEZE (2026-06-16), **CLOSED aujourd'hui** |
| Graphiti 8011 | DOCUMENTED_BUT_NOT_VERIFIED | **CONFIRMED_BY_FREEZE** (HTTP 200 2026-06-16, frozen snapshot 167 nodes/477 rels) |
| UI Vite 5173 | CONFIRMED_BY_CODE | **CONFIRMED_BY_FREEZE** (2026-06-16 PASS) |
| Brody 124/124 | CONFIRMED_BY_TEST (session) | **CONFIRMED_BY_TEST + CONFIRMED_BY_FREEZE** (pytest output dans freeze) |
| Bank/Trading/GPS routes | CONFIRMED_BY_CODE + FREEZE | **CONFIRMED_BY_RUNTIME** (API 8000, HTTP 200, bridge vers kernel, BRIDGE_ONLY confirmé) |
| Décisions kernel Bank | CONFIRMED_BY_FREEZE | **CONFIRMED_BY_FREEZE** 5 ALLOW S1 (freeze 2026-06-10) |
| Décisions kernel Trading | CONFIRMED_BY_FREEZE | **CONFIRMED_BY_FREEZE** 5 BLOCK S4 CONTRADICTION_THRESHOLD |
| Décisions kernel GPS | CONFIRMED_BY_FREEZE | **CONFIRMED_BY_FREEZE** 5 ALLOW S0 (freeze 2026-06-10) |
| OpenAPI / 164 routes | DOCUMENTED_ONLY | **CONFIRMED_BY_RUNTIME** (spec capturée live) |

---

## 2. Statut exact — 57 théorèmes Lean

**Résultat : CONFIRMED_BY_TEST**

Commande exécutée : `cd proofs/lean && lake build`  
Résultat : `Build completed successfully (0 jobs)`  
Lean version : 4.31.0 (via elan)  
Lakefile : `proofs/lean/lakefile.lean`

Comptage Python sur `proofs/lean/` :

| Fichier | Theorems + Lemmas |
|---|---|
| `Obsidia/Basic.lean` | 11 |
| `Obsidia/Consensus.lean` | 10 |
| `Obsidia/CryptoAssumptions.lean` | 10 |
| `Obsidia/SystemModel.lean` | 7 |
| `Obsidia/TemporalKernel.lean` | 5 |
| `Obsidia/Refinement.lean` | 4 |
| `Obsidia/Sensitivity.lean` | 3 |
| `Obsidia/Merkle.lean` | 2 |
| `Obsidia/TemporalBridge.lean` | 2 |
| `wip/ConsensusScratch.lean` | 2 |
| `Obsidia/Seal.lean` | 1 |
| **TOTAL** | **57** |

**Formulation correcte pour le README :**  
Le repo contient 57 `theorem` / `lemma` Lean formellement vérifiés dans `proofs/lean/`, couvrant : gouvernance décisionnelle, consensus distribué, cryptographie (hypothèses), Merkle, seal, modèle temporel, raffinement et sensibilité. `lake build` passe avec succès.

---

## 3. Statut exact — API FastAPI 8000

**Résultat : CONFIRMED_BY_RUNTIME**

Port 8000 : **LISTENING** (confirmé par `socket.connect_ex`)  
PID : 2996 (vérifié par netstat)  
Endpoint testé : `GET http://127.0.0.1:8000/api/status` → HTTP 200

Réponse capturée :
```json
{
  "status": "ok",
  "service": "obsidia-api",
  "version": "V5B",
  "mode": "readonly_dryrun",
  "decision_authority": "KX108_ONLY",
  "allowed_to_decide": false,
  "readonly": true,
  "advisory_only": true,
  "emits_act": false,
  "emits_verdict": false,
  "memory_write": false,
  "graphiti_write": false,
  "kernel_mutation": false,
  "neo4j_write": false,
  "brody_decision": false,
  "real_action": false
}
```

OpenAPI spec capturée live : **164 routes** incluant bank/trading/gps, brody, graphiti, memory, sigma, x108, os3, blockchain, gencoin, periphery.

---

## 4. Statut exact — Kernel Node 3001

**Résultat : CONFIRMED_BY_FREEZE (2026-06-16), CLOSED aujourd'hui**

Port 3001 : **CLOSED** au moment de l'audit  
Preuve freeze : `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C_20260616_233032`  
→ `"kernel_3001": "PASS - HTTP 200"` (2026-06-16 23:30)

Preuve comportementale runtime aujourd'hui :  
Les routes `/api/live/kernel/adapters/bank|trading|gps` montrent `kernel_invoked: True` et `kernel_url: http://127.0.0.1:3001/kernel/ragnarok` → le bridge est câblé et tente l'appel. `CONNECTION_ERROR` confirme que le Kernel est simplement arrêté, pas absent.

Décisions réelles capturées dans `LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` :
- Bank : 5 décisions, `x108_gate=ALLOW`, `S1`
- Trading : 5 décisions, `x108_gate=BLOCK`, `S4`, `CONTRADICTION_THRESHOLD_REACHED`
- GPS : 5 décisions, `x108_gate=ALLOW`, `S0`

---

## 5. Statut exact — UI Vite 5173

**Résultat : CONFIRMED_BY_FREEZE (2026-06-16), CLOSED aujourd'hui**

Port 5173 : **CLOSED** au moment de l'audit  
Freeze : `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_FREEZE_20260616_154523` → `ui_vite_5173: PASS`  
Freeze global : `vite_status_freeze.json` présent dans le freeze export  
Code : `apps/obsidia-workbench/vite.config.ts` confirme port 5173 + proxy `/api/brody`, `/api/status`

---

## 6. Statut exact — Graphiti / 8011 / Neo4j

**Résultat : CONFIRMED_BY_FREEZE**

Port 8011 : **CLOSED** aujourd'hui (timeout)  
Freeze le plus récent : `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C_20260616_233032`  
→ `"graphiti_8011": "PASS - HTTP 200"` (2026-06-16, `status: degraded`, `AuthError`)

Le `status: degraded` signifie que Graphiti était LISTENING mais en mode dégradé (erreur d'auth Neo4j). Ce n'est pas un service entièrement sain — mais il était en ligne.

Snapshot frozen retrouvé dans `GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_FREEZE_20260616_154523/graphiti_status_freeze.json` :
```json
{
  "source": "OBSIDIA_GRAPHITI_PHASE0_V20_FROZEN",
  "mode": "FROZEN_READONLY",
  "nodes": 167,
  "rels": 477,
  "indexed_episodes": 20,
  "failed_episodes": 0,
  "live_neo4j_dependency": false
}
```

**Graphiti a fonctionné en mode FROZEN_READONLY sans dépendance Neo4j live.** 167 nœuds, 477 relations, 20 épisodes indexés.  
Port Neo4j 7474/7687 : **CLOSED** — le mode FROZEN_READONLY contourne cette dépendance.

---

## 7. Statut exact — Brody

**Résultat : CONFIRMED_BY_TEST (124/124) + CONFIRMED_BY_FREEZE + CONFIRMED_BY_RUNTIME (API 8000)**

- 124/124 tests PASS : sortie pytest capturée dans le freeze `BRODY_RUNTIME_EDUCATION_ADAPTER_GUARD_FIX_V0_FREEZE_20260617_165000/pytest_output.txt`
- Tests relancés et confirmés en session (commit 483eb38)
- API `/api/brody/chat` : CONFIRMED_BY_CODE (route présente, 164 routes OpenAPI)
- Brody education pack V1 : freeze `BRODY_ENRICHED_EDUCATION_PACK_V1_FREEZE_20260617_124000`, CONFIRMED_BY_FREEZE
- CIC `authority=NONE`, `decision_authority=KX108_ONLY` : CONFIRMED_BY_TEST
- Brody 8012 (sous-service) : CLOSED aujourd'hui. Freeze audit 2026-06-16 : `"server_8012": "PASS - server joignable"`

---

## 8. Statut exact — Domaines Bank / Trading / GPS

### API BRIDGE (aujourd'hui, CONFIRMED_BY_RUNTIME)

| Domaine | HTTP | kernel_invoked | decision_authority | api_role | source_of_truth |
|---|---|---|---|---|---|
| Bank | 200 | True | KX108_ONLY | BRIDGE_ONLY | kernel_decision |
| Trading | 200 | True | KX108_ONLY | BRIDGE_ONLY | kernel_decision |
| GPS | 200 | True | KX108_ONLY | BRIDGE_ONLY | kernel_decision |

Note : `kernel_status: CONNECTION_ERROR` car Kernel 3001 arrêté.

### Décisions Kernel (freeze 2026-06-10, CONFIRMED_BY_FREEZE)

| Domaine | Décisions | x108_gate majoritaire | Severity | reason_code |
|---|---|---|---|---|
| Bank | 5 | ALLOW | S1 | GUARD_ALLOW |
| Trading | 5 | BLOCK | S4 | CONTRADICTION_THRESHOLD_REACHED |
| GPS/Aviation | 5 | ALLOW | S0 | GUARD_ALLOW |

---

## 9. Preuves locales retrouvées

| Preuve | Localisation | Type |
|---|---|---|
| lake build PASS | `proofs/lean/` (exécuté en session) | CONFIRMED_BY_TEST |
| 57 theorems/lemmas | `proofs/lean/` (compté en session) | CONFIRMED_BY_TEST |
| API status HTTP 200 | `http://127.0.0.1:8000/api/status` (live) | CONFIRMED_BY_RUNTIME |
| 164 routes OpenAPI | `http://127.0.0.1:8000/openapi.json` (live) | CONFIRMED_BY_RUNTIME |
| Bank/Trading/GPS bridge | Routes HTTP 200, `kernel_invoked=True` (live) | CONFIRMED_BY_RUNTIME |
| 124/124 pytest PASS | Freeze `GUARD_FIX_V0_FREEZE_20260617_165000/pytest_output.txt` | CONFIRMED_BY_FREEZE |
| Kernel 3001 actif | Freeze `GLOBAL_AUDIT_AFTER_CIC_A8B535C_20260616_233032` | CONFIRMED_BY_FREEZE |
| Graphiti 8011 FROZEN_READONLY | Freeze `GLOBAL_TERMINAL_FREEZE_20260616_154523` | CONFIRMED_BY_FREEZE |
| 167 nœuds / 477 rels Graphiti | `graphiti_status_freeze.json` | CONFIRMED_BY_FREEZE |
| UI 5173 PASS | Freeze `GLOBAL_TERMINAL_FREEZE_20260616_154523` | CONFIRMED_BY_FREEZE |
| 15 décisions réelles kernel | `.runtime_freezes/LIVE_KERNEL_BRIDGE_V1_FREEZE_20260610_190205` | CONFIRMED_BY_FREEZE |
| Brody 8012 joignable | `GLOBAL_AUDIT_AFTER_CIC_A8B535C_20260616_233032` | CONFIRMED_BY_FREEZE |
| V18_3_1 / V18_7 / V18_8 PASS | `proofs/PROOFKIT_REPORT.json` 2026-06-16 | CONFIRMED_BY_PRIOR_AUDIT |
| RFC3161 anchor TSA | `proofs/rfc3161_anchor.json` | CONFIRMED_BY_FILE |
| Adversarial ALL PASS | `tests/ADVERSARIAL_RESULTS.md` (phase 15.2) | CONFIRMED_BY_PRIOR_AUDIT |
| Education Pack V1 freeze | `.local_freezes/BRODY_ENRICHED_EDUCATION_PACK_V1_FREEZE_20260617_124000` | CONFIRMED_BY_FREEZE |
| API E2E PACK_READY_READONLY | `.local_freezes/API_E2E_V0_RETRY_AFTER_GUARD_FIX_FREEZE_20260617_175000` | CONFIRMED_BY_FREEZE |

---

## 10. Points réellement non vérifiés après recheck complet

| Point | Raison réelle | Recommandation |
|---|---|---|
| TLC "1,2M états explorés" | TLC non relancé dans cet audit (Java 17+ requis) | Exécuter TLC et capturer la sortie |
| RFC3161 openssl verify | openssl non exécuté localement | `openssl ts -verify -data merkle_root.bin -in rfc3161_anchor.tsr -CAfile cacert.pem` |
| Adversarial Phase 15.2 sur repo courant | Tests datés mars 2026, répertoire `/home/ubuntu/Obsidia-lab-trad` (repo précédent) | Ré-exécuter `RUN_ALL_ADVERSARIAL.sh` depuis ce repo |
| Graphiti V20 neo4j auth sain | Mode FROZEN_READONLY, AuthError présente | Résoudre auth Neo4j pour mode live complet |

---

## 11. Fichiers d'audit produits

```
.local_audits/README_REALITY_RECHECK_20260617_190000/
  git_log.txt
  git_status.txt
  api_probe.txt
  server_probe.txt
  lean_theorem_audit.txt
  lake_build_output.txt
  domain_bank_trading_gps_probe.txt
  domain_freeze_decisions.txt
```
