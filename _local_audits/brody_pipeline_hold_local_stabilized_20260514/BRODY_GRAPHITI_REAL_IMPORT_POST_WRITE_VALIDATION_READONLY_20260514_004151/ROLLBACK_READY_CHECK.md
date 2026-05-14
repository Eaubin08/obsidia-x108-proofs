# ROLLBACK_READY_CHECK
**Batch_ID :** `BRODY_REAL_IMPORT_20260514_003636`  
**Validé le :** 2026-05-14 — READONLY  
**Autorité :** KX108_ONLY

---

## État du rollback

| Check | Résultat |
|---|---|
| ROLLBACK_PLAN_FILE_EXISTS | **true** |
| Fichier | `_local_audits/BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1_20260514_003636/ROLLBACK_PLAN.cypher` |
| ROLLBACK_SCOPE_BATCH_ONLY | **true** |
| ROLLBACK_EXECUTED | **false** |
| DELETE_EXECUTED | **false** |

---

## Commande rollback (NON EXÉCUTÉE)

```cypher
MATCH (n:BrodyImportedMemory {batch_id: 'BRODY_REAL_IMPORT_20260514_003636'})
DETACH DELETE n
```

---

## Vérification du périmètre

| Champ | Valeur |
|---|---|
| Label ciblé | `BrodyImportedMemory` uniquement |
| Filtre | `batch_id = 'BRODY_REAL_IMPORT_20260514_003636'` |
| BrodyMemoryDoc impactés | **0** — corpus original intact |
| Relations | DETACH DELETE supprime relations incidentes uniquement |
| Nœuds supprimables si exécuté | **42** |

---

## Conditions d'exécution du rollback

Le rollback **NE DOIT PAS** être exécuté dans cette session car :

- `POST_IMPORT_READ_VALIDATION=PASS`
- `INTEGRITY_PASS=true`
- `IMPORTED_COUNT=42` == `EXPECTED_COUNT=42`
- `DUPLICATES_DETECTED=0`
- `LOW_MATERIAL=false`

Il ne peut être exécuté que si :
1. L'opérateur donne l'autorisation explicite
2. Un échec critique est constaté post-validation

---

**ROLLBACK_EXECUTED=false — AUTORISATION OPÉRATEUR REQUISE**
