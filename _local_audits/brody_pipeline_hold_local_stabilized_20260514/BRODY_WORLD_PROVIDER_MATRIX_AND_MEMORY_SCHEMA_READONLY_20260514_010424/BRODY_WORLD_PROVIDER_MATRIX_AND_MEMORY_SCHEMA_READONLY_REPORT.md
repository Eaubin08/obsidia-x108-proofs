# BRODY_WORLD_PROVIDER_MATRIX_AND_MEMORY_SCHEMA_READONLY — REPORT
## Timestamp: 20260514_010424
## Status: COMPLETE | READONLY

---

## PARTIE 1 — Vérification état actuel

| Check | Valeur | Status |
|---|---|---|
| Staged files root | 136 | PASS |
| Inner repo dirty | 1 fichier (LOW_MATERIAL patch uniquement) | PASS |
| Batch BrodyImportedMemory | 42 nodes | PRESENT |
| BrodyMemoryDoc total | 3267 | PRESENT |
| Neo4j labels live | 8 labels | CONFIRMED |
| 4 audit dirs présents | Oui | PASS |

**Neo4j labels:** BrodyImportedMemory, BrodyMemoryDoc, BrodyMemoryTag, Community, Document, Entity, Episodic, Saga

---

## PARTIE 2 — World Provider Matrix

| Provider | Status | Read | Write | POST | Crawler |
|---|---|---|---|---|---|
| LOCAL_FILES | ACTIVE_READONLY | Y | N | N | N |
| LOCAL_AUDITS | ACTIVE_READONLY | Y | N | N | N |
| GRAPHITI_READ | ACTIVE_READONLY | Y | N | N | N |
| NEO4J_READ | ACTIVE_READONLY | Y | N | N | N |
| API_GET_ONLY | ACTIVE_READONLY | Y | N | N | N |
| WEB_GET_ONLY | AVAILABLE_READONLY | Y | N | N | N |
| MEMORY_WRITE | WRITE_EXECUTED_ONCE_CONTROLLED | Y | **N** | N | N |
| GRAPHITI_WRITE | WRITE_EXECUTED_ONCE_CONTROLLED | Y | **N** | N | N |
| NEO4J_WRITE | WRITE_EXECUTED_ONCE_CONTROLLED | Y | **N** | N | N |
| SCRAPING_CRAWLER | NOT_ALLOWED | N | N | N | **N** |
| POST_MUTATION | NOT_ALLOWED | N | N | **N** | N |
| KERNEL_BINDING | NOT_ALLOWED | N | N | N | N |
| X108_RUNTIME_BINDING | NOT_ALLOWED | N | N | N | N |

**WRITE_EXECUTED_ONCE_CONTROLLED** = un write contrôlé autorisé par l'opérateur. Le write n'est pas un standing path — WRITE_ACTIVE=false par défaut. Tout nouveau write requiert une nouvelle gate.

---

## PARTIE 3 — Mémoire par couches

| Couche | Type | Dans Neo4j | Proxy existant | Tree Family |
|---|---|---|---|---|
| USER_MEMORY | Décisions opérateur, préférences | Non | Aucun | PENDING |
| BRODY_AGENT_MEMORY | Rôle Brody, permissions, limites | Partiel | BrodyMemoryDoc | PENDING |
| SESSION_MEMORY | Sessions (dates, décisions) | Non | Via audit dirs | PENDING |
| BATCH_MEMORY | Batchs import (BATCH_ID, rollback) | **Oui** | BrodyImportedMemory | PENDING |
| CASE_MEMORY | Patches, preuves, validations | Non | Via audit files | PENDING |
| SOURCE_MEMORY | Fichiers, audits, MD, JSON | Partiel | BrodyMemoryDoc | PARTIALLY_MAPPED |
| TREE_MEMORY | 34 arbres canoniques | Partiel | BrodyMemoryTag | **MAPPED** |
| BOUNDARY_MEMORY | Droits, write path, gates | Non | Via rapports locaux | PARTIALLY_MAPPED |

**Observation critique :** BrodyMemoryDoc est actuellement un fourre-tout — il sert de proxy pour SOURCE_MEMORY, BRODY_AGENT_MEMORY, et potentiellement TREE_MEMORY. La séparation en couches distinctes est le prochain grand chantier schéma.

---

## PARTIE 4 — Schéma cible proposé

8 nœuds proposés :

```
(:BrodyUserMemory)
(:BrodyAgentMemory)
(:BrodySessionMemory)
(:BrodyBatchMemory)
(:BrodyCaseMemory)
(:BrodySourceMemory)
(:BrodyTreeMemory)
(:BrodyBoundaryMemory)
```

8 relations proposées :

```
(:BrodyUserMemory)-[:RELATED_TO_CASE]->(:BrodyCaseMemory)
(:BrodyAgentMemory)-[:RELATED_TO_CASE]->(:BrodyCaseMemory)
(:BrodySessionMemory)-[:PRODUCED_CASE]->(:BrodyCaseMemory)
(:BrodyBatchMemory)-[:IMPORTED_CASE]->(:BrodyCaseMemory)
(:BrodyCaseMemory)-[:DERIVED_FROM]->(:BrodySourceMemory)
(:BrodyCaseMemory)-[:BELONGS_TO_TREE]->(:BrodyTreeMemory)
(:BrodyCaseMemory)-[:GUARDED_BY]->(:BrodyBoundaryMemory)
(:BrodyCaseMemory)-[:RELATED_TO]->(:BrodyCaseMemory)
```

**STATUS: PROPOSAL_ONLY. Aucun MERGE/SET/CREATE/DELETE exécuté.**

---

## PARTIE 5 — Liens mémoire candidats

12 liens identifiés :
- 9 READY (preuve directe)
- 2 PENDING_OPERATOR_REVIEW (corrélation forte, pas encore formelle)
- 1 BLOCKED_NO_EVIDENCE (pas encore de preuve)

Liens clés :
- LOW_MATERIAL patch → BRODY_AGENT_MEMORY (READY, confiance=0.97)
- Import batch 42 → BATCH_MEMORY (READY, confiance=0.99)
- Post-write validation → BOUNDARY_MEMORY (READY, confiance=0.99)
- Session 2026-05-14 → BATCH_MEMORY (READY, confiance=0.98)
- BrodyMemoryDoc corpus → CASE_MEMORY via triage (READY, confiance=0.99)

---

## PARTIE 6 — Réponses aux 12 questions

| # | Question | Réponse |
|---|---|---|
| 1 | Graphiti connecté ? | **OUI** — bolt://127.0.0.1:7688, Episodic/Entity/Community reachable |
| 2 | Neo4j connecté ? | **OUI** — 3267 BrodyMemoryDoc + 42 BrodyImportedMemory live |
| 3 | Import réel déjà exécuté ? | **OUI** — BATCH_ID=BRODY_REAL_IMPORT_20260514_003636, 42/42, integrity_pass=true |
| 4 | Mémoire rangée par couches ? | **NON** — BrodyMemoryDoc mixe source/agent/session/case. Séparation pas encore faite. |
| 5 | Couche user séparée ? | **NON** — USER_MEMORY existe seulement dans fichiers audit, pas dans Neo4j |
| 6 | Couche Brody séparée ? | **NON** — BRODY_AGENT_MEMORY partiellement dans BrodyMemoryDoc, pas séparé |
| 7 | Sessions traçables ? | **OUI (partiel)** — via timestamps audit dirs. Pas de BrodySessionMemory dans Neo4j. |
| 8 | Batchs traçables ? | **OUI** — batch_id sur 42 BrodyImportedMemory + ROLLBACK_PLAN.cypher |
| 9 | Arbres comme familles canoniques ? | **OUI** — 34 arbres / 8 familles, BrodyMemoryTag existe, anti-invention respecté |
| 10 | Manque avant schéma propre ? | 5 labels manquants + 3 familles PENDING_MAPPING + 6 gates BLOCKED |
| 11 | Déjà validé ? | Neo4j+Graphiti live, batch OK, 34 arbres mappés, LOW_MATERIAL résolu, boundaries all-false |
| 12 | Doit rester bloqué ? | POST / crawler / kernel / X108 binding/merge / T20-T22/T24/T30-T34 / git sans gate |

---

## Boundary state final

**BOUNDARY_ALL_FALSE=true**

| Flag | Valeur |
|---|---|
| readonly | true |
| memory_decision | false |
| kernel_mutation | false |
| x108_runtime_binding | false |
| x108_merge | false |
| graphiti_index_write | false |
| memory_intake | false |
| post_allowed | false |
| crawler_allowed | false |
| new_write_executed | false |
